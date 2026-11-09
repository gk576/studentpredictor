from django.core.management.base import BaseCommand

from api.mock_data import DATA_PATH, write_csv


class Command(BaseCommand):
    help = 'Generate the deterministic mock student dataset (CSV).'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=320)
        parser.add_argument('--seed', type=int, default=42)

    def handle(self, *args, **options):
        path = write_csv(count=options['count'], seed=options['seed'])
        self.stdout.write(
            self.style.SUCCESS(
                f'Wrote {options["count"]} mock records to {path.relative_to(DATA_PATH.parents[2])}'
            )
        )
