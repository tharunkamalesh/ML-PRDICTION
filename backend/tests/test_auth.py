"""
Comprehensive Authentication and Role-Based Authorization Tests for HealthAI Backend
Tests registration, login, logout, session expiration, protected routes,
cross-user data isolation, rate limiting, and admin controls.
"""

import sys
import os
import json
import pytest

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database import init_db, clear_history, get_db_connection

@pytest.fixture
def client():
    app.config["TESTING"] = True
    init_db()
    # Clean up test database records before tests
    conn = get_db_connection()
    conn.execute("DELETE FROM sessions")
    conn.execute("DELETE FROM login_attempts")
    conn.execute("DELETE FROM password_resets")
    conn.execute("DELETE FROM assessment_history")
    conn.execute("DELETE FROM users WHERE email != 'admin@healthai.local'")
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client


def test_user_registration_success(client):
    """Test standard user registration creates account and returns cookies."""
    payload = {
        "full_name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "Password123!"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["user"]["full_name"] == "Jane Doe"
    assert data["user"]["email"] == "jane.doe@example.com"
    assert data["user"]["role"] == "user"
    assert "csrf_token" in data

    # Verify session cookie was set
    cookies = response.headers.getlist("Set-Cookie")
    assert any("healthai_session" in c for c in cookies)
    assert any("healthai_csrf" in c for c in cookies)


def test_registration_password_strength_validation(client):
    """Test rejection when password does not satisfy security criteria."""
    # Too short (< 8 chars)
    resp = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": "test1@example.com",
        "password": "pass"
    })
    assert resp.status_code == 400
    assert "at least 8 characters" in json.loads(resp.data)["error"]

    # Missing digits/special characters
    resp2 = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": "test2@example.com",
        "password": "onlyletters"
    })
    assert resp2.status_code == 400
    assert "number or special character" in json.loads(resp2.data)["error"]


def test_registration_role_escalation_blocked(client):
    """Ensure users cannot self-assign the administrator role during signup."""
    payload = {
        "full_name": "Attacker",
        "email": "attacker@example.com",
        "password": "Password123!",
        "role": "admin"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["user"]["role"] == "user"  # Role must stay 'user'


def test_login_and_logout_flow(client):
    """Test full login, session validation via /me, and logout."""
    # Register user first
    client.post("/api/auth/register", json={
        "full_name": "Login User",
        "email": "login.user@example.com",
        "password": "SecurePassword99!"
    })

    # Log out
    client.post("/api/auth/logout")

    # Check /me is unauthenticated
    resp_me = client.get("/api/auth/me")
    assert resp_me.status_code == 200
    assert json.loads(resp_me.data)["authenticated"] is False

    # Log in
    login_resp = client.post("/api/auth/login", json={
        "email": "login.user@example.com",
        "password": "SecurePassword99!"
    })
    assert login_resp.status_code == 200
    login_data = json.loads(login_resp.data)
    assert login_data["success"] is True
    assert login_data["user"]["email"] == "login.user@example.com"

    # Verify /me is now authenticated
    resp_me2 = client.get("/api/auth/me")
    assert resp_me2.status_code == 200
    me_data = json.loads(resp_me2.data)
    assert me_data["authenticated"] is True
    assert me_data["user"]["email"] == "login.user@example.com"

    # Logout
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200

    # Verify session is invalidated
    resp_me3 = client.get("/api/auth/me")
    assert json.loads(resp_me3.data)["authenticated"] is False


def test_generic_login_errors_prevent_enumeration(client):
    """Test generic error responses for both wrong email and wrong password."""
    # Register real user
    client.post("/api/auth/register", json={
        "full_name": "Real User",
        "email": "real@example.com",
        "password": "Password123!"
    })

    # Wrong password for existing user
    resp1 = client.post("/api/auth/login", json={
        "email": "real@example.com",
        "password": "WrongPassword123!"
    })
    assert resp1.status_code == 401
    err1 = json.loads(resp1.data)["error"]

    # Non-existent user
    resp2 = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "AnyPassword123!"
    })
    assert resp2.status_code == 401
    err2 = json.loads(resp2.data)["error"]

    # Both errors must be identical to avoid user enumeration
    assert err1 == err2
    assert "Invalid email or password" in err1


def test_rate_limiting_brute_force_mitigation(client):
    """Test account/IP rate limiting locks out after repeated failed logins."""
    # Register target user
    client.post("/api/auth/register", json={
        "full_name": "Target User",
        "email": "target@example.com",
        "password": "CorrectPassword123!"
    })

    # Send 5 failed attempts
    for _ in range(5):
        client.post("/api/auth/login", json={
            "email": "target@example.com",
            "password": "WrongPassword1!"
        })

    # 6th attempt should be blocked with 429 Too Many Requests
    resp = client.post("/api/auth/login", json={
        "email": "target@example.com",
        "password": "CorrectPassword123!"
    })
    assert resp.status_code == 429
    assert "Too many failed login attempts" in json.loads(resp.data)["error"]


def test_cross_user_data_isolation(client):
    """Test that users can strictly only view and clear their own assessment records."""
    # 1. User Alpha registers and performs an assessment
    reg_a = client.post("/api/auth/register", json={
        "full_name": "User Alpha",
        "email": "alpha@example.com",
        "password": "PasswordAlpha123!"
    })
    csrf_a = json.loads(reg_a.data)["csrf_token"]

    pred_a = client.post("/api/predict", json={
        "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]
    }, headers={"X-CSRF-Token": csrf_a})
    assert pred_a.status_code == 200

    hist_a = client.get("/api/history")
    assert hist_a.status_code == 200
    assert json.loads(hist_a.data)["count"] == 1
    assert json.loads(hist_a.data)["data"][0]["primary_prediction"] == "Fungal infection"

    # User Alpha logs out
    client.post("/api/auth/logout")

    # 2. User Beta registers and performs a different assessment
    reg_b = client.post("/api/auth/register", json={
        "full_name": "User Beta",
        "email": "beta@example.com",
        "password": "PasswordBeta123!"
    })
    csrf_b = json.loads(reg_b.data)["csrf_token"]

    pred_b = client.post("/api/predict", json={
        "symptoms": ["joint_pain", "knee_pain", "neck_pain"]
    }, headers={"X-CSRF-Token": csrf_b})
    assert pred_b.status_code == 200

    # User Beta's history must ONLY have 1 record, not User Alpha's
    hist_b = client.get("/api/history")
    assert hist_b.status_code == 200
    b_data = json.loads(hist_b.data)
    assert b_data["count"] == 1
    assert b_data["data"][0]["primary_prediction"] == "Osteoarthristis"

    # User Beta clears their history
    clear_b = client.post("/api/history/clear", headers={"X-CSRF-Token": csrf_b})
    assert clear_b.status_code == 200
    assert json.loads(client.get("/api/history").data)["count"] == 0

    # User Beta logs out
    client.post("/api/auth/logout")

    # 3. Log back in as User Alpha - Alpha's record must still be intact!
    login_a = client.post("/api/auth/login", json={
        "email": "alpha@example.com",
        "password": "PasswordAlpha123!"
    })
    assert login_a.status_code == 200
    hist_a_again = client.get("/api/history")
    assert json.loads(hist_a_again.data)["count"] == 1


def test_role_based_access_control_admin_endpoints(client):
    """Test that regular users are blocked from admin endpoints, but admins are permitted."""
    # 1. Regular user login
    reg_user = client.post("/api/auth/register", json={
        "full_name": "Regular User",
        "email": "regular@example.com",
        "password": "Password123!"
    })
    user_csrf = json.loads(reg_user.data)["csrf_token"]

    # Attempt to access admin user list -> 403 Forbidden
    admin_list_resp = client.get("/api/admin/users")
    assert admin_list_resp.status_code == 403
    assert "Administrator privileges required" in json.loads(admin_list_resp.data)["error"]

    # Log out regular user
    client.post("/api/auth/logout")

    # 2. Administrator login using seeded admin account
    admin_login = client.post("/api/auth/login", json={
        "email": "admin@healthai.local",
        "password": "Admin@HealthAI2026!"
    })
    assert admin_login.status_code == 200
    admin_data = json.loads(admin_login.data)
    assert admin_data["user"]["role"] == "admin"
    admin_csrf = admin_data["csrf_token"]

    # Admin access to user management
    admin_users = client.get("/api/admin/users")
    assert admin_users.status_code == 200
    users_list = json.loads(admin_users.data)["data"]
    assert len(users_list) >= 2  # Admin + regular user

    # Admin cannot delete self
    self_del = client.delete(f"/api/admin/users/{admin_data['user']['id']}", headers={"X-CSRF-Token": admin_csrf})
    assert self_del.status_code == 400


def test_forgot_and_reset_password_flow(client):
    """Test generating a reset token and resetting account password."""
    # Register user
    client.post("/api/auth/register", json={
        "full_name": "Reset Tester",
        "email": "reset@example.com",
        "password": "OldPassword123!"
    })
    client.post("/api/auth/logout")

    # Request password reset
    forgot_resp = client.post("/api/auth/forgot-password", json={
        "email": "reset@example.com"
    })
    assert forgot_resp.status_code == 200
    token = json.loads(forgot_resp.data).get("simulated_reset_token")
    assert token is not None

    # Reset password with valid token
    reset_resp = client.post("/api/auth/reset-password", json={
        "token": token,
        "new_password": "NewStrongPassword456!"
    })
    assert reset_resp.status_code == 200
    assert "successfully reset" in json.loads(reset_resp.data)["message"]

    # Old password no longer works
    old_login = client.post("/api/auth/login", json={
        "email": "reset@example.com",
        "password": "OldPassword123!"
    })
    assert old_login.status_code == 401

    # New password works
    new_login = client.post("/api/auth/login", json={
        "email": "reset@example.com",
        "password": "NewStrongPassword456!"
    })
    assert new_login.status_code == 200


def test_user_account_self_deletion(client):
    """Test user can delete their account with password verification."""
    # Register user and add an assessment
    reg = client.post("/api/auth/register", json={
        "full_name": "Delete Me",
        "email": "delete.me@example.com",
        "password": "DeletePassword123!"
    })
    csrf = json.loads(reg.data)["csrf_token"]

    client.post("/api/predict", json={
        "symptoms": ["itching", "skin_rash"]
    }, headers={"X-CSRF-Token": csrf})

    # Wrong password should fail
    fail_del = client.delete("/api/auth/account", json={
        "password": "WrongPassword!"
    }, headers={"X-CSRF-Token": csrf})
    assert fail_del.status_code == 400

    # Correct password succeeds
    success_del = client.delete("/api/auth/account", json={
        "password": "DeletePassword123!"
    }, headers={"X-CSRF-Token": csrf})
    assert success_del.status_code == 200

    # User no longer exists
    login_again = client.post("/api/auth/login", json={
        "email": "delete.me@example.com",
        "password": "DeletePassword123!"
    })
    assert login_again.status_code == 401
