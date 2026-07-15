"""
Access Navigator AI - Pydantic Schemas
=======================================
Complete type system for stadium accessibility navigation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum


# ============== ENUMS ==============

class ZoneType(str, Enum):
    ramp = "ramp"
    elevator = "elevator"
    stairs = "stairs"
    accessible_path = "accessible_path"
    corridor = "corridor"
    destination = "destination"


class ZoneStatusEnum(str, Enum):
    operational = "operational"
    congested = "congested"
    maintenance = "maintenance"
    closed = "closed"
    emergency = "emergency"


class AccessibilityNeed(str, Enum):
    wheelchair = "wheelchair"
    hearing_impaired = "hearing_impaired"
    visual_impaired = "visual_impaired"
    mobility_limited = "mobility_limited"
    cognitive_support = "cognitive_support"
    both = "both"


class UrgencyLevel(str, Enum):
    normal = "normal"
    important = "important"
    critical = "critical"


class CaptionStyle(str, Enum):
    standard = "standard"
    highlighted = "highlighted"
    highlighted_red_banner = "highlighted_red_banner"


class ConfidenceLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class DensityTrend(str, Enum):
    rising = "rising"
    falling = "falling"
    stable = "stable"


# ============== BASE MODELS ==============

class ZoneStatus(BaseModel):
    """Live zone status with crowd metrics."""
    zone_id: str
    type: ZoneType
    status: ZoneStatusEnum
    crowd_density_pct: Optional[int] = None
    density_trend: Optional[str] = None
    last_updated: datetime
    accessibility_score: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    elevation_m: Optional[float] = Field(default=0.0)
    capacity: Optional[int] = Field(default=1000, gt=0)


class ZoneStatusUpdate(BaseModel):
    """Partial zone update for data ingestion."""
    zone_id: str
    type: Optional[ZoneType] = None
    status: Optional[ZoneStatusEnum] = None
    crowd_density_pct: Optional[int] = Field(default=None, ge=0, le=100)
    density_trend: Optional[DensityTrend] = None
    accessibility_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)


# ============== ROUTE MODELS ==============

class RouteRequest(BaseModel):
    """Route calculation request."""
    user_id: str
    stadium_id: str
    accessibility_need: AccessibilityNeed
    current_location: str
    destination: str


class PathSegment(BaseModel):
    """Individual segment in a route."""
    from_zone: str
    to_zone: str
    estimated_time_min: int
    distance_m: Optional[int] = None
    accessibility_notes: Optional[str] = None


class RouteResponse(BaseModel):
    """AI-recommended accessible route."""
    recommended_path: List[str]
    path_segments: Optional[List[PathSegment]] = []
    eta_minutes: int
    reasoning: str
    alternative_considered: str
    confidence: str
    agent_trace: Optional[Dict[str, Any]] = None
    accessibility_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    crowd_alerts: Optional[List[str]] = []
    generated_at: Optional[datetime] = None


# ============== CAPTION MODELS ==============

class AnnouncementInput(BaseModel):
    """Stadium PA announcement."""
    announcement_id: str = Field(default_factory=lambda: f"ann_{datetime.utcnow().timestamp()}")
    raw_text: str = Field(..., min_length=1)
    timestamp: Optional[datetime] = None
    source: Optional[str] = "stadium_pa"


class CaptionOutput(BaseModel):
    """Processed caption for Deaf/hard-of-hearing fans."""
    display_text: str
    urgency: UrgencyLevel
    style: CaptionStyle
    original_text: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    translated_languages: Optional[Dict[str, str]] = None


# ============== CONVERSATIONAL AI MODELS ==============

class ChatMessage(BaseModel):
    """Individual chat message."""
    role: Literal["user", "assistant", "system", "agent"]
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    agent_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Conversational AI request."""
    user_id: str
    stadium_id: Optional[str] = "metlife"
    accessibility_need: Optional[AccessibilityNeed] = AccessibilityNeed.wheelchair
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    use_streaming: Optional[bool] = True


class ChatResponse(BaseModel):
    """Conversational AI response with agent trace."""
    response: str
    agent_used: str
    actions: Optional[List[Dict[str, Any]]] = []
    suggested_routes: Optional[List[RouteResponse]] = []
    detected_intent: Optional[str] = None
    confidence: Optional[float] = None
    streaming: Optional[bool] = False


# ============== PREDICTION MODELS ==============

class CrowdPrediction(BaseModel):
    """AI crowd prediction for a zone."""
    zone_id: str
    current_density: int
    predicted_density: int
    prediction_horizon_min: int
    confidence: float
    trend_direction: str
    recommended_action: Optional[str] = None


class StadiumPrediction(BaseModel):
    """Full stadium prediction snapshot."""
    stadium_id: str
    generated_at: datetime
    predictions: List[CrowdPrediction]
    overall_risk_level: str
    summary: str


# ============== ANALYTICS MODELS ==============

class ZoneAnalytics(BaseModel):
    """Analytics for a single zone."""
    zone_id: str
    avg_crowd_1h: float
    peak_crowd_1h: int
    status_changes_1h: int
    congestion_time_pct: float
    accessibility_score: float


class StadiumAnalytics(BaseModel):
    """Full stadium analytics dashboard."""
    stadium_id: str
    generated_at: datetime
    total_fans_estimated: int
    avg_stadium_density: float
    most_congested_zones: List[str]
    accessibility_compliance_score: float
    zone_analytics: List[ZoneAnalytics]
    ai_insights: List[str]
    recommendations: List[str]


# ============== DATA INGESTION MODELS ==============

class DataUploadResponse(BaseModel):
    """Data upload result."""
    zones_ingested: int
    zones_updated: int
    errors: List[str]
    stadium_id: str
    processing_time_ms: Optional[int] = None


class BatchZoneUpdate(BaseModel):
    """Batch update multiple zones."""
    stadium_id: str
    updates: List[ZoneStatusUpdate]


# ============== DEMO MODELS ==============

class DemoScenario(BaseModel):
    """Demo scenario configuration."""
    scenario_type: Literal["normal", "blocked", "emergency", "halftime", "evacuation"]
    stadium_id: str = "metlife"


class DemoResponse(BaseModel):
    """Demo scenario activation result."""
    scenario: str
    zones_affected: int
    description: str
    active: bool = True


# ============== HEALTH ==============

class HealthResponse(BaseModel):
    """API health status."""
    status: str
    version: str = "2.0.0"
    features: Dict[str, bool]
    llm_providers: Dict[str, bool]
    uptime_seconds: Optional[int] = None
    stadiums_loaded: int = 3
