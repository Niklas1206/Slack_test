"""
Demo Service - Simuliert API-Calls für Testzwecke ohne echte API-Keys
"""

import random
import time
import json
from typing import Dict, Any

class DemoVapiClient:
    """Demo-Version des Vapi Clients für Tests ohne echte API-Keys"""
    
    def __init__(self):
        self.demo_mode = True
        
    def create_assistant(self) -> Dict[str, Any]:
        """Simuliert Assistant-Erstellung"""
        return {
            "id": f"demo_assistant_{random.randint(1000, 9999)}",
            "name": "HR Interview Agent (Demo)",
            "status": "created"
        }
    
    def initiate_call(self, phone_number: str, assistant_id: str) -> Dict[str, Any]:
        """Simuliert Call-Start"""
        call_id = f"demo_call_{random.randint(10000, 99999)}"
        
        print(f"[DEMO] Würde Anruf starten an: {phone_number}")
        print(f"[DEMO] Assistant ID: {assistant_id}")
        print(f"[DEMO] Call ID: {call_id}")
        
        return {
            "id": call_id,
            "status": "initiated",
            "phone_number": phone_number,
            "assistant_id": assistant_id
        }
    
    def get_call_details(self, call_id: str) -> Dict[str, Any]:
        """Simuliert Call-Details mit Sample-Transkript"""
        
        # Demo-Transkripte für verschiedene Kandidatentypen (guter, mittlerer, schlechter)
        sample_transcripts = [
            """
Interviewer: Hallo! Vielen Dank für Ihr Interesse an unserer Position. Könnten Sie sich zunächst kurz vorstellen?

Kandidat: Hallo! Ja gerne. Ich bin Max Mustermann, 28 Jahre alt und arbeite seit 5 Jahren als Software Entwickler. Ich habe Informatik studiert und spezialisiere mich hauptsächlich auf Python und JavaScript. Zurzeit arbeite ich bei einer kleinen Firma, aber ich suche neue Herausforderungen.

Interviewer: Das klingt interessant! Können Sie mir mehr über Ihre aktuellen Projekte erzählen?

Kandidat: Aktuell entwickle ich eine E-Commerce-Plattform mit Django und React. Wir haben auch ein Machine Learning-Modul integriert für Produktempfehlungen. Ich bin sehr motiviert und lerne gerne neue Technologien. Die Zusammenarbeit im Team gefällt mir besonders gut.

Interviewer: Warum interessieren Sie sich für unsere Position?

Kandidat: Ihre Firma hat einen sehr guten Ruf in der Branche und ich finde Ihre Projekte im Bereich KI sehr spannend. Ich möchte mich weiterentwickeln und bei einem größeren Team arbeiten. Außerdem bieten Sie interessante Benefits und Weiterbildungsmöglichkeiten.

Interviewer: Haben Sie Erfahrung mit agilen Entwicklungsmethoden?

Kandidat: Ja, wir arbeiten mit Scrum. Ich bin gewohnt in Sprints zu arbeiten und regelmäßige Standups zu haben. Code Reviews sind für mich selbstverständlich und ich verwende Git für Versionskontrolle.

Interviewer: Haben Sie noch Fragen an uns?

Kandidat: Ja, wie groß ist das Entwicklungsteam und welche Technologien setzen Sie hauptsächlich ein? Und gibt es Möglichkeiten für Remote Work?

Interviewer: Vielen Dank für das Gespräch! Sie erhalten in den nächsten Tagen eine Rückmeldung.
            """,
            """
Interviewer: Hallo! Vielen Dank für Ihr Interesse. Könnten Sie sich vorstellen?

Kandidat: Äh ja, hallo. Ich bin... äh... ich heiße Anna Schmidt. Ich habe... äh... Informatik studiert aber noch nicht so viel Erfahrung.

Interviewer: Können Sie mir von einem Projekt erzählen, an dem Sie gearbeitet haben?

Kandidat: Ja also... in der Uni haben wir mal eine Website gemacht. Mit HTML und CSS. War aber nicht so kompliziert. Ich habe auch mal versucht JavaScript zu lernen aber das war schwierig.

Interviewer: Warum interessieren Sie sich für diese Position?

Kandidat: Äh... ich brauche einen Job und... Programmieren ist ganz okay. Ich dachte mir... warum nicht mal probieren.

Interviewer: Haben Sie schon mal im Team gearbeitet?

Kandidat: Nicht wirklich... ich arbeite lieber alleine. Teamwork ist manchmal stressig.

Interviewer: Haben Sie Fragen?

Kandidat: Äh... wie viel verdient man denn so?
            """,
            """
Interviewer: Hallo! Freut mich, dass Sie Zeit für das Gespräch haben. Stellen Sie sich gerne vor.

Kandidat: Hallo! Sehr gerne. Ich bin Dr. Sarah Weber, Senior Software Architect mit 12 Jahren Erfahrung. Ich habe in Informatik promoviert und war zuletzt Lead Developer bei einem FinTech-Startup. Meine Expertise liegt in skalierbaren Backend-Systemen, Microservices und Cloud-Architekturen.

Interviewer: Sehr beeindruckend! Erzählen Sie von Ihren aktuellen Projekten.

Kandidat: Ich habe eine komplette Microservices-Architektur mit Kubernetes designed und implementiert. Wir haben dabei die Performance um 300% gesteigert und die Kosten um 40% reduziert. Ich habe auch ein Team von 8 Entwicklern geleitet und mentoring übernommen. Zusätzlich halte ich regelmäßig Tech-Talks und bin aktiv in der Open-Source-Community.

Interviewer: Warum wechseln Sie?

Kandidat: Ich suche neue technische Herausforderungen und möchte meine Führungskompetenzen ausbauen. Ihre Firma arbeitet an innovativen KI-Projekten, was perfekt zu meiner Vision passt. Ich möchte Teil eines Teams werden, das die Zukunft der Technologie mitgestaltet.

Interviewer: Wie gehen Sie mit schwierigen technischen Problemen um?

Kandidat: Ich analysiere systematisch, hole mir Input vom Team und nutze datengetriebene Entscheidungen. Ich bin es gewohnt, unter Zeitdruck zu arbeiten und komplexe Probleme zu strukturieren. Continuous Learning ist für mich essentiell.

Interviewer: Haben Sie Fragen?

Kandidat: Ja, wie ist die technische Roadmap für die nächsten zwei Jahre? Welche Investitionen plant das Unternehmen in neue Technologien? Und wie sieht die Karriereentwicklung für Senior-Positionen aus?
            """
        ]
        
        # Kandidatentyp basierend auf Call-ID bestimmen
        call_num = int(''.join(filter(str.isdigit, call_id)))
        candidate_type = call_num % 3  # 0=schlecht, 1=mittel, 2=gut
        transcript = sample_transcripts[candidate_type].strip()
        
        # Call-Details simulieren
        return {
            "id": call_id,
            "status": "completed",
            "duration": random.randint(900, 1800),  # 15-30 Minuten
            "transcript": transcript,
            "recording_url": f"https://demo.vapi.ai/recordings/{call_id}.mp3",
            "started_at": "2024-01-15T10:00:00Z",
            "ended_at": "2024-01-15T10:25:00Z"
        }

class DemoSlackNotifier:
    '''Demo-Version des Slack Notifiers - sendet echte Slack-Nachrichten.'''

    def __init__(self):
        import os
        slack_token = os.getenv('SLACK_BOT_TOKEN', '')

        if slack_token.startswith('xoxb-'):
            from slack_sdk import WebClient
            self.client = WebClient(token=slack_token)
            self.channel = os.getenv('SLACK_CHANNEL', 'bewerber')
            self.use_real_slack = True
            print('[INFO] Using REAL Slack notifications')
        else:
            self.use_real_slack = False
            print('[INFO] Using simulated Slack notifications')

    def send_interview_result(self, evaluation: Dict[str, Any], candidate_phone: str, call_id: str):
        '''Sendet Interview-Ergebnis an Slack (echt oder simuliert).'''
        empfehlung = evaluation.get('gesamtbewertung', {}).get('empfehlung', 'UNENTSCHIEDEN')
        score = evaluation.get('gesamtbewertung', {}).get('score', 0)
        reason_text = self._build_reason_text(evaluation)

        if self.use_real_slack:
            return self._send_real_slack_message(evaluation, candidate_phone, call_id, reason_text)

        print("\n[DEMO] Slack-Nachricht wuerde gesendet werden:")
        print(f"Kanal: #{getattr(self, 'channel', 'bewerber')}")
        print(f"Kandidat: {candidate_phone}")
        print(f"Score: {score}/10")
        print(f"Empfehlung: {empfehlung}")
        print(f"Call ID: {call_id}")
        if reason_text:
            print('Begruendung:')
            print(reason_text)
        if 'einzelbewertungen' in evaluation:
            for kategorie, bewertung in evaluation['einzelbewertungen'].items():
                print(f"  - {kategorie.title()}: {bewertung.get('score', 0)}/10")
        if evaluation.get('naechste_schritte'):
            print(f"Naechste Schritte: {evaluation['naechste_schritte']}")
        return {'ts': f'demo_message_{random.randint(1000, 9999)}'}

    def _send_real_slack_message(self, evaluation: Dict[str, Any], candidate_phone: str, call_id: str, reason_text: str):
        '''Sendet echte Slack-Nachricht.'''
        try:
            empfehlung = evaluation.get('gesamtbewertung', {}).get('empfehlung', 'UNENTSCHIEDEN')
            score = evaluation.get('gesamtbewertung', {}).get('score', 0)

            color_map = {
                'EINLADEN': 'good',
                'ABLEHNEN': 'danger',
                'UNENTSCHIEDEN': 'warning',
            }
            color = color_map.get(empfehlung, 'good')

            blocks = [
                {
                    'type': 'header',
                    'text': {
                        'type': 'plain_text',
                        'text': f'Interview abgeschlossen - {empfehlung}',
                    },
                },
                {
                    'type': 'section',
                    'fields': [
                        {'type': 'mrkdwn', 'text': f'*Kandidat:* {candidate_phone}'},
                        {'type': 'mrkdwn', 'text': f'*Gesamtscore:* {score}/10'},
                        {'type': 'mrkdwn', 'text': f'*Call ID:* {call_id}'},
                        {'type': 'mrkdwn', 'text': f'*Empfehlung:* {empfehlung}'},
                    ],
                },
            ]

            if reason_text:
                blocks.append({
                    'type': 'section',
                    'text': {'type': 'mrkdwn', 'text': f'*Begruendung:*\\n{reason_text}'},
                })

            einzelbewertungen = evaluation.get('einzelbewertungen', {})
            if einzelbewertungen:
                lines = []
                for kategorie, bewertung in einzelbewertungen.items():
                    detail = f"- {kategorie.title()}: {bewertung.get('score', 0)}/10"
                    kommentar = bewertung.get('kommentar', '').strip()
                    if kommentar:
                        detail += f" ({kommentar})"
                    lines.append(detail)
                if lines:
                    blocks.append({
                        'type': 'section',
                        'text': {'type': 'mrkdwn', 'text': '*Einzelbewertungen:*\\n' + '\\n'.join(lines)},
                    })

            if evaluation.get('naechste_schritte'):
                blocks.append({
                    'type': 'section',
                    'text': {'type': 'mrkdwn', 'text': f"*Naechste Schritte:*\\n{evaluation['naechste_schritte']}"},
                })

            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                attachments=[{'color': color, 'fallback': f'Interview Result: {empfehlung}'}],
            )
            print(f'[SUCCESS] Slack message sent to #{self.channel}')
            return response

        except Exception as exc:
            print(f'[ERROR] Slack notification failed: {exc}')
            return None

    def send_error_notification(self, error_message: str, call_id: str = None):
        '''Sendet Fehler-Benachrichtigung.'''
        if self.use_real_slack:
            try:
                self.client.chat_postMessage(
                    channel=self.channel,
                    text=f"FEHLER: Interview System Error\\n{error_message}\\nCall ID: {call_id or 'Unknown'}",
                )
            except Exception as exc:
                print(f'[ERROR] Slack error notification failed: {exc}')
        else:
            print("\n[DEMO] Fehler-Slack-Nachricht:")
            print(f"Error: {error_message}")
            print(f"Call ID: {call_id or 'Unknown'}")

    @staticmethod
    def _build_reason_text(evaluation: Dict[str, Any]) -> str:
        summary = evaluation.get('zusammenfassung', '').strip()
        strengths = [item for item in evaluation.get('staerken', []) if item]
        weaknesses = [item for item in evaluation.get('schwaechen', []) if item]

        sections = []
        if summary:
            sections.append(summary)
        if strengths:
            sections.append('*Pluspunkte:*\\n' + '\\n'.join(f'- {item}' for item in strengths))
        if weaknesses:
            sections.append('*Zu beachten:*\\n' + '\\n'.join(f'- {item}' for item in weaknesses))

        return '\\n\\n'.join(sections).strip()

class DemoEvaluator:
    """Demo-Version des Interview Evaluators"""
    
    def __init__(self):
        self.demo_mode = True
    
    def evaluate_interview(self, transcript: str) -> Dict[str, Any]:
        """Simuliert Interview-Bewertung basierend auf Transkript-Keywords"""
        
        # Einfache Keyword-basierte Bewertung für Demo
        keywords_positive = ['erfahrung', 'projekt', 'team', 'motiviert', 'lernen', 'technologie', 'entwicklung']
        keywords_negative = ['äh', 'nicht', 'schwierig', 'weiß nicht', 'keine ahnung']
        
        positive_count = sum(1 for word in keywords_positive if word.lower() in transcript.lower())
        negative_count = sum(1 for word in keywords_negative if word.lower() in transcript.lower())
        
        # Basis-Score berechnen
        base_score = 5 + positive_count - negative_count
        base_score = max(1, min(10, base_score))  # 1-10 begrenzen
        
        # Verschiedene Bewertungsdimensionen simulieren
        kommunikation_score = base_score + random.uniform(-1, 1)
        fachkompetenz_score = base_score + random.uniform(-1.5, 1.5)
        motivation_score = base_score + random.uniform(-1, 1)
        cultural_fit_score = base_score + random.uniform(-1, 1)
        problemloesung_score = base_score + random.uniform(-1, 1)
        
        # Scores normalisieren
        scores = [kommunikation_score, fachkompetenz_score, motivation_score, cultural_fit_score, problemloesung_score]
        scores = [max(1, min(10, score)) for score in scores]
        
        gesamt_score = sum(scores) / len(scores)
        
        # Empfehlung ableiten
        if gesamt_score >= 7:
            empfehlung = "EINLADEN"
        elif gesamt_score <= 4:
            empfehlung = "ABLEHNEN"
        else:
            empfehlung = "UNENTSCHIEDEN"
        
        return {
            "gesamtbewertung": {
                "score": round(gesamt_score, 1),
                "empfehlung": empfehlung
            },
            "einzelbewertungen": {
                "kommunikation": {
                    "score": round(scores[0], 1),
                    "kommentar": "Ausdrucksfähigkeit und Verständlichkeit"
                },
                "fachkompetenz": {
                    "score": round(scores[1], 1),
                    "kommentar": "Technisches Wissen und Erfahrung"
                },
                "motivation": {
                    "score": round(scores[2], 1),
                    "kommentar": "Engagement und Interesse"
                },
                "cultural_fit": {
                    "score": round(scores[3], 1),
                    "kommentar": "Passung zur Unternehmenskultur"
                },
                "problemloesung": {
                    "score": round(scores[4], 1),
                    "kommentar": "Analytisches Denken"
                }
            },
            "zusammenfassung": f"Kandidat zeigt {'gute' if gesamt_score >= 6 else 'moderate'} Eignung für die Position.",
            "staerken": ["Kommunikationsfähigkeit", "Technische Grundlagen"] if gesamt_score >= 6 else ["Grundlegende Kenntnisse"],
            "schwaechen": ["Mehr Praxiserfahrung nötig"] if gesamt_score < 6 else ["Kleinere Verbesserungen möglich"],
            "naechste_schritte": f"{'Einladung zur nächsten Runde' if empfehlung == 'EINLADEN' else 'Weitere Überlegung nötig' if empfehlung == 'UNENTSCHIEDEN' else 'Absage'}"
        }
    
    def calculate_overall_score(self, einzelbewertungen: Dict) -> float:
        """Berechnet Gesamtscore"""
        weights = {
            "kommunikation": 0.25,
            "fachkompetenz": 0.30,
            "motivation": 0.20,
            "cultural_fit": 0.15,
            "problemloesung": 0.10
        }
        
        weighted_score = sum(
            einzelbewertungen.get(key, {}).get("score", 0) * weight
            for key, weight in weights.items()
        )
        
        return round(weighted_score, 2)

def is_demo_mode() -> bool:
    """Prüft ob Demo-Modus aktiv ist"""
    import os
    return os.getenv('VAPI_API_KEY', '').startswith('demo_') or os.getenv('OPENAI_API_KEY', '').startswith('demo_')