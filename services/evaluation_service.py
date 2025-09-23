import openai
import os
from typing import Dict, Any

class InterviewEvaluator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def evaluate_interview(self, transcript: str) -> Dict[str, Any]:
        """
        Bewertet ein Interview-Transkript und erstellt ein strukturiertes Protokoll
        
        Bewertungsdimensionen:
        1. Kommunikationsfähigkeit (1-10)
        2. Fachliche Kompetenz (1-10) 
        3. Motivation & Engagement (1-10)
        4. Cultural Fit (1-10)
        5. Problemlösungsfähigkeit (1-10)
        """
        
        prompt = f"""
Analysiere das folgende Interview-Transkript und erstelle eine strukturierte Bewertung:

TRANSKRIPT:
{transcript}

Erstelle eine Bewertung im folgenden JSON-Format:

{{
    "gesamtbewertung": {{
        "score": [1-10],
        "empfehlung": "EINLADEN/ABLEHNEN/UNENTSCHIEDEN"
    }},
    "einzelbewertungen": {{
        "kommunikation": {{
            "score": [1-10],
            "kommentar": "..."
        }},
        "fachkompetenz": {{
            "score": [1-10], 
            "kommentar": "..."
        }},
        "motivation": {{
            "score": [1-10],
            "kommentar": "..."
        }},
        "cultural_fit": {{
            "score": [1-10],
            "kommentar": "..."
        }},
        "problemloesung": {{
            "score": [1-10],
            "kommentar": "..."
        }}
    }},
    "zusammenfassung": "Kurze Zusammenfassung der wichtigsten Punkte",
    "staerken": ["Stärke 1", "Stärke 2", "..."],
    "schwaechen": ["Schwäche 1", "Schwäche 2", "..."],
    "naechste_schritte": "Empfehlung für weiteres Vorgehen"
}}

Bewerte objektiv und fair. Berücksichtige deutsche Arbeitskultur und -standards. Gebe auch eine ausfürhliche Angabe wieso du was bewertet hast.
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Du bist ein erfahrener HR-Experte, der Interview-Transkripte bewertet."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            evaluation_text = response.choices[0].message.content
            
            # JSON parsen (vereinfacht - in Produktion robuster implementieren)
            import json
            try:
                evaluation_data = json.loads(evaluation_text)
                return evaluation_data
            except:
                # Fallback falls JSON-Parsing fehlschlägt
                return {
                    "gesamtbewertung": {"score": 5, "empfehlung": "UNENTSCHIEDEN"},
                    "zusammenfassung": evaluation_text,
                    "error": "JSON-Parsing fehlgeschlagen"
                }
                
        except Exception as e:
            return {
                "error": f"Bewertung fehlgeschlagen: {str(e)}",
                "gesamtbewertung": {"score": 0, "empfehlung": "FEHLER"}
            }
    
    def calculate_overall_score(self, einzelbewertungen: Dict) -> float:
        """Berechnet Gesamtscore aus Einzelbewertungen mit Gewichtung"""
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