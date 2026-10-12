"""
Flask REST API for AI-Based Disease Prediction System
Exposes endpoints for symptom selection, ML prediction, model evaluation metrics,
and privacy-compliant assessment history.
"""

import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from model_service import prediction_service
from database import init_db, log_assessment, get_history, get_assessment_stats, clear_history

app = Flask(__name__)
# Enable CORS for all domains or frontend local servers
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Ensure database is initialized on startup
init_db()

@app.route("/api/health", methods=["GET"])
def health_check():
    """System health check endpoint."""
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
def get_symptoms():
    """Retrieve full catalog of supported symptoms grouped by anatomical/clinical category."""
    try:
        data = prediction_service.get_symptoms()
        return jsonify({
            "success": True,
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/predict", methods=["POST"])
def predict_disease():
    """
    Perform disease prediction given user-selected symptoms.
    Validates input, computes class probabilities, determines uncertainty,
    checks for emergency conditions, and optionally records anonymous stats.
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

        # Log anonymous assessment for dashboard stats
        primary_disease = result["primary_prediction"]["disease"]
        confidence = result["primary_prediction"]["confidence"]
        is_emergency = result["emergency_alert"] is not None
        specialist = result["primary_prediction"]["specialist"]
        
        assessment_id = log_assessment(
            symptoms=result["selected_symptoms_processed"],
            primary_prediction=primary_disease,
            confidence=confidence,
            emergency_flag=is_emergency,
            specialist=specialist
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

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """
    Retrieve model evaluation metrics evaluated strictly on the held-out test split.
    Includes Accuracy, Precision, Recall, F1 scores, Confusion Matrix, and Feature Importances.
    """
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

@app.route("/api/history", methods=["GET"])
def get_assessment_history():
    """Retrieve recent anonymous assessments without exposing personal health information."""
    try:
        limit = request.args.get("limit", default=50, type=int)
        history = get_history(limit=limit)
        return jsonify({
            "success": True,
            "count": len(history),
            "data": history
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/history/clear", methods=["POST"])
def clear_assessment_history():
    """Admin endpoint to purge stored anonymous assessment records for privacy compliance."""
    try:
        clear_history()
        return jsonify({
            "success": True,
            "message": "All assessment records cleared successfully."
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Disease Prediction REST API server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
