import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app

# Test configuration
TEST_USER_DATA = {
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123"
}

TEST_AGENT_DATA = {
    "name": "Test Agent",
    "description": "A test agent for automated testing",
    "prompt": "You are a helpful test assistant.",
    "provider_config": {
        "tts_provider": "openai",
        "stt_provider": "openai", 
        "llm_provider": "openai",
        "tts_config": {"voice": "alloy"},
        "stt_config": {"model": "whisper-1"},
        "llm_config": {"model": "gpt-3.5-turbo"}
    },
    "features": {
        "voice_chat": True,
        "text_chat": True,
        "file_upload": False,
        "web_search": True,
        "memory": True,
        "custom_functions": ["search", "calculate"]
    }
}


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client fixture"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoints:
    """Test health and basic endpoints"""
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestUserEndpoints:
    """Test user-related endpoints"""
    
    def test_user_registration(self, client):
        response = client.post("/api/v1/auth/register", json=TEST_USER_DATA)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == TEST_USER_DATA["email"]
        assert data["username"] == TEST_USER_DATA["username"]
        assert "id" in data
    
    def test_user_login(self, client):
        # First register a user
        client.post("/api/v1/auth/register", json=TEST_USER_DATA)
        
        # Then try to login
        login_data = {
            "username": TEST_USER_DATA["username"],
            "password": TEST_USER_DATA["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


class TestAgentEndpoints:
    """Test agent-related endpoints"""
    
    def test_create_agent_requires_auth(self, client):
        response = client.post("/api/v1/agents/", json=TEST_AGENT_DATA)
        assert response.status_code == 401
    
    def test_get_agents_requires_auth(self, client):
        response = client.get("/api/v1/agents/")
        assert response.status_code == 401


# Run tests with: pytest tests/ -v