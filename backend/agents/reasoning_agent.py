"""
Access Navigator AI - Reasoning Agent
======================================
Multi-factor tradeoff analysis using Chain-of-Thought prompting.
Performs route optimization, caption classification, and intent detection.
"""
import json
from typing import List, Dict, Any, Optional
from services.llm_service import llm_service


class ReasoningAgent:
    """
    Reasoning Agent: Analyze → Evaluate → Decide
    
    Uses Chain-of-Thought (CoT) prompting for transparent,
    explainable AI decisions. Every recommendation includes
    full reasoning trace for auditability.
    """

    agent_name = "Reasoning"
    icon = "brain"
    color = "#8b5cf6"  # violet

    @staticmethod
    def _build_route_system_prompt() -> str:
        """Advanced CoT prompt for route reasoning."""
        return """You are AccessNavigator-Reasoner, an expert accessibility routing AI for stadium environments.

## YOUR TASK
Select the optimal accessible route for a fan with specific accessibility needs.

## CONSTRAINTS & RULES
1. WHEELCHAIR USERS:
   - NEVER route through stairs
   - NEVER route through elevators/ramp with status 'maintenance' or 'closed'
   - Prefer ramps and accessible_paths
   - Maximum acceptable detour: 2x the shortest path

2. HEARING IMPAIRED:
   - Prefer routes with visual displays and captioning
   - Avoid isolated areas

3. VISUAL IMPAIRED:
   - Prefer routes with tactile guidance
   - Avoid construction zones

4. GENERAL:
   - Prefer lower crowd density (<70%)
   - Avoid zones with 'rising' trend if >60%
   - Factor in accessibility_score of each zone

## CHAIN-OF-THOUGHT PROCESS
Think step by step:
1. Filter: Which paths are INVALID for this accessibility need?
2. Score: Rate each valid path on accessibility (0-100)
3. Compare: Weigh accessibility vs time vs crowd
4. Select: Choose the best path
5. Explain: Write clear reasoning

## OUTPUT FORMAT
Respond ONLY in JSON:
{
  "recommended_path": ["zone_id1", "zone_id2", ...],
  "eta_minutes": 0,
  "reasoning": "2-3 sentences explaining the decision in plain language",
  "alternative_considered": "What other path was considered and why it was rejected",
  "confidence": "high|medium|low",
  "accessibility_score": 0.0-1.0,
  "crowd_alerts": ["any crowd warnings along the route"]
}

## FEW-SHOT EXAMPLE
Input: Wheelchair user, paths include one with broken elevator
Thought: The direct path uses elevator_b which is under maintenance. 
The alternate path uses ramp_south which is accessible but 3 min longer.
The ramp path has lower crowd density (40% vs 85%).
Decision: Choose ramp path for safety and accessibility.
Output: {"recommended_path": ["gate_a", "ramp_south", "section_101"], "eta_minutes": 8, "reasoning": "...", "confidence": "high", "accessibility_score": 0.95}

Never invent zone IDs. Use ONLY zones provided in the input."""

    @staticmethod
    async def calculate_route(
        accessibility_need: str,
        situational_summary: str,
        candidate_paths: List[Dict[str, Any]],
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate optimal accessible route using CoT reasoning.
        
        Args:
            accessibility_need: Type of accessibility required
            situational_summary: Current zone status summary
            candidate_paths: Possible paths from graph search
            provider: Preferred LLM provider
            
        Returns:
            RouteResponse with full reasoning trace
        """
        system_prompt = ReasoningAgent._build_route_system_prompt()

        user_prompt = json.dumps({
            "accessibility_need": accessibility_need,
            "situational_summary": situational_summary,
            "candidate_paths": candidate_paths,
            "timestamp": datetime.utcnow().isoformat(),
        }, indent=2)

        # Call LLM with CoT
        result = await llm_service.generate(system_prompt, user_prompt, json_mode=True, provider=provider)

        if result["success"]:
            data = result["data"]
            data["agent_trace"] = {
                "perception_summary": situational_summary[:500],
                "reasoning_note": f"Evaluated {len(candidate_paths)} paths using {result.get('provider', 'AI')}",
                "llm_provider": result.get("provider", "unknown"),
                "fallback_used": result.get("fallback_used", False),
            }
            data["generated_at"] = datetime.utcnow().isoformat()
            return data
        else:
            # Fallback: select path with fewest obstacles
            return ReasoningAgent._fallback_route(accessibility_need, candidate_paths, result.get("error", "Unknown"))

    @staticmethod
    def _fallback_route(need: str, paths: List[Dict], error: str) -> Dict[str, Any]:
        """Heuristic fallback when LLM fails."""
        if not paths:
            return {
                "recommended_path": [],
                "eta_minutes": 0,
                "reasoning": f"No valid routes found. Error: {error}",
                "alternative_considered": "None",
                "confidence": "low",
                "accessibility_score": 0,
                "crowd_alerts": [],
            }

        # Simple heuristic: pick shortest path
        best = min(paths, key=lambda p: p.get("distance_min", 999))
        return {
            "recommended_path": best.get("path", []),
            "eta_minutes": best.get("distance_min", 0),
            "reasoning": f"Fallback selection (AI service unavailable: {error}). Selected shortest available path.",
            "alternative_considered": f"Evaluated {len(paths)} paths",
            "confidence": "low",
            "accessibility_score": 0.5,
            "crowd_alerts": ["Using fallback routing - verify accessibility"],
        }

    @staticmethod
    async def classify_caption(raw_text: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify announcement urgency and generate accessible caption.
        
        Args:
            raw_text: Raw PA announcement text
            provider: Preferred LLM provider
            
        Returns:
            CaptionOutput with urgency classification
        """
        system_prompt = """You are AccessNavigator-Captioner, an AI assistant for Deaf and hard-of-hearing stadium fans.

## YOUR TASK
Convert stadium PA announcements into clear, concise visual captions.

## URGENCY CLASSIFICATION
- CRITICAL: Immediate safety action required (evacuation, medical emergency, severe weather, active threat)
  → style: "highlighted_red_banner", include warning emoji
- IMPORTANT: Time-sensitive but not safety-critical (gate changes, delays, halftime)
  → style: "highlighted", clear and prominent
- NORMAL: General information (entertainment, promotions, welcome messages)
  → style: "standard"

## RULES
1. NEVER downgrade urgency - safety first
2. Preserve ALL safety-relevant facts exactly
3. Remove filler words, keep essential info
4. Maximum 15 words for display text
5. Include translations hint if relevant

## OUTPUT FORMAT
{
  "display_text": "under 15 words, clear and actionable",
  "urgency": "normal|important|critical",
  "style": "standard|highlighted|highlighted_red_banner",
  "confidence": 0.0-1.0,
  "key_facts": ["list of critical facts extracted"]
}

## EXAMPLES
Input: "Attention all fans, halftime entertainment will begin in five minutes at the north stand."
Output: {"display_text": "Halftime show starts in 5 min at North Stand", "urgency": "normal", "style": "standard", "confidence": 0.95, "key_facts": ["Halftime entertainment", "5 minutes", "North stand"]}

Input: "Due to severe weather approaching, all fans in the upper tier must move to covered seating immediately."
Output: {"display_text": "SEVERE WEATHER: Move to covered seating NOW", "urgency": "critical", "style": "highlighted_red_banner", "confidence": 0.98, "key_facts": ["Severe weather", "Upper tier evacuation", "Covered seating required"]}

Never invent information not in the source text."""

        user_prompt = json.dumps({"raw_text": raw_text, "timestamp": datetime.utcnow().isoformat()})

        result = await llm_service.generate(system_prompt, user_prompt, json_mode=True, provider=provider)

        if result["success"]:
            data = result["data"]
            data["original_text"] = raw_text
            data["ai_provider"] = result.get("provider", "unknown")
            return data
        else:
            return {
                "display_text": "[Announcement unclear - please check nearest steward]",
                "urgency": "normal",
                "style": "standard",
                "confidence": 0.0,
                "original_text": raw_text,
                "error": result.get("error", "Unknown"),
            }

    @staticmethod
    async def detect_intent(message: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """Detect user intent from natural language message."""
        system_prompt = """You are an intent classification AI for a stadium navigation assistant.
Classify the user's message into one or more intents.

Possible intents:
- "route_request": User wants directions
- "status_check": User wants to know about zone/area status
- "accessibility_info": User needs accessibility information
- "emergency": User reports or needs emergency help
- "general_chat": Casual conversation or greeting
- "announcement": User wants to make/report an announcement

OUTPUT JSON:
{
  "primary_intent": "intent_name",
  "confidence": 0.0-1.0,
  "entities": {"location": "...", "accessibility_need": "...", "destination": "..."},
  "response_strategy": "route|status|help|chat|emergency"
}"""

        user_prompt = json.dumps({"message": message})
        result = await llm_service.generate(system_prompt, user_prompt, json_mode=True, provider=provider)

        if result["success"]:
            return result["data"]
        return {"primary_intent": "general_chat", "confidence": 0.5, "entities": {}, "response_strategy": "chat"}


from datetime import datetime
