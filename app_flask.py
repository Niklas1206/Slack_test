#!/usr/bin/env python3
"""
Flask-basiertes Backend für AI Interview Agent
Kompatibel mit Python 3.13
"""

from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os
import threading
import time
from dotenv import load_dotenv

from config.database_sqlite import DatabaseManager, InterviewSession
from services.demo_service import DemoVapiClient, DemoSlackNotifier, DemoEvaluator, is_demo_mode
from services.gemini_service import GeminiEvaluator

load_dotenv()
def build_transcript_url(call_id: str) -> str:
    base = os.getenv("TRANSCRIPT_BASE_URL")
    if not base:
        port = os.getenv("API_PORT", "8000")
        base = f"http://localhost:{port}"
    return f"{base.rstrip('/')}/interviews/{call_id}/transcript"

app = Flask(__name__)
db_manager = DatabaseManager()

# API Services Setup
gemini_api_key = os.getenv('OPENAI_API_KEY', '')
has_gemini = gemini_api_key.startswith('AIzaSy')

if is_demo_mode() and not has_gemini:
    print("[INFO] Running in DEMO MODE - using simulated services")
    vapi_client = DemoVapiClient()
    evaluator = DemoEvaluator()
    slack_notifier = DemoSlackNotifier()
elif has_gemini:
    print("[INFO] Running in GEMINI MODE - using Gemini AI for evaluation")
    vapi_client = DemoVapiClient()  # VAPI bleibt Demo
    evaluator = GeminiEvaluator()
    slack_notifier = DemoSlackNotifier()  # Slack bleibt Demo
else:
    print("[INFO] Running in PRODUCTION MODE - using real APIs")
    from services.vapi_client import VapiClient
    from services.evaluation_service import InterviewEvaluator
    from services.slack_notifier import SlackNotifier
    
    vapi_client = VapiClient()
    evaluator = InterviewEvaluator()
    slack_notifier = SlackNotifier()

# Datenbank beim Import initialisieren
db_manager.create_tables()

@app.route('/start-interview', methods=['POST'])
def start_interview():
    """Startet ein Interview mit einem Kandidaten"""
    try:
        data = request.get_json()
        candidate_phone = data.get('candidate_phone')
        position = data.get('position', 'Software Developer')
        
        if not candidate_phone:
            return jsonify({"error": "candidate_phone is required"}), 400
        
        # Erstelle Assistant (oder verwende bestehenden)
        assistant = vapi_client.create_assistant()
        assistant_id = assistant.get('id')
        
        if not assistant_id:
            return jsonify({"error": "Failed to create assistant"}), 500
        
        # Starte Anruf
        call_result = vapi_client.initiate_call(
            phone_number=candidate_phone,
            assistant_id=assistant_id
        )
        
        call_id = call_result.get('id')
        if not call_id:
            return jsonify({"error": "Failed to initiate call"}), 500
        
        # Speichere Session in DB
        db_session = db_manager.get_session()
        try:
            interview_session = InterviewSession(
                vapi_call_id=call_id,
                candidate_phone=candidate_phone,
                position=position,
                status="in_progress"
            )
            db_session.add(interview_session)
            db_session.commit()
        finally:
            db_session.close()
        
        return jsonify({
            "success": True,
            "call_id": call_id,
            "message": f"Interview started for {candidate_phone}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook/vapi', methods=['POST'])
def vapi_webhook():
    """Webhook für Vapi Events"""
    data = request.get_json()
    
    if data.get('type') == 'call-ended':
        call_id = data.get('call', {}).get('id')
        if call_id:
            # Background processing in separatem Thread
            thread = threading.Thread(target=process_completed_call, args=(call_id,))
            thread.start()
        
    return jsonify({"status": "received"})

def process_completed_call(call_id: str):
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


@app.route('/interviews/<call_id>/transcript', methods=['GET'])
def get_interview_transcript(call_id):
    db_session = db_manager.get_session()
    try:
        session = db_session.query(InterviewSession).filter_by(
            vapi_call_id=call_id
        ).first()
        if not session:
            return jsonify({'error': 'Interview not found'}), 404
        if not session.transcript:
            return jsonify({'error': 'Transcript not available'}), 404
        return jsonify({
            'call_id': session.vapi_call_id,
            'candidate_phone': session.candidate_phone,
            'transcript': session.transcript,
            'recording_url': session.recording_url,
            'completed_at': session.completed_at.isoformat() if session.completed_at else None
        })
    finally:
        db_session.close()

@app.route('/demo/complete-interview', methods=['POST'])
def demo_complete_interview():
    """Demo-Endpoint um ein Interview manuell als abgeschlossen zu markieren"""
    if not is_demo_mode():
        return jsonify({"error": "Only available in demo mode"}), 400
    
    call_id = request.get_json().get('call_id')
    if not call_id:
        return jsonify({"error": "call_id is required"}), 400
    
    # Background processing
    thread = threading.Thread(target=process_completed_call, args=(call_id,))
    thread.start()
    
    return jsonify({"message": f"Interview {call_id} wird verarbeitet"})

@app.route('/interviews', methods=['GET'])
def get_interviews():
    """Liste aller Interviews"""
    db_session = db_manager.get_session()
    try:
        sessions = db_session.query(InterviewSession).all()
        return jsonify([
            {
                "id": s.id,
                "candidate_phone": s.candidate_phone,
                "position": s.position,
                "status": s.status,
                "score": s.evaluation_score,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None
            }
            for s in sessions
        ])
    finally:
        db_session.close()

@app.route('/status', methods=['GET'])
def get_system_status():
    """System-Status und Konfiguration"""
    return jsonify({
        "status": "healthy",
        "mode": "demo" if is_demo_mode() else "production",
        "database": "SQLite",
        "version": "1.0.0"
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/')
def index():
    """Web Interface"""
    return render_template('index.html')

if __name__ == "__main__":
    # Port aus ENV oder default 8000
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "127.0.0.1")
    
    print(f"\n[START] AI Interview Agent Backend (Flask)")
    print(f"   Mode: {'DEMO' if is_demo_mode() else 'PRODUCTION'}")
    print(f"   URL: http://{host}:{port}")
    print(f"   Database: SQLite (data/interview_agent.db)")
    print(f"\n[ENDPOINTS] Available:")
    print(f"   POST /start-interview")
    print(f"   POST /webhook/vapi")
    print(f"   GET  /interviews")
    print(f"   GET  /status")
    if is_demo_mode():
        print(f"   POST /demo/complete-interview")
    
    app.run(host=host, port=port, debug=True)

