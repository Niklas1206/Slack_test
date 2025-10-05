# AI Interview Agent

Ein automatisiertes Interview System das Kandidaten telefonisch bewertet und die Ergebnisse per Slack benachrichtigt.

## Was macht diese Anwendung

Das System führt automatische Telefoninterviews mit Bewerbern durch und bewertet diese mithilfe von KI. Nach dem Interview wird eine detaillierte Bewertung erstellt und per Slack an das HR Team gesendet.

### Hauptfunktionen

- Automatische Telefoninterviews über Vapi
- KI basierte Bewertung der Antworten (Gemini AI oder Demo Modus)
- Speicherung aller Gespräche und Bewertungen in SQLite Datenbank
- Slack Benachrichtigungen mit Bewertungsergebnissen
- Web Interface zur Übersicht aller Interviews
- Demo Modus für Testing ohne echte API Aufrufe

## Installation

1. Repository klonen
2. Python Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```

3. Umgebungsvariablen konfigurieren (optional .env Datei erstellen):
   ```
   API_PORT=8000
   API_HOST=127.0.0.1
   OPENAI_API_KEY=AIzaSy... (für Gemini)
   SLACK_WEBHOOK_URL=https://hooks.slack.com/...
   VAPI_API_KEY=your_vapi_key
   DEMO_MODE=true
   ```

## Verwendung

### Mit Flask starten
```
python app_flask.py
```

### Mit FastAPI starten  
```
python main.py
```

Das System startet auf http://localhost:8000 und bietet folgende Endpunkte:

- `POST /start-interview` - Neues Interview starten
- `GET /interviews` - Alle Interviews anzeigen
- `GET /status` - System Status
- `POST /webhook/vapi` - Webhook für Vapi Events
- `POST /demo/complete-interview` - Demo Interview abschließen (nur im Demo Modus)

### Web Interface

Über http://localhost:8000 ist eine einfache Weboberfläche verfügbar um Interviews zu starten und zu verwalten.

## Konfiguration

### Demo Modus

Standardmäßig läuft das System im Demo Modus. Dabei werden simulierte Antworten verwendet statt echter API Aufrufe. Für Produktiveinsatz müssen echte API Keys konfiguriert werden.

### Datenbank

Das System verwendet SQLite und erstellt automatisch eine Datei `data/interview_agent.db`. Die Tabellen werden beim ersten Start automatisch angelegt.

### API Integration

- **Vapi**: Für Telefonanrufe und Spracherkennung
- **Gemini AI**: Für intelligente Bewertung der Antworten  
- **Slack**: Für Benachrichtigungen an das Team

## Projekt Struktur

- `main.py` - FastAPI Backend
- `app_flask.py` - Flask Backend (Alternative)
- `config/` - Datenbankonfiguration
- `services/` - API Services und Business Logic
- `templates/` - HTML Templates
- `scripts/` - Setup und Test Scripts
- `data/` - SQLite Datenbank

## Testing

Im `scripts/` Ordner befinden sich verschiedene Test Scripts:

- `test_api.py` - API Endpunkt Tests
- `test_mysql.py` - MySQL Verbindungstest
- `setup_database.py` - Datenbank Setup

## Entwickelt für

- Python 3.13
- SQLite Datenbank
- REST API Design