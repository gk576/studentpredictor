# EduPredict 

A local MVP web application that predicts whether a student is likely to pass
or fail a course, so that lecturers and personal tutors can prioritise support.


| | |
|---|---|
| **Frontend** | React 19 (Create React App), runs on `http://localhost:3000` |
| **Backend** | Django 6 + Django REST Framework, runs on `http://127.0.0.1:8000` |
| **Database** | SQLite 3 — a single local file (`db.sqlite3`) |
| **AI** | scikit-learn Random Forest binary classifier |
| **Auth** | JWT (SimpleJWT), local demo account |

---

## 1. Quick Start Guide

### Prerequisites

- Python 3.12 or newer
- Node.js 18 or newer
- PowerShell on Windows

### 1. Set up the project

Open PowerShell in the project root and run:

```powershell
.\setup_local.ps1
```

If PowerShell blocks the script, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup_local.ps1
```

### 2. Start the app

```powershell
.\run_local.ps1
```

This opens the Django API and React app in two PowerShell windows. You can also
double-click `run_local.bat`.

### 3. Open the app

| Service | URL |
|---|---|
| Web app | http://localhost:3000 |
| REST API | http://127.0.0.1:8000/api/ |
| Django admin | http://127.0.0.1:8000/admin/ |

**Demo login:** `demo` / `demo12345`

The demo account is a local superuser, so the same credentials open both the web app and
the Django admin.

### Manual setup

If you prefer to run each step yourself:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt

.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py generate_mock_data
.\venv\Scripts\python.exe manage.py train_model
.\venv\Scripts\python.exe manage.py seed_data

.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm start
```

---

## 2. What the app does

1. A tutor logs in with a username and password.
2. They add a student record with three AI input features:
   **weekly study hours**, **attendance %** and **previous assessment score %**.
3. The model immediately returns:
   - **Pass / Fail** prediction,
   - **pass probability** (0–1),
   - **confidence** (%), and
   - **risk level** (Low / Medium / High).
4. The prediction is saved with the student and an audit entry is written to
   `PredictionRecord`.
5. The dashboard shows pass/fail counts, high-risk students and live model metrics
   (accuracy, precision, recall, feature importance).
6. An **Instant AI check** panel runs a prediction without saving a student record.
7. Records can be edited (the model re-runs) or deleted.
8. Where the real outcome is known, the table highlights prediction mismatches so the
   model's errors are visible.
9. The Django admin provides a second view of the database tables for evidence.

Screenshots: [login](docs/screenshots/01-login.png),
[dashboard](docs/screenshots/02-dashboard.png),
[instant prediction](docs/screenshots/03-instant-prediction.png),
[admin student table](docs/screenshots/04-admin-students.png),
[admin prediction history](docs/screenshots/05-admin-predictions.png).

---

---

## 4. AI model at a glance

| Item | Value |
|---|---|
| Technique | Classification (binary) |
| Algorithm | `RandomForestClassifier` |
| Features | `study_hours`, `attendance`, `previous_score` |
| Target | `actual_result` → Pass / Fail |
| Dataset | 320 synthetic students (60% pass / 40% fail) |
| Split | 80% train (256) / 20% test (64), stratified |
| Preprocessing | median imputation + standard scaling in a `Pipeline` |
| Test accuracy | **79.7%** |
| Precision / recall | **77.8% / 92.1%** |
| Inference latency | ~61 ms mean per single prediction (local CPU) |

