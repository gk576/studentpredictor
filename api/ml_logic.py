from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / 'api' / 'data' / 'mock_students.csv'
ARTIFACT_DIR = ROOT_DIR / 'api' / 'ml_artifacts'
MODEL_PATH = ARTIFACT_DIR / 'student_pass_model.joblib'
METRICS_PATH = ARTIFACT_DIR / 'metrics.json'

FEATURES = ['study_hours', 'attendance', 'previous_score']
TARGET = 'actual_result'
RANDOM_STATE = 42
TEST_SIZE = 0.20


def _load_dataset(data_path: Path | None = None) -> pd.DataFrame:
    source = Path(data_path) if data_path else DATA_PATH
    if not source.exists():
        raise FileNotFoundError(
            f'Training data not found at {source}. '
            'Run "python manage.py seed_data" to create the mock dataset.'
        )

    df = pd.read_csv(source)

    required = set(FEATURES + [TARGET])
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f'Training data is missing columns: {sorted(missing)}')

    for column in ['study_hours', 'attendance', 'previous_score']:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    df = df.dropna(subset=FEATURES + [TARGET]).copy()
    df['study_hours'] = df['study_hours'].clip(lower=0, upper=168)
    df['attendance'] = df['attendance'].clip(lower=0, upper=100)
    df['previous_score'] = df['previous_score'].clip(lower=0, upper=100)
    df[TARGET] = df[TARGET].astype(str).str.strip().str.title()

    df = df[df[TARGET].isin(['Pass', 'Fail'])]
    return df


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
            (
                'classifier',
                RandomForestClassifier(
                    n_estimators=200,
                    max_depth=8,
                    min_samples_leaf=4,
                    class_weight='balanced',
                    random_state=RANDOM_STATE,
                    n_jobs=1,
                ),
            ),
        ]
    )


def _evaluate(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_pred = model.predict(X_test)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()

    return {
        'accuracy': round(float(accuracy_score(y_test, y_pred)) * 100, 1),
        'precision': round(float(precision_score(y_test, y_pred, zero_division=0)) * 100, 1),
        'recall': round(float(recall_score(y_test, y_pred, zero_division=0)) * 100, 1),
        'confusion_matrix': {
            'true_negative': int(tn),
            'false_positive': int(fp),
            'false_negative': int(fn),
            'true_positive': int(tp),
        },
        'test_samples': int(len(y_test)),
    }


def train_model(save_artifacts: bool = True, data_path: Path | None = None) -> dict:
    df = _load_dataset(data_path)
    X = df[FEATURES]
    y = (df[TARGET] == 'Pass').astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = build_pipeline()
    model.fit(X_train, y_train)
    metrics = _evaluate(model, X_test, y_test)

    classifier = model.named_steps['classifier']
    metrics.update(
        {
            'train_samples': int(len(y_train)),
            'dataset_samples': int(len(df)),
            'pass_rate': round(float(y.mean()) * 100, 1),
            'feature_importance': {
                name: round(float(score), 3)
                for name, score in zip(FEATURES, classifier.feature_importances_)
            },
            'model_version': datetime.now(timezone.utc).strftime('rf-v%Y%m%d%H%M%S'),
            'trained_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'algorithm': 'RandomForestClassifier (scikit-learn)',
            'data_source': (Path(data_path) if data_path else DATA_PATH).name,
        }
    )

    bundle = {'model': model, 'metrics': metrics, 'features': FEATURES}

    if save_artifacts:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(bundle, MODEL_PATH)
        METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding='utf-8')

    return bundle


_MODEL_CACHE = {'mtime': None, 'bundle': None}


def get_model_bundle() -> dict:
    if MODEL_PATH.exists():
        mtime = MODEL_PATH.stat().st_mtime
        if _MODEL_CACHE['mtime'] == mtime and _MODEL_CACHE['bundle'] is not None:
            return _MODEL_CACHE['bundle']
        try:
            bundle = joblib.load(MODEL_PATH)
            _MODEL_CACHE.update(mtime=mtime, bundle=bundle)
            return bundle
        except Exception:
            pass

    bundle = train_model(save_artifacts=True)
    _MODEL_CACHE.update(
        mtime=MODEL_PATH.stat().st_mtime if MODEL_PATH.exists() else None,
        bundle=bundle,
    )
    return bundle


def get_model_metrics() -> dict:
    return get_model_bundle()['metrics']


def predict_student(study_hours: float, attendance: float, previous_score: float) -> dict:
    try:
        study_hours = float(study_hours)
        attendance = float(attendance)
        previous_score = float(previous_score)
    except (TypeError, ValueError) as exc:
        raise ValueError('All inputs must be numeric.') from exc

    if not 0 <= study_hours <= 168:
        raise ValueError('Study hours must be between 0 and 168 per week.')
    if not 0 <= attendance <= 100:
        raise ValueError('Attendance must be between 0 and 100.')
    if not 0 <= previous_score <= 100:
        raise ValueError('Previous score must be between 0 and 100.')

    bundle = get_model_bundle()
    model: Pipeline = bundle['model']
    metrics = bundle['metrics']

    sample = pd.DataFrame(
        [[study_hours, attendance, previous_score]],
        columns=bundle['features'],
    )
    probabilities = model.predict_proba(sample)[0]
    classes = list(model.named_steps['classifier'].classes_)
    pass_probability = float(probabilities[classes.index(1)])
    prediction = 'Pass' if pass_probability >= 0.5 else 'Fail'

    if pass_probability >= 0.75:
        risk_level = 'Low'
    elif pass_probability >= 0.50:
        risk_level = 'Medium'
    else:
        risk_level = 'High'

    return {
        'prediction': prediction,
        'probability': round(pass_probability, 4),
        'confidence': round(max(pass_probability, 1 - pass_probability) * 100, 1),
        'risk_level': risk_level,
        'model_version': metrics['model_version'],
        'model_accuracy': metrics['accuracy'],
    }
