import csv

from django.core.management.base import BaseCommand

from api.mock_data import CSV_COLUMNS
from api.models import Student


class Command(BaseCommand):
    help = (
        'Export student records with a known actual_result to a CSV file. '
        'Use this to close the feedback loop: database -> training data -> model.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='api/data/db_training_data.csv',
            help='Destination CSV path (relative to the project root).',
        )

    def handle(self, *args, **options):
        rows = (
            Student.objects.exclude(actual_result='')
            .select_related('course')
            .order_by('student_number')
        )

        output = options['output']
        count = 0
        with open(output, 'w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for student in rows:
                writer.writerow(
                    {
                        'student_number': student.student_number,
                        'full_name': student.full_name,
                        'email': student.email,
                        'course_code': student.course.code if student.course else '',
                        'study_hours': student.study_hours,
                        'attendance': student.attendance,
                        'previous_score': student.previous_score,
                        'actual_result': student.actual_result,
                    }
                )
                count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Exported {count} labelled students to {output}')
        )
