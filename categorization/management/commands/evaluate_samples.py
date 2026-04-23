import json

from django.core.management.base import BaseCommand

from categorization.services.evaluation import evaluate_samples


class Command(BaseCommand):
    help = "Run the sample evaluation set against the current provider."

    def handle(self, *args, **options):
        self.stdout.write(json.dumps(evaluate_samples(), indent=2))
