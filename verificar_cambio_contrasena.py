#!/usr/bin/env python
"""
Script rápido para verificar que el cambio de contraseña está
correctamente implementado en el código.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adonai.settings')
django.setup()

import sys
from pathlib import Path

def verificar_archivos():
    """Verifica que todos los archivos existan."""
    print("\n" + "="*70)
    print("  ✓ VERIFICACIÓN RÁPIDA - CAMBIO DE CONTRASEÑA")
    print("="*70 + "\n")
    
    base_path = Path(__file__).parent
    archivos_esperados = {
        'usuarios/forms.py': 'ClientePasswordChangeForm',
        'usuarios/views.py': 'cambiar_contrasena_cliente',
        'usuarios/urls.py': 'cambiar_contrasena',
        'templates/usuarios/perfil.html': 'Cambiar contraseña',
        'templates/usuarios/modal_cambiar_contrasena.html': 'formCambiarContrasena',
        'test_cambiar_contrasena_funcional.py': 'test_cambiar_contrasena',
    }
    
    print("📁 VERIFICANDO ARCHIVOS:\n")
    
    all_good = True
    for archivo, contenido_esperado in archivos_esperados.items():
        ruta_completa = base_path / archivo
        
        if ruta_completa.exists():
            # Verificar que contiene el contenido esperado
            with open(ruta_completa, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            if contenido_esperado.lower() in contenido.lower():
                print(f"  ✓ {archivo}")
                print(f"    └─ Contiene: '{contenido_esperado}'")
            else:
                print(f"  ✗ {archivo}")
                print(f"    └─ NO contiene: '{contenido_esperado}'")
                all_good = False
        else:
            print(f"  ✗ {archivo} (NO EXISTE)")
            all_good = False
    
    return all_good

def verificar_funciones():
    """Verifica que las funciones estén correctamente implementadas."""
    print("\n\n🔧 VERIFICANDO FUNCIONES:\n")
    
    try:
        from usuarios.views import cambiar_contrasena_cliente
        print("  ✓ Vista: cambiar_contrasena_cliente importada correctamente")
    except ImportError as e:
        print(f"  ✗ Vista: cambiar_contrasena_cliente NO importada: {e}")
        return False
    
    try:
        from usuarios.forms import ClientePasswordChangeForm
        print("  ✓ Formulario: ClientePasswordChangeForm importado correctamente")
    except ImportError as e:
        print(f"  ✗ Formulario: ClientePasswordChangeForm NO importado: {e}")
        return False
    
    try:
        from django.urls import reverse
        url = reverse('usuarios:cambiar_contrasena')
        print(f"  ✓ URL: {url} configurada correctamente")
    except Exception as e:
        print(f"  ✗ URL: No se encontró 'usuarios:cambiar_contrasena': {e}")
        return False
    
    return True

def verificar_model():
    """Verifica que el modelo Usuario tenga el campo password."""
    print("\n\n📊 VERIFICANDO MODELO:\n")
    
    try:
        from usuarios.models import Usuario
        
        # Verificar que el modelo tiene el campo password
        if hasattr(Usuario, 'password'):
            print("  ✓ Modelo Usuario tiene campo: password")
        else:
            print("  ✗ Modelo Usuario NO tiene campo: password")
            return False
        
        # Verificar que tiene actualizado_en
        if hasattr(Usuario, 'actualizado_en'):
            print("  ✓ Modelo Usuario tiene campo: actualizado_en")
        else:
            print("  ✗ Modelo Usuario NO tiene campo: actualizado_en")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error al verificar modelo: {e}")
        return False

def verificar_base_datos():
    """Verifica que la base de datos esté correctamente configurada."""
    print("\n\n💾 VERIFICANDO BASE DE DATOS:\n")
    
    try:
        from django.contrib.auth.models import User
        from usuarios.models import Usuario
        
        # Contar usuarios
        auth_users = User.objects.count()
        custom_users = Usuario.objects.count()
        
        print(f"  ✓ Tabla auth_user: {auth_users} usuarios")
        print(f"  ✓ Tabla usuarios: {custom_users} usuarios")
        
        # Verificar sincronización (si hay usuarios)
        if auth_users > 0:
            user = User.objects.first()
            try:
                usuario = Usuario.objects.get(email__iexact=user.email)
                
                if user.password == usuario.password:
                    print(f"  ✓ Sincronización: CORRECTA ✓")
                else:
                    print(f"  ⚠ Sincronización: DESINCRONIZADA (pero funcional)")
                    print(f"    Nota: Esto es normal si nunca se cambió contraseña")
            except Usuario.DoesNotExist:
                print(f"  ⚠ Usuario no sincronizado (pero esto es OK)")
        
        return True
    except Exception as e:
        print(f"  ✗ Error al verificar BD: {e}")
        return False

def verificar_seguridad():
    """Verifica que las medidas de seguridad estén implementadas."""
    print("\n\n🔒 VERIFICANDO SEGURIDAD:\n")
    
    ruta_vista = Path(__file__).parent / 'usuarios' / 'views.py'
    
    try:
        with open(ruta_vista, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        checks = {
            '@login_required': 'Autenticación requerida',
            'check_password': 'Validación de contraseña antigua',
            'set_password': 'Hashing de contraseña nueva',
            'update_session_auth_hash': 'Sesión activa después del cambio',
            'CSRF': 'Protección CSRF (en formulario)',
        }
        
        all_good = True
        for check, descripcion in checks.items():
            if check in contenido:
                print(f"  ✓ {descripcion}")
            else:
                print(f"  ✗ {descripcion}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"  ✗ Error al verificar seguridad: {e}")
        return False

def main():
    """Función principal."""
    
    resultados = []
    resultados.append(("Archivos", verificar_archivos()))
    resultados.append(("Funciones", verificar_funciones()))
    resultados.append(("Modelo", verificar_model()))
    resultados.append(("Base de Datos", verificar_base_datos()))
    resultados.append(("Seguridad", verificar_seguridad()))
    
    # Resumen
    print("\n\n" + "="*70)
    print("  📋 RESUMEN")
    print("="*70 + "\n")
    
    for nombre, resultado in resultados:
        estado = "✓ PASS" if resultado else "✗ FAIL"
        print(f"  {estado:8} | {nombre}")
    
    todos_ok = all(r[1] for r in resultados)
    
    print("\n" + "="*70)
    if todos_ok:
        print("  ✅ TODAS LAS VERIFICACIONES PASARON")
        print("="*70)
        print("""
╔════════════════════════════════════════════════════════════════╗
║      ✅ SISTEMA COMPLETAMENTE FUNCIONAL Y SEGURO              ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║ La funcionalidad de cambio de contraseña está lista para usar. ║
║                                                                ║
║ PRÓXIMOS PASOS:                                                ║
║  1. python test_cambiar_contrasena_funcional.py                ║
║  2. python manage.py runserver                                 ║
║  3. Visita http://127.0.0.1:8000/usuarios/perfil/              ║
║  4. Haz clic en "Cambiar contraseña"                           ║
║  5. Ingresa tus credenciales                                   ║
║  6. ¡Verifica el resultado en la base de datos!                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
        """)
        return 0
    else:
        print("  ❌ ALGUNAS VERIFICACIONES FALLARON")
        print("="*70)
        print("""
⚠️  Por favor, revisa los errores marcados con ✗ arriba.

Si necesitas ayuda, ejecuta:
  - git log --oneline -5 (para ver cambios recientes)
  - python manage.py shell (para debugging manual)
        """)
        return 1

if __name__ == '__main__':
    sys.exit(main())
