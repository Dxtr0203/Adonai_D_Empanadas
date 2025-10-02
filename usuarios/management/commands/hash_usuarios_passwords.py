# usuarios/management/commands/hash_usuarios_passwords.py
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password, identify_hasher
from usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Hashea contraseñas planas en usuarios.password si no están ya hasheadas'

    def handle(self, *args, **options):
        usuarios = Usuario.objects.all()
        updated = 0
        for u in usuarios:
            pwd = (u.password or '').strip()
            if not pwd:
                continue
            needs_hash = True
            try:
                # si identify_hasher no lanza excepción, ya estaba hasheada
                identify_hasher(pwd)
                needs_hash = False
            except Exception:
                needs_hash = True

            if needs_hash:
                u.password = make_password(pwd)
                u.save(update_fields=['password'])
                updated += 1
                self.stdout.write(self.style.SUCCESS(f'Hasheada: {u.email}'))
        self.stdout.write(self.style.SUCCESS(f'Completado. Contraseñas actualizadas: {updated}'))
