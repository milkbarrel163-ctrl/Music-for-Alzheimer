#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for MusicAlzheimer
Provides AI assistant integration for therapeutic music sessions
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging
from dotenv import load_dotenv

# Import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gpt_client import GPTClient
from audio_generator import AudioGenerator

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger()

# Initialize FastAPI app
app = FastAPI(
    title="MusicAlzheimer MCP Server",
    description="Model Context Protocol server for AI-assisted music therapy",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class EmotionType(str, Enum):
    CALM = "calm"
    HAPPY = "happy"
    NOSTALGIC = "nostalgic"
    ENERGETIC = "energetic"
    PEACEFUL = "peaceful"
    MELANCHOLIC = "melancholic"

class MusicCategory(str, Enum):
    FAMILIAR = "familiar"
    SOOTHING = "soothing"
    UPLIFTING = "uplifting"
    GENERATED = "generated"

class EngagementLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class PatientProfile(BaseModel):
    """Patient profile for personalized therapy"""
    patient_id: str
    name: str
    age: Optional[int] = None
    musical_preferences: List[str] = Field(default_factory=list)
    favorite_era: Optional[str] = None
    cognitive_level: Optional[str] = None
    response_history: List[Dict] = Field(default_factory=list)
    notes: Optional[str] = None

class SessionData(BaseModel):
    """Music therapy session data"""
    session_id: str
    patient_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    emotion_log: List[Dict[str, Any]] = Field(default_factory=list)
    tracks_played: List[str] = Field(default_factory=list)
    responses: List[Dict] = Field(default_factory=list)
    engagement_level: EngagementLevel = EngagementLevel.MEDIUM
    notes: Optional[str] = None

class MusicRequest(BaseModel):
    """Request for music generation or selection"""
    emotion: EmotionType
    category: MusicCategory
    prompt: Optional[str] = None
    duration: int = 120  # seconds
    patient_id: Optional[str] = None
    use_memory_prompt: bool = False
    memory_description: Optional[str] = None

class ToolCall(BaseModel):
    """MCP tool call structure"""
    tool: str
    parameters: Dict[str, Any]
    request_id: Optional[str] = None

class ToolResponse(BaseModel):
    """MCP tool response structure"""
    tool: str
    result: Any
    error: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ============================================================================
# MCP Protocol Handler
# ============================================================================

class MCPServer:
    """Main MCP server implementation"""

    def __init__(self):
        self.sessions: Dict[str, SessionData] = {}
        self.patients: Dict[str, PatientProfile] = {}
        self.gpt_client = GPTClient()
        self.audio_generator = AudioGenerator()
        self.active_connections: List[WebSocket] = []

    async def initialize(self):
        """Initialize server components"""
        logger.info("Initializing MCP Server...")

        logger.info("MCP Server initialized successfully")

    async def handle_tool_call(self, tool_call: ToolCall) -> ToolResponse:
        """Route tool calls to appropriate handlers"""
        try:
            tool_name = tool_call.tool
            params = tool_call.parameters

            # Route to appropriate tool handler
            if tool_name == "start_session":
                result = await self.start_therapy_session(**params)
            elif tool_name == "end_session":
                result = await self.end_therapy_session(**params)
            elif tool_name == "generate_music":
                result = await self.generate_therapeutic_music(**params)
            elif tool_name == "select_music":
                result = await self.select_music_from_library(**params)
            elif tool_name == "log_response":
                result = await self.log_patient_response(**params)
            elif tool_name == "get_suggestions":
                result = await self.get_ai_suggestions(**params)
            elif tool_name == "analyze_session":
                result = await self.analyze_session_data(**params)
            elif tool_name == "get_patient_profile":
                result = await self.get_patient_profile(**params)
            elif tool_name == "update_patient_profile":
                result = await self.update_patient_profile(**params)
            elif tool_name == "get_session_history":
                result = await self.get_session_history(**params)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            return ToolResponse(
                tool=tool_name,
                result=result,
                request_id=tool_call.request_id
            )

        except Exception as e:
            logger.error(f"Error handling tool call {tool_call.tool}: {e}")
            return ToolResponse(
                tool=tool_call.tool,
                result=None,
                error=str(e),
                request_id=tool_call.request_id
            )

    # ========================================================================
    # Tool Implementations
    # ========================================================================

    async def start_therapy_session(
        self,
        patient_id: str,
        initial_emotion: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a new music therapy session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{patient_id}"

        session = SessionData(
            session_id=session_id,
            patient_id=patient_id,
            start_time=datetime.now()
        )

        if initial_emotion:
            session.emotion_log.append({
                "timestamp": datetime.now().isoformat(),
                "emotion": initial_emotion
            })

        self.sessions[session_id] = session

        logger.info(f"Started therapy session {session_id} for patient {patient_id}")

        return {
            "session_id": session_id,
            "status": "started",
            "patient_id": patient_id,
            "start_time": session.start_time.isoformat(),
            "message": "Therapy session started successfully"
        }

    async def end_therapy_session(self, session_id: str) -> Dict[str, Any]:
        """End an active therapy session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        session.end_time = datetime.now()

        # Calculate session duration
        duration = (session.end_time - session.start_time).total_seconds()

        # Generate session summary
        summary = {
            "session_id": session_id,
            "patient_id": session.patient_id,
            "duration_minutes": round(duration / 60, 1),
            "tracks_played": len(session.tracks_played),
            "responses_recorded": len(session.responses),
            "engagement_level": session.engagement_level.value,
            "emotion_changes": len(session.emotion_log),
            "end_time": session.end_time.isoformat()
        }

        logger.info(f"Ended therapy session {session_id}")

        return summary

    async def generate_therapeutic_music(
        self,
        emotion: str,
        prompt: Optional[str] = None,
        duration: int = 120,
        patient_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered therapeutic music"""
        try:
            # Get patient preferences if available
            preferences = {}
            if patient_id and patient_id in self.patients:
                patient = self.patients[patient_id]
                preferences = {
                    "musical_preferences": patient.musical_preferences,
                    "favorite_era": patient.favorite_era
                }

            # Generate music using AudioGenerator
            music_data = await self.audio_generator.generate_music(
                emotion=emotion,
                prompt=prompt,
                duration=duration,
                preferences=preferences
            )

            # Log to session if provided
            if session_id and session_id in self.sessions:
                self.sessions[session_id].tracks_played.append(music_data["track_id"])

            logger.info(f"Generated therapeutic music for emotion: {emotion}")

            return {
                "track_id": music_data["track_id"],
                "url": music_data["url"],
                "duration": duration,
                "emotion": emotion,
                "generated_at": datetime.now().isoformat(),
                "message": "Music generated successfully"
            }

        except Exception as e:
            logger.error(f"Error generating music: {e}")
            raise

    async def select_music_from_library(
        self,
        category: str,
        emotion: str,
        patient_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Select appropriate music from the library"""
        # This would interface with your music library
        # For now, returning a mock response

        library_path = Path("backend/assets/music") / category

        # Mock selection logic
        selected_track = {
            "track_id": f"{category}_{emotion}_001",
            "title": f"Therapeutic {emotion.title()} Music",
            "category": category,
            "emotion": emotion,
            "duration": "3:45",
            "url": f"/api/music/{category}/{emotion}_001.mp3"
        }

        logger.info(f"Selected music from library: {selected_track['title']}")

        return selected_track

    async def log_patient_response(
        self,
        session_id: str,
        response_type: str,
        response_value: Any,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log patient response during session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        response = {
            "timestamp": timestamp or datetime.now().isoformat(),
            "type": response_type,
            "value": response_value
        }

        self.sessions[session_id].responses.append(response)

        # Update engagement level based on responses
        if response_type == "engagement":
            self.sessions[session_id].engagement_level = EngagementLevel(response_value)

        logger.info(f"Logged patient response for session {session_id}")

        return {
            "status": "logged",
            "session_id": session_id,
            "response": response
        }

    async def get_ai_suggestions(
        self,
        session_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        current_emotion: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get AI-powered suggestions for the therapy session"""
        suggestions = []

        # Analyze current context
        context = {
            "current_emotion": current_emotion,
            "session_active": session_id is not None
        }

        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            context.update({
                "tracks_played": len(session.tracks_played),
                "session_duration": (datetime.now() - session.start_time).total_seconds() / 60,
                "engagement": session.engagement_level.value
            })

        # Generate suggestions using GPT
        gpt_suggestions = await self.gpt_client.generate_suggestions(context)

        # Format suggestions
        suggestions = [
            {
                "type": "music",
                "priority": "high",
                "title": "Try Calming Classical",
                "description": "Based on current emotional state, classical music may help",
                "action": "play_classical"
            },
            {
                "type": "activity",
                "priority": "medium",
                "title": "Memory Sharing",
                "description": "Good time to encourage memory sharing",
                "action": "start_memory_prompt"
            }
        ]

        # Add GPT suggestions
        if gpt_suggestions:
            suggestions.extend(gpt_suggestions)

        logger.info(f"Generated {len(suggestions)} AI suggestions")

        return {
            "suggestions": suggestions,
            "context": context,
            "generated_at": datetime.now().isoformat()
        }

    async def analyze_session_data(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Analyze session data for insights"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Calculate metrics
        duration = datetime.now() - session.start_time

        analysis = {
            "session_id": session_id,
            "metrics": {
                "duration_minutes": duration.total_seconds() / 60,
                "tracks_played": len(session.tracks_played),
                "response_count": len(session.responses),
                "emotion_changes": len(session.emotion_log),
                "engagement_score": self._calculate_engagement_score(session)
            },
            "patterns": {
                "most_common_emotion": self._get_most_common_emotion(session),
                "response_rate": len(session.responses) / max(1, len(session.tracks_played)),
                "engagement_trend": self._analyze_engagement_trend(session)
            },
            "recommendations": [
                "Continue with current music selection",
                "Consider more interactive elements"
            ]
        }

        logger.info(f"Analyzed session {session_id}")

        return analysis

    async def get_patient_profile(self, patient_id: str) -> Dict[str, Any]:
        """Retrieve patient profile"""
        if patient_id not in self.patients:
            # Create default profile
            self.patients[patient_id] = PatientProfile(
                patient_id=patient_id,
                name=f"Patient {patient_id}"
            )

        patient = self.patients[patient_id]
        return patient.dict()

    async def update_patient_profile(
        self,
        patient_id: str,
        **updates
    ) -> Dict[str, Any]:
        """Update patient profile information"""
        if patient_id not in self.patients:
            self.patients[patient_id] = PatientProfile(
                patient_id=patient_id,
                name=updates.get("name", f"Patient {patient_id}")
            )

        patient = self.patients[patient_id]

        # Update fields
        for key, value in updates.items():
            if hasattr(patient, key):
                setattr(patient, key, value)

        logger.info(f"Updated profile for patient {patient_id}")

        return patient.dict()

    async def get_session_history(
        self,
        patient_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get session history for a patient or all patients"""
        sessions = []

        for session_id, session in self.sessions.items():
            if patient_id and session.patient_id != patient_id:
                continue

            sessions.append({
                "session_id": session_id,
                "patient_id": session.patient_id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "engagement_level": session.engagement_level.value,
                "tracks_played": len(session.tracks_played)
            })

        # Sort by start time (most recent first)
        sessions.sort(key=lambda x: x["start_time"], reverse=True)

        return {
            "sessions": sessions[:limit],
            "total_count": len(sessions),
            "patient_id": patient_id
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _calculate_engagement_score(self, session: SessionData) -> float:
        """Calculate engagement score from session data"""
        score = 0.5  # Base score

        # Adjust based on responses
        if len(session.responses) > 0:
            score += min(0.3, len(session.responses) * 0.05)

        # Adjust based on engagement level
        engagement_scores = {
            EngagementLevel.HIGH: 0.3,
            EngagementLevel.MEDIUM: 0.15,
            EngagementLevel.LOW: 0.05,
            EngagementLevel.NONE: 0
        }
        score += engagement_scores.get(session.engagement_level, 0)

        return min(1.0, score)

    def _get_most_common_emotion(self, session: SessionData) -> Optional[str]:
        """Get the most common emotion from session"""
        if not session.emotion_log:
            return None

        emotions = [log["emotion"] for log in session.emotion_log]
        return max(set(emotions), key=emotions.count)

    def _analyze_engagement_trend(self, session: SessionData) -> str:
        """Analyze engagement trend over session"""
        if len(session.responses) < 2:
            return "stable"

        # Simple trend analysis
        recent_responses = session.responses[-3:]
        if all(r.get("type") == "positive" for r in recent_responses):
            return "improving"
        elif all(r.get("type") == "negative" for r in recent_responses):
            return "declining"

        return "stable"

# ============================================================================
# WebSocket Connection Handler
# ============================================================================

mcp_server = MCPServer()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time MCP communication"""
    await websocket.accept()
    mcp_server.active_connections.append(websocket)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle tool call
            if message.get("type") == "tool_call":
                tool_call = ToolCall(**message["data"])
                response = await mcp_server.handle_tool_call(tool_call)

                # Send response
                await websocket.send_text(json.dumps({
                    "type": "tool_response",
                    "data": response.dict()
                }))

            # Handle other message types
            elif message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))

    except WebSocketDisconnect:
        mcp_server.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        mcp_server.active_connections.remove(websocket)

# ============================================================================
# REST API Endpoints
# ============================================================================

@app.post("/api/tool")
async def execute_tool(tool_call: ToolCall):
    """REST endpoint for tool execution"""
    response = await mcp_server.handle_tool_call(tool_call)
    if response.error:
        raise HTTPException(status_code=400, detail=response.error)
    return response

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(mcp_server.sessions),
        "active_connections": len(mcp_server.active_connections)
    }

@app.get("/api/tools")
async def list_available_tools():
    """List all available MCP tools"""
    return {
        "tools": [
            {
                "name": "start_session",
                "description": "Start a new therapy session",
                "parameters": ["patient_id", "initial_emotion"]
            },
            {
                "name": "end_session",
                "description": "End an active therapy session",
                "parameters": ["session_id"]
            },
            {
                "name": "generate_music",
                "description": "Generate therapeutic music",
                "parameters": ["emotion", "prompt", "duration", "patient_id", "session_id"]
            },
            {
                "name": "select_music",
                "description": "Select music from library",
                "parameters": ["category", "emotion", "patient_id"]
            },
            {
                "name": "log_response",
                "description": "Log patient response",
                "parameters": ["session_id", "response_type", "response_value", "timestamp"]
            },
            {
                "name": "get_suggestions",
                "description": "Get AI suggestions",
                "parameters": ["session_id", "patient_id", "current_emotion"]
            },
            {
                "name": "analyze_session",
                "description": "Analyze session data",
                "parameters": ["session_id"]
            },
            {
                "name": "get_patient_profile",
                "description": "Get patient profile",
                "parameters": ["patient_id"]
            },
            {
                "name": "update_patient_profile",
                "description": "Update patient profile",
                "parameters": ["patient_id", "updates"]
            },
            {
                "name": "get_session_history",
                "description": "Get session history",
                "parameters": ["patient_id", "limit"]
            }
        ]
    }

# ============================================================================
# Server Lifecycle
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize server on startup"""
    logger.info("Starting MCP Server...")
    await mcp_server.initialize()
    logger.info("MCP Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down MCP Server...")
    # Close all WebSocket connections
    for connection in mcp_server.active_connections:
        await connection.close()
    logger.info("MCP Server shut down")

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run server
    uvicorn.run(
        "mcp_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )