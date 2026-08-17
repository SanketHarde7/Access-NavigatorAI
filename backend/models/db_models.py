"""
SQLAlchemy ORM Models for PostgreSQL Database
=============================================
Stores stadiums, zones, graph edges, telemetry logs, user profiles, and navigation logs.
Fully compatible with Supabase (PostgreSQL 15+).
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class StadiumDB(Base):
    """Stadium entity storing venue metadata and coordinates."""
    __tablename__ = "stadiums"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    city = Column(String(50), nullable=True)
    country = Column(String(50), default="India")
    capacity = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    zones = relationship("ZoneDB", back_populates="stadium", cascade="all, delete-orphan")
    edges = relationship("EdgeDB", back_populates="stadium", cascade="all, delete-orphan")


class ZoneDB(Base):
    """Zone entity with live crowd and accessibility metrics."""
    __tablename__ = "zones"

    id = Column(String(50), primary_key=True)
    stadium_id = Column(String(50), ForeignKey("stadiums.id", ondelete="CASCADE"), primary_key=True)
    name = Column(String(100), nullable=False)
    zone_type = Column(String(50), nullable=False)  # gate, elevator, ramp, destination, corridor, restroom
    status = Column(String(30), default="operational")  # operational, congested, maintenance, closed
    crowd_density_pct = Column(Integer, default=0)
    density_trend = Column(String(20), default="stable")  # rising, falling, stable
    accessibility_score = Column(Float, default=1.0)
    elevation_m = Column(Float, default=0.0)
    capacity = Column(Integer, default=1000)
    coord_x = Column(Float, nullable=True)  # Normalized 0..1 x coordinate for map
    coord_y = Column(Float, nullable=True)  # Normalized 0..1 y coordinate for map
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stadium = relationship("StadiumDB", back_populates="zones")
    telemetry_logs = relationship(
        "TelemetryDB",
        back_populates="zone",
        cascade="all, delete-orphan",
        primaryjoin="and_(ZoneDB.id==TelemetryDB.zone_id, ZoneDB.stadium_id==TelemetryDB.stadium_id)",
    )

    __table_args__ = (
        Index("idx_zone_stadium", "stadium_id"),
        Index("idx_zone_status", "status"),
    )


class EdgeDB(Base):
    """Connectivity graph edges between zones."""
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stadium_id = Column(String(50), ForeignKey("stadiums.id", ondelete="CASCADE"), nullable=False)
    source_zone_id = Column(String(50), nullable=False)
    target_zone_id = Column(String(50), nullable=False)
    weight_minutes = Column(Integer, default=2)
    distance_meters = Column(Float, default=50.0)
    is_wheelchair_accessible = Column(Boolean, default=True)
    has_elevator = Column(Boolean, default=False)
    has_ramp = Column(Boolean, default=False)
    step_count = Column(Integer, default=0)

    # Relationships
    stadium = relationship("StadiumDB", back_populates="edges")

    __table_args__ = (
        Index("idx_edge_stadium_source", "stadium_id", "source_zone_id"),
    )


class TelemetryDB(Base):
    """Time-series telemetry readings from CCTV vision / sensor simulation."""
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stadium_id = Column(String(50), nullable=False)
    zone_id = Column(String(50), nullable=False)
    crowd_density_pct = Column(Integer, nullable=False)
    detected_people_count = Column(Integer, default=0)
    anomaly_detected = Column(Boolean, default=False)
    status = Column(String(30), default="operational")
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    zone = relationship(
        "ZoneDB",
        back_populates="telemetry_logs",
        primaryjoin="and_(TelemetryDB.zone_id==ZoneDB.id, TelemetryDB.stadium_id==ZoneDB.stadium_id)",
    )

    __table_args__ = (
        ForeignKeyConstraint(["zone_id", "stadium_id"], ["zones.id", "zones.stadium_id"], ondelete="CASCADE"),
        Index("idx_telemetry_time", "recorded_at"),
        Index("idx_telemetry_zone", "stadium_id", "zone_id"),
    )


class UserProfileDB(Base):
    """User accessibility preferences."""
    __tablename__ = "user_profiles"

    id = Column(String(50), primary_key=True)
    wheelchair_user = Column(Boolean, default=False)
    visually_impaired = Column(Boolean, default=False)
    hearing_impaired = Column(Boolean, default=False)
    max_stairs_allowed = Column(Integer, default=0)
    preferred_language = Column(String(20), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)


class NavigationLogDB(Base):
    """Navigation history, Agent Chain-of-Thought logs, and user feedback."""
    __tablename__ = "navigation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stadium_id = Column(String(50), nullable=False)
    start_zone = Column(String(50), nullable=False)
    end_zone = Column(String(50), nullable=False)
    need = Column(String(50), default="wheelchair")
    recommended_path = Column(JSON, nullable=True)
    eta_minutes = Column(Integer, default=5)
    confidence = Column(String(20), default="high")
    cot_reasoning = Column(Text, nullable=True)
    user_rating = Column(Integer, nullable=True)  # 1 to 5 stars
    user_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_nav_stadium_created", "stadium_id", "created_at"),
    )
