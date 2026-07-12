"""
Access Navigator AI - Perception Agent
=======================================
Normalizes raw sensor data into structured situational summaries.
Uses deterministic + LLM-based summarization for maximum reliability.
"""
import json
from typing import List, Dict, Any
from datetime import datetime
from core.database import db, ZoneData


class PerceptionAgent:
    """
    Perception Agent: Senses → Normalizes → Summarizes
    
    Converts raw zone status data into plain-language situational summaries
    that the Reasoning Agent can use for route calculations.
    """

    agent_name = "Perception"
    icon = "eye"
    color = "#10b981"  # emerald

    @staticmethod
    def summarize_zones(zones: List[ZoneData]) -> str:
        """
        Create a structured situational summary from zone data.
        Uses deterministic formatting for reliability.
        """
        summary_lines = []
        critical_issues = []
        warnings = []

        for z in zones:
            status_text = f"status is {z.status}"
            if z.crowd_density_pct is not None:
                status_text += f" with {z.crowd_density_pct}% crowd density"
            if z.density_trend:
                status_text += f", trend: {z.density_trend}"
            if z.accessibility_score is not None:
                status_text += f", accessibility: {z.accessibility_score:.0%}"

            summary_lines.append(f"- Zone '{z.zone_id}' (type: {z.zone_type}): {status_text}.")

            # Flag issues
            if z.status in ("maintenance", "closed"):
                critical_issues.append(f"{z.zone_id} is {z.status}")
            elif z.status == "congested":
                warnings.append(f"{z.zone_id} is congested ({z.crowd_density_pct}%)")
            elif z.crowd_density_pct and z.crowd_density_pct > 80:
                warnings.append(f"{z.zone_id} is nearing capacity ({z.crowd_density_pct}%)")

        header = "=== SITUATIONAL AWARENESS REPORT ===\n"
        header += f"Generated: {datetime.utcnow().strftime('%H:%M:%S UTC')}\n"
        header += f"Total zones monitored: {len(zones)}\n"

        if critical_issues:
            header += f"\nCRITICAL ({len(critical_issues)}): {', '.join(critical_issues)}\n"
        if warnings:
            header += f"WARNINGS ({len(warnings)}): {', '.join(warnings[:5])}{'...' if len(warnings) > 5 else ''}\n"

        header += "\n--- Zone Details ---\n"

        return header + "\n".join(summary_lines)

    @staticmethod
    def get_accessibility_summary(zones: List[ZoneData], need: str) -> str:
        """Generate accessibility-specific summary for the user's need."""
        relevant = []
        for z in zones:
            if need == "wheelchair" and z.zone_type in ("ramp", "elevator", "accessible_path"):
                relevant.append(z)
            elif need == "hearing_impaired" and z.zone_type in ("destination", "corridor"):
                relevant.append(z)
            elif need == "both":
                relevant.append(z)

        lines = [f"=== ACCESSIBILITY ASSESSMENT FOR: {need.upper()} ==="]
        for z in relevant:
            lines.append(f"- {z.zone_id}: {z.status}, density: {z.crowd_density_pct}%, accessible: {'YES' if z.accessibility_score > 0.7 else 'CAUTION'}")

        blocked = [z.zone_id for z in relevant if z.status in ("maintenance", "closed")]
        if blocked:
            lines.append(f"\nBLOCKED PATHS: {', '.join(blocked)}")

        return "\n".join(lines)

    @staticmethod
    def detect_anomalies(zones: List[ZoneData]) -> List[Dict[str, Any]]:
        """Detect anomalous patterns in zone data."""
        anomalies = []
        avg_density = sum(z.crowd_density_pct for z in zones) / len(zones) if zones else 0

        for z in zones:
            # Density anomaly
            if z.crowd_density_pct > avg_density * 1.5 and z.crowd_density_pct > 70:
                anomalies.append({
                    "type": "density_spike",
                    "zone_id": z.zone_id,
                    "severity": "high" if z.crowd_density_pct > 90 else "medium",
                    "details": f"{z.zone_id} at {z.crowd_density_pct}% (avg: {avg_density:.0f}%)",
                })

            # Status anomaly
            if z.status in ("maintenance", "closed") and z.zone_type in ("elevator", "ramp"):
                anomalies.append({
                    "type": "accessibility_blocked",
                    "zone_id": z.zone_id,
                    "severity": "critical",
                    "details": f"{z.zone_type} {z.zone_id} is {z.status} - impacts wheelchair users",
                })

        return anomalies
