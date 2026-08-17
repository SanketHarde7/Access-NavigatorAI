"""
PostgreSQL / Supabase Database Seeding Script
=============================================
Initializes and populates all 5 Indian stadiums, zones, and graph edges
into PostgreSQL / Supabase.

Usage:
    python seed_db.py
"""
import asyncio
import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.pg_database import engine, init_db, AsyncSessionLocal
from backend.models.db_models import StadiumDB, ZoneDB, EdgeDB
from backend.core.database import STADIUMS
from sqlalchemy import select


async def seed_database():
    print("=" * 60)
    print("Access Navigator AI -- Seeding PostgreSQL Database")
    print("=" * 60)

    # 1. Create tables
    await init_db()
    print("[OK] Verified/created all database schema tables.")

    if AsyncSessionLocal is None:
        print("[ERROR] Database session maker not available.")
        return

    async with AsyncSessionLocal() as session:
        for sid, stadium_cfg in STADIUMS.items():
            # Check if stadium already exists
            res = await session.execute(select(StadiumDB).where(StadiumDB.id == sid))
            existing_stadium = res.scalar_one_or_none()

            city = stadium_cfg.location.split(",")[-1].strip() if "," in stadium_cfg.location else stadium_cfg.location
            if not existing_stadium:
                stadium_row = StadiumDB(
                    id=sid,
                    name=stadium_cfg.name,
                    location=stadium_cfg.location,
                    city=city,
                    country="India" if "India" in stadium_cfg.location or sid in ["narendra_modi", "wankhede", "chinnaswamy", "eden_gardens", "arun_jaitley"] else "International",
                    capacity=stadium_cfg.capacity,
                )
                session.add(stadium_row)
                print(f"  + Added Stadium: {stadium_cfg.name} ({stadium_cfg.capacity:,} capacity)")

            # Seed zones
            for zid, zdata in stadium_cfg.zones.items():
                res = await session.execute(
                    select(ZoneDB).where(ZoneDB.stadium_id == sid, ZoneDB.id == zid)
                )
                existing_zone = res.scalar_one_or_none()
                coord = stadium_cfg.coordinates.get(zid, {"x": 0.5, "y": 0.5})

                if not existing_zone:
                    zone_row = ZoneDB(
                        id=zid,
                        stadium_id=sid,
                        name=zid.replace("_", " ").title(),
                        zone_type=zdata.zone_type,
                        status=zdata.status,
                        crowd_density_pct=zdata.crowd_density_pct,
                        density_trend=zdata.density_trend,
                        accessibility_score=zdata.accessibility_score,
                        elevation_m=zdata.elevation_m,
                        capacity=zdata.capacity,
                        coord_x=coord.get("x", 0.5),
                        coord_y=coord.get("y", 0.5),
                    )
                    session.add(zone_row)

            # Seed graph edges
            for source_id, targets in stadium_cfg.graph.items():
                for target_id, weight in targets.items():
                    res = await session.execute(
                        select(EdgeDB).where(
                            EdgeDB.stadium_id == sid,
                            EdgeDB.source_zone_id == source_id,
                            EdgeDB.target_zone_id == target_id,
                        )
                    )
                    if not res.scalar_one_or_none():
                        edge_row = EdgeDB(
                            stadium_id=sid,
                            source_zone_id=source_id,
                            target_zone_id=target_id,
                            weight_minutes=weight,
                            distance_meters=weight * 30.0,
                            is_wheelchair_accessible=True,
                            has_elevator="elevator" in source_id or "elevator" in target_id,
                            has_ramp="ramp" in source_id or "ramp" in target_id,
                            step_count=15 if "stairs" in source_id or "stairs" in target_id else 0,
                        )
                        session.add(edge_row)

        await session.commit()
        print("[OK] All stadiums, zones, and graph edges successfully seeded!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_database())
