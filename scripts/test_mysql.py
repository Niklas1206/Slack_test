#!/usr/bin/env python3
"""
Simple MySQL Connection Test
"""

import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def test_mysql_connection():
    """Teste direkte MySQL-Verbindung"""
    try:
        print("[INFO] Testing direct MySQL connection...")
        
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'bewerbung'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                result = cursor.fetchone()
                print(f"[SUCCESS] MySQL Version: {result['VERSION()']}")
                
                cursor.execute("SELECT DATABASE()")
                result = cursor.fetchone()
                print(f"[SUCCESS] Connected to database: {result['DATABASE()']}")
                
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"[INFO] Existing tables: {[t[list(t.keys())[0]] for t in tables]}")
                
        return True
        
    except Exception as e:
        print(f"[ERROR] MySQL connection failed: {str(e)}")
        return False

def create_tables_directly():
    """Erstelle Tabellen direkt mit PyMySQL"""
    try:
        print("[INFO] Creating tables directly with PyMySQL...")
        
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'bewerbung'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection:
            with connection.cursor() as cursor:
                # Erstelle interview_sessions Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS interview_sessions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        vapi_call_id VARCHAR(255) UNIQUE NULL,
                        candidate_phone VARCHAR(20) NOT NULL,
                        candidate_name VARCHAR(100) NULL,
                        position VARCHAR(100) DEFAULT 'Software Developer',
                        status VARCHAR(50) DEFAULT 'pending',
                        call_duration INT NULL,
                        transcript TEXT NULL,
                        recording_url VARCHAR(500) NULL,
                        evaluation_score FLOAT NULL,
                        evaluation_data JSON NULL,
                        recommendation VARCHAR(50) NULL,
                        hr_notified BOOLEAN DEFAULT FALSE,
                        slack_message_ts VARCHAR(50) NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        call_started_at DATETIME NULL,
                        completed_at DATETIME NULL,
                        hr_notes TEXT NULL,
                        next_steps VARCHAR(200) NULL
                    )
                """)
                print("[OK] Created interview_sessions table")
                
                # Erstelle candidates Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS candidates (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        phone VARCHAR(20) UNIQUE NOT NULL,
                        name VARCHAR(100) NULL,
                        email VARCHAR(150) NULL,
                        position_applied VARCHAR(100) NULL,
                        application_source VARCHAR(100) NULL,
                        cv_url VARCHAR(500) NULL,
                        total_interviews INT DEFAULT 0,
                        last_interview_date DATETIME NULL,
                        status VARCHAR(50) DEFAULT 'new',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("[OK] Created candidates table")
                
                # Erstelle system_config Tabelle
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_config (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        config_key VARCHAR(100) UNIQUE NOT NULL,
                        config_value TEXT NULL,
                        description VARCHAR(200) NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("[OK] Created system_config table")
                
                # Füge Basis-Konfiguration hinzu
                configs = [
                    ('interview_duration_minutes', '30', 'Standard-Interviewdauer in Minuten'),
                    ('evaluation_threshold_invite', '7.0', 'Mindestpunktzahl für Einladung'),
                    ('evaluation_threshold_reject', '4.0', 'Unter dieser Punktzahl wird abgelehnt'),
                    ('default_position', 'Software Developer', 'Standard-Position'),
                    ('vapi_assistant_id', 'demo_assistant_id', 'Vapi Assistant ID')
                ]
                
                for key, value, desc in configs:
                    cursor.execute("""
                        INSERT IGNORE INTO system_config (config_key, config_value, description)
                        VALUES (%s, %s, %s)
                    """, (key, value, desc))
                    print(f"[OK] Added config: {key}")
                
                # Test-Kandidat hinzufügen
                cursor.execute("""
                    INSERT IGNORE INTO candidates (phone, name, email, position_applied, application_source)
                    VALUES (%s, %s, %s, %s, %s)
                """, ('+49123456789', 'Max Mustermann', 'max.mustermann@example.com', 'Software Developer', 'Demo'))
                print("[OK] Added test candidate")
                
            connection.commit()
            
        print("[SUCCESS] All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Table creation failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== MySQL Direct Connection Test ===\n")
    
    if test_mysql_connection():
        if create_tables_directly():
            print("\n[SUCCESS] Database setup completed!")
            print("You can now start the FastAPI application.")
        else:
            print("\n[ERROR] Database setup failed!")
    else:
        print("\n[ERROR] Cannot connect to MySQL!")
        print("Please check:")
        print("1. MySQL Server is running")
        print("2. Database 'bewerbung' exists")
        print("3. User credentials are correct")
        print("4. User has sufficient privileges")