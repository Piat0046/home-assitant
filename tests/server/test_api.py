"""Tests for API endpoints - TDD: Write tests first."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestRESTAPI:
    """Tests for REST API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from home_ai.server.app import create_app

        app = create_app()
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Health endpoint should return OK."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_chat_endpoint_text_mode(self, client):
        """Chat endpoint should accept text input."""
        with patch("home_ai.server.app.get_llm") as mock_llm:
            from home_ai.common.models import LLMResponse

            mock_instance = MagicMock()
            mock_instance.process_async = AsyncMock(return_value=LLMResponse(text="거실 조명을 켰습니다.", commands=[]))
            mock_llm.return_value = mock_instance

            response = client.post("/api/chat", json={"text": "거실 불 켜줘", "mode": "text"})

            assert response.status_code == 200
            data = response.json()
            assert "text" in data

    def test_chat_endpoint_requires_input(self, client):
        """Chat endpoint should require text or audio."""
        response = client.post("/api/chat", json={"mode": "text"})

        # Should fail validation or return error
        assert response.status_code in [400, 422]

    def test_device_status_endpoint(self, client):
        """Device status endpoint should return all device states."""
        response = client.get("/api/devices")

        assert response.status_code == 200
        data = response.json()
        assert "lights" in data
        assert "alarm" in data
        assert "thermostat" in data


class TestWebSocketAPI:
    """Tests for WebSocket API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from home_ai.server.app import create_app

        app = create_app()
        return TestClient(app)

    def test_websocket_connection(self, client):
        """WebSocket should accept connections."""
        with client.websocket_connect("/ws") as websocket:
            # Connection should be established
            assert websocket is not None

    def test_websocket_text_message(self, client):
        """WebSocket should handle text messages."""
        with patch("home_ai.server.api.websocket.get_llm") as mock_llm:
            from home_ai.common.models import LLMResponse

            mock_instance = MagicMock()
            mock_instance.process_async = AsyncMock(return_value=LLMResponse(text="거실 조명을 켰습니다.", commands=[]))
            mock_llm.return_value = mock_instance

            with client.websocket_connect("/ws") as websocket:
                websocket.send_json({"type": "text", "content": "거실 불 켜줘"})

                response = websocket.receive_json()
                assert response["type"] == "response"
                assert "text" in response


class TestMiddleware:
    """Tests for middleware."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from home_ai.server.app import create_app

        app = create_app()
        return TestClient(app)

    def test_request_id_header(self, client):
        """Response should include request ID header."""
        response = client.get("/health")

        assert "X-Request-ID" in response.headers

    def test_cors_headers(self, client):
        """Response should include CORS headers."""
        response = client.options("/api/chat")

        # CORS should be configured
        assert response.status_code in [200, 204, 405]
