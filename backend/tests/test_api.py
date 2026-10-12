"""
Unit and Integration Tests for AI-Based Disease Prediction System Backend
Validates health, symptom catalog, ML prediction, model evaluation, and history logging.
"""

import sys
import os
import json
import pytest

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database import init_db, clear_history

@pytest.fixture
def client():
    app.config["TESTING"] = True
    init_db()
    clear_history(is_admin=True)
    with app.test_client() as client:
        yield client

import uuid

@pytest.fixture
def auth_client(client):
    """Fixture providing an authenticated client and valid CSRF token."""
    email = f"apitest_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/api/auth/register", json={
        "full_name": "API Test User",
        "email": email,
        "password": "Password123!"
    })
    csrf_token = json.loads(resp.data)["csrf_token"]
    return client, csrf_token

def test_health_endpoint(client):
    """Verify system health and model status is public."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["total_symptoms_supported"] > 100

def test_symptoms_endpoint(client):
    """Verify symptom catalog format and categorization is public."""
    response = client.get("/api/symptoms")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "categories" in data["data"]
    assert len(data["data"]["categories"]) > 0
    assert "flat_list" in data["data"]
    assert data["data"]["total_count"] > 100

def test_predict_requires_authentication(client):
    """Verify that unauthenticated prediction requests are rejected with 401."""
    payload = {
        "symptoms": ["itching", "skin_rash"]
    }
    response = client.post("/api/predict", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data["success"] is False
    assert data["code"] == "UNAUTHORIZED"

def test_predict_valid_symptoms(auth_client):
    """Test standard prediction with valid symptoms when authenticated."""
    client, csrf = auth_client
    payload = {
        "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions", "dischromic_patches"]
    }
    response = client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-CSRF-Token": csrf}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    prediction = data["data"]["primary_prediction"]
    assert prediction["disease"] == "Fungal infection"
    assert "confidence" in prediction
    assert prediction["confidence"] > 0.4
    assert len(prediction["precautions"]) > 0
    assert data["data"]["emergency_alert"] is None
    assert "disclaimer" in data["data"]

def test_predict_emergency_trigger(auth_client):
    """Test emergency alert trigger when critical symptoms are reported."""
    client, csrf = auth_client
    payload = {
        "symptoms": ["chest_pain", "breathlessness", "sweating"]
    }
    response = client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-CSRF-Token": csrf}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    emergency = data["data"]["emergency_alert"]
    assert emergency is not None
    assert emergency["triggered"] is True
    assert "Chest Pain" in emergency["detected_symptoms"] or "Breathlessness" in emergency["detected_symptoms"]
    assert "CRITICAL" in emergency["warning_level"]

def test_predict_empty_symptoms_validation(auth_client):
    """Test error handling when empty symptom array is sent."""
    client, csrf = auth_client
    payload = {"symptoms": []}
    response = client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-CSRF-Token": csrf}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False

def test_predict_unrecognized_symptoms_validation(auth_client):
    """Test error handling when invalid symptoms not in dataset are sent."""
    client, csrf = auth_client
    payload = {"symptoms": ["space_fever", "alien_cough"]}
    response = client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-CSRF-Token": csrf}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False

def test_model_metrics_endpoint(client):
    """Verify genuine model evaluation metrics are served."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    metrics = data["data"]
    assert "accuracy" in metrics
    assert "precision_macro" in metrics
    assert "recall_macro" in metrics
    assert "f1_macro" in metrics
    assert "confusion_matrix" in metrics
    assert len(metrics["top_features"]) > 0

def test_dashboard_stats_and_history(auth_client):
    """Verify assessment logging and dashboard statistics retrieval."""
    client, csrf = auth_client
    # Perform a prediction first
    payload = {"symptoms": ["joint_pain", "neck_pain", "knee_pain"]}
    client.post(
        "/api/predict",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-CSRF-Token": csrf}
    )

    # Fetch stats
    stats_resp = client.get("/api/dashboard/stats")
    assert stats_resp.status_code == 200
    stats_data = json.loads(stats_resp.data)["data"]
    assert stats_data["total_assessments"] >= 1

    # Fetch history
    hist_resp = client.get("/api/history")
    assert hist_resp.status_code == 200
    hist_data = json.loads(hist_resp.data)
    assert hist_data["count"] >= 1
    assert hist_data["data"][0]["primary_prediction"] == "Osteoarthristis"

    # Test clear history
    clear_resp = client.post("/api/history/clear", headers={"X-CSRF-Token": csrf})
    assert clear_resp.status_code == 200
    hist_resp2 = client.get("/api/history")
    assert json.loads(hist_resp2.data)["count"] == 0
