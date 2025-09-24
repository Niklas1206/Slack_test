import os
from typing import Any, Dict, List, Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


COLOR_MAP = {
    "EINLADEN": "#36a64f",
    "ABLEHNEN": "#ff0000",
    "UNENTSCHIEDEN": "#ffaa00",
}


def _format_category_name(name: str) -> str:
    return name.replace('_', ' ').title()


def _make_section(title: str, body: str) -> Dict[str, Any]:
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"{title}\n{body.strip()}"
        },
    }


def build_interview_payload(
    evaluation: Dict[str, Any],
    candidate_phone: str,
    call_id: str,
    transcript_url: Optional[str] = None,
) -> Dict[str, Any]:
    empfehlung = evaluation.get("gesamtbewertung", {}).get("empfehlung", "UNENTSCHIEDEN")
    score = evaluation.get("gesamtbewertung", {}).get("score", 0)
    color = COLOR_MAP.get(empfehlung, "#36a64f")

    summary_fields: List[Dict[str, Any]] = [
        {"type": "mrkdwn", "text": f"*Kandidat:*\n{candidate_phone}"},
        {"type": "mrkdwn", "text": f"*Gesamtscore:*\n{score}/10"},
        {"type": "mrkdwn", "text": f"*Call ID:*\n{call_id}"},
        {"type": "mrkdwn", "text": f"*Empfehlung:*\n{empfehlung}"},
    ]

    blocks: List[Dict[str, Any]] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Interview abgeschlossen - {empfehlung}",
            },
        },
        {"type": "section", "fields": summary_fields},
        {"type": "divider"},
    ]

    summary_text = evaluation.get("zusammenfassung", "").strip()
    if summary_text:
        blocks.append(_make_section("*Begruendung:*", summary_text))

    strengths = [item for item in evaluation.get("staerken", []) if item]
    if strengths:
        strength_body = "\n".join(f"- {item}" for item in strengths)
        blocks.append(_make_section("*Pluspunkte:*", strength_body))

    weaknesses = [item for item in evaluation.get("schwaechen", []) if item]
    if weaknesses:
        weakness_body = "\n".join(f"- {item}" for item in weaknesses)
        blocks.append(_make_section("*Zu beachten:*", weakness_body))

    einzelbewertungen = evaluation.get("einzelbewertungen", {})
    detail_lines: List[str] = []
    for kategorie, bewertung in einzelbewertungen.items():
        kategorie_name = _format_category_name(kategorie)
        score_detail = bewertung.get("score", 0)
        kommentar = bewertung.get("kommentar", "").strip()
        line = f"- {kategorie_name}: {score_detail}/10"
        if kommentar:
            line += f" ({kommentar})"
        detail_lines.append(line)

    if detail_lines:
        blocks.append(_make_section("*Einzelbewertungen:*", "\n".join(detail_lines)))

    naechste_schritte = evaluation.get("naechste_schritte")
    if naechste_schritte:
        blocks.append(_make_section("*Naechste Schritte:*", naechste_schritte))

    if transcript_url:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":page_facing_up: <{transcript_url}|Vollstaendiges Transkript anzeigen>",
                },
            }
        )

    return {
        "color": color,
        "empfehlung": empfehlung,
        "score": score,
        "blocks": blocks,
    }


class SlackNotifier:
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.channel = os.getenv("SLACK_CHANNEL", "hr-notifications")

    def send_interview_result(
        self,
        evaluation: Dict[str, Any],
        candidate_phone: str,
        call_id: str,
        transcript_url: Optional[str] = None,
    ):
        """Sendet Bewertungsergebnis an Slack-Channel."""

        payload = build_interview_payload(evaluation, candidate_phone, call_id, transcript_url)

        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=payload["blocks"],
                attachments=[{"color": payload["color"], "fallback": f"Interview Result: {payload['empfehlung']}"}],
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
