# Guía de Recuperación de Contraseña

## Resumen de Implementación

Se ha implementado un sistema completo de recuperación de contraseña en el login con modales emergentes. El flujo es el siguiente:

### Paso 1: Acceder a la Recuperación
1. En la página de login (`http://127.0.0.1:8000/usuarios/login/`), hay un nuevo enlace que dice:
   **"¿Olvidaste tu contraseña? Recupérala"**
   
   Este enlace aparece **ANTES** de la opción "¿No tienes cuenta?"

### Paso 2: Modal 1 - Solicitar Usuario y Teléfono
Al hacer clic en el enlace, aparece un modal emergente que pide:
- **Usuario**: El nombre de usuario o email
- **Número de teléfono**: El número de teléfono asociado a la cuenta (siempre será: 75257525)

Después de completar los campos y presionar "Recuperar":
- Se verifica que el usuario exista en la base de datos
- Se muestra el siguiente modal

### Paso 3: Modal 2 - Verificar Código
Se muestra otro modal con los siguientes campos:
- **Código de 6 dígitos**: El código enviado al celular (valor predefinido: `QWE123`)
- **Nueva Contraseña**: La nueva contraseña que deseas establecer

Hay dos opciones:

#### Opción A: "Listo"
- Verifica el código
- Cambia la contraseña
- Muestra un mensaje de éxito
- Cierra el modal
- Recarga la página

#### Opción B: "Cambiar Contraseña"
- Verifica el código
- Cambia la contraseña
- Inicia sesión automáticamente con el nuevo usuario y contraseña
- Redirige a `http://127.0.0.1:8000/usuarios/perfil/`
- El usuario llega como si hubiera iniciado sesión normalmente
- Desde aquí, puede hacer clic en "Cambiar contraseña" (en el perfil) si lo desea

## Valores de Prueba

- **Código de verificación**: `QWE123` (6 dígitos)
- **Teléfono**: `75257525` (siempre será este número)

## Archivos Modificados

### Frontend (Templates)
- `templates/usuarios/login.html`: 
  - Agregado enlace de recuperación
  - Agregados dos modales emergentes
  - Agregado CSS para estilos de modales
  - Agregado JavaScript para manejar la lógica

### Backend (Python/Django)
- `usuarios/views.py`:
  - `recovery_verify()`: Verifica usuario y teléfono
  - `recovery_verify_code()`: Verifica código y cambia contraseña
  - `recovery_verify_code_only()`: Verifica solo el código (no usado en versión final)
  - `change_password_recovery()`: Cambia contraseña e inicia sesión

- `usuarios/urls.py`:
  - Rutas AJAX para las funciones de recuperación

## Flujo Técnico

1. Usuario hace clic en "¿Olvidaste tu contraseña? Recupérala"
2. Se abre Modal 1 (form para usuario y teléfono)
3. Envía datos a `/usuarios/recovery/verify/` (AJAX POST)
4. Si es válido, se abre Modal 2 (código + nueva contraseña)
5. Usuario ingresa código (QWE123) y contraseña
6. Si presiona "Listo":
   - Envía a `/usuarios/recovery/verify-code/`
   - Cambia la contraseña
   - Muestra éxito y recarga
7. Si presiona "Cambiar Contraseña":
   - Envía a `/usuarios/recovery/change-password-recovery/`
   - Cambia la contraseña
   - Inicia sesión automáticamente
   - Redirige a `/usuarios/perfil/`

## URLs Disponibles

- `POST /usuarios/recovery/verify/` - Verifica usuario y teléfono
- `POST /usuarios/recovery/verify-code/` - Verifica código y cambia contraseña
- `POST /usuarios/recovery/change-password-recovery/` - Cambia contraseña e inicia sesión

## Notas de Producción

Para llevar esto a producción:
1. Integrar servicio de SMS (Twilio, AWS SNS, etc.)
2. Generar código aleatorio de 6 dígitos en lugar de QWE123
3. Almacenar códigos en caché con expiración (5-10 minutos)
4. Verificar teléfono contra el registrado en BD
5. Agregar rate limiting para evitar fuerza bruta
6. Implementar logging y auditoría
