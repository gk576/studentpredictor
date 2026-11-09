from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / 'api' / 'data' / 'mock_students.csv'

COURSES = [
    {'code': 'CS101', 'title': 'BSc Computer Science', 'credits': 20},
    {'code': 'BUS201', 'title': 'BA Business Management', 'credits': 20},
    {'code': 'NUR101', 'title': 'BSc Nursing', 'credits': 20},
    {'code': 'ENG102', 'title': 'BEng Engineering', 'credits': 20},
]

FIRST_NAMES = [
    'Amelia', 'Noah', 'Olivia', 'Liam', 'Isla', 'Ethan', 'Ava', 'Mason',
    'Sophia', 'Lucas', 'Mia', 'Logan', 'Grace', 'James', 'Ella', 'Aiden',
    'Freya', 'Jacob', 'Chloe', 'Daniel', 'Ruby', 'Ryan', 'Alice', 'Owen',
    'Evie', 'Leo', 'Erin', 'Adam', 'Maya', 'Tom', 'Niamh', 'Sam',
]

LAST_NAMES = [
    'Smith', 'Jones', 'Taylor', 'Brown', 'Williams', 'Wilson', 'Johnson',
    'Davies', 'Robinson', 'Wright', 'Thompson', 'Evans', 'Walker', 'White',
    'Roberts', 'Green', 'Hall', 'Wood', 'Jackson', 'Clarke', 'Patel', 'Khan',
    'Murphy', 'Kelly',
]

CSV_COLUMNS = [
    'student_number',
    'full_name',
    'email',
    'course_code',
    'study_hours',
    'attendance',
    'previous_score',
    'actual_result',
]


def generate_rows(count: int = 320, seed: int = 42) -> list[dict]:
    rng = np.random.default_rng(seed)

    study_hours = np.clip(rng.gamma(shape=2.4, scale=3.8, size=count), 0.5, 28.0)
    attendance = np.clip(rng.normal(loc=76, scale=14, size=count), 35, 100)
    previous_score = np.clip(rng.normal(loc=62, scale=14, size=count), 25, 99)

    score = (
        0.45 * (previous_score / 100)
        + 0.35 * (attendance / 100)
        + 0.20 * np.clip(study_hours / 20, 0, 1)
    )

    passed = score >= 0.60
    noise_mask = rng.random(count) < 0.08
    passed[noise_mask] = ~passed[noise_mask]

    rows = []
    for index in range(count):
        first = FIRST_NAMES[index % len(FIRST_NAMES)]
        last = LAST_NAMES[(index // len(FIRST_NAMES)) % len(LAST_NAMES)]
        student_number = f'STU{index + 1:04d}'
        rows.append(
            {
                'student_number': student_number,
                'full_name': f'{first} {last}',
                'email': f'{first.lower()}.{last.lower()}{index + 1}@example.edu',
                'course_code': COURSES[index % len(COURSES)]['code'],
                'study_hours': round(float(study_hours[index]), 1),
                'attendance': int(round(float(attendance[index]))),
                'previous_score': round(float(previous_score[index]), 1),
                'actual_result': 'Pass' if bool(passed[index]) else 'Fail',
            }
        )

    return rows


def write_csv(path: Path = DATA_PATH, count: int = 320, seed: int = 42) -> Path:
    rows = generate_rows(count=count, seed=seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path
