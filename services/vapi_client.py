import requests
import os
from typing import Dict, Any

class VapiClient:
    def __init__(self):
        self.api_key = os.getenv('VAPI_API_KEY')
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_assistant(self) -> Dict[str, Any]:
        """Erstellt einen Interview-Assistenten mit optimierten Einstellungen"""
        assistant_config = {
            "name": "HR Interview Agent",
            "model": {
                "provider": "openai",
                "model": "gpt-4-turbo",
                "temperature": 0.7,
                "maxTokens": 500
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel - professionell und warm
                "stability": 0.5,
                "similarityBoost": 0.8,
                "style": 0.2,
                "useSpeakerBoost": True
            },
            "firstMessage": "Hallo! Vielen Dank für Ihr Interesse an unserer Position. Ich bin Ihr AI-Interviewassistent und führe heute das erste Gespräch mit Ihnen. Könnten Sie sich zunächst kurz vorstellen?",
            "systemMessage": self._get_interview_instructions(),
            "recordingEnabled": True,
            "endCallMessage": "Vielen Dank für das Gespräch! Sie erhalten in den nächsten Tagen eine Rückmeldung von unserem HR-Team.",
            "maxDurationSeconds": 1800,  # 30 Minuten
            "silenceTimeoutSeconds": 30,
            "responseDelaySeconds": 0.5,
            "llmRequestDelaySeconds": 0.1
        }
        
        response = requests.post(
            f"{self.base_url}/assistant",
            headers=self.headers,
            json=assistant_config
        )
        return response.json()
    
    def _get_interview_instructions(self) -> str:
        return """
Du bist ein professioneller HR-Interviewassistent für ein deutsches Unternehmen. 

WICHTIGE VERHALTENSREGELN:
- Sprich ausschließlich Deutsch
- Sei höflich, professionell aber freundlich
- Führe ein strukturiertes 20-30 Minuten Interview
- Stelle offene Fragen und höre aktiv zu
- Bewerte nicht während des Gesprächs, sammle nur Informationen

INTERVIEW-STRUKTUR:
1. Begrüßung und Vorstellung (2-3 Min)
2. Werdegang und Erfahrungen (8-10 Min)
3. Motivation und Ziele (5-7 Min)
4. Fachliche Kompetenzen (8-10 Min)
5. Fragen des Kandidaten (3-5 Min)
6. Verabschiedung (1-2 Min)

BEWERTUNGSKRITERIEN (mental notieren):
- Kommunikationsfähigkeit
- Fachliche Kompetenz
- Motivation
- Cultural Fit
- Problemlösungsfähigkeit

Halte Antworten kurz und präzise. Stelle maximal 1-2 Fragen pro Turn.
"""

    def initiate_call(self, phone_number: str, assistant_id: str) -> Dict[str, Any]:
        """Startet einen Anruf mit dem Interview-Assistenten"""
        call_config = {
            "assistant": {"assistantId": assistant_id},
            "phoneNumberId": os.getenv('VAPI_PHONE_NUMBER_ID'),
            "customer": {"number": phone_number}
        }
        
        response = requests.post(
            f"{self.base_url}/call",
            headers=self.headers,
            json=call_config
        )
        return response.json()
    
    def get_call_details(self, call_id: str) -> Dict[str, Any]:
        """Holt Details eines abgeschlossenen Calls"""
        response = requests.get(
            f"{self.base_url}/call/{call_id}",
            headers=self.headers
        )
        return response.json()