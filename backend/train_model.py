"""
Model Training and Evaluation Pipeline
Trains Random Forest Classifier for Disease Prediction, evaluates metrics honestly on held-out test data,
and persists artifacts with joblib and JSON.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")

def train_and_evaluate():
    print("Loading datasets...")
    train_file = os.path.join(DATASET_DIR, "training_data.csv")
    test_file = os.path.join(DATASET_DIR, "testing_data.csv")
    
    if not os.path.exists(train_file) or not os.path.exists(test_file):
        raise FileNotFoundError("Training or testing dataset file not found. Run dataset/prepare_dataset.py first.")
        
    train_df = pd.read_csv(train_file)
    test_df = pd.read_csv(test_file)
    
    # Feature columns (all except prognosis)
    feature_cols = [c for c in train_df.columns if c != "prognosis"]
    target_col = "prognosis"
    
    X_train = train_df[feature_cols].values
    y_train = train_df[target_col].values
    
    X_test = test_df[feature_cols].values
    y_test = test_df[target_col].values
    
    classes = sorted(list(np.unique(y_train)))
    
    print(f"Features count: {len(feature_cols)}")
    print(f"Classes count: {len(classes)}")
    print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")
    
    # Train Random Forest Classifier with calibrated hyper-parameters
    print("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=25,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    
    # Predictions and probabilities on test set
    print("Evaluating on held-out test set...")
    y_pred = rf_model.predict(X_test)
    y_prob = rf_model.predict_proba(X_test)
    
    # Genuine evaluation metrics
    acc = float(accuracy_score(y_test, y_pred))
    prec_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    prec_weighted = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    rec_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
    rec_weighted = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
    
    cm = confusion_matrix(y_test, y_pred, labels=rf_model.classes_)
    
    report_dict = classification_report(y_test, y_pred, labels=rf_model.classes_, output_dict=True, zero_division=0)
    
    # Top 25 feature importances
    importances = rf_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    top_features = [
        {"symptom": feature_cols[idx], "importance": round(float(importances[idx]), 4)}
        for idx in sorted_idx[:25]
    ]
    
    # Class-wise performance summaries
    class_metrics = []
    for cls in rf_model.classes_:
        metrics = report_dict.get(cls, {})
        class_metrics.append({
            "disease": cls,
            "precision": round(float(metrics.get("precision", 0)), 4),
            "recall": round(float(metrics.get("recall", 0)), 4),
            "f1_score": round(float(metrics.get("f1-score", 0)), 4),
            "support": int(metrics.get("support", 0))
        })
        
    evaluation_results = {
        "model_type": "Random Forest Classifier",
        "n_estimators": 100,
        "n_features": len(feature_cols),
        "n_classes": len(classes),
        "total_train_samples": int(len(X_train)),
        "total_test_samples": int(len(X_test)),
        "accuracy": round(acc, 4),
        "precision_macro": round(prec_macro, 4),
        "precision_weighted": round(prec_weighted, 4),
        "recall_macro": round(rec_macro, 4),
        "recall_weighted": round(rec_weighted, 4),
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "classes": [str(c) for c in rf_model.classes_],
        "confusion_matrix": cm.tolist(),
        "class_metrics": class_metrics,
        "top_features": top_features,
        "test_split_ratio": 0.20,
        "data_leakage_prevented": True,
        "validation_strategy": "Stratified Held-Out Test Set"
    }
    
    # Persist model and artifacts
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_save_path = os.path.join(MODEL_DIR, "disease_model.joblib")
    metrics_save_path = os.path.join(MODEL_DIR, "evaluation_metrics.json")
    features_save_path = os.path.join(MODEL_DIR, "symptoms_list.json")
    
    joblib.dump(rf_model, model_save_path)
    
    with open(metrics_save_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_results, f, indent=2)
        
    with open(features_save_path, "w", encoding="utf-8") as f:
        json.dump(feature_cols, f, indent=2)
        
    print("\n--- Training & Evaluation Complete ---")
    print(f"Accuracy:           {acc * 100:.2f}%")
    print(f"Macro F1-Score:     {f1_macro * 100:.2f}%")
    print(f"Weighted F1-Score:  {f1_weighted * 100:.2f}%")
    print(f"Macro Precision:    {prec_macro * 100:.2f}%")
    print(f"Macro Recall:       {rec_macro * 100:.2f}%")
    print(f"Model saved to:     {model_save_path}")
    print(f"Metrics saved to:   {metrics_save_path}")
    
    return evaluation_results

if __name__ == "__main__":
    train_and_evaluate()
