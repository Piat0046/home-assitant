"""FastAPI application setup."""

from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from home_ai.common.config import get_settings
from home_ai.server.api.rest import router as rest_router
from home_ai.server.api.websocket import handle_websocket


# Global instances
_llm = None
_stt = None
_tts = None


def get_llm():
    """Get or create LLM instance."""
    global _llm
    if _llm is None:
        settings = get_settings()
        if settings.llm_provider == "openai":
            from home_ai.server.llm.openai_llm import OpenAILLM
            _llm = OpenAILLM(api_key=settings.openai_api_key)
        else:
            from home_ai.server.llm.claude_llm import ClaudeLLM
            _llm = ClaudeLLM(api_key=settings.anthropic_api_key)
    return _llm


def get_stt():
    """Get or create STT instance."""
    global _stt
    if _stt is None:
        settings = get_settings()
        if settings.stt_provider == "openai":
            from home_ai.common.stt.openai_stt import OpenAISTT
            _stt = OpenAISTT(api_key=settings.openai_api_key)
        else:
            from home_ai.common.stt.google_stt import GoogleSTT
            _stt = GoogleSTT()
    return _stt


def get_tts():
    """Get or create TTS instance."""
    global _tts
    if _tts is None:
        settings = get_settings()
        if settings.tts_provider == "openai":
            from home_ai.common.tts.openai_tts import OpenAITTS
            _tts = OpenAITTS(api_key=settings.openai_api_key)
        else:
            from home_ai.common.tts.gtts_impl import GTTSImpl
            _tts = GTTSImpl()
    return _tts


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title="Home AI Assistant",
        description="Voice-controlled Home IoT Assistant API",
        version="0.1.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request ID middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    
    # Health check endpoint
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "home-ai-server"}
    
    # Include REST router
    app.include_router(rest_router)
    
    # WebSocket endpoint
    from fastapi import WebSocket
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await handle_websocket(websocket)
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "home_ai.server.app:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True
    )

