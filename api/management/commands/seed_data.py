import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from api.ml_logic import predict_student
from api.mock_data import COURSES, DATA_PATH, write_csv
from api.models import Course, PredictionRecord, Student

DEMO_USERNAME = 'demo'
DEMO_PASSWORD = 'demo12345'
DEMO_EMAIL = 'demo@example.edu'


class Command(BaseCommand):
    help = (
        'Create the demo user, sample courses and sample students, then attach '
        'an AI prediction to every student. Safe to run multiple times.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing demo students first.')

    def handle(self, *args, **options):
        User = get_user_model()

        if not DATA_PATH.exists():
            write_csv()
            self.stdout.write(self.style.WARNING('Mock dataset was missing; generated a fresh one.'))

        user, _ = User.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={'email': DEMO_EMAIL},
        )
        user.email = DEMO_EMAIL
        user.set_password(DEMO_PASSWORD)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        course_by_code = {}
        for course in COURSES:
            obj, _ = Course.objects.update_or_create(
                code=course['code'],
                defaults={'title': course['title'], 'credits': course['credits']},
            )
            course_by_code[obj.code] = obj

        if options['reset']:
            deleted, _ = Student.objects.filter(created_by=user).delete()
            self.stdout.write(f'Deleted {deleted} existing demo-related rows.')

        created = 0
        updated = 0
        with DATA_PATH.open(newline='', encoding='utf-8') as handle:
            for row in csv.DictReader(handle):
                result = predict_student(
                    row['study_hours'],
                    row['attendance'],
                    row['previous_score'],
                )

                defaults = {
                    'full_name': row['full_name'],
                    'email': row['email'],
                    'course': course_by_code.get(row['course_code']),
                    'study_hours': float(row['study_hours']),
                    'attendance': int(row['attendance']),
                    'previous_score': float(row['previous_score']),
                    'actual_result': row['actual_result'],
                    'prediction': result['prediction'],
                    'probability': result['probability'],
                    'confidence': result['confidence'],
                    'risk_level': result['risk_level'],
                    'created_by': user,
                }

                student, was_created = Student.objects.update_or_create(
                    student_number=row['student_number'],
                    defaults=defaults,
                )
                created += int(was_created)
                updated += int(not was_created)

                if not student.prediction_history.exists():
                    PredictionRecord.objects.create(
                        student=student,
                        study_hours=student.study_hours,
                        attendance=student.attendance,
                        previous_score=student.previous_score,
                        prediction=result['prediction'],
                        probability=result['probability'],
                        confidence=result['confidence'],
                        risk_level=result['risk_level'],
                        model_version=result['model_version'],
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Seed complete: {created} students created, {updated} updated. '
                f'Login with {DEMO_USERNAME} / {DEMO_PASSWORD}.'
            )
        )
