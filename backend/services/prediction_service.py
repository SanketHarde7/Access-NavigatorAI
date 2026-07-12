"""
Access Navigator AI - Predictive Analytics Service
==================================================
Uses LLM + historical data to predict crowd patterns
and provide proactive accessibility recommendations.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from services.llm_service import llm_service
from core.database import db


class PredictionService:
    """AI-powered crowd prediction and analytics."""

    @staticmethod
    async def predict_crowd(stadium_id: str, horizon_minutes: int = 30) -> Dict[str, Any]:
        """Predict future crowd density using LLM + historical patterns."""
        zones = db.get_zones(stadium_id)
        history = db.get_history(stadium_id, minutes=60)

        # Build context for LLM
        current_state = []
        for z in zones:
            current_state.append({
                "zone_id": z.zone_id,
                "type": z.zone_type,
                "current_density": z.crowd_density_pct,
                "trend": z.density_trend,
                "status": z.status,
                "capacity": z.capacity,
            })

        historical_summary = []
        if history:
            recent = history[-10:]  # Last 10 snapshots
            for snap in recent:
                ts = snap["timestamp"]
                zone_avgs = {}
                for z in snap["zones"]:
                    zid = z["zone_id"]
                    if zid not in zone_avgs:
                        zone_avgs[zid] = []
                    zone_avgs[zid].append(z["crowd_density_pct"])

        system_prompt = """You are an expert crowd management AI for stadium operations.
Predict crowd density for each zone based on current state and trends.
Respond ONLY in JSON format with this exact structure:
{
  "predictions": [
    {
      "zone_id": "string",
      "predicted_density": 0-100,
      "confidence": 0.0-1.0,
      "trend_direction": "rising|falling|stable",
      "risk_level": "low|medium|high|critical",
      "recommended_action": "string"
    }
  ],
  "overall_risk": "low|medium|high|critical",
  "summary": "string - 2-3 sentence summary"
}

Consider:
- Current density and trend
- Zone type (destinations get more crowded)
- Time patterns (halftime, pre-game, post-game)
- Accessibility impact (high density = harder for wheelchair users)
- If density >85%, risk is high. If >95%, critical.
Never invent zone IDs not in the input."""

        user_prompt = json.dumps({
            "stadium_id": stadium_id,
            "prediction_horizon_minutes": horizon_minutes,
            "current_time": datetime.utcnow().isoformat(),
            "current_zone_states": current_state,
        }, indent=2)

        result = await llm_service.generate(system_prompt, user_prompt, json_mode=True)

        if result["success"]:
            data = result["data"]
            data["stadium_id"] = stadium_id
            data["generated_at"] = datetime.utcnow().isoformat()
            data["prediction_horizon_min"] = horizon_minutes
            data["ai_provider"] = result.get("provider", "unknown")
            return data
        else:
            # Fallback to simple linear prediction
            predictions = []
            for z in zones:
                if z.density_trend == "rising":
                    predicted = min(100, z.crowd_density_pct + horizon_minutes // 5)
                elif z.density_trend == "falling":
                    predicted = max(0, z.crowd_density_pct - horizon_minutes // 5)
                else:
                    predicted = z.crowd_density_pct

                risk = "low"
                if predicted > 95:
                    risk = "critical"
                elif predicted > 85:
                    risk = "high"
                elif predicted > 70:
                    risk = "medium"

                predictions.append({
                    "zone_id": z.zone_id,
                    "predicted_density": predicted,
                    "confidence": 0.6,
                    "trend_direction": z.density_trend,
                    "risk_level": risk,
                    "recommended_action": "Monitor closely" if risk in ["high", "critical"] else "Normal operations",
                })

            return {
                "predictions": predictions,
                "overall_risk": "medium",
                "summary": f"Fallback prediction for {stadium_id}. Some zones may experience increased density.",
                "stadium_id": stadium_id,
                "generated_at": datetime.utcnow().isoformat(),
                "prediction_horizon_min": horizon_minutes,
                "ai_provider": "fallback_heuristic",
            }

    @staticmethod
    async def generate_analytics(stadium_id: str) -> Dict[str, Any]:
        """Generate comprehensive stadium analytics with AI insights."""
        zones = db.get_zones(stadium_id)
        history = db.get_history(stadium_id, minutes=120)

        total_density = sum(z.crowd_density_pct for z in zones)
        avg_density = total_density / len(zones) if zones else 0
        total_estimated = sum(int(z.capacity * z.crowd_density_pct / 100) for z in zones)

        most_congested = sorted(zones, key=lambda z: z.crowd_density_pct, reverse=True)[:5]

        # Calculate accessibility compliance
        accessible_zones = [z for z in zones if z.accessibility_score >= 0.8]
        compliance_score = len(accessible_zones) / len(zones) * 100 if zones else 0

        # Zone-level analytics
        zone_analytics = []
        for z in zones:
            zone_history = []
            for snap in history:
                for sz in snap["zones"]:
                    if sz["zone_id"] == z.zone_id:
                        zone_history.append(sz["crowd_density_pct"])

            avg_1h = sum(zone_history) / len(zone_history) if zone_history else z.crowd_density_pct
            peak_1h = max(zone_history) if zone_history else z.crowd_density_pct
            status_changes = sum(
                1 for i in range(1, len(zone_history))
                if zone_history[i] != zone_history[i-1]
            )
            congestion_pct = sum(1 for d in zone_history if d > 70) / len(zone_history) * 100 if zone_history else 0

            zone_analytics.append({
                "zone_id": z.zone_id,
                "avg_crowd_1h": round(avg_1h, 1),
                "peak_crowd_1h": peak_1h,
                "status_changes_1h": status_changes,
                "congestion_time_pct": round(congestion_pct, 1),
                "accessibility_score": z.accessibility_score,
            })

        # AI-powered insights
        system_prompt = """You are a stadium operations AI analyst.
Generate 3-5 actionable insights and 2-3 recommendations based on the data.
Respond ONLY in JSON:
{
  "insights": ["string"],
  "recommendations": ["string"]
}

Focus on:
- Accessibility concerns for fans with disabilities
- Crowd flow optimization
- Safety considerations
- Operational efficiency"""

        user_prompt = json.dumps({
            "stadium_id": stadium_id,
            "avg_density": avg_density,
            "total_fans": total_estimated,
            "most_congested": [z.zone_id for z in most_congested[:3]],
            "compliance_score": compliance_score,
            "zone_analytics_summary": zone_analytics[:5],
        })

        result = await llm_service.generate(system_prompt, user_prompt, json_mode=True)

        if result["success"]:
            ai_data = result["data"]
        else:
            ai_data = {
                "insights": [
                    f"Average stadium density is {avg_density:.1f}% - {'High' if avg_density > 70 else 'Normal'} load",
                    f"Top congested zones: {', '.join(z.zone_id for z in most_congested[:3])}",
                    f"Accessibility compliance: {compliance_score:.1f}%",
                ],
                "recommendations": [
                    "Monitor high-density zones for accessibility issues" if avg_density > 60 else "Continue normal operations",
                    "Deploy additional staff to congested areas" if any(z.crowd_density_pct > 80 for z in zones) else "Standard staffing sufficient",
                ],
            }

        return {
            "stadium_id": stadium_id,
            "generated_at": datetime.utcnow().isoformat(),
            "total_fans_estimated": total_estimated,
            "avg_stadium_density": round(avg_density, 1),
            "most_congested_zones": [z.zone_id for z in most_congested],
            "accessibility_compliance_score": round(compliance_score, 1),
            "zone_analytics": zone_analytics,
            "ai_insights": ai_data.get("insights", []),
            "recommendations": ai_data.get("recommendations", []),
            "ai_provider": result.get("provider", "fallback"),
        }


prediction_service = PredictionService()
