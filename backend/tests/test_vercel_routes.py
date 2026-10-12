"""
Test suite verifying Vercel routing entry points, root endpoint discovery,
dual route aliases (with and without /api prefix), and custom JSON 404 handling.
"""

import pytest
import sys
import os

# Ensure backend and repo root are in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_root_and_api_discovery_endpoints(client):
    """GET / and GET /api should return 200 with service information and endpoint catalog."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    data_root = res_root.get_json()
    assert data_root["status"] == "online"
    assert data_root["service"] == "HealthAI Disease Prediction Engine API"
    assert data_root["model_loaded"] is True
    assert "endpoints" in data_root
    assert data_root["endpoints"]["health"] == "/api/health"

    res_api = client.get("/api")
    assert res_api.status_code == 200
    data_api = res_api.get_json()
    assert data_api["status"] == "online"


def test_health_dual_routes(client):
    """GET /api/health and GET /health should both return 200 healthy status."""
    res_api_health = client.get("/api/health")
    assert res_api_health.status_code == 200
    data_api_health = res_api_health.get_json()
    assert data_api_health["status"] == "healthy"
    assert data_api_health["model_loaded"] is True

    res_health = client.get("/health")
    assert res_health.status_code == 200
    data_health = res_health.get_json()
    assert data_health["status"] == "healthy"
    assert data_health["model_loaded"] is True


def test_symptoms_dual_routes(client):
    """GET /api/symptoms and GET /symptoms should both return 200 with symptom data."""
    res_api = client.get("/api/symptoms")
    assert res_api.status_code == 200
    assert res_api.get_json()["success"] is True

    res_raw = client.get("/symptoms")
    assert res_raw.status_code == 200
    assert res_raw.get_json()["success"] is True


def test_metrics_dual_routes(client):
    """GET /api/metrics and GET /metrics should both return 200 with model metrics."""
    res_api = client.get("/api/metrics")
    assert res_api.status_code == 200
    assert res_api.get_json()["success"] is True

    res_raw = client.get("/metrics")
    assert res_raw.status_code == 200
    assert res_raw.get_json()["success"] is True


def test_dashboard_stats_dual_routes(client):
    """GET /api/dashboard/stats and GET /dashboard/stats should both return 200."""
    res_api = client.get("/api/dashboard/stats")
    assert res_api.status_code == 200
    assert res_api.get_json()["success"] is True

    res_raw = client.get("/dashboard/stats")
    assert res_raw.status_code == 200
    assert res_raw.get_json()["success"] is True


def test_custom_json_404_handler(client):
    """Unmatched routes should return structured JSON 404 with endpoint discovery."""
    res = client.get("/nonexistent/endpoint")
    assert res.status_code == 404
    data = res.get_json()
    assert data["success"] is False
    assert data["error"] == "Not Found"
    assert "endpoints" in data


def test_vercel_entrypoint_imports():
    """Verify that both api/index.py and backend/api/index.py expose the valid Flask 'app'."""
    # Test root api/index.py
    import importlib.util
    root_api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "api", "index.py"))
    spec = importlib.util.spec_from_file_location("root_api_index", root_api_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from flask import Flask
    assert hasattr(module, "app")
    assert isinstance(module.app, Flask)

    # Test backend/api/index.py
    backend_api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api", "index.py"))
    spec_b = importlib.util.spec_from_file_location("backend_api_index", backend_api_path)
    module_b = importlib.util.module_from_spec(spec_b)
    spec_b.loader.exec_module(module_b)
    assert hasattr(module_b, "app")
    assert isinstance(module_b.app, Flask)


def test_vercel_path_fix_middleware(client):
    """
    Simulate Vercel edge rewrite where PATH_INFO is /api/index.py or /api/index
    and HTTP_X_FORWARDED_URI contains the true original client request URL.
    """
    # 1. Simulating Vercel rewrite of /api/health to /api/index.py
    res = client.get("/api/index.py", headers={"X-Forwarded-Uri": "/api/health"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True

    # 2. Simulating Vercel rewrite of root / to /api/index.py
    res_root = client.get("/api/index.py", headers={"X-Forwarded-Uri": "/"})
    assert res_root.status_code == 200
    assert res_root.get_json()["status"] == "online"

    # 3. Simulating Vercel rewrite of /api/symptoms to /api/index
    res_sym = client.get("/api/index", headers={"X-Forwarded-Uri": "/api/symptoms"})
    assert res_sym.status_code == 200
    assert res_sym.get_json()["success"] is True

    # 4. Direct request to /api/index.py without headers should also return 200 online info
    res_direct = client.get("/api/index.py")
    assert res_direct.status_code == 200
    assert res_direct.get_json()["status"] == "online"
