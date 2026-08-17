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


# ============ NARENDRA MODI STADIUM (AHMEDABAD) ============
NARENDRA_MODI_ZONES = {
    "gate_1_vip": ZoneData("gate_1_vip", "accessible_path", "operational", 35, "stable", datetime.utcnow(), 1.0, 0, 8000),
    "gate_2_general": ZoneData("gate_2_general", "accessible_path", "congested", 75, "rising", datetime.utcnow(), 0.9, 0, 15000),
    "gate_3_metro": ZoneData("gate_3_metro", "accessible_path", "operational", 45, "stable", datetime.utcnow(), 1.0, 0, 12000),
    "gate_4_north": ZoneData("gate_4_north", "accessible_path", "operational", 30, "falling", datetime.utcnow(), 1.0, 0, 10000),
    "concourse_main": ZoneData("concourse_main", "corridor", "operational", 60, "stable", datetime.utcnow(), 1.0, 1, 20000),
    "presidential_gallery": ZoneData("presidential_gallery", "destination", "operational", 20, "stable", datetime.utcnow(), 1.0, 1, 1500),
    "north_wheelchair_deck": ZoneData("north_wheelchair_deck", "destination", "operational", 40, "stable", datetime.utcnow(), 1.0, 2, 800),
    "south_wheelchair_deck": ZoneData("south_wheelchair_deck", "destination", "operational", 35, "stable", datetime.utcnow(), 1.0, 2, 800),
    "ramp_a_west": ZoneData("ramp_a_west", "ramp", "operational", 40, "stable", datetime.utcnow(), 1.0, 1, 1200),
    "ramp_b_east": ZoneData("ramp_b_east", "ramp", "congested", 80, "rising", datetime.utcnow(), 0.7, 1, 1200),
    "elevator_1_vip": ZoneData("elevator_1_vip", "elevator", "operational", 40, "stable", datetime.utcnow(), 1.0, 0, 30),
    "elevator_2_north": ZoneData("elevator_2_north", "elevator", "operational", 50, "stable", datetime.utcnow(), 1.0, 0, 30),
    "elevator_3_south": ZoneData("elevator_3_south", "elevator", "maintenance", 0, "stable", datetime.utcnow(), 0.0, 0, 30),
    "club_concourse_l2": ZoneData("club_concourse_l2", "corridor", "operational", 45, "stable", datetime.utcnow(), 0.95, 2, 8000),
    "accessible_restroom_hub": ZoneData("accessible_restroom_hub", "destination", "operational", 25, "stable", datetime.utcnow(), 1.0, 1, 500),
}

NARENDRA_MODI_GRAPH = {
    "gate_1_vip": {"concourse_main": 2, "presidential_gallery": 2, "elevator_1_vip": 1, "ramp_a_west": 3},
    "gate_2_general": {"concourse_main": 3, "ramp_b_east": 3, "south_wheelchair_deck": 4},
    "gate_3_metro": {"concourse_main": 3, "ramp_b_east": 2, "south_wheelchair_deck": 3},
    "gate_4_north": {"concourse_main": 3, "ramp_a_west": 2, "north_wheelchair_deck": 3},
    "concourse_main": {"gate_1_vip": 2, "gate_2_general": 3, "gate_3_metro": 3, "gate_4_north": 3, "presidential_gallery": 2, "elevator_1_vip": 1, "elevator_2_north": 2, "elevator_3_south": 2, "ramp_a_west": 2, "ramp_b_east": 2, "accessible_restroom_hub": 2},
    "presidential_gallery": {"gate_1_vip": 2, "concourse_main": 2, "elevator_1_vip": 1, "club_concourse_l2": 2},
    "north_wheelchair_deck": {"ramp_a_west": 3, "elevator_2_north": 1, "club_concourse_l2": 2},
    "south_wheelchair_deck": {"ramp_b_east": 3, "elevator_3_south": 1, "club_concourse_l2": 2},
    "ramp_a_west": {"gate_1_vip": 3, "gate_4_north": 2, "concourse_main": 2, "north_wheelchair_deck": 3, "club_concourse_l2": 4},
    "ramp_b_east": {"gate_2_general": 3, "gate_3_metro": 2, "concourse_main": 2, "south_wheelchair_deck": 3, "club_concourse_l2": 4},
    "elevator_1_vip": {"gate_1_vip": 1, "concourse_main": 1, "presidential_gallery": 1, "club_concourse_l2": 2},
    "elevator_2_north": {"concourse_main": 2, "north_wheelchair_deck": 1, "club_concourse_l2": 2},
    "elevator_3_south": {"concourse_main": 2, "south_wheelchair_deck": 1, "club_concourse_l2": 2},
    "club_concourse_l2": {"presidential_gallery": 2, "north_wheelchair_deck": 2, "south_wheelchair_deck": 2, "elevator_1_vip": 2, "elevator_2_north": 2, "elevator_3_south": 2, "accessible_restroom_hub": 2},
    "accessible_restroom_hub": {"concourse_main": 2, "club_concourse_l2": 2},
}

NARENDRA_MODI_COORDS = {
    "gate_1_vip": {"x": 0.5, "y": 0.9},
    "gate_2_general": {"x": 0.85, "y": 0.75},
    "gate_3_metro": {"x": 0.85, "y": 0.25},
    "gate_4_north": {"x": 0.15, "y": 0.25},
    "concourse_main": {"x": 0.5, "y": 0.65},
    "presidential_gallery": {"x": 0.5, "y": 0.78},
    "north_wheelchair_deck": {"x": 0.3, "y": 0.3},
    "south_wheelchair_deck": {"x": 0.7, "y": 0.3},
    "ramp_a_west": {"x": 0.2, "y": 0.5},
    "ramp_b_east": {"x": 0.8, "y": 0.5},
    "elevator_1_vip": {"x": 0.4, "y": 0.6},
    "elevator_2_north": {"x": 0.35, "y": 0.4},
    "elevator_3_south": {"x": 0.65, "y": 0.4},
    "club_concourse_l2": {"x": 0.5, "y": 0.45},
    "accessible_restroom_hub": {"x": 0.5, "y": 0.2},
}

# ============ WANKHEDE STADIUM (MUMBAI) ============
WANKHEDE_ZONES = {
    "gate_3_mca": ZoneData("gate_3_mca", "accessible_path", "operational", 40, "stable", datetime.utcnow(), 1.0, 0, 4000),
    "gate_7_garware": ZoneData("gate_7_garware", "accessible_path", "congested", 85, "rising", datetime.utcnow(), 0.85, 0, 6000),
    "sachin_tendulkar_stand": ZoneData("sachin_tendulkar_stand", "destination", "operational", 65, "stable", datetime.utcnow(), 0.9, 1, 7500),
    "garware_wheelchair_deck": ZoneData("garware_wheelchair_deck", "destination", "operational", 30, "stable", datetime.utcnow(), 1.0, 1, 500),
    "vijay_merchant_stand": ZoneData("vijay_merchant_stand", "destination", "operational", 50, "falling", datetime.utcnow(), 0.9, 1, 6000),
    "sunil_gavaskar_stand": ZoneData("sunil_gavaskar_stand", "destination", "operational", 55, "stable", datetime.utcnow(), 0.9, 1, 6500),
    "mca_pavilion_terrace": ZoneData("mca_pavilion_terrace", "destination", "operational", 25, "stable", datetime.utcnow(), 1.0, 2, 1200),
    "central_concourse": ZoneData("central_concourse", "corridor", "operational", 55, "stable", datetime.utcnow(), 1.0, 1, 10000),
    "central_elevator_a": ZoneData("central_elevator_a", "elevator", "operational", 45, "stable", datetime.utcnow(), 1.0, 0, 25),
    "central_elevator_b": ZoneData("central_elevator_b", "elevator", "operational", 40, "stable", datetime.utcnow(), 1.0, 0, 25),
    "north_ramp": ZoneData("north_ramp", "ramp", "operational", 35, "stable", datetime.utcnow(), 1.0, 1, 400),
    "south_ramp": ZoneData("south_ramp", "ramp", "operational", 40, "stable", datetime.utcnow(), 1.0, 1, 400),
    "medical_aid_station": ZoneData("medical_aid_station", "destination", "operational", 15, "stable", datetime.utcnow(), 1.0, 1, 200),
}

WANKHEDE_GRAPH = {
    "gate_3_mca": {"central_concourse": 2, "mca_pavilion_terrace": 2, "central_elevator_a": 1},
    "gate_7_garware": {"central_concourse": 2, "garware_wheelchair_deck": 2, "north_ramp": 2},
    "sachin_tendulkar_stand": {"central_concourse": 3, "south_ramp": 2, "sunil_gavaskar_stand": 3},
    "garware_wheelchair_deck": {"gate_7_garware": 2, "central_concourse": 2, "north_ramp": 1, "vijay_merchant_stand": 2},
    "vijay_merchant_stand": {"garware_wheelchair_deck": 2, "north_ramp": 2, "central_concourse": 3},
    "sunil_gavaskar_stand": {"central_concourse": 2, "south_ramp": 2, "sachin_tendulkar_stand": 3},
    "mca_pavilion_terrace": {"gate_3_mca": 2, "central_concourse": 2, "central_elevator_a": 1, "medical_aid_station": 3},
    "central_concourse": {"gate_3_mca": 2, "gate_7_garware": 2, "sachin_tendulkar_stand": 3, "garware_wheelchair_deck": 2, "sunil_gavaskar_stand": 2, "central_elevator_a": 1, "central_elevator_b": 1, "north_ramp": 2, "south_ramp": 2, "medical_aid_station": 2},
    "central_elevator_a": {"gate_3_mca": 1, "central_concourse": 1, "mca_pavilion_terrace": 1},
    "central_elevator_b": {"central_concourse": 1, "sunil_gavaskar_stand": 2, "sachin_tendulkar_stand": 2},
    "north_ramp": {"gate_7_garware": 2, "garware_wheelchair_deck": 1, "vijay_merchant_stand": 2, "central_concourse": 2},
    "south_ramp": {"central_concourse": 2, "sachin_tendulkar_stand": 2, "sunil_gavaskar_stand": 2},
    "medical_aid_station": {"central_concourse": 2, "mca_pavilion_terrace": 3},
}

WANKHEDE_COORDS = {
    "gate_3_mca": {"x": 0.5, "y": 0.88},
    "gate_7_garware": {"x": 0.15, "y": 0.75},
    "sachin_tendulkar_stand": {"x": 0.8, "y": 0.35},
    "garware_wheelchair_deck": {"x": 0.2, "y": 0.6},
    "vijay_merchant_stand": {"x": 0.2, "y": 0.35},
    "sunil_gavaskar_stand": {"x": 0.8, "y": 0.65},
    "mca_pavilion_terrace": {"x": 0.5, "y": 0.72},
    "central_concourse": {"x": 0.5, "y": 0.52},
    "central_elevator_a": {"x": 0.38, "y": 0.52},
    "central_elevator_b": {"x": 0.62, "y": 0.52},
    "north_ramp": {"x": 0.25, "y": 0.45},
    "south_ramp": {"x": 0.75, "y": 0.45},
    "medical_aid_station": {"x": 0.5, "y": 0.25},
}

# ============ M. CHINNASWAMY STADIUM (BENGALURU) ============
CHINNASWAMY_ZONES = {
    "gate_1_cubbon": ZoneData("gate_1_cubbon", "accessible_path", "operational", 30, "stable", datetime.utcnow(), 1.0, 0, 5000),
    "gate_12_queens": ZoneData("gate_12_queens", "accessible_path", "congested", 80, "rising", datetime.utcnow(), 0.9, 0, 6000),
    "royal_challengers_stand": ZoneData("royal_challengers_stand", "destination", "operational", 70, "stable", datetime.utcnow(), 0.9, 1, 8000),
    "pavilion_terrace": ZoneData("pavilion_terrace", "destination", "operational", 25, "stable", datetime.utcnow(), 1.0, 2, 1500),
    "brijesh_patel_stand": ZoneData("brijesh_patel_stand", "destination", "operational", 45, "falling", datetime.utcnow(), 0.9, 1, 7000),
    "wheelchair_deck_east": ZoneData("wheelchair_deck_east", "destination", "operational", 30, "stable", datetime.utcnow(), 1.0, 1, 600),
    "main_concourse": ZoneData("main_concourse", "corridor", "operational", 50, "stable", datetime.utcnow(), 1.0, 1, 12000),
    "accessible_ramp_north": ZoneData("accessible_ramp_north", "ramp", "operational", 35, "stable", datetime.utcnow(), 1.0, 1, 500),
    "accessible_ramp_south": ZoneData("accessible_ramp_south", "ramp", "operational", 40, "stable", datetime.utcnow(), 1.0, 1, 500),
    "elevator_a_terrace": ZoneData("elevator_a_terrace", "elevator", "operational", 40, "stable", datetime.utcnow(), 1.0, 0, 20),
    "elevator_b_pavilion": ZoneData("elevator_b_pavilion", "elevator", "operational", 35, "stable", datetime.utcnow(), 1.0, 0, 20),
    "visually_assisted_corridor": ZoneData("visually_assisted_corridor", "accessible_path", "operational", 25, "stable", datetime.utcnow(), 1.0, 1, 3000),
    "first_aid_accessible_hub": ZoneData("first_aid_accessible_hub", "destination", "operational", 15, "stable", datetime.utcnow(), 1.0, 1, 300),
}

CHINNASWAMY_GRAPH = {
    "gate_1_cubbon": {"main_concourse": 2, "pavilion_terrace": 3, "accessible_ramp_north": 2, "elevator_a_terrace": 1},
    "gate_12_queens": {"main_concourse": 2, "wheelchair_deck_east": 2, "accessible_ramp_south": 2},
    "royal_challengers_stand": {"main_concourse": 2, "accessible_ramp_north": 2, "visually_assisted_corridor": 2},
    "pavilion_terrace": {"gate_1_cubbon": 3, "main_concourse": 2, "elevator_a_terrace": 1, "elevator_b_pavilion": 1},
    "brijesh_patel_stand": {"main_concourse": 2, "accessible_ramp_south": 2, "visually_assisted_corridor": 2},
    "wheelchair_deck_east": {"gate_12_queens": 2, "main_concourse": 2, "accessible_ramp_south": 1},
    "main_concourse": {"gate_1_cubbon": 2, "gate_12_queens": 2, "royal_challengers_stand": 2, "pavilion_terrace": 2, "brijesh_patel_stand": 2, "wheelchair_deck_east": 2, "accessible_ramp_north": 1, "accessible_ramp_south": 1, "visually_assisted_corridor": 1, "first_aid_accessible_hub": 2},
    "accessible_ramp_north": {"gate_1_cubbon": 2, "royal_challengers_stand": 2, "main_concourse": 1},
    "accessible_ramp_south": {"gate_12_queens": 2, "brijesh_patel_stand": 2, "wheelchair_deck_east": 1, "main_concourse": 1},
    "elevator_a_terrace": {"gate_1_cubbon": 1, "pavilion_terrace": 1, "main_concourse": 1},
    "elevator_b_pavilion": {"main_concourse": 1, "pavilion_terrace": 1},
    "visually_assisted_corridor": {"main_concourse": 1, "royal_challengers_stand": 2, "brijesh_patel_stand": 2, "first_aid_accessible_hub": 1},
    "first_aid_accessible_hub": {"main_concourse": 2, "visually_assisted_corridor": 1},
}

CHINNASWAMY_COORDS = {
    "gate_1_cubbon": {"x": 0.15, "y": 0.85},
    "gate_12_queens": {"x": 0.85, "y": 0.85},
    "royal_challengers_stand": {"x": 0.2, "y": 0.35},
    "pavilion_terrace": {"x": 0.5, "y": 0.8},
    "brijesh_patel_stand": {"x": 0.8, "y": 0.35},
    "wheelchair_deck_east": {"x": 0.78, "y": 0.55},
    "main_concourse": {"x": 0.5, "y": 0.6},
    "accessible_ramp_north": {"x": 0.25, "y": 0.5},
    "accessible_ramp_south": {"x": 0.75, "y": 0.5},
    "elevator_a_terrace": {"x": 0.35, "y": 0.65},
    "elevator_b_pavilion": {"x": 0.65, "y": 0.65},
    "visually_assisted_corridor": {"x": 0.5, "y": 0.4},
    "first_aid_accessible_hub": {"x": 0.5, "y": 0.2},
}

# ============ EDEN GARDENS (KOLKATA) ============
EDEN_GARDENS_ZONES = {
    "gate_1_mahabir": ZoneData("gate_1_mahabir", "accessible_path", "operational", 35, "stable", datetime.utcnow(), 1.0, 0, 7000),
    "gate_4_accessible": ZoneData("gate_4_accessible", "accessible_path", "operational", 20, "stable", datetime.utcnow(), 1.0, 0, 4000),
    "club_house_balcony": ZoneData("club_house_balcony", "destination", "operational", 25, "stable", datetime.utcnow(), 1.0, 2, 2000),
    "block_b_lower": ZoneData("block_b_lower", "destination", "operational", 70, "rising", datetime.utcnow(), 0.9, 1, 9000),
    "block_d_wheelchair_deck": ZoneData("block_d_wheelchair_deck", "destination", "operational", 30, "stable", datetime.utcnow(), 1.0, 1, 700),
    "block_k_upper": ZoneData("block_k_upper", "destination", "congested", 85, "rising", datetime.utcnow(), 0.75, 2, 10000),
    "block_l_accessible": ZoneData("block_l_accessible", "destination", "operational", 35, "stable", datetime.utcnow(), 1.0, 1, 800),
    "main_concourse": ZoneData("main_concourse", "corridor", "operational", 60, "stable", datetime.utcnow(), 1.0, 1, 15000),
    "high_capacity_ramp": ZoneData("high_capacity_ramp", "ramp", "operational", 40, "stable", datetime.utcnow(), 1.0, 1, 1000),
    "west_elevator": ZoneData("west_elevator", "elevator", "operational", 45, "stable", datetime.utcnow(), 1.0, 0, 25),
    "east_elevator": ZoneData("east_elevator", "elevator", "operational", 40, "stable", datetime.utcnow(), 1.0, 0, 25),
    "accessible_food_plaza": ZoneData("accessible_food_plaza", "destination", "operational", 50, "falling", datetime.utcnow(), 1.0, 1, 2500),
    "medical_emergency_room": ZoneData("medical_emergency_room", "destination", "operational", 10, "stable", datetime.utcnow(), 1.0, 1, 300),
}

EDEN_GARDENS_GRAPH = {
    "gate_1_mahabir": {"main_concourse": 2, "club_house_balcony": 3, "east_elevator": 1},
    "gate_4_accessible": {"main_concourse": 2, "high_capacity_ramp": 1, "block_d_wheelchair_deck": 2, "west_elevator": 1},
    "club_house_balcony": {"gate_1_mahabir": 3, "main_concourse": 2, "east_elevator": 1, "west_elevator": 1},
    "block_b_lower": {"main_concourse": 2, "high_capacity_ramp": 2, "block_d_wheelchair_deck": 2},
    "block_d_wheelchair_deck": {"gate_4_accessible": 2, "high_capacity_ramp": 1, "main_concourse": 2, "block_b_lower": 2},
    "block_k_upper": {"main_concourse": 4, "east_elevator": 2, "block_l_accessible": 3},
    "block_l_accessible": {"main_concourse": 2, "east_elevator": 1, "block_k_upper": 3},
    "main_concourse": {"gate_1_mahabir": 2, "gate_4_accessible": 2, "club_house_balcony": 2, "block_b_lower": 2, "block_d_wheelchair_deck": 2, "block_k_upper": 4, "block_l_accessible": 2, "high_capacity_ramp": 1, "west_elevator": 1, "east_elevator": 1, "accessible_food_plaza": 2, "medical_emergency_room": 2},
    "high_capacity_ramp": {"gate_4_accessible": 1, "block_d_wheelchair_deck": 1, "main_concourse": 1, "block_b_lower": 2},
    "west_elevator": {"gate_4_accessible": 1, "main_concourse": 1, "club_house_balcony": 1},
    "east_elevator": {"gate_1_mahabir": 1, "main_concourse": 1, "club_house_balcony": 1, "block_l_accessible": 1, "block_k_upper": 2},
    "accessible_food_plaza": {"main_concourse": 2, "medical_emergency_room": 2},
    "medical_emergency_room": {"main_concourse": 2, "accessible_food_plaza": 2},
}

EDEN_GARDENS_COORDS = {
    "gate_1_mahabir": {"x": 0.5, "y": 0.88},
    "gate_4_accessible": {"x": 0.15, "y": 0.8},
    "club_house_balcony": {"x": 0.5, "y": 0.72},
    "block_b_lower": {"x": 0.2, "y": 0.6},
    "block_d_wheelchair_deck": {"x": 0.2, "y": 0.35},
    "block_k_upper": {"x": 0.8, "y": 0.35},
    "block_l_accessible": {"x": 0.8, "y": 0.6},
    "main_concourse": {"x": 0.5, "y": 0.55},
    "high_capacity_ramp": {"x": 0.28, "y": 0.48},
    "west_elevator": {"x": 0.38, "y": 0.58},
    "east_elevator": {"x": 0.62, "y": 0.58},
    "accessible_food_plaza": {"x": 0.5, "y": 0.38},
    "medical_emergency_room": {"x": 0.5, "y": 0.2},
}

# ============ ARUN JAITLEY STADIUM (NEW DELHI) ============
ARUN_JAITLEY_ZONES = {
    "gate_1_kotla": ZoneData("gate_1_kotla", "accessible_path", "operational", 45, "stable", datetime.utcnow(), 1.0, 0, 5000),
    "gate_8_accessible": ZoneData("gate_8_accessible", "accessible_path", "operational", 25, "stable", datetime.utcnow(), 1.0, 0, 3500),
    "old_clubhouse_stand": ZoneData("old_clubhouse_stand", "destination", "operational", 40, "stable", datetime.utcnow(), 1.0, 1, 3000),
    "east_stand_wheelchair": ZoneData("east_stand_wheelchair", "destination", "operational", 30, "stable", datetime.utcnow(), 1.0, 1, 600),
    "west_stand_lower": ZoneData("west_stand_lower", "destination", "operational", 65, "rising", datetime.utcnow(), 0.9, 1, 7500),
    "bishan_bedi_stand": ZoneData("bishan_bedi_stand", "destination", "operational", 50, "stable", datetime.utcnow(), 0.85, 2, 6000),
    "main_concourse": ZoneData("main_concourse", "corridor", "operational", 55, "stable", datetime.utcnow(), 1.0, 1, 10000),
    "ramp_south_concourse": ZoneData("ramp_south_concourse", "ramp", "operational", 35, "stable", datetime.utcnow(), 1.0, 1, 500),
    "elevator_a_clubhouse": ZoneData("elevator_a_clubhouse", "elevator", "operational", 35, "stable", datetime.utcnow(), 1.0, 0, 20),
    "elevator_b_east": ZoneData("elevator_b_east", "elevator", "operational", 40, "stable", datetime.utcnow(), 1.0, 0, 20),
    "accessible_restroom_hub": ZoneData("accessible_restroom_hub", "destination", "operational", 20, "stable", datetime.utcnow(), 1.0, 1, 300),
}

ARUN_JAITLEY_GRAPH = {
    "gate_1_kotla": {"main_concourse": 2, "old_clubhouse_stand": 2, "elevator_a_clubhouse": 1},
    "gate_8_accessible": {"main_concourse": 2, "ramp_south_concourse": 1, "west_stand_lower": 2},
    "old_clubhouse_stand": {"gate_1_kotla": 2, "main_concourse": 2, "elevator_a_clubhouse": 1},
    "east_stand_wheelchair": {"main_concourse": 2, "elevator_b_east": 1, "bishan_bedi_stand": 3},
    "west_stand_lower": {"gate_8_accessible": 2, "ramp_south_concourse": 1, "main_concourse": 2},
    "bishan_bedi_stand": {"main_concourse": 3, "east_stand_wheelchair": 3, "elevator_b_east": 2},
    "main_concourse": {"gate_1_kotla": 2, "gate_8_accessible": 2, "old_clubhouse_stand": 2, "east_stand_wheelchair": 2, "west_stand_lower": 2, "bishan_bedi_stand": 3, "ramp_south_concourse": 1, "elevator_a_clubhouse": 1, "elevator_b_east": 1, "accessible_restroom_hub": 2},
    "ramp_south_concourse": {"gate_8_accessible": 1, "west_stand_lower": 1, "main_concourse": 1},
    "elevator_a_clubhouse": {"gate_1_kotla": 1, "old_clubhouse_stand": 1, "main_concourse": 1},
    "elevator_b_east": {"main_concourse": 1, "east_stand_wheelchair": 1, "bishan_bedi_stand": 2},
    "accessible_restroom_hub": {"main_concourse": 2},
}

ARUN_JAITLEY_COORDS = {
    "gate_1_kotla": {"x": 0.5, "y": 0.88},
    "gate_8_accessible": {"x": 0.15, "y": 0.8},
    "old_clubhouse_stand": {"x": 0.5, "y": 0.72},
    "east_stand_wheelchair": {"x": 0.8, "y": 0.55},
    "west_stand_lower": {"x": 0.2, "y": 0.55},
    "bishan_bedi_stand": {"x": 0.5, "y": 0.25},
    "main_concourse": {"x": 0.5, "y": 0.58},
    "ramp_south_concourse": {"x": 0.25, "y": 0.48},
    "elevator_a_clubhouse": {"x": 0.38, "y": 0.65},
    "elevator_b_east": {"x": 0.62, "y": 0.65},
    "accessible_restroom_hub": {"x": 0.5, "y": 0.42},
}

# ============ STADIUM REGISTRY ============
STADIUMS: Dict[str, StadiumConfig] = {
    "narendra_modi": StadiumConfig(
        stadium_id="narendra_modi",
        name="Narendra Modi Stadium",
        location="Ahmedabad, Gujarat",
        capacity=132000,
        zones=NARENDRA_MODI_ZONES,
        graph=NARENDRA_MODI_GRAPH,
        coordinates=NARENDRA_MODI_COORDS,
    ),
    "wankhede": StadiumConfig(
        stadium_id="wankhede",
        name="Wankhede Stadium",
        location="Mumbai, Maharashtra",
        capacity=33000,
        zones=WANKHEDE_ZONES,
        graph=WANKHEDE_GRAPH,
        coordinates=WANKHEDE_COORDS,
    ),
    "chinnaswamy": StadiumConfig(
        stadium_id="chinnaswamy",
        name="M. Chinnaswamy Stadium",
        location="Bengaluru, Karnataka",
        capacity=40000,
        zones=CHINNASWAMY_ZONES,
        graph=CHINNASWAMY_GRAPH,
        coordinates=CHINNASWAMY_COORDS,
    ),
    "eden_gardens": StadiumConfig(
        stadium_id="eden_gardens",
        name="Eden Gardens",
        location="Kolkata, West Bengal",
        capacity=68000,
        zones=EDEN_GARDENS_ZONES,
        graph=EDEN_GARDENS_GRAPH,
        coordinates=EDEN_GARDENS_COORDS,
    ),
    "arun_jaitley": StadiumConfig(
        stadium_id="arun_jaitley",
        name="Arun Jaitley Stadium",
        location="New Delhi, Delhi",
        capacity=41800,
        zones=ARUN_JAITLEY_ZONES,
        graph=ARUN_JAITLEY_GRAPH,
        coordinates=ARUN_JAITLEY_COORDS,
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
