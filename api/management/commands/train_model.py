import json
from pathlib import Path

from django.core.management.base import BaseCommand

from api.ml_logic import MODEL_PATH, train_model

DB_EXPORT_PATH = Path('api/data/db_training_data.csv')


class Command(BaseCommand):
    help = 'Train the Random Forest classifier, evaluate it and save model artifacts.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-db',
            action='store_true',
            help='Retrain from labelled Student rows in the database instead of the mock CSV.',
        )

    def handle(self, *args, **options):
        data_path = None
        if options['from_db']:
            from django.core.management import call_command

            call_command('export_training_data', output=str(DB_EXPORT_PATH))
            data_path = DB_EXPORT_PATH

        self.stdout.write('Loading data, preprocessing, training and evaluating...')
        bundle = train_model(save_artifacts=True, data_path=data_path)
        metrics = bundle['metrics']

        self.stdout.write(self.style.SUCCESS('Training complete.'))
        self.stdout.write(f'Model artifact: {MODEL_PATH}')
        self.stdout.write(
            json.dumps(
                {
                    'accuracy': metrics['accuracy'],
                    'precision': metrics['precision'],
                    'recall': metrics['recall'],
                    'confusion_matrix': metrics['confusion_matrix'],
                    'feature_importance': metrics['feature_importance'],
                    'dataset_samples': metrics['dataset_samples'],
                    'pass_rate': metrics['pass_rate'],
                    'data_source': metrics['data_source'],
                    'model_version': metrics['model_version'],
                },
                indent=2,
            )
        )
