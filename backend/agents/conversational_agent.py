"""
Access Navigator AI - Conversational Agent
============================================
Multi-agent conversational AI that orchestrates all agents
to provide natural language stadium assistance.
Uses ReAct (Reasoning + Acting) pattern for tool use.
"""
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from services.llm_service import llm_service
from core.database import db
from agents.perception_agent import PerceptionAgent
from agents.reasoning_agent import ReasoningAgent
from agents.communication_agent import CommunicationAgent


class ConversationalAgent:
    """
    Conversational Agent: Understand → Plan → Execute → Respond
    
    Uses ReAct pattern to:
    1. Understand user intent
    2. Plan which tools/agents to use
    3. Execute the plan
    4. Respond naturally with results
    
    This is the MAIN INTERFACE for natural language interaction.
    """

    agent_name = "Navigator"
    icon = "bot"
    color = "#f59e0b"  # amber

    @staticmethod
    def _build_system_prompt(stadium_id: str, accessibility_need: str) -> str:
        """Build dynamic system prompt with current stadium context."""
        stadium = db.get_stadium(stadium_id)
        stadium_name = stadium.name if stadium else "Unknown Stadium"
        zones_count = len(stadium.zones) if stadium else 0

        return f"""You are AccessNavigator (also known as Navi), the official smart, dynamic AI assistant for stadium accessibility navigation designed specifically for the PromptWars Virtual Competition.

## CURRENT CONTEXT
- Stadium: {stadium_name} (ID: {stadium_id})
- Monitored zones: {zones_count}
- User accessibility need: {accessibility_need}
- Time: {datetime.utcnow().strftime('%H:%M UTC')}

## YOUR CAPABILITIES
You have access to these tools/functions:
1. **get_route** - Find accessible routes between locations
2. **check_zone_status** - Get current status of any zone
3. **get_crowd_info** - Check crowd density and predictions
4. **explain_accessibility** - Explain accessibility features
5. **emergency_help** - Provide emergency assistance info

## STRICT DOMAIN RESTRICTIONS (CRITICAL)
You are an AI assistant dedicated EXCLUSIVELY to stadium navigation and accessibility.
- You MUST ABSOLUTELY REFUSE to answer any questions unrelated to stadiums, accessibility, routes, or facilities.
- If the user asks you to write code, do math, write essays, do general research, translate text, or anything outside of this specific domain, you MUST reply ONLY with: "I am an AI assistant dedicated exclusively to stadium navigation and accessibility. I cannot answer questions about coding, programming, or other unrelated topics."
- NEVER break character. NEVER provide general AI knowledge.

## RESPONSE STYLE
- Be friendly, helpful, and professional
- Use clear, simple language
- Always consider the user's accessibility needs
- Prioritize safety in all recommendations
- If you don't know something, say so and suggest alternatives

## WHEN USER ASKS FOR A ROUTE
Ask for:
- Current location
- Destination
- Confirm accessibility need

## SAFETY RULES
- If user reports emergency, immediately provide help info
- Never suggest unsafe routes for wheelchair users
- Always warn about high crowd density
- Include "contact nearest steward" for critical situations

Respond naturally. Use markdown for formatting. Be concise but thorough."""

    @staticmethod
    async def chat(
        message: str,
        user_id: str,
        stadium_id: str = "metlife",
        accessibility_need: str = "wheelchair",
        conversation_history: Optional[List[Dict]] = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a conversational message and return AI response.
        
        Uses ReAct pattern:
        1. Detect intent
        2. Gather context (zone data, etc.)
        3. Generate response with tool results
        """
        conversation_history = conversation_history or []

        # Step 1: Detect intent
        intent_result = await ReasoningAgent.detect_intent(message, provider=provider)
        primary_intent = intent_result.get("primary_intent", "general_chat")

        # Step 2: Gather context based on intent
        context = {}
        actions = []

        if primary_intent == "route_request":
            # Extract locations from message
            zones = db.get_zones(stadium_id)
            zone_names = [z.zone_id for z in zones]

            # Simple entity extraction - check if message contains zone names
            mentioned_zones = [z for z in zone_names if z.replace("_", " ").lower() in message.lower()]

            if len(mentioned_zones) >= 2:
                # User mentioned start and end
                context["mentioned_zones"] = mentioned_zones
                actions.append({
                    "type": "route_suggestion",
                    "start": mentioned_zones[0],
                    "end": mentioned_zones[-1],
                })

        elif primary_intent == "status_check":
            zones = db.get_zones(stadium_id)
            summary = PerceptionAgent.summarize_zones(zones)
            context["zone_summary"] = summary[:1000]

        elif primary_intent == "emergency":
            context["emergency"] = True
            actions.append({"type": "emergency_assist"})

        # Step 3: Generate response with context
        system_prompt = ConversationalAgent._build_system_prompt(stadium_id, accessibility_need)

        # Build conversation context
        history_text = ""
        for msg in conversation_history[-6:]:  # Last 6 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"

        user_prompt = json.dumps({
            "user_message": message,
            "detected_intent": primary_intent,
            "intent_confidence": intent_result.get("confidence", 0),
            "context": context,
            "conversation_history": history_text,
        }, indent=2)

        result = await llm_service.generate(system_prompt, user_prompt, json_mode=False, provider=provider)

        if result["success"]:
            response_text = result["data"] if isinstance(result["data"], str) else json.dumps(result["data"])
        else:
            # Graceful fallback
            response_text = ConversationalAgent._fallback_response(primary_intent, message)

        return CommunicationAgent.format_chat_response({
            "response": response_text,
            "agent_used": "ConversationalAgent",
            "detected_intent": primary_intent,
            "actions": actions,
            "confidence": intent_result.get("confidence", 0.5),
            "ai_provider": result.get("provider", "fallback"),
        })

    @staticmethod
    async def chat_stream(
        message: str,
        user_id: str,
        stadium_id: str = "metlife",
        accessibility_need: str = "wheelchair",
        conversation_history: Optional[List[Dict]] = None,
        provider: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream response tokens for real-time chat feel.
        """
        conversation_history = conversation_history or []

        # Detect intent first (non-streaming)
        intent_result = await ReasoningAgent.detect_intent(message, provider=provider)

        system_prompt = ConversationalAgent._build_system_prompt(stadium_id, accessibility_need)

        history_text = ""
        for msg in conversation_history[-6:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"

        user_prompt = json.dumps({
            "user_message": message,
            "detected_intent": intent_result.get("primary_intent", "general_chat"),
            "conversation_history": history_text,
        })

        # Stream tokens
        async for token in llm_service.generate_stream(system_prompt, user_prompt, provider=provider):
            yield token

    @staticmethod
    def _fallback_response(intent: str, message: str) -> str:
        """Graceful fallback when AI is unavailable."""
        fallbacks = {
            "route_request": "I'd be happy to help you find a route! Please use the route form on the left to select your current location and destination.",
            "status_check": "I can check zone status for you. Please look at the Live Stadium Map for current conditions, or ask me about a specific area.",
            "emergency": "If this is an emergency, please contact the nearest steward immediately or call stadium security. Your safety is our priority.",
            "accessibility_info": "Our stadium offers wheelchair ramps, elevators, and accessible seating. Check the map for accessible routes marked in green.",
        }
        return fallbacks.get(intent, f"I'm here to help! You asked: '{message}'. How can I assist you with navigating the stadium today?")
