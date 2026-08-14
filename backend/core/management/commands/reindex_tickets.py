from django.core.management.base import BaseCommand

from core.search.ticket_sync import reindex_all_tickets


class Command(BaseCommand):
    help = (
        "Rebuild the Elasticsearch tickets index " "from the current PostgreSQL data."
    )

    def handle(self, *args, **options):
        self.stdout.write("Rebuilding Elasticsearch ticket index...")

        indexed_count = reindex_all_tickets()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully indexed {indexed_count} tickets.")
        )
