from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Asegura que la tabla usuarios tenga la columna must_change_password (legacy DB)'

    def handle(self, *args, **options):
        with connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='usuarios' AND COLUMN_NAME='must_change_password'")
            exists = cur.fetchone()[0]
            if exists:
                self.stdout.write(self.style.SUCCESS('La columna must_change_password ya existe.'))
                return
            self.stdout.write('Añadiendo columna must_change_password a usuarios...')
            cur.execute("ALTER TABLE usuarios ADD COLUMN must_change_password TINYINT(1) DEFAULT 0")
            self.stdout.write(self.style.SUCCESS('Columna must_change_password añadida.'))
