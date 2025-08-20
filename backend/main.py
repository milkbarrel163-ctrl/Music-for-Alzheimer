from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import os
import json
import csv
import sqlite3
from pathlib import Path
import random
from typing import List, Optional
from audio_generator import AudioGenerator
from gpt_client import GPTClient

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
audio_generator = AudioGenerator()
gpt_client = GPTClient()

# Paths
BASE_DIR = Path(__file__).resolve().parent
MUSIC_DIR = BASE_DIR / "assets" / "music"
DATA_DIR = BASE_DIR / "data"
GENERATED_DIR = MUSIC_DIR / "generated"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect(DATA_DIR / "session_logs.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT,
            emotional_state TEXT,
            memory_response TEXT,
            song_played TEXT,
            song_category TEXT,
            duration_seconds INTEGER,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class SessionStart(BaseModel):
    session_id: str
    emotional_state: str  # Distressed, Neutral, Content, Joyful

class SessionLog(BaseModel):
    session_id: str
    emotional_state: str
    memory_response: str  # None, Some, Good
    song_played: str
    song_category: str
    duration_seconds: int
    notes: Optional[str] = ""

class MusicGenerationRequest(BaseModel):
    base_song: str
    tempo: str = "slow"  # slow, medium
    style: str = "simplified"  # simplified, instrumental

class GPTPromptRequest(BaseModel):
    emotional_state: str
    current_song: Optional[str] = None
    memory_response: str = "None"

# Routes
@app.get("/")
def read_root():
    return {"message": "Alzheimer's Music Therapy API"}

@app.post("/session/start")
def start_session(session: SessionStart):
    """Start a new therapy session"""
    try:
        # Log session start
        conn = sqlite3.connect(DATA_DIR / "session_logs.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (session_id, emotional_state, memory_response, song_played, song_category, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session.session_id, session.emotional_state, "None", "Session Started", "N/A", 0))
        conn.commit()
        conn.close()

        return {"status": "success", "session_id": session.session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/log")
def log_session_data(log: SessionLog):
    """Log session activity"""
    try:
        # Save to database
        conn = sqlite3.connect(DATA_DIR / "session_logs.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (session_id, emotional_state, memory_response, song_played, song_category, duration_seconds, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (log.session_id, log.emotional_state, log.memory_response, log.song_played,
              log.song_category, log.duration_seconds, log.notes))
        conn.commit()
        conn.close()

        # Also save to CSV for easy access
        csv_file = DATA_DIR / "sessions.csv"
        file_exists = csv_file.exists()

        with open(csv_file, 'a', newline='') as f:
            fieldnames = ['timestamp', 'session_id', 'emotional_state', 'memory_response',
                         'song_played', 'song_category', 'duration_seconds', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'session_id': log.session_id,
                'emotional_state': log.emotional_state,
                'memory_response': log.memory_response,
                'song_played': log.song_played,
                'song_category': log.song_category,
                'duration_seconds': log.duration_seconds,
                'notes': log.notes
            })

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/music/categories")
def get_music_categories():
    """Get available music categories"""
    categories = {
        "soothing": "Calming music for distressed states",
        "familiar": "Well-known songs from their era",
        "uplifting": "Happy, celebratory music"
    }
    return categories

@app.get("/music/{category}")
def get_music_by_category(category: str):
    """Get music files for a specific category"""
    category_path = MUSIC_DIR / category
    if not category_path.exists():
        raise HTTPException(status_code=404, detail="Category not found")

    music_files = []
    for file in category_path.glob("*.mp3"):
        music_files.append({
            "name": file.stem,
            "filename": file.name,
            "path": f"/music/{category}/{file.name}"
        })

    return music_files

@app.get("/music/{category}/{filename}")
def get_music_file(category: str, filename: str):
    """Serve a specific music file"""
    file_path = MUSIC_DIR / category / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="audio/mpeg")

@app.post("/music/generate")
async def generate_music(request: MusicGenerationRequest):
    """Generate simplified version of old songs"""
    try:
        # Generate simplified/slower version
        filename = await audio_generator.generate_simplified_version(
            base_song=request.base_song,
            tempo=request.tempo,
            style=request.style
        )

        return {
            "status": "success",
            "filename": filename,
            "path": f"/music/generated/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gpt/suggestions")
async def get_gpt_suggestions(request: GPTPromptRequest):
    """Get memory conversation starters from GPT"""
    try:
        suggestions = await gpt_client.get_memory_prompts(
            emotional_state=request.emotional_state,
            current_song=request.current_song,
            memory_response=request.memory_response
        )

        return {
            "status": "success",
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/analytics")
def get_session_analytics(days: int = 7):
    """Get session analytics for dashboard"""
    try:
        conn = sqlite3.connect(DATA_DIR / "session_logs.db")
        cursor = conn.cursor()

        # Get memory response patterns
        cursor.execute('''
            SELECT
                DATE(timestamp) as date,
                memory_response,
                COUNT(*) as count,
                AVG(duration_seconds) as avg_duration
            FROM sessions
            WHERE timestamp > datetime('now', '-' || ? || ' days')
            AND memory_response != 'None'
            GROUP BY DATE(timestamp), memory_response
            ORDER BY date DESC
        ''', (days,))

        memory_patterns = cursor.fetchall()

        # Get most effective songs
        cursor.execute('''
            SELECT
                song_played,
                song_category,
                memory_response,
                COUNT(*) as play_count,
                AVG(duration_seconds) as avg_duration
            FROM sessions
            WHERE memory_response = 'Good'
            AND timestamp > datetime('now', '-' || ? || ' days')
            GROUP BY song_played
            ORDER BY play_count DESC
            LIMIT 10
        ''', (days,))

        effective_songs = cursor.fetchall()

        # Get emotional state progression
        cursor.execute('''
            SELECT
                DATE(timestamp) as date,
                emotional_state,
                COUNT(*) as count
            FROM sessions
            WHERE timestamp > datetime('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp), emotional_state
            ORDER BY date DESC
        ''', (days,))

        emotional_patterns = cursor.fetchall()

        conn.close()

        return {
            "memory_patterns": memory_patterns,
            "effective_songs": effective_songs,
            "emotional_patterns": emotional_patterns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/recent")
def get_recent_sessions(limit: int = 10):
    """Get recent session logs"""
    try:
        conn = sqlite3.connect(DATA_DIR / "session_logs.db")
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM sessions
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        sessions = cursor.fetchall()
        conn.close()

        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)