"""
Access Navigator AI - Communication Agent
==========================================
Formats AI output for human consumption with accessibility-first design.
Handles multi-channel output (visual, haptic, audio cues).
"""
from typing import Dict, Any, Optional


class CommunicationAgent:
    """
    Communication Agent: Format → Adapt → Deliver
    
    Ensures all AI output is accessible, clear, and actionable.
    Handles formatting for different accessibility needs.
    """

    agent_name = "Communication"
    icon = "message-square"
    color = "#3b82f6"  # blue

    @staticmethod
    def format_route_response(route_data: Dict[str, Any], accessibility_need: str = "wheelchair") -> Dict[str, Any]:
        """Format route for the user's specific accessibility needs."""
        formatted = dict(route_data)

        # Add haptic feedback triggers for critical alerts
        crowd_alerts = formatted.get("crowd_alerts", [])
        if crowd_alerts:
            formatted["haptic_pattern"] = "long_pulse"

        # Format for hearing impaired
        if accessibility_need == "hearing_impaired":
            formatted["visual_cues"] = {
                "route_highlight": True,
                "turn_indicators": True,
                "distance_markers": True,
            }

        # Format for visual impaired
        if accessibility_need == "visual_impaired":
            formatted["audio_description"] = CommunicationAgent._route_to_audio(formatted)

        return formatted

    @staticmethod
    def format_caption_output(caption_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure caption styles match urgency with safety overrides."""
        formatted = dict(caption_data)

        # Safety override: never downgrade critical
        urgency = formatted.get("urgency", "normal")
        if urgency == "critical":
            formatted["style"] = "highlighted_red_banner"
            formatted["haptic"] = True
            formatted["priority"] = "maximum"
        elif urgency == "important":
            formatted["style"] = "highlighted"
            formatted["priority"] = "high"
        else:
            formatted["style"] = "standard"
            formatted["priority"] = "normal"

        return formatted

    @staticmethod
    def format_chat_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format conversational AI response with metadata."""
        formatted = dict(response_data)

        # Add timestamp
        from datetime import datetime
        formatted["timestamp"] = datetime.utcnow().isoformat()

        # Add suggested actions if available
        if "actions" not in formatted:
            formatted["actions"] = []

        return formatted

    @staticmethod
    def _route_to_audio(route: Dict[str, Any]) -> str:
        """Convert route to audio description for visually impaired users."""
        path = route.get("recommended_path", [])
        if not path:
            return "No route available. Please contact a steward."

        segments = []
        for i, zone in enumerate(path):
            zone_name = zone.replace("_", " ")
            if i == 0:
                segments.append(f"Start at {zone_name}.")
            elif i == len(path) - 1:
                segments.append(f"Arrive at {zone_name}.")
            else:
                segments.append(f"Continue to {zone_name}.")

        segments.append(f"Estimated time: {route.get('eta_minutes', 0)} minutes.")
        return " ".join(segments)

    @staticmethod
    def build_agent_message(agent_name: str, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Build a structured agent message for the frontend."""
        return {
            "role": "agent",
            "agent_name": agent_name,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
