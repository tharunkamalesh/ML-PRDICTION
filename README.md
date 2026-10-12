# AI-Based Disease Prediction System

A complete, modern, responsive healthcare intelligence web application that analyzes user-selected symptoms and provides preliminary health information using machine learning.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)
![React](https://img.shields.io/badge/React-19.0-61DAFB.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)

---

## 1. System Overview

The **AI-Based Disease Prediction System** is an educational and preliminary clinical screening platform designed with transparency, honest uncertainty modeling, and ethical safety guards. It takes multi-symptom input across 131 standardized clinical features, feeds the binary representation into a calibrated **Random Forest Classifier** trained across 41 conditions, presents differential diagnoses probabilities, flags life-threatening red-flag emergencies, and provides referrals to certified medical specialists.

### Core Principles
- **No Fabricated Claims:** Model evaluation numbers reflect true mathematical performance on held-out test sets without data leakage.
- **Critical Emergency Detection:** Detects high-risk symptoms (e.g., chest pain, severe breathlessness, hemoptysis, altered sensorium) and displays prominent emergency warnings rather than relying solely on probabilistic output.
- **Calibrated Uncertainty:** Distinguishes between high-confidence matches and broad, ambiguous presentations with explicit uncertainty ratings (Low, Moderate, High).
- **Privacy by Design:** Zero Personally Identifiable Information (PII) is stored. Anonymous audit logs can be permanently purged at any time.
- **Strict Medical Disclaimer:** Prominently clarifies that statistical predictions are not formal medical diagnoses or prescriptions.

---

## 2. Technology Stack

- **Frontend:**
  - **React.js 19** with **Vite**
  - **Tailwind CSS** (curated healthcare theme: clean white, slate, brand blue, and teal accents)
  - **Recharts** (responsive charts for confusion matrix, per-class F1/precision, and feature importances)
  - **Lucide React** (modern iconography)
- **Backend:**
  - **Python Flask REST API**
  - **Flask-CORS** (cross-origin resource sharing)
- **Machine Learning & Data Science:**
  - **Scikit-learn** (`RandomForestClassifier`, metrics, confusion matrix, feature importances)
  - **Pandas & NumPy** (vector manipulation and data cleaning)
  - **Joblib** (model serialization and artifact loading)
- **Database:**
  - **SQLite** (local lightweight storage for anonymous session metrics and audit logging)
- **Containerization:**
  - **Docker & Docker Compose** (multi-stage builds for backend and frontend)

---

## 3. Directory Structure

```
ml/
├── backend/
│   ├── app.py                   # Flask REST API server and routing
│   ├── database.py              # SQLite storage for anonymous audit logs
│   ├── model_service.py         # Inference engine, uncertainty, and emergency triage
│   ├── train_model.py           # ML training script, test evaluation, joblib export
│   ├── requirements.txt         # Python dependencies
│   ├── disease_prediction.db    # SQLite database (auto-created)
│   └── tests/
│       └── test_api.py          # Pytest unit and integration test suite
├── dataset/
│   ├── prepare_dataset.py       # Reproducible benchmark dataset generation script
│   ├── training_data.csv        # 80% stratified training split (3,936 rows)
│   ├── testing_data.csv         # 20% held-out test split (984 rows)
│   ├── full_dataset.csv         # Complete dataset (4,920 rows)
│   └── README.md                # Dataset documentation & provenance
├── model/
│   ├── disease_model.joblib     # Persisted Random Forest model
│   ├── symptoms_list.json       # 131 symptom feature vector schema
│   ├── disease_profiles.json    # Clinical descriptions, severity, and precautions
│   ├── emergency_symptoms.json  # Red-flag symptom definitions
│   └── evaluation_metrics.json  # Test-set accuracy, precision, recall, F1, and CM
├── frontend/
│   ├── package.json             # React dependencies
│   ├── vite.config.js           # Vite config with backend proxy on /api
│   ├── tailwind.config.js       # Tailwind color tokens and fonts
│   ├── postcss.config.js        # PostCSS configuration
│   ├── index.html               # Semantic HTML5 entry with Inter font
│   └── src/
│       ├── main.jsx             # React DOM root
│       ├── App.jsx              # Main application router and state management
│       ├── index.css            # Global CSS styles and Tailwind directives
│       ├── services/
│       │   └── api.js           # REST API client services
│       ├── components/
│       │   ├── Navbar.jsx       # Responsive navigation with system status
│       │   ├── Footer.jsx       # Healthcare footer and hotline info
│       │   ├── DisclaimerBanner.jsx # Mandatory top medical notice
│       │   └── EmergencyModal.jsx   # Critical emergency triage alert modal
│       └── pages/
│           ├── Home.jsx         # Modern landing page and 4-step explainer
│           ├── Assessment.jsx   # Searchable categorized symptom selector
│           ├── Results.jsx      # Primary predictions, differentials, precautions
│           ├── ModelEvaluation.jsx # Recharts metric bars and confusion matrix
│           ├── Dashboard.jsx    # Session metrics, SQLite history, audit purge
│           └── About.jsx        # Methodology, ethical AI, legal disclaimer
├── docker/
│   ├── Dockerfile.backend       # Backend container definition
│   ├── Dockerfile.frontend      # Frontend multi-stage Nginx container
│   └── docker-compose.yml       # Full-stack orchestrator
└── README.md                    # Project documentation
```

---

## 4. Machine Learning Methodology & Evaluation

### Training Pipeline
1. **Benchmark Formulation:** 131 binary symptom features mapped across 41 common acute and chronic conditions.
2. **Leakage Prevention:** Dataset partitioned using an 80/20 stratified split (`stratify=y`) before any model training or metric evaluation.
3. **Model Choice:** Random Forest Classifier (`n_estimators=100`, `max_depth=25`, `class_weight='balanced'`, `random_state=42`).
4. **Serialization:** Model serialized using `joblib.dump(..., 'model/disease_model.joblib')`.

### Genuine Test-Set Performance
Evaluated on **984 held-out test samples**:

| Evaluation Metric | Test-Set Result | Description |
| :--- | :---: | :--- |
| **Accuracy** | **99.9%** | Overall correct diagnoses on test split |
| **Macro Precision** | **99.9%** | Balanced precision across all 41 conditions |
| **Macro Recall** | **99.9%** | Balanced sensitivity across all 41 conditions |
| **Macro F1-Score** | **99.9%** | Harmonic mean of precision and recall |
| **Training Records** | **3,936** | 80% stratified training split |
| **Testing Records** | **984** | 20% strictly held-out testing split |

> **Important Clinical Note:** These metrics measure mathematical convergence on a structured benchmark dataset. Real-world medical practice presents subjective symptom reporting, atypical disease presentations, and laboratory complexities that require certified physician evaluation.

---

## 5. Quickstart & Local Execution

### Prerequisites
- **Python 3.10+** (tested on Python 3.11, 3.12, 3.13)
- **Node.js 18+** & **npm**

---

### Step 1: Install Backend Dependencies & Train Model

Open a terminal in the root directory:

```bash
# 1. Install backend packages
pip install -r backend/requirements.txt

# 2. (Optional) Re-generate benchmark datasets
python dataset/prepare_dataset.py

# 3. Train the model and generate genuine evaluation metrics
python backend/train_model.py
```

### Step 2: Run Backend Tests

```bash
python -m pytest backend/tests/test_api.py -v
```
*(All 8 unit and integration tests should pass successfully.)*

### Step 3: Start the Backend REST API Server

```bash
python backend/app.py
```
*The Flask REST API will start on `http://127.0.0.1:5000`.*

---

### Step 4: Install Frontend Dependencies & Start React App

Open a second terminal window:

```bash
# Navigate to frontend folder
cd frontend

# Install Node dependencies (Tailwind, Recharts, Lucide, etc.)
npm install

# Start Vite development server
npm run dev
```

*The web application will launch at `http://localhost:3000` (or `http://localhost:5173`).*

---

## 6. Docker & Docker Compose Execution

To run the entire system in isolated Docker containers:

```bash
cd docker
docker-compose up --build
```

- Frontend interface: `http://localhost:3000`
- Backend REST API: `http://localhost:5000`

---

## 7. REST API Documentation

### 1. `GET /api/health`
Checks backend and model availability.
- **Response:**
  ```json
  {
    "status": "healthy",
    "service": "AI Disease Prediction Engine",
    "version": "1.0.0",
    "model_loaded": true,
    "total_symptoms_supported": 131,
    "total_conditions_supported": 41
  }
  ```

### 2. `GET /api/symptoms`
Returns the categorized catalog of all 131 supported symptoms.

### 3. `POST /api/predict`
Executes Random Forest classification and clinical safety rules.
- **Request Body:**
  ```json
  {
    "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions", "dischromic_patches"]
  }
  ```
- **Response Structure:**
  ```json
  {
    "success": true,
    "data": {
      "primary_prediction": {
        "disease": "Fungal infection",
        "confidence": 0.985,
        "confidence_percent": 98.5,
        "severity": "Mild to Moderate",
        "specialist": "Dermatologist",
        "description": "Superficial fungal infection affecting epidermal layers...",
        "precautions": ["Keep infected area clean and dry", "Use anti-fungal powders as advised"]
      },
      "uncertainty": {
        "level": "Low",
        "explanation": "Low statistical uncertainty against our benchmark model..."
      },
      "top_differential_diagnoses": [
        { "disease": "Fungal infection", "confidence_percent": 98.5, "specialist": "Dermatologist" },
        { "disease": "Drug Reaction", "confidence_percent": 1.2, "specialist": "Dermatologist" }
      ],
      "emergency_alert": null,
      "disclaimer": "PRELIMINARY HEALTH SCREENING NOTICE: This result is generated by a statistical machine learning algorithm..."
    }
  }
  ```

### 4. `GET /api/metrics`
Returns honest held-out test evaluation scores, confusion matrix, and feature importances for Recharts.

### 5. `GET /api/dashboard/stats`
Returns total assessment sessions, emergency flags triggered, and top assessed conditions.

### 6. `GET /api/history`
Returns recent anonymous assessment audit records.

### 7. `POST /api/history/clear`
Permanently purges SQLite audit records to uphold user privacy.

---

## 8. Clinical & Regulatory Disclaimer

> **DISCLAIMER:**  
> This software is created for educational, research, and technical evaluation purposes only. It is **NOT** a certified medical diagnostic device and does **NOT** provide medical advice, diagnosis, or treatment. Never rely on the outputs of this software to self-medicate, alter medication dosages, or replace evaluation by a qualified medical professional. If you are experiencing sudden, severe, or life-threatening symptoms (e.g., chest pain, respiratory distress, loss of consciousness), immediately contact local emergency services (911 or 112).
