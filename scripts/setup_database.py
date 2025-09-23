#!/usr/bin/env python3
"""
Database Setup Script
Erstellt alle benötigten Tabellen und Basiskonfiguration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from config.database import DatabaseManager, Base, SystemConfig, Candidate
from sqlalchemy.exc import IntegrityError

load_dotenv()

def setup_database():
    """Erstellt Tabellen und Basiskonfiguration"""
    print("[INFO] Setting up database...")
    
    try:
        db_manager = DatabaseManager()
        
        # Tabellen erstellen
        print("[INFO] Creating tables...")
        Base.metadata.create_all(db_manager.engine)
        print("[SUCCESS] Tables created successfully")
        
        # Basiskonfiguration einfügen
        print("[INFO] Setting up initial configuration...")
        session = db_manager.get_session()
        
        try:
            # System-Konfigurationen
            configs = [
                {
                    "key": "interview_duration_minutes",
                    "value": "30",
                    "description": "Standard-Interviewdauer in Minuten"
                },
                {
                    "key": "evaluation_threshold_invite",
                    "value": "7.0",
                    "description": "Mindestpunktzahl für Einladung zur nächsten Runde"
                },
                {
                    "key": "evaluation_threshold_reject",
                    "value": "4.0",
                    "description": "Unter dieser Punktzahl wird abgelehnt"
                },
                {
                    "key": "default_position",
                    "value": "Software Developer",
                    "description": "Standard-Position für neue Bewerbungen"
                },
                {
                    "key": "vapi_assistant_id",
                    "value": "demo_assistant_id",
                    "description": "Vapi Assistant ID für Interviews"
                }
            ]
            
            for config in configs:
                try:
                    new_config = SystemConfig(
                        key=config["key"],
                        value=config["value"],
                        description=config["description"]
                    )
                    session.add(new_config)
                    session.commit()
                    print(f"  [OK] Added config: {config['key']}")
                except IntegrityError:
                    session.rollback()
                    print(f"  [WARN] Config {config['key']} already exists")
            
            # Test-Kandidat einfügen (falls gewünscht)
            try:
                test_candidate = Candidate(
                    phone="+49123456789",
                    name="Max Mustermann",
                    email="max.mustermann@example.com",
                    position_applied="Software Developer",
                    application_source="Demo"
                )
                session.add(test_candidate)
                session.commit()
                print("  [OK] Added test candidate")
            except IntegrityError:
                session.rollback()
                print("  [WARN] Test candidate already exists")
                
        finally:
            session.close()
            
        print("[SUCCESS] Database setup completed successfully!")
        print("\n[INFO] Database Info:")
        print(f"   Host: {os.getenv('DB_HOST')}")
        print(f"   Database: {os.getenv('DB_NAME')}")
        print(f"   Tables: interview_sessions, candidates, system_config")
        
    except Exception as e:
        print(f"[ERROR] Database setup failed: {str(e)}")
        return False
        
    return True

def check_database_connection():
    """Testet die Datenbankverbindung"""
    print("[INFO] Testing database connection...")
    
    try:
        db_manager = DatabaseManager()
        session = db_manager.get_session()
        
        # Einfache Query zum Testen
        result = session.execute("SELECT 1").fetchone()
        session.close()
        
        if result:
            print("[SUCCESS] Database connection successful")
            return True
        else:
            print("[ERROR] Database connection failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Database connection error: {str(e)}")
        return False

def show_database_status():
    """Zeigt aktuellen Datenbankstatus"""
    print("\n[INFO] Database Status:")
    
    try:
        db_manager = DatabaseManager()
        session = db_manager.get_session()
        
        # Zeige Tabelleninhalt
        from config.database import InterviewSession, Candidate, SystemConfig
        
        interview_count = session.query(InterviewSession).count()
        candidate_count = session.query(Candidate).count()
        config_count = session.query(SystemConfig).count()
        
        print(f"   Interview Sessions: {interview_count}")
        print(f"   Candidates: {candidate_count}")
        print(f"   System Configs: {config_count}")
        
        session.close()
        
    except Exception as e:
        print(f"   Error getting status: {str(e)}")

if __name__ == "__main__":
    print("=== AI Interview Agent - Database Setup ===\n")
    
    # Check connection first
    if not check_database_connection():
        print("\n[ERROR] Cannot connect to database. Please check:")
        print("   1. MySQL is running")
        print("   2. Database 'bewerbung' exists")
        print("   3. Credentials in .env are correct")
        sys.exit(1)
    
    # Setup database
    if setup_database():
        show_database_status()
        print("\n[SUCCESS] Ready to start the application!")
    else:
        sys.exit(1)