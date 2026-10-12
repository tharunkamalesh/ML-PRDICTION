# AI-Based Disease Prediction System with Secure Authentication

A complete, modern, responsive healthcare intelligence web application that analyzes user-selected symptoms and provides preliminary health information using machine learning, now reinforced with an enterprise-grade, privacy-compliant **Authentication & Role-Based Access Control (RBAC)** architecture.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)
![React](https://img.shields.io/badge/React-19.0-61DAFB.svg)
![Security](https://img.shields.io/badge/Security-Argon2%20%2F%20bcrypt%20%7C%20HttpOnly%20%7C%20CSRF-emerald.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)

---

## 1. System Overview

The **AI-Based Disease Prediction System** is an educational and preliminary clinical screening platform designed with transparency, honest uncertainty modeling, and ethical safety guards. It takes multi-symptom input across 131 standardized clinical features, feeds the binary representation into a calibrated **Random Forest Classifier** trained across 41 conditions, presents differential diagnoses probabilities, flags life-threatening red-flag emergencies, and provides referrals to certified medical specialists.

### Core Principles & Security Standards
- **Secure Authentication & RBAC:** Complete authentication system powered by Flask, bcrypt password hashing, server-side session tracking, and HttpOnly cookies.
- **Strict User Data Isolation:** Regular users only see and manage their own screening assessments; cross-user data leakage is strictly prohibited at the database query layer.
- **Administrator Controls:** Dedicated admin capabilities for user account lifecycle management (inspect accounts, toggle activation, delete users) and privacy-compliant system audit records.
- **Brute-Force & CSRF Protection:** Login and registration endpoints are protected with rate limiting (IP and email lockout); all mutating endpoints validate session CSRF tokens.
- **No Fabricated Claims:** Model evaluation numbers reflect true mathematical performance on held-out test sets without data leakage.
- **Critical Emergency Detection:** Detects high-risk symptoms (e.g., chest pain, severe breathlessness, hemoptysis, altered sensorium) and displays prominent emergency warnings rather than relying solely on probabilistic output.
- **Calibrated Uncertainty:** Distinguishes between high-confidence matches and broad, ambiguous presentations with explicit uncertainty ratings (Low, Moderate, High).
- **User Right to Erasure:** Users can permanently delete their accounts and purge all associated personal assessment history with password confirmation.
- **Strict Medical Disclaimer:** Prominently clarifies that statistical predictions are not formal medical diagnoses or prescriptions. Authentication does not make the model clinically validated.

---

## 2. Technology Stack

- **Frontend:**
  - **React.js 19** with **Vite**
  - **Tailwind CSS** (curated healthcare theme: clean white, slate, brand blue `#0284c7`, and teal `#0d9488` accents)
  - **Recharts** (responsive charts for confusion matrix, per-class F1/precision, and feature importances)
  - **Lucide React** (modern iconography)
  - **Auth Context** (centralized session state, CSRF injection, and route guards)
- **Backend:**
  - **Python Flask REST API**
  - **bcrypt** (salt rounds 12 for password hashing)
  - **Flask-CORS** (cross-origin resource sharing with credentials support)
  - **python-dotenv** (environment variable configuration)
- **Machine Learning & Data Science:**
  - **Scikit-learn** (`RandomForestClassifier`, metrics, confusion matrix, feature importances)
  - **Pandas & NumPy** (vector manipulation and data cleaning)
  - **Joblib** (model serialization and artifact loading)
- **Database:**
  - **SQLite** (`disease_prediction.db` with normalized tables for `users`, `sessions`, `login_attempts`, `password_resets`, and `assessment_history`)
- **Testing:**
  - **Pytest** (19 comprehensive unit, integration, authentication, RBAC, and data isolation tests)

---

## 3. User Roles & Access Control

| Feature / Page | Public / Unauthenticated | Regular User | Administrator |
| :--- | :---: | :---: | :---: |
| **Landing Page & Navigation** | Full Access | Full Access | Full Access |
| **Model Evaluation & Metrics** | Full Access | Full Access | Full Access |
| **About & Clinical Notice** | Full Access | Full Access | Full Access |
| **Symptom Catalog** | Full Access | Full Access | Full Access |
| **Check Symptoms Tool** | View only (Redirects to Login) | Full Access | Full Access |
| **AI Disease Prediction** | Blocked (Requires Login) | Full Access (Linked to Profile) | Full Access (Linked to Profile) |
| **Personal Screening History** | None | Private to user | Private to user |
| **Profile Settings & Password Change** | None | Full Access | Full Access |
| **Account Self-Deletion** | None | Full Access (Purges personal data) | Full Access |
| **User Account Management** | Blocked (401) | Blocked (403) | Full Access (List, Suspend, Delete) |
| **System-Wide Assessment Purge** | Blocked (401) | Blocked (403) | Full Access (Confirmed purge) |

> **Security Rule:** Users cannot select or grant themselves the administrator role during registration. The registration API strictly enforces `role = 'user'`.

---

## 4. Environment Variables Configuration

Copy `.env.example` to `.env` in the repository root:

```ini
# HealthAI Disease Prediction System - Environment Configuration
SECRET_KEY=healthai-dev-secret-key-change-in-production-2026-secure
PORT=5000

# Cookie Security (set to True in production with HTTPS)
SESSION_COOKIE_SECURE=False

# Initial Default Administrator Account (auto-seeded on first run)
ADMIN_EMAIL=admin@healthai.local
ADMIN_PASSWORD=Admin@HealthAI2026!
ADMIN_NAME=System Administrator

# Optional SMTP Email Configuration for Password Reset
SMTP_SERVER=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
FROM_EMAIL=noreply@healthai.local
```

---

## 5. Directory Structure

```
ml/
├── .env                         # Local environment settings
├── .env.example                 # Environment variable templates
├── backend/
│   ├── app.py                   # Flask REST API server with Auth & RBAC
│   ├── database.py              # SQLite storage, bcrypt hashing, sessions, and migrations
│   ├── model_service.py         # Inference engine, uncertainty, and emergency triage
│   ├── train_model.py           # ML training script, test evaluation, joblib export
│   ├── requirements.txt         # Python dependencies
│   ├── disease_prediction.db    # SQLite database (auto-initialized)
│   └── tests/
│       ├── test_api.py          # Pytest API integration tests
│       └── test_auth.py         # Pytest Authentication, rate limiting & RBAC tests
├── dataset/
│   ├── prepare_dataset.py       # Reproducible benchmark dataset generation script
│   ├── training_data.csv        # 80% stratified training split (3,936 rows)
│   ├── testing_data.csv         # 20% held-out test split (984 rows)
│   └── full_dataset.csv         # Complete dataset (4,920 rows)
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
│   └── src/
│       ├── App.jsx              # Main application router with AuthProvider
│       ├── context/
│       │   └── AuthContext.jsx  # Authentication context & session state
│       ├── services/
│       │   └── api.js           # REST API client with HttpOnly cookies & CSRF
│       ├── components/
│       │   ├── Navbar.jsx       # Responsive navigation with login/user controls
│       │   ├── Footer.jsx       # Healthcare footer and hotline info
│       │   ├── DisclaimerBanner.jsx # Top medical notice
│       │   └── EmergencyModal.jsx   # Critical emergency alert modal
│       └── pages/
│           ├── Home.jsx         # Landing page and 4-step explainer
│           ├── Login.jsx        # Login page with password toggle and demo fill
│           ├── Register.jsx     # Registration page with password strength meter
│           ├── ForgotPassword.jsx # Reset password flow (token/email)
│           ├── Profile.jsx      # Profile settings and account deletion
│           ├── Assessment.jsx   # Authenticated symptom selector
│           ├── Results.jsx      # Primary predictions & differential diagnoses
│           ├── ModelEvaluation.jsx # Model metrics and confusion matrix
│           ├── Dashboard.jsx    # User history & Admin user management
│           └── About.jsx        # Methodology, ethical AI, legal disclaimer
└── README.md                    # Project documentation
```

---

## 6. Quickstart & Local Execution

### Prerequisites
- **Python 3.10+** (tested on Python 3.11, 3.12, 3.13)
- **Node.js 18+** & **npm**

---

### Step 1: Install Backend Dependencies & Initialize Database

Open a terminal in the root directory:

```bash
# 1. Install backend packages
pip install -r backend/requirements.txt

# 2. Initialize database schema & seed initial admin account
python backend/database.py

# 3. (Optional) Retrain model and refresh test evaluation artifacts
python backend/train_model.py
```

### Step 2: Run Backend Tests

Run the complete 19-test test suite covering endpoints, authentication, rate limiting, and RBAC:

```bash
python -m pytest backend/tests -v
```

### Step 3: Start the Backend REST API Server

```bash
python backend/app.py
```
*The Flask REST API starts on `http://127.0.0.1:5000`.*

---

### Step 4: Install Frontend Dependencies & Start React App

Open a second terminal window:

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

*The web application will launch at `http://localhost:5173` (or `http://localhost:3000`).*

---

## 7. Default Credentials for Testing

| Role | Email | Password |
| :--- | :--- | :--- |
| **System Administrator** | `admin@healthai.local` | `Admin@HealthAI2026!` |
| **Regular User** | *Create any user via Sign Up* | *Must be 8+ chars with letters & numbers* |

---

## 8. REST API Documentation

### Authentication Endpoints
- `POST /api/auth/register` — Register a new account (`full_name`, `email`, `password`). Sets HttpOnly session cookie.
- `POST /api/auth/login` — Sign in with email and password. Rate-limited against brute force (5 attempts/15 min).
- `POST /api/auth/logout` — Invalidate server session and clear authentication cookies.
- `GET /api/auth/me` — Retrieve active session profile and CSRF token.
- `PUT /api/auth/profile` — Update name, email, or password (requires current password).
- `DELETE /api/auth/account` — Permanently delete user account and associated personal assessment records.
- `POST /api/auth/forgot-password` — Issue password reset token.
- `POST /api/auth/reset-password` — Consume reset token and assign new password.

### Clinical & Diagnostic Endpoints
- `GET /api/health` — **Public.** System and model readiness.
- `GET /api/symptoms` — **Public.** 131 standardized symptoms catalog.
- `POST /api/predict` — **Authenticated.** Perform Random Forest inference and log assessment under user ID.
- `GET /api/metrics` — **Public.** Held-out test evaluation scores (99.9% test accuracy) and confusion matrix.
- `GET /api/dashboard/stats` — Aggregate assessment statistics.
- `GET /api/history` — **Authenticated.** Retrieves user's private assessment history (or all records for admin if `view=all`).
- `POST /api/history/clear` — **Authenticated.** Clears personal records (or all records if admin).

### Administrator Endpoints
- `GET /api/admin/users` — **Admin only.** List all registered user accounts with assessment counts and statuses.
- `PUT /api/admin/users/<id>/status` — **Admin only.** Toggle active/suspended status or update user role.
- `DELETE /api/admin/users/<id>` — **Admin only.** Permanently delete a user account and their associated records.

---

## 9. Clinical & Regulatory Disclaimer

> **DISCLAIMER:**  
> This software is created for educational, research, and technical evaluation purposes only. It is **NOT** a certified medical diagnostic device and does **NOT** provide medical advice, diagnosis, or treatment. Never rely on the outputs of this software to self-medicate, alter medication dosages, or replace evaluation by a qualified medical professional. If you are experiencing sudden, severe, or life-threatening symptoms (e.g., chest pain, respiratory distress, loss of consciousness), immediately contact local emergency services (911 or 112).
