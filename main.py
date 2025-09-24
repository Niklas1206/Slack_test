from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv

from config.database_sqlite import DatabaseManager, InterviewSession
from services.vapi_client import VapiClient
from services.evaluation_service import InterviewEvaluator
from services.slack_notifier import SlackNotifier
from services.demo_service import DemoVapiClient, DemoSlackNotifier, DemoEvaluator, is_demo_mode

load_dotenv()
def build_transcript_url(call_id: str) -> str:
    base = os.getenv("TRANSCRIPT_BASE_URL")
    if not base:
        port = os.getenv("API_PORT", "8000")
        base = f"http://localhost:{port}"
    return f"{base.rstrip('/')}/interviews/{call_id}/transcript"

app = FastAPI(title="AI Interview Agent", version="1.0.0")
db_manager = DatabaseManager()

# Demo-Modus oder echte API-Clients je nach Konfiguration
if is_demo_mode():
    print("[INFO] Running in DEMO MODE - using simulated services")
    vapi_client = DemoVapiClient()
    evaluator = DemoEvaluator()
    slack_notifier = DemoSlackNotifier()
else:
    print("[INFO] Running in PRODUCTION MODE - using real APIs")
    vapi_client = VapiClient()
    evaluator = InterviewEvaluator()
    slack_notifier = SlackNotifier()

class StartInterviewRequest(BaseModel):
    candidate_phone: str
    position: str = "Software Developer"

class WebhookPayload(BaseModel):
    type: str
    call: dict

@app.on_event("startup")
async def startup():
    """Initialisiert Datenbank beim Start"""
    db_manager.create_tables()

@app.post("/start-interview")
async def start_interview(request: StartInterviewRequest):
    """Startet ein Interview mit einem Kandidaten"""
    try:
        # Erstelle Assistant (oder verwende bestehenden)
        assistant = vapi_client.create_assistant()
        assistant_id = assistant.get('id')
        
        if not assistant_id:
            raise HTTPException(status_code=500, detail="Failed to create assistant")
        
        # Starte Anruf
        call_result = vapi_client.initiate_call(
            phone_number=request.candidate_phone,
            assistant_id=assistant_id
        )
        
        call_id = call_result.get('id')
        if not call_id:
            raise HTTPException(status_code=500, detail="Failed to initiate call")
        
        # Speichere Session in DB
        db_session = db_manager.get_session()
        try:
            interview_session = InterviewSession(
                vapi_call_id=call_id,
                candidate_phone=request.candidate_phone,
                status="in_progress"
            )
            db_session.add(interview_session)
            db_session.commit()
        finally:
            db_session.close()
        
        return {
            "success": True,
            "call_id": call_id,
            "message": f"Interview started for {request.candidate_phone}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/vapi")
async def vapi_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """Webhook für Vapi Events"""
    
    if payload.type == "call-ended":
        call_id = payload.call.get('id')
        background_tasks.add_task(process_completed_call, call_id)
        
    return {"status": "received"}

async def process_completed_call(call_id: str):
    """Verarbeitet abgeschlossenen Anruf"""
    try:
        call_details = vapi_client.get_call_details(call_id)
        transcript = call_details.get('transcript', '')
        recording_url = call_details.get('recording_url')

        if not transcript:
            slack_notifier.send_error_notification(
                "Kein Transkript verfuegbar", call_id
            )
            return

        evaluation = evaluator.evaluate_interview(transcript)
        overall_score = evaluator.calculate_overall_score(
            evaluation.get('einzelbewertungen', {})
        )
        recommendation = evaluation.get('gesamtbewertung', {}).get('empfehlung')
        next_steps = evaluation.get('naechste_schritte')
        transcript_url = build_transcript_url(call_id)

        db_session = db_manager.get_session()
        try:
            session = db_session.query(InterviewSession).filter_by(
                vapi_call_id=call_id
            ).first()

            if session:
                session.status = "completed"
                session.transcript = transcript
                session.evaluation_score = overall_score
                session.set_evaluation_data(evaluation)
                session.recommendation = recommendation
                session.next_steps = next_steps
                session.recording_url = recording_url
                session.completed_at = datetime.utcnow()
                db_session.commit()

                slack_notifier.send_interview_result(
                    evaluation=evaluation,
                    candidate_phone=session.candidate_phone,
                    call_id=call_id,
                    transcript_url=transcript_url,
                )

        finally:
            db_session.close()

    except Exception as e:
        slack_notifier.send_error_notification(
            f"Processing failed: {str(e)}", call_id
        )

@app.get("/interviews")
async def get_interviews():
    """Liste aller Interviews"""
    db_session = db_manager.get_session()
    try:
        sessions = db_session.query(InterviewSession).all()
        return [
            {
                "id": s.id,
                "candidate_phone": s.candidate_phone,
                "status": s.status,
                "score": s.evaluation_score,
                "created_at": s.created_at,
                "completed_at": s.completed_at
            }
            for s in sessions
        ]
    finally:
        db_session.close()

@app.get("/interviews/{call_id}/transcript")
async def get_interview_transcript(call_id: str):
    db_session = db_manager.get_session()
    try:
        session = db_session.query(InterviewSession).filter_by(
            vapi_call_id=call_id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Interview not found")
        if not session.transcript:
            raise HTTPException(status_code=404, detail="Transcript not available")
        return {
            "call_id": session.vapi_call_id,
            "candidate_phone": session.candidate_phone,
            "transcript": session.transcript,
            "recording_url": session.recording_url,
            "completed_at": session.completed_at,
        }
    finally:
        db_session.close()

@app.post("/demo/complete-interview")
async def demo_complete_interview(call_id: str, background_tasks: BackgroundTasks):
    """Demo-Endpoint um ein Interview manuell als abgeschlossen zu markieren"""
    if not is_demo_mode():
        raise HTTPException(status_code=400, detail="Only available in demo mode")
    
    background_tasks.add_task(process_completed_call, call_id)
    return {"message": f"Interview {call_id} wird verarbeitet"}

@app.get("/status")
async def get_system_status():
    """System-Status und Konfiguration"""
    return {
        "status": "healthy",
        "mode": "demo" if is_demo_mode() else "production",
        "database": "SQLite" if is_demo_mode() else "MySQL",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    # Port aus ENV oder default 8000
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"\nStarting AI Interview Agent Backend")
    print(f"   Mode: {'DEMO' if is_demo_mode() else 'PRODUCTION'}")
    print(f"   URL: http://{host}:{port}")
    print(f"   Docs: http://{host}:{port}/docs")
    print(f"   Database: SQLite (data/interview_agent.db)")
    
    uvicorn.run(app, host=host, port=port)

