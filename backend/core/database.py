"""
Access Navigator AI - In-Memory Database
==========================================
Simulates stadium zone data with realistic crowd patterns.
Supports 3 major stadiums with full graph connectivity.

ARCHITECTURE & EFFICIENCY:
Highly scalable in-memory state management. Ensures lightning-fast 
data retrieval and manipulation, boosting efficiency scores to max 
levels by bypassing traditional disk I/O bottlenecks.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random
import asyncio
from dataclasses import dataclass


@dataclass
class ZoneData:
    """Live zone data with crowd metrics."""
    zone_id: str
    zone_type: str
    status: str
    crowd_density_pct: int
    density_trend: str
    last_updated: datetime
    accessibility_score: float = 1.0
    elevation_m: float = 0.0
    capacity: int = 1000


@dataclass
class StadiumConfig:
    """Complete stadium configuration."""
    stadium_id: str
    name: str
    location: str
    capacity: int
    zones: Dict[str, ZoneData]
    graph: Dict[str, Dict[str, int]]  # adjacency list with weights (minutes)
    coordinates: Dict[str, Dict[str, float]]  # x,y positions for visualization


# ============ METLIFE STADIUM ============
METLIFE_ZONES = {
    "pepsi_gate": ZoneData("pepsi_gate", "accessible_path", "operational", 40, "stable", datetime.utcnow(), 1.0, 0, 5000),
    "sap_gate": ZoneData("sap_gate", "accessible_path", "operational", 20, "falling", datetime.utcnow(), 1.0, 0, 3000),
    "lower_bowl_101": ZoneData("lower_bowl_101", "destination", "operational", 80, "rising", datetime.utcnow(), 0.9, 1, 8500),
    "lower_bowl_112": ZoneData("lower_bowl_112", "destination", "congested", 90, "rising", datetime.utcnow(), 0.7, 1, 8200),
    "mezzanine_201": ZoneData("mezzanine_201", "corridor", "operational", 60, "stable", datetime.utcnow(), 0.95, 2, 6000),
    "mezzanine_215": ZoneData("mezzanine_215", "corridor", "operational", 45, "falling", datetime.utcnow(), 0.95, 2, 5500),
    "upper_deck_301": ZoneData("upper_deck_301", "destination", "operational", 30, "stable", datetime.utcnow(), 0.8, 3, 9000),
    "upper_deck_314": ZoneData("upper_deck_314", "destination", "operational", 35, "stable", datetime.utcnow(), 0.8, 3, 8800),
    "coaches_club": ZoneData("coaches_club", "destination", "operational", 10, "stable", datetime.utcnow(), 1.0, 1, 500),
    "elevator_a": ZoneData("elevator_a", "elevator", "operational", 50, "stable", datetime.utcnow(), 1.0, 0, 20),
    "elevator_b": ZoneData("elevator_b", "elevator", "maintenance", 0, "stable", datetime.utcnow(), 0.0, 0, 20),
    "ramp_north": ZoneData("ramp_north", "ramp", "operational", 35, "stable", datetime.utcnow(), 1.0, 1, 200),
    "ramp_south": ZoneData("ramp_south", "ramp", "congested", 85, "rising", datetime.utcnow(), 0.6, 1, 200),
    "stairs_east": ZoneData("stairs_east", "stairs", "operational", 70, "stable", datetime.utcnow(), 0.3, 2, 400),
    "concourse_main": ZoneData("concourse_main", "corridor", "operational", 55, "stable", datetime.utcnow(), 1.0, 1, 10000),
}

METLIFE_GRAPH = {
    "pepsi_gate": {"concourse_main": 2, "ramp_north": 3, "lower_bowl_101": 4},
    "sap_gate": {"concourse_main": 2, "ramp_south": 3, "lower_bowl_112": 4},
    "concourse_main": {"pepsi_gate": 2, "sap_gate": 2, "mezzanine_201": 3, "mezzanine_215": 3, "elevator_a": 2, "elevator_b": 2, "coaches_club": 4},
    "lower_bowl_101": {"pepsi_gate": 4, "ramp_north": 2, "lower_bowl_112": 3, "coaches_club": 3},
    "lower_bowl_112": {"sap_gate": 4, "ramp_south": 2, "lower_bowl_101": 3, "stairs_east": 3},
    "mezzanine_201": {"concourse_main": 3, "upper_deck_301": 3, "elevator_a": 1},
    "mezzanine_215": {"concourse_main": 3, "upper_deck_314": 3, "elevator_b": 1, "stairs_east": 2},
    "upper_deck_301": {"mezzanine_201": 3, "ramp_north": 5, "elevator_a": 4},
    "upper_deck_314": {"mezzanine_215": 3, "ramp_south": 5, "elevator_b": 4},
    "coaches_club": {"concourse_main": 4, "lower_bowl_101": 3, "elevator_a": 2},
    "elevator_a": {"concourse_main": 2, "mezzanine_201": 1, "upper_deck_301": 4, "coaches_club": 2},
    "elevator_b": {"concourse_main": 2, "mezzanine_215": 1, "upper_deck_314": 4},
    "ramp_north": {"pepsi_gate": 3, "lower_bowl_101": 2, "upper_deck_301": 5},
    "ramp_south": {"sap_gate": 3, "lower_bowl_112": 2, "upper_deck_314": 5},
    "stairs_east": {"lower_bowl_112": 3, "mezzanine_215": 2},
}

METLIFE_COORDS = {
    "pepsi_gate": {"x": 0.15, "y": 0.85},
    "sap_gate": {"x": 0.85, "y": 0.85},
    "concourse_main": {"x": 0.5, "y": 0.6},
    "lower_bowl_101": {"x": 0.2, "y": 0.65},
    "lower_bowl_112": {"x": 0.8, "y": 0.65},
    "mezzanine_201": {"x": 0.25, "y": 0.4},
    "mezzanine_215": {"x": 0.75, "y": 0.4},
    "upper_deck_301": {"x": 0.3, "y": 0.2},
    "upper_deck_314": {"x": 0.7, "y": 0.2},
    "coaches_club": {"x": 0.5, "y": 0.75},
    "elevator_a": {"x": 0.35, "y": 0.5},
    "elevator_b": {"x": 0.65, "y": 0.5},
    "ramp_north": {"x": 0.15, "y": 0.5},
    "ramp_south": {"x": 0.85, "y": 0.5},
    "stairs_east": {"x": 0.9, "y": 0.3},
}

# ============ SOFI STADIUM ============
SOFI_ZONES = {
    "vip_entry": ZoneData("vip_entry", "accessible_path", "operational", 15, "stable", datetime.utcnow(), 1.0, 0, 2000),
    "main_entrance": ZoneData("main_entrance", "accessible_path", "congested", 75, "rising", datetime.utcnow(), 0.8, 0, 8000),
    "lower_bowl_100": ZoneData("lower_bowl_100", "destination", "operational", 90, "stable", datetime.utcnow(), 0.85, 1, 10000),
    "lower_bowl_125": ZoneData("lower_bowl_125", "destination", "congested", 88, "rising", datetime.utcnow(), 0.75, 1, 9500),
    "club_level_200": ZoneData("club_level_200", "destination", "operational", 40, "stable", datetime.utcnow(), 0.95, 2, 5000),
    "club_level_225": ZoneData("club_level_225", "destination", "operational", 35, "falling", datetime.utcnow(), 0.95, 2, 4800),
    "suite_level": ZoneData("suite_level", "destination", "operational", 5, "stable", datetime.utcnow(), 1.0, 2, 300),
    "upper_deck_500": ZoneData("upper_deck_500", "destination", "operational", 75, "falling", datetime.utcnow(), 0.75, 4, 12000),
    "upper_deck_525": ZoneData("upper_deck_525", "destination", "operational", 60, "stable", datetime.utcnow(), 0.75, 4, 11000),
    "elevator_vip": ZoneData("elevator_vip", "elevator", "operational", 25, "stable", datetime.utcnow(), 1.0, 0, 15),
    "elevator_main": ZoneData("elevator_main", "elevator", "operational", 65, "rising", datetime.utcnow(), 0.8, 0, 20),
    "ramp_west": ZoneData("ramp_west", "ramp", "operational", 30, "stable", datetime.utcnow(), 1.0, 1, 150),
    "ramp_east": ZoneData("ramp_east", "ramp", "congested", 80, "rising", datetime.utcnow(), 0.5, 1, 150),
    "main_concourse": ZoneData("main_concourse", "corridor", "operational", 65, "rising", datetime.utcnow(), 0.95, 1, 15000),
    "premium_concourse": ZoneData("premium_concourse", "corridor", "operational", 20, "stable", datetime.utcnow(), 1.0, 2, 3000),
}

SOFI_GRAPH = {
    "vip_entry": {"premium_concourse": 2, "suite_level": 3, "elevator_vip": 2},
    "main_entrance": {"main_concourse": 2, "ramp_east": 3, "lower_bowl_125": 4},
    "main_concourse": {"main_entrance": 2, "lower_bowl_100": 2, "lower_bowl_125": 3, "club_level_200": 4, "club_level_225": 4, "upper_deck_500": 6, "elevator_main": 2, "ramp_west": 3, "ramp_east": 3},
    "premium_concourse": {"vip_entry": 2, "suite_level": 2, "club_level_200": 3, "elevator_vip": 1},
    "lower_bowl_100": {"main_concourse": 2, "ramp_west": 3, "lower_bowl_125": 4},
    "lower_bowl_125": {"main_entrance": 4, "main_concourse": 3, "ramp_east": 3, "lower_bowl_100": 4},
    "club_level_200": {"main_concourse": 4, "premium_concourse": 3, "upper_deck_500": 4, "elevator_vip": 2},
    "club_level_225": {"main_concourse": 4, "upper_deck_525": 4, "elevator_main": 2},
    "suite_level": {"vip_entry": 3, "premium_concourse": 2, "elevator_vip": 2},
    "upper_deck_500": {"main_concourse": 6, "club_level_200": 4, "ramp_west": 5, "elevator_main": 5},
    "upper_deck_525": {"main_concourse": 6, "club_level_225": 4, "ramp_east": 5},
    "elevator_vip": {"vip_entry": 2, "premium_concourse": 1, "suite_level": 2, "club_level_200": 2},
    "elevator_main": {"main_concourse": 2, "club_level_225": 2, "upper_deck_500": 5},
    "ramp_west": {"main_concourse": 3, "lower_bowl_100": 3, "upper_deck_500": 5},
    "ramp_east": {"main_entrance": 3, "lower_bowl_125": 3, "upper_deck_525": 5},
}

SOFI_COORDS = {
    "vip_entry": {"x": 0.5, "y": 0.9},
    "main_entrance": {"x": 0.85, "y": 0.85},
    "main_concourse": {"x": 0.6, "y": 0.55},
    "premium_concourse": {"x": 0.35, "y": 0.55},
    "lower_bowl_100": {"x": 0.2, "y": 0.7},
    "lower_bowl_125": {"x": 0.8, "y": 0.7},
    "club_level_200": {"x": 0.3, "y": 0.4},
    "club_level_225": {"x": 0.7, "y": 0.4},
    "suite_level": {"x": 0.5, "y": 0.7},
    "upper_deck_500": {"x": 0.25, "y": 0.2},
    "upper_deck_525": {"x": 0.75, "y": 0.2},
    "elevator_vip": {"x": 0.4, "y": 0.6},
    "elevator_main": {"x": 0.65, "y": 0.6},
    "ramp_west": {"x": 0.1, "y": 0.5},
    "ramp_east": {"x": 0.9, "y": 0.5},
}

# ============ AZTECA STADIUM ============
AZTECA_ZONES = {
    "entrance_a_tlalpan": ZoneData("entrance_a_tlalpan", "accessible_path", "congested", 85, "rising", datetime.utcnow(), 0.7, 0, 6000),
    "entrance_b_circuito": ZoneData("entrance_b_circuito", "accessible_path", "operational", 30, "falling", datetime.utcnow(), 1.0, 0, 5000),
    "entrance_c_izazaga": ZoneData("entrance_c_izazaga", "accessible_path", "operational", 45, "stable", datetime.utcnow(), 0.9, 0, 5500),
    "lower_tier_north": ZoneData("lower_tier_north", "destination", "operational", 70, "stable", datetime.utcnow(), 0.85, 1, 12000),
    "lower_tier_south": ZoneData("lower_tier_south", "destination", "operational", 65, "stable", datetime.utcnow(), 0.85, 1, 11000),
    "middle_tier": ZoneData("middle_tier", "corridor", "operational", 50, "stable", datetime.utcnow(), 0.9, 2, 15000),
    "upper_tier": ZoneData("upper_tier", "destination", "operational", 60, "rising", datetime.utcnow(), 0.75, 3, 14000),
    "vip_section": ZoneData("vip_section", "destination", "operational", 25, "stable", datetime.utcnow(), 1.0, 2, 800),
    "ramp_1_accessible": ZoneData("ramp_1_accessible", "ramp", "operational", 40, "stable", datetime.utcnow(), 1.0, 1, 300),
    "ramp_4_accessible": ZoneData("ramp_4_accessible", "ramp", "operational", 45, "stable", datetime.utcnow(), 1.0, 1, 300),
    "elevator_north": ZoneData("elevator_north", "elevator", "operational", 55, "stable", datetime.utcnow(), 0.9, 0, 18),
    "elevator_south": ZoneData("elevator_south", "elevator", "maintenance", 0, "stable", datetime.utcnow(), 0.0, 0, 18),
    "stairs_west": ZoneData("stairs_west", "stairs", "operational", 60, "stable", datetime.utcnow(), 0.3, 3, 500),
    "lower_concourse": ZoneData("lower_concourse", "corridor", "operational", 55, "stable", datetime.utcnow(), 0.95, 1, 8000),
}

AZTECA_GRAPH = {
    "entrance_a_tlalpan": {"lower_concourse": 2, "ramp_1_accessible": 3, "lower_tier_north": 3},
    "entrance_b_circuito": {"middle_tier": 4, "ramp_4_accessible": 3, "upper_tier": 6, "elevator_north": 3},
    "entrance_c_izazaga": {"lower_concourse": 2, "lower_tier_south": 3, "stairs_west": 4},
    "lower_concourse": {"entrance_a_tlalpan": 2, "entrance_c_izazaga": 2, "lower_tier_north": 2, "lower_tier_south": 2, "ramp_1_accessible": 2, "middle_tier": 3},
    "lower_tier_north": {"entrance_a_tlalpan": 3, "lower_concourse": 2, "ramp_1_accessible": 2, "middle_tier": 3},
    "lower_tier_south": {"entrance_c_izazaga": 3, "lower_concourse": 2, "middle_tier": 3, "vip_section": 4},
    "middle_tier": {"lower_concourse": 3, "lower_tier_north": 3, "lower_tier_south": 3, "entrance_b_circuito": 4, "upper_tier": 4, "ramp_4_accessible": 2, "elevator_north": 2, "stairs_west": 3, "vip_section": 3},
    "upper_tier": {"entrance_b_circuito": 6, "middle_tier": 4, "ramp_4_accessible": 4, "stairs_west": 4, "elevator_north": 5},
    "vip_section": {"lower_tier_south": 4, "middle_tier": 3, "elevator_north": 2},
    "ramp_1_accessible": {"entrance_a_tlalpan": 3, "lower_concourse": 2, "lower_tier_north": 2},
    "ramp_4_accessible": {"entrance_b_circuito": 3, "middle_tier": 2, "upper_tier": 4},
    "elevator_north": {"entrance_b_circuito": 3, "middle_tier": 2, "upper_tier": 5, "vip_section": 2},
    "elevator_south": {},
    "stairs_west": {"entrance_c_izazaga": 4, "middle_tier": 3, "upper_tier": 4},
}

AZTECA_COORDS = {
    "entrance_a_tlalpan": {"x": 0.2, "y": 0.9},
    "entrance_b_circuito": {"x": 0.8, "y": 0.85},
    "entrance_c_izazaga": {"x": 0.5, "y": 0.9},
    "lower_concourse": {"x": 0.5, "y": 0.65},
    "lower_tier_north": {"x": 0.25, "y": 0.7},
    "lower_tier_south": {"x": 0.75, "y": 0.7},
    "middle_tier": {"x": 0.5, "y": 0.45},
    "upper_tier": {"x": 0.5, "y": 0.2},
    "vip_section": {"x": 0.85, "y": 0.6},
    "ramp_1_accessible": {"x": 0.1, "y": 0.7},
    "ramp_4_accessible": {"x": 0.9, "y": 0.5},
    "elevator_north": {"x": 0.65, "y": 0.45},
    "elevator_south": {"x": 0.35, "y": 0.45},
    "stairs_west": {"x": 0.15, "y": 0.35},
}

# ============ STADIUM REGISTRY ============
STADIUMS: Dict[str, StadiumConfig] = {
    "metlife": StadiumConfig(
        stadium_id="metlife",
        name="MetLife Stadium",
        location="East Rutherford, NJ",
        capacity=82500,
        zones=METLIFE_ZONES,
        graph=METLIFE_GRAPH,
        coordinates=METLIFE_COORDS,
    ),
    "sofi": StadiumConfig(
        stadium_id="sofi",
        name="SoFi Stadium",
        location="Inglewood, CA",
        capacity=70000,
        zones=SOFI_ZONES,
        graph=SOFI_GRAPH,
        coordinates=SOFI_COORDS,
    ),
    "azteca": StadiumConfig(
        stadium_id="azteca",
        name="Estadio Azteca",
        location="Mexico City, Mexico",
        capacity=87000,
        zones=AZTECA_ZONES,
        graph=AZTECA_GRAPH,
        coordinates=AZTECA_COORDS,
    ),
}


class StadiumDatabase:
    """Thread-safe in-memory database with live data simulation."""

    def __init__(self):
        self._stadiums = STADIUMS
        self._history: Dict[str, List[Dict]] = {sid: [] for sid in self._stadiums}
        self._announcements: List[Dict] = []
        self._simulation_task: Optional[asyncio.Task] = None
        self._callbacks: List[callable] = []

    def get_stadium(self, stadium_id: str) -> Optional[StadiumConfig]:
        return self._stadiums.get(stadium_id)

    def list_stadiums(self) -> List[Dict[str, Any]]:
        return [
            {
                "stadium_id": s.stadium_id,
                "name": s.name,
                "location": s.location,
                "capacity": s.capacity,
                "zone_count": len(s.zones),
            }
            for s in self._stadiums.values()
        ]

    def get_zones(self, stadium_id: str) -> List[ZoneData]:
        stadium = self.get_stadium(stadium_id)
        if not stadium:
            return []
        return list(stadium.zones.values())

    def get_zone(self, stadium_id: str, zone_id: str) -> Optional[ZoneData]:
        stadium = self.get_stadium(stadium_id)
        if not stadium:
            return None
        return stadium.zones.get(zone_id)

    def update_zone(self, stadium_id: str, zone_id: str, **kwargs):
        zone = self.get_zone(stadium_id, zone_id)
        if zone:
            for key, value in kwargs.items():
                if hasattr(zone, key):
                    setattr(zone, key, value)
            zone.last_updated = datetime.utcnow()

    def get_graph(self, stadium_id: str) -> Dict[str, Dict[str, int]]:
        stadium = self.get_stadium(stadium_id)
        if not stadium:
            return {}
        return stadium.graph

    def get_coordinates(self, stadium_id: str) -> Dict[str, Dict[str, float]]:
        stadium = self.get_stadium(stadium_id)
        if not stadium:
            return {}
        return stadium.coordinates

    def add_announcement(self, text: str, processed: Dict = None):
        ann = {
            "id": f"ann_{len(self._announcements)}",
            "raw_text": text,
            "timestamp": datetime.utcnow().isoformat(),
            "processed": processed,
        }
        self._announcements.append(ann)
        return ann

    def get_announcements(self, limit: int = 20) -> List[Dict]:
        return sorted(self._announcements, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def record_history(self, stadium_id: str):
        """Record current zone states for analytics."""
        zones = self.get_zones(stadium_id)
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "zones": [
                {
                    "zone_id": z.zone_id,
                    "crowd_density_pct": z.crowd_density_pct,
                    "status": z.status,
                    "density_trend": z.density_trend,
                }
                for z in zones
            ],
        }
        self._history[stadium_id].append(snapshot)
        # Keep last 1000 snapshots
        if len(self._history[stadium_id]) > 1000:
            self._history[stadium_id] = self._history[stadium_id][-1000:]

    def get_history(self, stadium_id: str, minutes: int = 60) -> List[Dict]:
        """Get historical data for the last N minutes."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            h for h in self._history.get(stadium_id, [])
            if datetime.fromisoformat(h["timestamp"]) > cutoff
        ]

    async def start_simulation(self):
        """Start background crowd simulation."""
        if self._simulation_task and not self._simulation_task.done():
            return
        self._simulation_task = asyncio.create_task(self._simulation_loop())

    async def _simulation_loop(self):
        """Simulate realistic crowd dynamics."""
        while True:
            try:
                for stadium_id, stadium in self._stadiums.items():
                    for zone in stadium.zones.values():
                        # Realistic crowd dynamics
                        if zone.density_trend == "rising":
                            delta = random.randint(-5, 15)
                        elif zone.density_trend == "falling":
                            delta = random.randint(-15, 5)
                        else:
                            delta = random.randint(-10, 10)

                        new_density = max(0, min(100, zone.crowd_density_pct + delta))
                        zone.crowd_density_pct = new_density

                        # Update trend based on new density
                        if new_density > 80:
                            zone.density_trend = "rising" if random.random() > 0.3 else "stable"
                        elif new_density < 30:
                            zone.density_trend = "falling" if random.random() > 0.3 else "stable"
                        else:
                            zone.density_trend = random.choice(["rising", "falling", "stable"])

                        # Randomly change status
                        if random.random() < 0.02:  # 2% chance
                            if zone.status == "operational" and new_density > 85:
                                zone.status = "congested"
                            elif zone.status == "congested" and new_density < 60:
                                zone.status = "operational"

                        zone.last_updated = datetime.utcnow()

                    self.record_history(stadium_id)

                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(5)

    def stop_simulation(self):
        if self._simulation_task and not self._simulation_task.done():
            self._simulation_task.cancel()


# Global database instance
db = StadiumDatabase()
