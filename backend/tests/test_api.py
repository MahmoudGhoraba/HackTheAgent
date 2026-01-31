"""
API endpoint tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and utility endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "vector_db" in data or "error" in data


class TestEmailEndpoints:
    """Test email loading and normalization"""
    
    def test_load_emails(self):
        """Test loading emails"""
        response = client.get("/tool/emails/load")
        assert response.status_code == 200
        data = response.json()
        assert "emails" in data
        assert len(data["emails"]) > 0
    
    def test_normalize_emails(self):
        """Test email normalization"""
        # First load emails
        load_response = client.get("/tool/emails/load")
        emails = load_response.json()["emails"]
        
        # Then normalize
        response = client.post("/tool/emails/normalize", json={"emails": emails})
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) == len(emails)


class TestSemanticEndpoints:
    """Test semantic search endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Load and index emails"""
        # Load emails
        load_response = client.get("/tool/emails/load")
        emails = load_response.json()["emails"]
        
        # Normalize
        normalize_response = client.post("/tool/emails/normalize", json={"emails": emails})
        messages = normalize_response.json()["messages"]
        
        # Index
        client.post("/tool/semantic/index", json={"messages": messages})
    
    def test_semantic_search(self):
        """Test semantic search"""
        response = client.post(
            "/tool/semantic/search",
            json={"query": "urgent deadline", "top_k": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_semantic_search_invalid_top_k(self):
        """Test semantic search with invalid top_k"""
        response = client.post(
            "/tool/semantic/search",
            json={"query": "test", "top_k": 100}
        )
        assert response.status_code == 422  # Validation error


class TestRAGEndpoints:
    """Test RAG endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Load and index emails"""
        # Load emails
        load_response = client.get("/tool/emails/load")
        emails = load_response.json()["emails"]
        
        # Normalize
        normalize_response = client.post("/tool/emails/normalize", json={"emails": emails})
        messages = normalize_response.json()["messages"]
        
        # Index
        client.post("/tool/semantic/index", json={"messages": messages})
    
    def test_rag_answer(self):
        """Test RAG answer generation"""
        response = client.post(
            "/tool/rag/answer",
            json={"question": "What is the IBM hackathon about?", "top_k": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "citations" in data
        assert isinstance(data["citations"], list)


class TestClassificationEndpoints:
    """Test classification endpoints"""
    
    def test_classify_emails(self):
        """Test email classification"""
        # Load emails
        load_response = client.get("/tool/emails/load")
        emails = load_response.json()["emails"]
        
        # Classify
        response = client.post("/tool/emails/classify", json={"emails": emails})
        assert response.status_code == 200
        data = response.json()
        assert "classifications" in data
        assert len(data["classifications"]) == len(emails)
        
        # Check classification structure
        if data["classifications"]:
            classification = data["classifications"][0]
            assert "categories" in classification
            assert "priority" in classification
            assert "sentiment" in classification
    
    def test_detect_threads(self):
        """Test thread detection"""
        # Load emails
        load_response = client.get("/tool/emails/load")
        emails = load_response.json()["emails"]
        
        # Detect threads
        response = client.post("/tool/emails/threads", json={"emails": emails})
        assert response.status_code == 200
        data = response.json()
        assert "threads" in data
        assert "total_threads" in data


class TestAnalyticsEndpoints:
    """Test analytics endpoints"""
    
    def test_email_analytics(self):
        """Test email analytics"""
        response = client.get("/analytics/emails")
        assert response.status_code == 200
        data = response.json()
        assert "overview" in data
        assert "senders" in data
        assert "categories" in data
        assert "timeline" in data
    
    def test_search_analytics(self):
        """Test search analytics"""
        response = client.get("/analytics/search")
        assert response.status_code == 200
        data = response.json()
        assert "total_searches" in data
        assert "avg_latency_ms" in data
    
    def test_clear_search_analytics(self):
        """Test clearing search analytics"""
        response = client.delete("/analytics/search/clear")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cleared"