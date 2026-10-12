"""
Flask REST API for AI-Based Disease Prediction System
Includes secure authentication, session management, CSRF protection,
role-based access control, rate limiting, and ML prediction endpoints.
"""

import os
import sys
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from model_service import prediction_service
from database import (
    init_db,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_profile,
    delete_user_account,
    list_all_users,
    update_user_status,
    verify_password,
    create_session,
    get_session,
    delete_session,
    delete_all_user_sessions,
    record_login_attempt,
    is_rate_limited,
    clear_failed_attempts,
    create_password_reset_token,
    verify_password_reset_token,
    consume_password_reset_token,
    log_assessment,
    get_history,
    get_assessment_stats,
    clear_history
)

from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# Enable ProxyFix to correctly interpret reverse proxy headers from Render
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Secret key & Configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "healthai-secure-secret-key-2026")
SESSION_COOKIE_NAME = "healthai_session"
CSRF_COOKIE_NAME = "healthai_csrf"
COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").strip().lower() in ("true", "1")
COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "None" if COOKIE_SECURE else "Lax")

# Configure CORS dynamically for deployed frontend and local development
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:3000"
]
frontend_url = os.environ.get("FRONTEND_URL", "").strip().rstrip("/")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

extra_origins = os.environ.get("ALLOWED_ORIGINS", "").strip()
if extra_origins:
    for origin in extra_origins.split(","):
        cleaned = origin.strip().rstrip("/")
        if cleaned and cleaned not in allowed_origins:
            allowed_origins.append(cleaned)

CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": allowed_origins}}
)

# Ensure database tables and initial admin exist
init_db()


# ============================================================================
# Security & Authentication Helpers
# ============================================================================

def get_client_ip():
    """Extracts client IP address safely, checking X-Forwarded-For if behind a proxy."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def get_current_user_and_session():
    """Extracts and verifies active session from HttpOnly cookie or Authorization header."""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_id = auth_header.split(" ", 1)[1].strip()

    if not session_id:
        return None, None

    session_data = get_session(session_id)
    if not session_data:
        return None, None

    user = session_data["user"]
    if not user.get("is_active"):
        return None, None

    return user, session_data


def validate_password_strength(password: str):
    """
    Validates password strength:
    - Minimum 8 characters
    - Maximum 128 characters (mitigate CPU denial-of-service on hashing)
    - At least one letter and at least one digit or special character
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 128:
        return False, "Password cannot exceed 128 characters."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one alphabetical letter."
    if not re.search(r"[0-9!@#$%^&*()_+\-=\[\]{};':\",.<>?]", password):
        return False, "Password must contain at least one number or special character."
    return True, None


def validate_email_format(email: str):
    """Validates email format using regex."""
    if not email:
        return False, "Email address is required."
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email.strip()):
        return False, "Please enter a valid email address."
    return True, None


def login_required(f):
    """Decorator ensuring request has valid authenticated session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user, session_data = get_current_user_and_session()
        if not user:
            return jsonify({
                "success": False,
                "error": "Authentication required. Please log in to proceed.",
                "code": "UNAUTHORIZED"
            }), 401

        # CSRF validation for mutating methods (POST, PUT, DELETE)
        if request.method in ["POST", "PUT", "DELETE"]:
            client_csrf = request.headers.get("X-CSRF-Token")
            session_csrf = session_data.get("csrf_token")
            # If request is from cookie session, verify CSRF token
            if request.cookies.get(SESSION_COOKIE_NAME):
                if not client_csrf or client_csrf != session_csrf:
                    return jsonify({
                        "success": False,
                        "error": "CSRF verification failed. Please refresh and try again.",
                        "code": "CSRF_ERROR"
                    }), 403

        return f(user, session_data, *args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator ensuring request has valid authenticated administrator session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user, session_data = get_current_user_and_session()
        if not user:
            return jsonify({
                "success": False,
                "error": "Authentication required. Please log in with administrator privileges.",
                "code": "UNAUTHORIZED"
            }), 401
        if user.get("role") != "admin":
            return jsonify({
                "success": False,
                "error": "Access denied. Administrator privileges required.",
                "code": "FORBIDDEN"
            }), 403

        # CSRF validation for mutating methods
        if request.method in ["POST", "PUT", "DELETE"]:
            client_csrf = request.headers.get("X-CSRF-Token")
            session_csrf = session_data.get("csrf_token")
            if request.cookies.get(SESSION_COOKIE_NAME):
                if not client_csrf or client_csrf != session_csrf:
                    return jsonify({
                        "success": False,
                        "error": "CSRF verification failed. Please refresh and try again.",
                        "code": "CSRF_ERROR"
                    }), 403

        return f(user, session_data, *args, **kwargs)
    return decorated_function


def set_auth_cookies(response, session_id: str, csrf_token: str):
    """Sets secure HttpOnly session cookie and accessible CSRF token cookie."""
    # HttpOnly session cookie
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_id,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=7 * 24 * 3600,
        path="/"
    )
    # Accessible CSRF cookie for frontend client header injection
    response.set_cookie(
        CSRF_COOKIE_NAME,
        csrf_token,
        httponly=False,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=7 * 24 * 3600,
        path="/"
    )
    return response


def clear_auth_cookies(response):
    """Clears session and CSRF cookies upon logout or account deletion."""
    response.delete_cookie(
        SESSION_COOKIE_NAME,
        path="/",
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE
    )
    response.delete_cookie(
        CSRF_COOKIE_NAME,
        path="/",
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE
    )
    return response


# ============================================================================
# Public Service & Diagnostic Endpoints
# ============================================================================

@app.route("/", methods=["GET"])
@app.route("/api", methods=["GET"])
def root_info():
    """Root endpoint providing service discovery, status, and endpoint catalog."""
    model_ready = prediction_service.model is not None
    return jsonify({
        "service": "HealthAI Disease Prediction Engine API",
        "status": "online",
        "version": "1.0.0",
        "model_loaded": model_ready,
        "total_symptoms_supported": len(prediction_service.symptoms_list),
        "total_conditions_supported": len(prediction_service.disease_profiles),
        "endpoints": {
            "health": "/api/health",
            "symptoms": "/api/symptoms",
            "metrics": "/api/metrics",
            "predict": "/api/predict",
            "dashboard_stats": "/api/dashboard/stats",
            "auth": {
                "register": "/api/auth/register",
                "login": "/api/auth/login",
                "logout": "/api/auth/logout",
                "me": "/api/auth/me"
            }
        }
    }), 200


@app.route("/api/health", methods=["GET"])
@app.route("/health", methods=["GET"])
def health_check():
    """Public system health check endpoint."""
    model_ready = prediction_service.model is not None
    return jsonify({
        "status": "healthy" if model_ready else "degraded",
        "service": "AI Disease Prediction Engine",
        "version": "1.0.0",
        "model_loaded": model_ready,
        "total_symptoms_supported": len(prediction_service.symptoms_list),
        "total_conditions_supported": len(prediction_service.disease_profiles)
    }), 200


@app.route("/api/symptoms", methods=["GET"])
@app.route("/symptoms", methods=["GET"])
def get_symptoms():
    """Public symptom catalog grouped by anatomical/clinical category."""
    try:
        data = prediction_service.get_symptoms()
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/metrics", methods=["GET"])
@app.route("/metrics", methods=["GET"])
def get_metrics():
    """Public model evaluation metrics evaluated on held-out test split."""
    try:
        metrics = prediction_service.evaluation_metrics
        if not metrics:
            return jsonify({
                "success": False,
                "error": "Model evaluation metrics are not available. Please run train_model.py."
            }), 404

        return jsonify({
            "success": True,
            "data": metrics
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard/stats", methods=["GET"])
@app.route("/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Retrieve aggregate usage statistics and model benchmark summary."""
    try:
        db_stats = get_assessment_stats()
        metrics = prediction_service.evaluation_metrics

        summary = {
            "total_assessments": db_stats["total_assessments"],
            "total_emergencies_flagged": db_stats["total_emergencies"],
            "top_assessed_conditions": db_stats["top_conditions"],
            "model_accuracy": metrics.get("accuracy", 0.0),
            "model_f1_macro": metrics.get("f1_macro", 0.0),
            "model_precision_macro": metrics.get("precision_macro", 0.0),
            "model_recall_macro": metrics.get("recall_macro", 0.0),
            "total_test_samples": metrics.get("total_test_samples", 0),
            "total_train_samples": metrics.get("total_train_samples", 0),
            "total_classes": metrics.get("n_classes", 0),
            "total_features": metrics.get("n_features", 0)
        }
        return jsonify({"success": True, "data": summary}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Authentication API Endpoints
# ============================================================================

@app.route("/api/auth/register", methods=["POST"])
@app.route("/auth/register", methods=["POST"])
def register():
    """
    Registers a new regular user account.
    Enforces password rules, validates email format, hashes with bcrypt,
    and automatically creates an active session.
    """
    ip = get_client_ip()
    if is_rate_limited(ip, max_attempts=10, window_minutes=15):
        return jsonify({
            "success": False,
            "error": "Too many registration attempts. Please try again in 15 minutes."
        }), 429

    payload = request.get_json(silent=True) or {}
    full_name = payload.get("full_name", "").strip()
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")

    if not full_name:
        return jsonify({"success": False, "error": "Full name is required."}), 400

    valid_email, email_err = validate_email_format(email)
    if not valid_email:
        return jsonify({"success": False, "error": email_err}), 400

    valid_pwd, pwd_err = validate_password_strength(password)
    if not valid_pwd:
        return jsonify({"success": False, "error": pwd_err}), 400

    # Check if email is already registered
    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({
            "success": False,
            "error": "An account with this email address already exists. Please log in."
        }), 409

    # Create user with role strictly 'user'
    try:
        user = create_user(full_name=full_name, email=email, password=password, role="user")
        session_info = create_session(user["id"], ip_address=ip, user_agent=request.user_agent.string)

        resp = make_response(jsonify({
            "success": True,
            "message": "Account created successfully.",
            "user": {
                "id": user["id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": user["role"]
            },
            "csrf_token": session_info["csrf_token"]
        }), 201)

        return set_auth_cookies(resp, session_info["session_id"], session_info["csrf_token"])

    except Exception as e:
        app.logger.error(f"Registration error: {e}")
        return jsonify({"success": False, "error": "An error occurred during account creation."}), 500


@app.route("/api/auth/login", methods=["POST"])
@app.route("/auth/login", methods=["POST"])
def login():
    """
    Authenticates user using email and password.
    Implements brute-force rate limiting and generic error messages.
    """
    ip = get_client_ip()
    payload = request.get_json(silent=True) or {}
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required."}), 400

    # Rate limit check for IP and email
    if is_rate_limited(ip, max_attempts=5, window_minutes=15) or is_rate_limited(email, max_attempts=5, window_minutes=15):
        return jsonify({
            "success": False,
            "error": "Too many failed login attempts. For security reasons, please try again in 15 minutes."
        }), 429

    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        record_login_attempt(ip, success=False)
        record_login_attempt(email, success=False)
        return jsonify({
            "success": False,
            "error": "Invalid email or password. Please check your credentials."
        }), 401

    if not user.get("is_active"):
        return jsonify({
            "success": False,
            "error": "This account has been deactivated. Please contact an administrator."
        }), 403

    # Reset failed attempts
    clear_failed_attempts(ip)
    clear_failed_attempts(email)
    record_login_attempt(ip, success=True)
    record_login_attempt(email, success=True)

    session_info = create_session(user["id"], ip_address=ip, user_agent=request.user_agent.string)

    resp = make_response(jsonify({
        "success": True,
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"]
        },
        "csrf_token": session_info["csrf_token"]
    }), 200)

    return set_auth_cookies(resp, session_info["session_id"], session_info["csrf_token"])


@app.route("/api/auth/logout", methods=["POST"])
@app.route("/auth/logout", methods=["POST"])
def logout():
    """Invalidates active session and clears authentication cookies."""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_id = auth_header.split(" ", 1)[1].strip()

    if session_id:
        delete_session(session_id)

    resp = make_response(jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200)
    return clear_auth_cookies(resp)


@app.route("/api/auth/me", methods=["GET"])
@app.route("/auth/me", methods=["GET"])
def get_current_user():
    """
    Checks if active session exists.
    Returns user details and CSRF token if authenticated, or authenticated: False.
    """
    user, session_data = get_current_user_and_session()
    if not user:
        return jsonify({
            "authenticated": False,
            "user": None,
            "csrf_token": None
        }), 200

    return jsonify({
        "authenticated": True,
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"]
        },
        "csrf_token": session_data["csrf_token"]
    }), 200


@app.route("/api/auth/profile", methods=["PUT"])
@app.route("/auth/profile", methods=["PUT"])
@login_required
def update_profile(current_user, session_data):
    """Updates user profile information (name, email, password)."""
    payload = request.get_json(silent=True) or {}
    full_name = payload.get("full_name")
    email = payload.get("email")
    current_password = payload.get("current_password")
    new_password = payload.get("new_password")

    # Fetch full user record to verify current password if updating sensitive fields
    user_record = get_user_by_id(current_user["id"])

    if email or new_password:
        if not current_password or not verify_password(current_password, user_record["password_hash"]):
            return jsonify({
                "success": False,
                "error": "Current password is required to update email or password."
            }), 400

    if email:
        valid_email, email_err = validate_email_format(email)
        if not valid_email:
            return jsonify({"success": False, "error": email_err}), 400
        # Check if email is used by another user
        existing = get_user_by_email(email)
        if existing and existing["id"] != current_user["id"]:
            return jsonify({"success": False, "error": "This email address is already in use."}), 409

    if new_password:
        valid_pwd, pwd_err = validate_password_strength(new_password)
        if not valid_pwd:
            return jsonify({"success": False, "error": pwd_err}), 400

    updated = update_user_profile(
        user_id=current_user["id"],
        full_name=full_name,
        email=email,
        password=new_password
    )

    return jsonify({
        "success": True,
        "message": "Profile updated successfully.",
        "user": {
            "id": updated["id"],
            "full_name": updated["full_name"],
            "email": updated["email"],
            "role": updated["role"]
        }
    }), 200


@app.route("/api/auth/account", methods=["DELETE"])
@app.route("/auth/account", methods=["DELETE"])
@login_required
def delete_account(current_user, session_data):
    """
    Securely deletes user account and all personal assessment history.
    Requires current password confirmation.
    """
    payload = request.get_json(silent=True) or {}
    password = payload.get("password", "")

    user_record = get_user_by_id(current_user["id"])
    if not password or not verify_password(password, user_record["password_hash"]):
        return jsonify({
            "success": False,
            "error": "Password verification failed. Incorrect password provided."
        }), 400

    delete_user_account(current_user["id"])

    resp = make_response(jsonify({
        "success": True,
        "message": "Your account and all associated assessment data have been permanently deleted."
    }), 200)
    return clear_auth_cookies(resp)


@app.route("/api/auth/forgot-password", methods=["POST"])
@app.route("/auth/forgot-password", methods=["POST"])
def forgot_password():
    """
    Generates a password reset token for the given email.
    If email delivery is configured, dispatches an email.
    Otherwise, returns simulation info for local testing.
    """
    ip = get_client_ip()
    if is_rate_limited(ip, max_attempts=5, window_minutes=15):
        return jsonify({
            "success": False,
            "error": "Too many reset requests. Please try again later."
        }), 429

    payload = request.get_json(silent=True) or {}
    email = payload.get("email", "").strip().lower()

    if not email:
        return jsonify({"success": False, "error": "Email address is required."}), 400

    user = get_user_by_email(email)
    simulated_token = None
    email_sent = False

    if user and user.get("is_active"):
        token = create_password_reset_token(user["id"])
        smtp_server = os.environ.get("SMTP_SERVER", "").strip()

        if smtp_server:
            try:
                smtp_port = int(os.environ.get("SMTP_PORT", 587))
                smtp_user = os.environ.get("SMTP_USERNAME", "").strip()
                smtp_pass = os.environ.get("SMTP_PASSWORD", "").strip()
                from_email = os.environ.get("FROM_EMAIL", "noreply@healthai.local")

                msg = MIMEMultipart()
                msg["From"] = from_email
                msg["To"] = email
                msg["Subject"] = "HealthAI - Password Reset Request"
                body = f"Hello {user['full_name']},\n\nUse this token to reset your HealthAI password: {token}\nThis token expires in 60 minutes.\n\nIf you did not request this, please ignore this email."
                msg.attach(MIMEText(body, "plain"))

                server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
                server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                server.quit()
                email_sent = True
            except Exception as e:
                app.logger.error(f"SMTP sending failed: {e}")
                simulated_token = token
        else:
            simulated_token = token

    response_data = {
        "success": True,
        "message": "If this email is registered in our system, password reset instructions have been issued.",
        "email_configured": email_sent
    }
    if simulated_token:
        response_data["simulated_reset_token"] = simulated_token

    return jsonify(response_data), 200


@app.route("/api/auth/reset-password", methods=["POST"])
@app.route("/auth/reset-password", methods=["POST"])
def reset_password():
    """Consumes password reset token and sets new password."""
    payload = request.get_json(silent=True) or {}
    token = payload.get("token", "").strip()
    new_password = payload.get("new_password", "")

    if not token:
        return jsonify({"success": False, "error": "Reset token is required."}), 400

    valid_pwd, pwd_err = validate_password_strength(new_password)
    if not valid_pwd:
        return jsonify({"success": False, "error": pwd_err}), 400

    success = consume_password_reset_token(token, new_password)
    if not success:
        return jsonify({
            "success": False,
            "error": "Invalid or expired password reset token. Please request a new one."
        }), 400

    return jsonify({
        "success": True,
        "message": "Password has been successfully reset. Please log in with your new credentials."
    }), 200


# ============================================================================
# Protected Clinical Assessment & ML Inference Endpoints
# ============================================================================

@app.route("/api/predict", methods=["POST"])
@app.route("/predict", methods=["POST"])
@login_required
def predict_disease(current_user, session_data):
    """
    Perform disease prediction given user-selected symptoms.
    Protected endpoint: requires authenticated session. Links assessment to current_user.
    """
    try:
        payload = request.get_json(force=True, silent=True)
        if not payload or "symptoms" not in payload:
            return jsonify({
                "success": False,
                "error": "Invalid request payload. Expected JSON with 'symptoms' key (list of strings)."
            }), 400

        symptoms = payload.get("symptoms", [])
        if not isinstance(symptoms, list) or len(symptoms) == 0:
            return jsonify({
                "success": False,
                "error": "Please select at least one symptom to perform an assessment."
            }), 400

        # Execute prediction
        result = prediction_service.predict(symptoms)

        # Log assessment linked to the authenticated user
        primary_disease = result["primary_prediction"]["disease"]
        confidence = result["primary_prediction"]["confidence"]
        is_emergency = result["emergency_alert"] is not None
        specialist = result["primary_prediction"]["specialist"]

        assessment_id = log_assessment(
            symptoms=result["selected_symptoms_processed"],
            primary_prediction=primary_disease,
            confidence=confidence,
            emergency_flag=is_emergency,
            specialist=specialist,
            user_id=current_user["id"]
        )
        result["assessment_id"] = assessment_id

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except ValueError as ve:
        return jsonify({
            "success": False,
            "error": str(ve)
        }), 400
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An internal error occurred during prediction analysis."
        }), 500


@app.route("/api/history", methods=["GET"])
@app.route("/history", methods=["GET"])
@login_required
def get_assessment_history(current_user, session_data):
    """
    Retrieve assessment history.
    - Regular users: strictly limited to their own assessment records.
    - Administrators: can pass view=all to inspect system-wide anonymous audit records.
    """
    try:
        limit = request.args.get("limit", default=50, type=int)
        view_param = request.args.get("view", default="").lower()

        # Only admins can view system-wide audit records
        view_all = (view_param == "all" and current_user.get("role") == "admin")

        if view_all:
            history = get_history(limit=limit, user_id=None, view_all=True)
        else:
            history = get_history(limit=limit, user_id=current_user["id"], view_all=False)

        return jsonify({
            "success": True,
            "count": len(history),
            "data": history,
            "view_mode": "system_audit" if view_all else "personal"
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/history/clear", methods=["POST"])
@app.route("/history/clear", methods=["POST"])
@login_required
def clear_assessment_history(current_user, session_data):
    """
    Clear assessment records.
    - Regular users: purges only their personal records.
    - Administrators: can purge all system audit records if confirm=true is passed.
    """
    try:
        is_admin = current_user.get("role") == "admin"
        scope = request.args.get("scope", "personal")

        if is_admin and scope == "all":
            clear_history(user_id=None, is_admin=True)
            msg = "All system assessment audit records have been permanently cleared."
        else:
            clear_history(user_id=current_user["id"], is_admin=False)
            msg = "Your personal assessment history has been cleared."

        return jsonify({
            "success": True,
            "message": msg
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# Administrator Management Endpoints
# ============================================================================

@app.route("/api/admin/users", methods=["GET"])
@app.route("/admin/users", methods=["GET"])
@admin_required
def admin_get_users(current_user, session_data):
    """Administrator endpoint: lists all registered user accounts."""
    try:
        users = list_all_users()
        return jsonify({
            "success": True,
            "count": len(users),
            "data": users
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/admin/users/<int:user_id>", methods=["DELETE"])
@app.route("/admin/users/<int:user_id>", methods=["DELETE"])
@admin_required
def admin_delete_user(current_user, session_data, user_id):
    """Administrator endpoint: deletes a user account after authorization."""
    if user_id == current_user["id"]:
        return jsonify({
            "success": False,
            "error": "Administrators cannot delete their own account from this panel."
        }), 400

    target = get_user_by_id(user_id)
    if not target:
        return jsonify({"success": False, "error": "User not found."}), 404

    delete_user_account(user_id)
    return jsonify({
        "success": True,
        "message": f"User account for '{target['full_name']}' has been deleted."
    }), 200


@app.route("/api/admin/users/<int:user_id>/status", methods=["PUT"])
@app.route("/admin/users/<int:user_id>/status", methods=["PUT"])
@admin_required
def admin_update_user_status(current_user, session_data, user_id):
    """Administrator endpoint: toggles user activation or changes role."""
    target = get_user_by_id(user_id)
    if not target:
        return jsonify({"success": False, "error": "User not found."}), 404

    payload = request.get_json(silent=True) or {}
    is_active = payload.get("is_active")
    role = payload.get("role")

    if user_id == current_user["id"] and role and role != "admin":
        return jsonify({"success": False, "error": "Cannot revoke your own administrator role."}), 400

    update_user_status(user_id, is_active=is_active, role=role)
    updated = get_user_by_id(user_id)

    return jsonify({
        "success": True,
        "message": "User status updated successfully.",
        "data": {
            "id": updated["id"],
            "full_name": updated["full_name"],
            "email": updated["email"],
            "role": updated["role"],
            "is_active": bool(updated["is_active"])
        }
    }), 200


@app.errorhandler(404)
def handle_404_not_found(error):
    """Custom JSON 404 handler for unmatched routes."""
    return jsonify({
        "success": False,
        "error": "Not Found",
        "message": f"The requested URL '{request.path}' was not found on this server.",
        "endpoints": {
            "root": "/",
            "health": "/api/health",
            "symptoms": "/api/symptoms",
            "metrics": "/api/metrics",
            "predict": "/api/predict",
            "dashboard_stats": "/api/dashboard/stats"
        }
    }), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Disease Prediction REST API server with Auth on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
