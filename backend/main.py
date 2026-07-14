"""
Access Navigator AI - FastAPI Backend
=======================================
Production-ready API with multi-agent AI system, streaming,
predictive analytics, and comprehensive accessibility features.

Agents:
  - PerceptionAgent: Senses and normalizes stadium data
  - ReasoningAgent: CoT route planning and decision making
  - CommunicationAgent: Formats output for accessibility
  - ConversationalAgent: Natural language interface (ReAct)

Services:
  - LLM Service: Multi-provider (Groq, Gemini) with fallback
  - Prediction Service: AI crowd forecasting
"""
import os
import sys
import json
import heapq
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Query, File, UploadFile, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.config import settings
from core.database import db, StadiumDatabase
from models.schemas import (
    ZoneStatus, ZoneStatusUpdate, RouteRequest, RouteResponse,
    PathSegment, AnnouncementInput, CaptionOutput,
    ChatRequest, ChatResponse, ChatMessage,
    StadiumPrediction, StadiumAnalytics,
    DataUploadResponse, BatchZoneUpdate,
    DemoScenario, DemoResponse,
    HealthResponse,
)
from agents.perception_agent import PerceptionAgent
from agents.reasoning_agent import ReasoningAgent
from agents.communication_agent import CommunicationAgent
from agents.conversational_agent import ConversationalAgent
from services.llm_service import llm_service
from services.prediction_service import prediction_service

# Startup time for uptime tracking
STARTUP_TIME = datetime.utcnow()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - start/stop background tasks."""
    # Startup
    print("Starting Access Navigator AI...")
    await db.start_simulation()
    print(f"Simulation started for {len(db.list_stadiums())} stadiums")
    yield
    # Shutdown
    print("Shutting down...")
    db.stop_simulation()


app = FastAPI(
    title="Access Navigator AI",
    description="AI-powered accessibility navigation for stadiums",
    version="2.0.0",
    lifespan=lifespan,
)

# Rate Limiter Configuration
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://access-navigator-ai.vercel.app",
        "https://access-navigator-ai.vercel.app/",
        "http://access-navigator-ai.vercel.app",
        "http://access-navigator-ai.vercel.app/"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Note: Render free tier sleeps after 15 mins of inactivity. 
# The first request after sleep can take 30-60s. This is expected behavior.
# A keep-alive cron job (hitting /api/health) is used to minimize this.


# ============== HEALTH ==============

@app.get("/")
async def root():
    """Root endpoint for basic connectivity check."""
    return {"status": "ok", "message": "Access Navigator API is running. Visit /docs for API documentation or /api/health for system status."}

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check with feature flags."""
    uptime = int((datetime.utcnow() - STARTUP_TIME).total_seconds())
    providers = llm_service.get_available_providers()
    return HealthResponse(
        status="ok",
        version="2.0.0",
        features={
            "streaming": settings.ENABLE_STREAMING,
            "voice_input": settings.ENABLE_VOICE_INPUT,
            "predictions": settings.ENABLE_PREDICTIONS,
            "analytics": settings.ENABLE_ANALYTICS,
            "conversational_ai": settings.ENABLE_CONVERSATIONAL_AI,
        },
        llm_providers=providers,
        uptime_seconds=uptime,
        stadiums_loaded=len(db.list_stadiums()),
    )


# ============== STADIUMS ==============

@app.get("/api/stadiums")
async def list_stadiums():
    """List all available stadiums."""
    return {"stadiums": db.list_stadiums()}


@app.get("/api/stadiums/{stadium_id}")
async def get_stadium(stadium_id: str):
    """Get stadium details."""
    stadium = db.get_stadium(stadium_id)
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return {
        "stadium_id": stadium.stadium_id,
        "name": stadium.name,
        "location": stadium.location,
        "capacity": stadium.capacity,
        "zone_count": len(stadium.zones),
    }


# ============== ZONES ==============

@app.get("/api/zones", response_model=List[ZoneStatus])
async def get_zones(stadium_id: str = Query("metlife")):
    """Get all zones for a stadium."""
    if stadium_id not in [s["stadium_id"] for s in db.list_stadiums()]:
        raise HTTPException(status_code=404, detail="Stadium not found")
    zones = db.get_zones(stadium_id)
    return [
        ZoneStatus(
            zone_id=z.zone_id,
            type=z.zone_type,
            status=z.status,
            crowd_density_pct=z.crowd_density_pct,
            density_trend=z.density_trend,
            last_updated=z.last_updated,
            accessibility_score=z.accessibility_score,
            elevation_m=z.elevation_m,
            capacity=z.capacity,
        )
        for z in zones
    ]


@app.get("/api/zones/{zone_id}")
async def get_zone(zone_id: str, stadium_id: str = Query("metlife")):
    """Get specific zone details."""
    zone = db.get_zone(stadium_id, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return {
        "zone_id": zone.zone_id,
        "type": zone.zone_type,
        "status": zone.status,
        "crowd_density_pct": zone.crowd_density_pct,
        "density_trend": zone.density_trend,
        "accessibility_score": zone.accessibility_score,
        "last_updated": zone.last_updated.isoformat(),
    }


@app.post("/api/zones/batch-update")
async def batch_update_zones(update: BatchZoneUpdate):
    """Batch update zone statuses."""
    stadium = db.get_stadium(update.stadium_id)
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")

    updated = 0
    errors = []

    for u in update.updates:
        zone = db.get_zone(update.stadium_id, u.zone_id)
        if zone:
            kwargs = {}
            if u.status:
                kwargs["status"] = u.status.value
            if u.crowd_density_pct is not None:
                kwargs["crowd_density_pct"] = u.crowd_density_pct
            if u.density_trend:
                kwargs["density_trend"] = u.density_trend.value
            if u.accessibility_score is not None:
                kwargs["accessibility_score"] = u.accessibility_score

            db.update_zone(update.stadium_id, u.zone_id, **kwargs)
            updated += 1
        else:
            errors.append(f"Zone {u.zone_id} not found")

    return {"updated": updated, "errors": errors}


# ============== GRAPH ==============

@app.get("/api/graph")
async def get_graph(stadium_id: str = Query("metlife")):
    """Get stadium connectivity graph."""
    graph = db.get_graph(stadium_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return graph


@app.get("/api/coordinates")
async def get_coordinates(stadium_id: str = Query("metlife")):
    """Get zone coordinates for visualization."""
    coords = db.get_coordinates(stadium_id)
    if not coords:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return coords


# ============== ROUTING ==============

def find_candidate_paths(start: str, end: str, stadium_id: str, max_paths: int = 5) -> List[Dict[str, Any]]:
    """Find candidate paths using modified Dijkstra's algorithm."""
    graph = db.get_graph(stadium_id)
    if not graph:
        return []

    # Priority queue: (distance, path)
    queue = [(0, [start])]
    seen = set()
    paths = []

    while queue and len(paths) < max_paths:
        dist, path = heapq.heappop(queue)
        node = path[-1]

        if node == end:
            paths.append({"path": path, "distance_min": max(2, dist)})
            continue

        if node in seen and len(path) > 1:
            continue
        seen.add(node)

        for adjacent, weight in graph.get(node, {}).items():
            if adjacent not in path:
                heapq.heappush(queue, (dist + weight, path + [adjacent]))

    return paths


@app.post("/api/route")
async def get_route(
    request: RouteRequest,
    provider: Optional[str] = Query(None),
):
    """
    Calculate optimal accessible route using multi-agent AI system.
    
    Pipeline:
    1. PerceptionAgent: Analyze current zone conditions
    2. ReasoningAgent: CoT route optimization
    3. CommunicationAgent: Format for user needs
    """
    start_time = time.time()

    if request.stadium_id not in [s["stadium_id"] for s in db.list_stadiums()]:
        raise HTTPException(status_code=404, detail="Stadium not found")

    stadium_zones = db.get_zones(request.stadium_id)

    if request.current_location == request.destination:
        return RouteResponse(
            recommended_path=[request.current_location],
            path_segments=[],
            eta_minutes=0,
            reasoning="You are already at your destination!",
            alternative_considered="None",
            confidence="high",
            accessibility_score=1.0,
            generated_at=datetime.utcnow(),
        )

    # Step 1: Perception - gather situational awareness
    summary = PerceptionAgent.summarize_zones(stadium_zones)
    accessibility_summary = PerceptionAgent.get_accessibility_summary(stadium_zones, request.accessibility_need.value)
    anomalies = PerceptionAgent.detect_anomalies(stadium_zones)

    full_summary = f"{summary}\n\n{accessibility_summary}"
    if anomalies:
        full_summary += f"\n\nANOMALIES DETECTED: {len(anomalies)}"

    # Step 2: Find candidate paths
    candidate_paths = find_candidate_paths(
        request.current_location,
        request.destination,
        request.stadium_id,
    )

    if not candidate_paths:
        return RouteResponse(
            recommended_path=[],
            path_segments=[],
            eta_minutes=0,
            reasoning="No accessible routes found between these locations. Please contact a steward for assistance.",
            alternative_considered="None",
            confidence="low",
            crowd_alerts=["No path available"],
            generated_at=datetime.utcnow(),
        )

    # Step 3: Reasoning - AI route optimization
    route_data = await ReasoningAgent.calculate_route(
        accessibility_need=request.accessibility_need.value,
        situational_summary=full_summary,
        candidate_paths=candidate_paths,
        provider=provider,
    )

    # Build path segments
    path = route_data.get("recommended_path", [])
    segments = []
    for i in range(len(path) - 1):
        graph = db.get_graph(request.stadium_id)
        time_cost = graph.get(path[i], {}).get(path[i + 1], 5)
        segments.append(PathSegment(
            from_zone=path[i],
            to_zone=path[i + 1],
            estimated_time_min=time_cost,
        ))

    route_data["path_segments"] = [s.model_dump() for s in segments]
    route_data["generated_at"] = datetime.utcnow()

    processing_time = int((time.time() - start_time) * 1000)

    return RouteResponse(**route_data)


@app.post("/api/route/simple")
async def get_route_simple(
    stadium_id: str = Query("metlife"),
    start: str = Query(...),
    end: str = Query(...),
    accessibility_need: str = Query("wheelchair"),
):
    """Simplified route endpoint for quick lookups."""
    req = RouteRequest(
        user_id="quick_user",
        stadium_id=stadium_id,
        accessibility_need=accessibility_need,
        current_location=start,
        destination=end,
    )
    return await get_route(req)


# ============== CAPTIONS ==============

@app.post("/api/caption")
async def process_caption(
    announcement: AnnouncementInput,
    provider: Optional[str] = Query(None),
):
    """
    Process stadium announcement into accessible caption.
    
    Uses ReasoningAgent for urgency classification and caption generation.
    """
    if not announcement.raw_text.strip():
        return CaptionOutput(
            display_text="[No announcement text provided]",
            urgency="normal",
            style="standard",
            confidence=0,
        )

    caption_data = await ReasoningAgent.classify_caption(announcement.raw_text, provider=provider)
    formatted = CommunicationAgent.format_caption_output(caption_data)

    # Store in history
    db.add_announcement(announcement.raw_text, formatted)

    return CaptionOutput(**formatted)


@app.post("/api/caption/quick")
async def quick_caption(
    raw_text: str = Query(..., min_length=1),
    provider: Optional[str] = Query(None),
):
    """Quick caption endpoint."""
    ann = AnnouncementInput(raw_text=raw_text)
    return await process_caption(ann, provider=provider)


# ============== CONVERSATIONAL AI ==============

@app.post("/api/chat")
@limiter.limit("4/minute")
async def chat(request: Request, body: ChatRequest):
    """
    Conversational AI interface - natural language stadium assistance.
    
    Uses ConversationalAgent with ReAct pattern:
    - Understands natural language
    - Detects intent
    - Coordinates other agents
    - Responds naturally
    """
    if not settings.ENABLE_CONVERSATIONAL_AI:
        raise HTTPException(status_code=503, detail="Conversational AI is disabled")

    result = await ConversationalAgent.chat(
        message=body.message,
        user_id=body.user_id,
        stadium_id=body.stadium_id or "metlife",
        accessibility_need=body.accessibility_need.value if body.accessibility_need else "wheelchair",
        conversation_history=[m.model_dump() for m in (body.conversation_history or [])],
    )

    return ChatResponse(**result)


@app.post("/api/chat/stream")
@limiter.limit("4/minute")
async def chat_stream(request: Request, body: ChatRequest):
    """
    Streaming conversational AI for real-time responses.
    
    Returns Server-Sent Events (SSE) with token-by-token output
    for a more interactive experience.
    """
    if not settings.ENABLE_STREAMING:
        raise HTTPException(status_code=503, detail="Streaming is disabled")

    async def event_generator():
        async for token in ConversationalAgent.chat_stream(
            message=body.message,
            user_id=body.user_id,
            stadium_id=body.stadium_id or "metlife",
            accessibility_need=body.accessibility_need.value if body.accessibility_need else "wheelchair",
            conversation_history=[m.model_dump() for m in (body.conversation_history or [])],
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============== PREDICTIONS & ANALYTICS ==============

@app.get("/api/predictions/{stadium_id}")
async def get_predictions(
    stadium_id: str,
    horizon_minutes: int = Query(30, ge=5, le=120),
):
    """
    AI-powered crowd density predictions.
    
    Uses PredictionService with LLM-based forecasting.
    """
    if not settings.ENABLE_PREDICTIONS:
        raise HTTPException(status_code=503, detail="Predictions are disabled")

    if stadium_id not in [s["stadium_id"] for s in db.list_stadiums()]:
        raise HTTPException(status_code=404, detail="Stadium not found")

    predictions = await prediction_service.predict_crowd(stadium_id, horizon_minutes)
    return predictions


@app.get("/api/analytics/{stadium_id}")
async def get_analytics(stadium_id: str):
    """
    Comprehensive stadium analytics with AI insights.
    
    Includes crowd patterns, accessibility compliance,
    and AI-generated recommendations.
    """
    if not settings.ENABLE_ANALYTICS:
        raise HTTPException(status_code=503, detail="Analytics are disabled")

    if stadium_id not in [s["stadium_id"] for s in db.list_stadiums()]:
        raise HTTPException(status_code=404, detail="Stadium not found")

    analytics = await prediction_service.generate_analytics(stadium_id)
    return analytics


# ============== DATA INGESTION ==============

@app.post("/api/data/upload")
async def upload_data(
    stadium_id: str = Query("metlife"),
    file: UploadFile = File(...),
):
    """
    Upload zone data via CSV or JSON.
    
    Supports bulk updates for jury evaluation.
    """
    if stadium_id not in [s["stadium_id"] for s in db.list_stadiums()]:
        raise HTTPException(status_code=404, detail="Stadium not found")

    import csv
    import io

    content = await file.read()
    ingested = 0
    errors = []

    if file.filename.endswith(".json"):
        try:
            data = json.loads(content)
            for item in data:
                try:
                    if "zone_id" in item and item["zone_id"] in db.get_stadium(stadium_id).zones:
                        kwargs = {}
                        if "status" in item:
                            kwargs["status"] = item["status"]
                        if "crowd_density_pct" in item:
                            kwargs["crowd_density_pct"] = item["crowd_density_pct"]
                        if "density_trend" in item:
                            kwargs["density_trend"] = item["density_trend"]
                        db.update_zone(stadium_id, item["zone_id"], **kwargs)
                        ingested += 1
                except Exception as e:
                    errors.append(str(e))
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid JSON: {str(e)}")

    elif file.filename.endswith(".csv"):
        try:
            reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
            for row in reader:
                try:
                    zone_id = row.get("zone_id", "")
                    if zone_id in db.get_stadium(stadium_id).zones:
                        kwargs = {}
                        if row.get("status"):
                            kwargs["status"] = row["status"]
                        if row.get("crowd_density_pct"):
                            kwargs["crowd_density_pct"] = int(row["crowd_density_pct"])
                        if row.get("density_trend"):
                            kwargs["density_trend"] = row["density_trend"]
                        db.update_zone(stadium_id, zone_id, **kwargs)
                        ingested += 1
                except Exception as e:
                    errors.append(str(e))
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid CSV: {str(e)}")
    else:
        raise HTTPException(status_code=422, detail="Only .csv and .json files supported")

    return DataUploadResponse(
        zones_ingested=ingested,
        zones_updated=ingested,
        errors=errors,
        stadium_id=stadium_id,
    )


# ============== DEMO SCENARIOS ==============

@app.post("/api/demo/scenario")
async def trigger_scenario(scenario: DemoScenario):
    """
    Trigger demo scenarios for presentation.
    
    Scenarios: normal, blocked, emergency, halftime, evacuation
    """
    stadium = db.get_stadium(scenario.stadium_id)
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")

    affected = 0
    description = ""

    if scenario.scenario_type == "normal":
        for z in stadium.zones.values():
            db.update_zone(scenario.stadium_id, z.zone_id,
                         status="operational",
                         crowd_density_pct=min(z.crowd_density_pct, 50),
                         density_trend="stable")
        affected = len(stadium.zones)
        description = "All zones normalized to operational status with moderate crowd levels."

    elif scenario.scenario_type == "blocked":
        # Block some key accessibility routes
        for z in stadium.zones.values():
            if z.zone_type in ("elevator", "ramp") and z.zone_id.endswith(("a", "north", "1")):
                db.update_zone(scenario.stadium_id, z.zone_id,
                             status="maintenance",
                             crowd_density_pct=0)
                affected += 1
        # Increase congestion elsewhere
        for z in stadium.zones.values():
            if z.zone_type == "destination":
                db.update_zone(scenario.stadium_id, z.zone_id,
                             crowd_density_pct=min(95, z.crowd_density_pct + 20),
                             density_trend="rising")
        description = f"Blocked {affected} accessibility routes and increased crowd density to test AI rerouting."

    elif scenario.scenario_type == "emergency":
        for z in stadium.zones.values():
            if z.zone_type in ("destination", "corridor") and z.elevation_m > 1:
                db.update_zone(scenario.stadium_id, z.zone_id,
                             crowd_density_pct=95,
                             density_trend="rising")
        affected = len(stadium.zones)
        description = "Emergency scenario: High density in upper levels. AI should recommend evacuation routes."

    elif scenario.scenario_type == "halftime":
        for z in stadium.zones.values():
            if z.zone_type in ("corridor", "accessible_path"):
                db.update_zone(scenario.stadium_id, z.zone_id,
                             crowd_density_pct=min(90, z.crowd_density_pct + 30),
                             density_trend="rising")
        affected = len(stadium.zones)
        description = "Halftime crowd surge in concourses and paths."

    elif scenario.scenario_type == "evacuation":
        for z in stadium.zones.values():
            if z.zone_type == "stairs":
                db.update_zone(scenario.stadium_id, z.zone_id,
                             status="congested",
                             crowd_density_pct=100)
            elif z.zone_type in ("elevator", "ramp"):
                db.update_zone(scenario.stadium_id, z.zone_id,
                             crowd_density_pct=min(100, z.crowd_density_pct + 40))
        affected = len(stadium.zones)
        description = "Evacuation scenario: All exits congested. AI finds best accessible egress."

    return DemoResponse(
        scenario=scenario.scenario_type,
        zones_affected=affected,
        description=description,
    )


@app.get("/api/announcements")
async def get_announcements(limit: int = Query(20, le=100)):
    """Get recent announcement history."""
    return {"announcements": db.get_announcements(limit)}


# ============== ERROR HANDLERS ==============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global error handler for graceful failures."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
