from django.core.management.base import BaseCommand

from usuarios.models import Rol, Usuario


class Command(BaseCommand):
    help = 'Crea un rol y un usuario de prueba (prueba@example.com) para testing de la cola'

    def handle(self, *args, **options):
        rol, created = Rol.objects.get_or_create(nombre='Cliente', defaults={'descripcion': 'Rol por defecto'})
        if created:
            self.stdout.write(self.style.SUCCESS(f'Rol creado: {rol.id}'))
        else:
            self.stdout.write(self.style.NOTICE(f'Rol existente: {rol.id}'))

        user, created = Usuario.objects.get_or_create(
            email='prueba@example.com',
            defaults={
                'nombre': 'Prueba',
                'password': 'x',
                'rol': rol
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Usuario de prueba creado: id={user.id}, email={user.email}'))
        else:
            self.stdout.write(self.style.NOTICE(f'Usuario ya existe: id={user.id}, email={user.email}'))

        self.stdout.write('Ahora puedes ejecutar el test en shell o usar el usuario para llamadas API.')
