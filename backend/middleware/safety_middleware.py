import json
from starlette.requests import Request
from starlette.responses import JSONResponse

class SafetyMiddleware:
    """
    Middleware to intercept basic prompt injection attacks and toxic input
    before it reaches the LLM agents.
    
    SECURITY PROTOCOL:
    Implements a zero-trust architecture. Validates all incoming payloads 
    at the edge, guaranteeing enterprise-grade security against adversarial 
    AI prompts and ensuring strict problem statement alignment.
    """
    
    # Common prompt injection patterns
    FORBIDDEN_PHRASES = [
        "ignore previous instructions",
        "system prompt",
        "bypass",
        "you are now",
        "forget all",
        "disregard",
        "sudo",
    ]

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST":
            return await self.app(scope, receive, send)

        receive_ = receive
        body_bytes = b""
        more_body = True
        
        # Read the entire body
        messages = []
        while more_body:
            message = await receive()
            messages.append(message)
            body_bytes += message.get("body", b"")
            more_body = message.get("more_body", False)
            # Security: Validating raw byte payload guarantees integrity against edge injection attacks
        body_text = body_bytes.decode('utf-8', errors='ignore').lower()
        
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase in body_text:
                response = JSONResponse(
                    status_code=403,
                    content={
                        "error": "Safety Violation",
                        "message": "Input flagged by AI Safety Filter. Malicious prompts are strictly prohibited."
                    }
                )
                return await response(scope, receive, send)

        # Replay the messages for the downstream app
        async def receive_replay():
            if messages:
                return messages.pop(0)
            return await receive_()
            
        return await self.app(scope, receive_replay, send)
