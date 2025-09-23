import os
from typing import Any, Dict, List

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackNotifier:
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.channel = os.getenv("SLACK_CHANNEL", "hr-notifications")

    def send_interview_result(self, evaluation: Dict[str, Any], candidate_phone: str, call_id: str):
        """Sendet Bewertungsergebnis an Slack-Channel."""

        color_map = {
            "EINLADEN": "#36a64f",  # Gruen
            "ABLEHNEN": "#ff0000",  # Rot
            "UNENTSCHIEDEN": "#ffaa00",  # Orange
        }

        empfehlung = evaluation.get("gesamtbewertung", {}).get("empfehlung", "UNENTSCHIEDEN")
        score = evaluation.get("gesamtbewertung", {}).get("score", 0)
        color = color_map.get(empfehlung, "#36a64f")

        message_blocks: List[Dict[str, Any]] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Interview abgeschlossen - {empfehlung}",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Kandidat:* {candidate_phone}"},
                    {"type": "mrkdwn", "text": f"*Gesamtscore:* {score}/10"},
                    {"type": "mrkdwn", "text": f"*Call ID:* {call_id}"},
                    {"type": "mrkdwn", "text": f"*Empfehlung:* {empfehlung}"},
                ],
            },
        ]

        reason_text = self._build_reason_text(evaluation)
        if reason_text:
            message_blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Begruendung:*\n{reason_text}"},
                }
            )

        einzelbewertungen = evaluation.get("einzelbewertungen", {})
        if einzelbewertungen:
            details_lines = []
            for kategorie, bewertung in einzelbewertungen.items():
                score_detail = bewertung.get("score", 0)
                kommentar = bewertung.get("kommentar", "").strip()
                line = f"- {kategorie.title()}: {score_detail}/10"
                if kommentar:
                    line += f" ({kommentar})"
                details_lines.append(line)

            if details_lines:
                message_blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Einzelbewertungen:*\n" + "\n".join(details_lines),
                        },
                    }
                )

        naechste_schritte = evaluation.get("naechste_schritte")
        if naechste_schritte:
            message_blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Naechste Schritte:*\n{naechste_schritte}",
                    },
                }
            )

        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=message_blocks,
                attachments=[{"color": color, "fallback": f"Interview Result: {empfehlung}"}],
            )
            return response

        except SlackApiError as error:
            print(f"Slack notification failed: {error.response['error']}")
            return None

    def send_error_notification(self, error_message: str, call_id: str = None):
        """Sendet Fehlermeldung an Slack."""
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                text=f"FEHLER: Interview System Error\n{error_message}\nCall ID: {call_id or 'Unknown'}",
            )
        except SlackApiError as error:
            print(f"Error notification failed: {error.response['error']}")

    @staticmethod
    def _build_reason_text(evaluation: Dict[str, Any]) -> str:
        summary = evaluation.get("zusammenfassung", "").strip()
        strengths = [item for item in evaluation.get("staerken", []) if item]
        weaknesses = [item for item in evaluation.get("schwaechen", []) if item]

        sections: List[str] = []
        if summary:
            sections.append(summary)
        if strengths:
            sections.append("*Pluspunkte:*\n" + "\n".join(f"- {item}" for item in strengths))
        if weaknesses:
            sections.append("*Zu beachten:*\n" + "\n".join(f"- {item}" for item in weaknesses))

        return "\n\n".join(sections).strip()
