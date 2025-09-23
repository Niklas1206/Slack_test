# AI Interview Agent - Backend Complete

Ein vollständig funktionsfähiges Backend für automatisierte Vorstellungsgespräche mit KI-basierter Bewertung.

## Implementiert

### Core Features
- **Interview-Management**: Start und Tracking von Interviews
- **KI-Bewertung**: Automatische Analyse von Gesprächstranskripten  
- **Slack-Integration**: Benachrichtigungen für HR-Team
- **Datenbank**: Vollständige Persistierung (SQLite für Demo, MySQL-ready)
- **Demo-Modus**: Funktioniert ohne echte API-Keys zum Testen

### Architektur
```
Projektstruktur:
├── config/
│   ├── database.py         # MySQL-Konfiguration (production)
│   └── database_sqlite.py  # SQLite-Konfiguration (demo)
├── services/
│   ├── vapi_client.py      # Vapi API Integration
│   ├── evaluation_service.py # KI-Bewertung
│   ├── slack_notifier.py   # Slack-Benachrichtigungen
│   └── demo_service.py     # Demo-Simulationen
├── scripts/
│   ├── setup_sqlite.py     # Datenbank-Setup
│   └── test_api.py         # API-Tests
├── app_flask.py            # Flask Backend (Python 3.13 kompatibel)
├── main.py                 # FastAPI Backend (für ältere Python-Versionen)
└── data/                   # SQLite-Datenbank
```

## Quick Start

### 1. Setup
```bash
# Dependencies installieren
pip install -r requirements.txt

# Datenbank einrichten  
python scripts/setup_sqlite.py

# Backend starten
python app_flask.py
```

### 2. API testen
```bash
# Kompletter API-Test
python scripts/test_api.py

# Oder manuell:
curl -X GET http://127.0.0.1:8000/status
curl -X POST http://127.0.0.1:8000/start-interview \
  -H "Content-Type: application/json" \
  -d '{"candidate_phone":"+49123456789","position":"Software Developer"}'
```

## API Endpoints

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/status` | GET | System-Status und Konfiguration |
| `/start-interview` | POST | Interview starten |
| `/interviews` | GET | Alle Interviews auflisten |
| `/webhook/vapi` | POST | Vapi Webhook (für Production) |
| `/demo/complete-interview` | POST | Interview manuell abschließen (Demo) |

## Konfiguration

### Demo-Modus (Standard)
- Verwendet simulierte APIs
- SQLite-Datenbank
- Keine echten API-Keys nötig
- Sample-Transkripte für Bewertung

### Production-Modus
Echte API-Keys in `.env` eintragen:
```bash
VAPI_API_KEY=your_real_key
OPENAI_API_KEY=your_real_key  
SLACK_BOT_TOKEN=your_real_token
```

## Bewertungssystem

**5 Dimensionen mit Gewichtung:**
- **Fachkompetenz** (30%): Technisches Wissen und Erfahrung
- **Kommunikation** (25%): Ausdrucksfähigkeit und Verständlichkeit  
- **Motivation** (20%): Engagement und Interesse
- **Cultural Fit** (15%): Passung zur Unternehmenskultur
- **Problemlösung** (10%): Analytisches Denken

**Output:** 
- Gesamtscore (1-10)
- Empfehlung: EINLADEN/ABLEHNEN/UNENTSCHIEDEN
- Detaillierte Kommentare pro Dimension
- Stärken und Verbesserungspotentiale

## Demo-Features

Das System simuliert einen kompletten Interview-Workflow:

1. **Interview starten** → Vapi-Call simuliert
2. **Transkript generieren** → Sample-Gespräche verschiedener Kandidatentypen
3. **KI-Bewertung** → Keyword-basierte Analyse + OpenAI-Format
4. **Slack-Benachrichtigung** → Formatierte HR-Nachricht (simuliert)
5. **Datenbank-Tracking** → Vollständige Persistierung

