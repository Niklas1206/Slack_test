import json
import os
from typing import Any, Dict, Optional

import google.generativeai as genai


class GeminiEvaluator:
    """Gemini-basierte Interviewbewertung mit Modell-Fallback."""

    MODEL_CANDIDATES = (
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    )

    def __init__(self):
        genai.configure(api_key=os.getenv("OPENAI_API_KEY"))
        self._model_cache: Dict[str, Any] = {}

    def evaluate_interview(self, transcript: str) -> Dict[str, Any]:
        prompt = f"""
Analysiere das folgende Interview-Transkript und erstelle eine strukturierte Bewertung:

TRANSKRIPT:
{transcript}

Erstelle eine Bewertung im folgenden JSON-Format:

{
    "gesamtbewertung": {
        "score": [1-10],
        "empfehlung": "EINLADEN/ABLEHNEN/UNENTSCHIEDEN"
    },
    "einzelbewertungen": {
        "kommunikation": {
            "score": [1-10],
            "kommentar": "..."
        },
        "fachkompetenz": {
            "score": [1-10],
            "kommentar": "..."
        },
        "motivation": {
            "score": [1-10],
            "kommentar": "..."
        },
        "cultural_fit": {
            "score": [1-10],
            "kommentar": "..."
        },
        "problemloesung": {
            "score": [1-10],
            "kommentar": "..."
        }
    },
    "zusammenfassung": "Kurze Zusammenfassung der wichtigsten Punkte",
    "staerken": ["Stärke 1", "Stärke 2", "..."],
    "schwaechen": ["Schwäche 1", "Schwäche 2", "..."],
    "naechste_schritte": "Empfehlung für weiteres Vorgehen"
}

Bewerte objektiv und fair. Berücksichtige deutsche Arbeitskultur und -standards.
"""

        try:
            response = self._generate_with_fallback(prompt)
            evaluation_text = getattr(response, "text", "")
            if not evaluation_text:
                raise ValueError("Gemini response contained no text")

            try:
                return json.loads(evaluation_text)
            except json.JSONDecodeError:
                return {
                    "gesamtbewertung": {"score": 5, "empfehlung": "UNENTSCHIEDEN"},
                    "zusammenfassung": evaluation_text,
                    "error": "JSON-Parsing fehlgeschlagen",
                }

        except Exception as exc:
            return {
                "error": f"Bewertung fehlgeschlagen: {exc}",
                "gesamtbewertung": {"score": 0, "empfehlung": "FEHLER"},
            }

    def _generate_with_fallback(self, prompt: str):
        last_error: Optional[Exception] = None
        for model_name in self.MODEL_CANDIDATES:
            try:
                model = self._model_cache.get(model_name)
                if model is None:
                    model = genai.GenerativeModel(model_name)
                    self._model_cache[model_name] = model
                return model.generate_content(prompt)
            except Exception as exc:
                last_error = exc
                self._model_cache.pop(model_name, None)
        raise last_error if last_error else RuntimeError("Keine Gemini-Modelle verfügbar")

    def calculate_overall_score(self, einzelbewertungen: Dict) -> float:
        weights = {
            "kommunikation": 0.25,
            "fachkompetenz": 0.30,
            "motivation": 0.20,
            "cultural_fit": 0.15,
            "problemloesung": 0.10,
        }

        weighted_score = sum(
            einzelbewertungen.get(key, {}).get("score", 0) * weight
            for key, weight in weights.items()
        )

        return round(weighted_score, 2)
