"""
Model Service - Inference Engine and Clinical Safety Logic
Handles model loading, feature preprocessing, prediction ranking, uncertainty calculation,
and critical emergency symptom detection.
"""

import os
import json
import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")

class DiseasePredictionService:
    def __init__(self):
        self.model = None
        self.symptoms_list = []
        self.disease_profiles = {}
        self.emergency_symptoms = set()
        self.evaluation_metrics = {}
        self.load_artifacts()

    def load_artifacts(self):
        """Loads trained Random Forest model and clinical reference metadata."""
        model_path = os.path.join(MODEL_DIR, "disease_model.joblib")
        symptoms_path = os.path.join(MODEL_DIR, "symptoms_list.json")
        profiles_path = os.path.join(MODEL_DIR, "disease_profiles.json")
        emergency_path = os.path.join(MODEL_DIR, "emergency_symptoms.json")
        metrics_path = os.path.join(MODEL_DIR, "evaluation_metrics.json")

        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print(f"Loaded trained Random Forest model from {model_path}")
        else:
            print(f"Warning: Model not found at {model_path}. Train model first.")

        if os.path.exists(symptoms_path):
            with open(symptoms_path, "r", encoding="utf-8") as f:
                self.symptoms_list = json.load(f)

        if os.path.exists(profiles_path):
            with open(profiles_path, "r", encoding="utf-8") as f:
                self.disease_profiles = json.load(f)

        if os.path.exists(emergency_path):
            with open(emergency_path, "r", encoding="utf-8") as f:
                self.emergency_symptoms = set(json.load(f))

        if os.path.exists(metrics_path):
            with open(metrics_path, "r", encoding="utf-8") as f:
                self.evaluation_metrics = json.load(f)

    def get_symptoms(self):
        """Returns the complete list of supported standardized symptoms with labels and categories."""
        # Categorize symptoms into intuitive user-facing groups
        categories_map = {
            "Systemic & Fever": [
                "high_fever", "mild_fever", "chills", "shivering", "sweating",
                "fatigue", "malaise", "lethargy", "weight_loss", "weight_gain",
                "dehydration", "restlessness"
            ],
            "Head, Eyes, ENT & Neurological": [
                "headache", "dizziness", "spinning_movements", "loss_of_balance", "unsteadiness",
                "blurred_and_distorted_vision", "visual_disturbances", "redness_of_eyes",
                "watering_from_eyes", "pain_behind_the_eyes", "sunken_eyes", "loss_of_smell",
                "sinus_pressure", "runny_nose", "congestion", "patches_in_throat",
                "throat_irritation", "continuous_sneezing", "slurred_speech", "altered_sensorium",
                "lack_of_concentration", "anxiety", "depression", "irritability", "mood_swings"
            ],
            "Respiratory & Chest": [
                "cough", "breathlessness", "chest_pain", "phlegm", "mucoid_sputum",
                "rusty_sputum", "blood_in_sputum", "fast_heart_rate", "palpitations"
            ],
            "Gastrointestinal & Abdominal": [
                "nausea", "vomiting", "stomach_pain", "abdominal_pain", "belly_pain",
                "acidity", "indigestion", "loss_of_appetite", "constipation", "diarrhoea",
                "passage_of_gases", "swelling_of_stomach", "distention_of_abdomen",
                "stomach_bleeding", "ulcers_on_tongue"
            ],
            "Liver & Jaundice Signs": [
                "yellowish_skin", "yellowing_of_eyes", "yellow_urine", "dark_urine",
                "acute_liver_failure", "fluid_overload"
            ],
            "Urinary & Reproductive": [
                "burning_micturition", "spotting_urination", "bladder_discomfort",
                "foul_smell_of_urine", "continuous_feel_of_urine", "polyuria",
                "abnormal_menstruation"
            ],
            "Skin & Allergies": [
                "itching", "skin_rash", "nodal_skin_eruptions", "dischromic_patches",
                "pus_filled_pimples", "blackheads", "scurring", "skin_peeling",
                "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails",
                "blister", "red_sore_around_nose", "yellow_crust_ooze",
                "red_spots_over_body", "bruising", "internal_itching"
            ],
            "Musculoskeletal & Joints": [
                "joint_pain", "neck_pain", "back_pain", "knee_pain", "hip_joint_pain",
                "stiff_neck", "swelling_joints", "movement_stiffness", "painful_walking",
                "muscle_pain", "muscle_weakness", "muscle_wasting", "weakness_in_limbs",
                "weakness_of_one_body_side", "cramps"
            ],
            "Endocrine & Vascular": [
                "cold_hands_and_feets", "excessive_hunger", "increased_appetite",
                "irregular_sugar_level", "enlarged_thyroid", "puffy_face_and_eyes",
                "brittle_nails", "swollen_extremeties", "swollen_legs", "swollen_blood_vessels",
                "prominent_veins_on_calf", "drying_and_tingling_lips", "obesity"
            ]
        }

        # Build categorized response
        categorized = []
        assigned = set()
        for cat_name, sym_keys in categories_map.items():
            valid_keys = [s for s in sym_keys if s in self.symptoms_list]
            assigned.update(valid_keys)
            categorized.append({
                "category": cat_name,
                "symptoms": [
                    {
                        "id": s,
                        "name": s.replace("_", " ").title(),
                        "is_emergency": s in self.emergency_symptoms
                    }
                    for s in valid_keys
                ]
            })

        # Add any remaining symptoms to "Other Manifestations"
        remaining = [s for s in self.symptoms_list if s not in assigned]
        if remaining:
            categorized.append({
                "category": "Other Manifestations",
                "symptoms": [
                    {
                        "id": s,
                        "name": s.replace("_", " ").title(),
                        "is_emergency": s in self.emergency_symptoms
                    }
                    for s in remaining
                ]
            })

        flat_list = [
            {
                "id": s,
                "name": s.replace("_", " ").title(),
                "is_emergency": s in self.emergency_symptoms
            }
            for s in self.symptoms_list
        ]

        return {
            "total_count": len(self.symptoms_list),
            "categories": categorized,
            "flat_list": flat_list
        }

    def predict(self, selected_symptoms):
        """
        Executes prediction pipeline:
        1. Validates and normalizes selected symptoms
        2. Detects red-flag emergency symptoms
        3. Encodes binary feature vector
        4. Predicts class probabilities
        5. Estimates calibration and uncertainty
        6. Enriches with clinical guidelines and specialist information
        """
        if not self.model:
            raise RuntimeError("Model is not initialized.")

        if not selected_symptoms or not isinstance(selected_symptoms, list):
            raise ValueError("Please provide a non-empty list of selected symptoms.")

        # Normalize symptom IDs
        normalized_selected = set()
        unrecognized = []
        for s in selected_symptoms:
            s_clean = str(s).strip().lower().replace(" ", "_")
            if s_clean in self.symptoms_list:
                normalized_selected.add(s_clean)
            else:
                unrecognized.append(s)

        if len(normalized_selected) == 0:
            raise ValueError(f"None of the provided symptoms were recognized in the clinical dataset. Unrecognized: {unrecognized}")

        # Check for Critical Emergency Symptoms
        detected_emergencies = [
            s.replace("_", " ").title()
            for s in normalized_selected
            if s in self.emergency_symptoms
        ]
        has_emergency = len(detected_emergencies) > 0

        # Construct feature vector
        feature_vector = np.zeros(len(self.symptoms_list), dtype=int)
        for idx, sym in enumerate(self.symptoms_list):
            if sym in normalized_selected:
                feature_vector[idx] = 1

        feature_matrix = feature_vector.reshape(1, -1)

        # Get class probabilities
        probabilities = self.model.predict_proba(feature_matrix)[0]
        classes = self.model.classes_

        # Rank all predictions by descending probability
        ranked_indices = np.argsort(probabilities)[::-1]
        
        # Determine top predictions (probabilities > 0.02 or top 3)
        top_candidates = []
        for idx in ranked_indices:
            prob = float(probabilities[idx])
            disease_name = str(classes[idx])
            profile = self.disease_profiles.get(disease_name, {})
            
            top_candidates.append({
                "disease": disease_name,
                "probability": round(prob, 4),
                "confidence_percent": round(prob * 100, 1),
                "specialist": profile.get("specialist", "General Physician"),
                "severity": profile.get("severity", "Moderate"),
                "description": profile.get("description", "A medical condition affecting physiological systems.")
            })
            if len(top_candidates) >= 5 and prob < 0.05:
                break

        primary = top_candidates[0]
        top_prob = primary["probability"]

        # Honest Uncertainty Assessment
        # If user selected very few symptoms (e.g. 1-2 generic symptoms) or top prob is diffuse
        symptom_count = len(normalized_selected)
        if symptom_count <= 2 or top_prob < 0.40:
            uncertainty_level = "High"
            uncertainty_explanation = (
                "High clinical uncertainty: Only a minimal set of non-specific symptoms was provided, "
                "or the symptoms overlap broadly across multiple medical conditions. "
                "Additional clinical history and laboratory evaluation are required."
            )
        elif top_prob < 0.70 or symptom_count < 4:
            uncertainty_level = "Moderate"
            uncertainty_explanation = (
                "Moderate uncertainty: Multiple plausible conditions share similar symptom signatures. "
                "Differential diagnosis by a medical professional is recommended."
            )
        else:
            uncertainty_level = "Low"
            uncertainty_explanation = (
                "Low statistical uncertainty against our benchmark model: The symptom cluster matches typical presentations. "
                "However, statistical certainty does NOT replace clinical laboratory confirmation."
            )

        # Fetch clinical recommendations for primary predicted disease
        primary_profile = self.disease_profiles.get(primary["disease"], {})

        emergency_response = None
        if has_emergency:
            emergency_response = {
                "triggered": True,
                "detected_symptoms": detected_emergencies,
                "warning_level": "CRITICAL",
                "action_required": "Seek immediate emergency medical care (Call 911 / emergency local ambulance). Do not delay.",
                "advisory": (
                    "You have reported severe red-flag symptoms (such as "
                    + ", ".join(detected_emergencies)
                    + ") that can indicate life-threatening cardiac, pulmonary, or cerebrovascular emergencies."
                )
            }

        return {
            "primary_prediction": {
                "disease": primary["disease"],
                "confidence": round(top_prob, 4),
                "confidence_percent": round(top_prob * 100, 1),
                "specialist": primary_profile.get("specialist", "General Physician"),
                "severity": primary_profile.get("severity", "Moderate"),
                "description": primary_profile.get("description", ""),
                "precautions": primary_profile.get("precautions", [
                    "Consult a qualified healthcare provider",
                    "Keep track of symptom duration and changes",
                    "Avoid self-prescribing medications"
                ])
            },
            "uncertainty": {
                "level": uncertainty_level,
                "explanation": uncertainty_explanation
            },
            "top_differential_diagnoses": top_candidates[:5],
            "emergency_alert": emergency_response,
            "selected_symptoms_processed": [s.replace("_", " ").title() for s in sorted(list(normalized_selected))],
            "symptom_count": len(normalized_selected),
            "unrecognized_symptoms": unrecognized,
            "disclaimer": (
                "PRELIMINARY HEALTH SCREENING NOTICE: This result is generated by a statistical machine learning algorithm "
                "for educational and preliminary screening demonstration purposes only. It is NOT a medical diagnosis, "
                "clinical prognosis, or treatment prescription. Always consult a licensed medical doctor for proper diagnosis."
            )
        }

# Global singleton
prediction_service = DiseasePredictionService()
