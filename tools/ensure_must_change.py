"""Script de ayuda: asegura que la tabla `usuarios` tenga la columna `must_change_password`.

Ejecuta: python tools\ensure_must_change.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

from django.db import connection

with connection.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='usuarios' AND COLUMN_NAME='must_change_password'")
    exists = cur.fetchone()[0]
    print('must_change_password exists?', bool(exists))
    if not exists:
        print('Adding column must_change_password to usuarios...')
        cur.execute("ALTER TABLE usuarios ADD COLUMN must_change_password TINYINT(1) DEFAULT 0")
        print('Column added')
    else:
        print('No action needed')
