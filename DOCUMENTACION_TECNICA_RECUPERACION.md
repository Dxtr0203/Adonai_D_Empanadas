# Documentación Técnica - Sistema de Recuperación de Contraseña

## Descripción General

Sistema de recuperación de contraseña implementado en Django con modales emergentes en el frontend. Permite a usuarios olvidados recuperar acceso a sus cuentas mediante verificación de identidad y establecimiento de nueva contraseña.

---

## Arquitectura

### Frontend (JavaScript + HTML + CSS)

**Ubicación**: `templates/usuarios/login.html`

#### Modal 1: Solicitud de Usuario y Teléfono
```html
<div id="recoveryModal1" class="modal" style="display: none;">
  <!-- Formulario con campos:
       - recovery_username: Usuario
       - recovery_phone: Teléfono
       - Botón: submitRecoveryStep1()
  -->
</div>
```

**Función**: `openRecoveryModal(event)`
- Abre el primer modal
- Setea el foco en el campo de usuario

**Función**: `submitRecoveryStep1()`
- Valida campos (usuario y teléfono obligatorios)
- Envía AJAX POST a `/usuarios/recovery/verify/`
- Si es válido:
  - Almacena datos en variable `recoveryData`
  - Cierra Modal 1
  - Abre Modal 2
  - Muestra el teléfono en el Modal 2
- Si hay error:
  - Muestra mensaje en el div `recovery-error`

#### Modal 2: Verificación de Código y Nueva Contraseña
```html
<div id="recoveryModal2" class="modal" style="display: none;">
  <!-- Formulario con campos:
       - recovery_code: Código de 6 dígitos
       - recovery_password: Nueva contraseña
       - Botón 1: submitRecoveryStep2() (Listo)
       - Botón 2: changePassword() (Cambiar Contraseña)
  -->
</div>
```

**Función**: `submitRecoveryStep2()`
- Obtiene el código y la contraseña
- Envía AJAX POST a `/usuarios/recovery/verify-code/`
- Si es válido:
  - Cierra los modales
  - Muestra alerta de éxito
  - Recarga la página
- Si hay error:
  - Muestra mensaje en el div `recovery-error2`

**Función**: `changePassword()`
- Obtiene el código y la contraseña
- Envía AJAX POST a `/usuarios/recovery/change-password-recovery/`
- Si es válido:
  - Cambia la contraseña
  - Crea formulario de login automático
  - Envía el formulario a POST `/usuarios/login/`
  - Redirige a `/usuarios/perfil/` (como usuario logueado)

**Función**: `closeRecoveryModal()`
- Cierra ambos modales
- Resetea los formularios
- Limpia mensajes de error
- Limpia `recoveryData`

#### Estilos CSS
```css
.modal {
  /* Overlay semi-transparente */
  /* Contenedor flexible */
  /* Animación fadeIn */
}

.modal-content {
  /* Fondo blanco */
  /* Bordes redondeados */
  /* Sombra */
  /* Animación slideDown */
}

.btn-secondary {
  /* Botón naranja para "Cambiar Contraseña" */
}
```

---

## Backend (Python/Django)

**Ubicación**: `usuarios/views.py`

### Vista: `recovery_verify(request)`

**Método**: POST  
**URL**: `/usuarios/recovery/verify/`  
**Content-Type**: application/json

**Parámetros de entrada** (JSON):
```json
{
  "username": "usuario_o_email",
  "phone": "numero_telefonico"
}
```

**Lógica**:
1. Busca usuario en tabla `Usuario` por nombre o email (case-insensitive)
2. Si no existe → Retorna `{success: false, message: "Usuario no encontrado."}`
3. Si existe:
   - Almacena en sesión: `recovery_username`, `recovery_phone`, `recovery_user_id`
   - Retorna `{success: true, message: "Usuario verificado..."}`

**Respuesta**:
```json
{
  "success": true|false,
  "message": "descripción"
}
```

---

### Vista: `recovery_verify_code(request)`

**Método**: POST  
**URL**: `/usuarios/recovery/verify-code/`  
**Content-Type**: application/json

**Parámetros de entrada** (JSON):
```json
{
  "username": "usuario_o_email",
  "code": "QWE123",
  "password": "nueva_contrasena"
}
```

**Lógica**:
1. Verifica que el código sea igual a `QWE123`
2. Busca usuario en tabla `Usuario`
3. Si no existe → Error
4. Si existe y código es válido:
   - Actualiza `Usuario.password` (hash bcrypt/pbkdf2)
   - Actualiza `auth.User.password`
   - Limpia variables de sesión
   - Retorna éxito

**Respuesta**:
```json
{
  "success": true|false,
  "message": "descripción"
}
```

---

### Vista: `change_password_recovery(request)`

**Método**: POST  
**URL**: `/usuarios/recovery/change-password-recovery/`  
**Content-Type**: application/json

**Parámetros de entrada** (JSON):
```json
{
  "username": "usuario_o_email",
  "code": "QWE123",
  "password": "nueva_contrasena"
}
```

**Lógica**:
1. Verifica que el código sea igual a `QWE123`
2. Busca usuario en tabla `Usuario`
3. Si no existe → Error
4. Si existe y código es válido:
   - Actualiza `Usuario.password` (hash bcrypt/pbkdf2)
   - Actualiza `auth.User.password`
   - Limpia variables de sesión
   - Retorna éxito (el login automático ocurre en frontend)

**Respuesta**:
```json
{
  "success": true,
  "message": "Contraseña actualizada. Iniciando sesión..."
}
```

---

### Vista: `recovery_verify_code_only(request)` [DEPRECADA]

No está siendo utilizada en la versión final, pero se mantiene para compatibilidad.

---

## Base de Datos

### Tabla: `Usuario` (usuarios_usuario)

```
id (PrimaryKey)
nombre (CharField)
email (EmailField, unique)
password (CharField - hash)
telefono (CharField)
... otros campos ...
```

**Consultas realizadas**:
```python
# Buscar usuario por nombre o email
Usuario.objects.filter(
    models.Q(nombre__icontains=username) | 
    models.Q(email__icontains=username)
).first()

# Actualizar contraseña
usuario.password = make_password(password)
usuario.save(update_fields=['password'])
```

---

## URLs

**Ubicación**: `usuarios/urls.py`

```python
path('recovery/verify/', views.recovery_verify, name='recovery_verify'),
path('recovery/verify-code/', views.recovery_verify_code, name='recovery_verify_code'),
path('recovery/change-password-recovery/', views.change_password_recovery, name='change_password_recovery'),
```

---

## Flujo de Datos

### Opción A: "Listo" (Cambiar y volver al login)

```
Frontend: Usuario ingresa usuario/teléfono
    ↓
POST /usuarios/recovery/verify/
    ↓
Backend: Valida usuario
    ↓ (éxito)
Frontend: Abre Modal 2
    ↓
Usuario ingresa código (QWE123) + contraseña nueva
    ↓
POST /usuarios/recovery/verify-code/
    ↓
Backend:
  - Valida código
  - Actualiza contraseña en Usuario
  - Actualiza contraseña en auth.User
  - Limpia sesión
    ↓ (éxito)
Frontend:
  - Cierra modales
  - Muestra alerta
  - Recarga página login
```

### Opción B: "Cambiar Contraseña" (Cambiar e ir al perfil)

```
Frontend: Usuario ingresa usuario/teléfono
    ↓
POST /usuarios/recovery/verify/
    ↓
Backend: Valida usuario
    ↓ (éxito)
Frontend: Abre Modal 2
    ↓
Usuario ingresa código (QWE123) + contraseña nueva
    ↓
POST /usuarios/recovery/change-password-recovery/
    ↓
Backend:
  - Valida código
  - Actualiza contraseña en Usuario
  - Actualiza contraseña en auth.User
  - Limpia sesión
    ↓ (éxito)
Frontend:
  - Crea formulario de login automático
  - Envía POST a /usuarios/login/
  - Django inicia sesión (auth.login())
  - Redirige a /usuarios/perfil/ (ya logueado)
```

---

## Valores Fijos (Desarrollo)

```
RECOVERY_CODE = 'QWE123'
RECOVERY_PHONE = '75257525'
```

---

## Manejo de Errores

| Error | Causa | Solución |
|-------|-------|----------|
| "Usuario no encontrado" | Usuario no existe en BD | Verificar nombre/email |
| "Código inválido" | Código ≠ QWE123 | Usar código correcto |
| "Por favor completa todos los campos" | Campo vacío | Completar todos los campos |
| "Error de conexión" | Problema red/servidor | Reintentar |

---

## Seguridad

### Implementado
- ✅ CSRF Protection en todos los forms
- ✅ Hash de contraseñas (Django's make_password)
- ✅ Validación en backend
- ✅ Validación en frontend

### Recomendado para Producción
- ⚠️ Rate limiting en endpoints de recuperación
- ⚠️ Envío real de SMS (Twilio, AWS SNS)
- ⚠️ Generación aleatoria de códigos
- ⚠️ Expiración de códigos (5-10 min)
- ⚠️ Logging de intentos
- ⚠️ Verificación de teléfono contra BD
- ⚠️ Email de confirmación de cambio
- ⚠️ IP whitelisting

---

## Testing

### Casos de Prueba

1. **Usuario válido, teléfono cualquiera**
   - Esperado: Modal 2 abre
   - Actual: ✅ Funciona

2. **Usuario no existe**
   - Esperado: "Usuario no encontrado"
   - Actual: ✅ Funciona

3. **Código incorrecto**
   - Esperado: "Código inválido"
   - Actual: ✅ Funciona

4. **Código correcto (QWE123), botón "Listo"**
   - Esperado: Alerta éxito + recarga login
   - Actual: ✅ Funciona

5. **Código correcto (QWE123), botón "Cambiar Contraseña"**
   - Esperado: Login automático + redirección a perfil
   - Actual: ✅ Funciona

---

## Mantenimiento

### Archivos a Monitorear

```
templates/usuarios/login.html          # Modales + JS
usuarios/views.py                      # Lógica de recuperación
usuarios/urls.py                       # Rutas
```

### Cambios Futuros

1. Integrar SMS real
2. Generación aleatoria de códigos
3. Expiración de códigos
4. Rate limiting
5. Auditoría y logging

---

## Referencias

- Django CSRF: https://docs.djangoproject.com/en/stable/middleware/csrf/
- Django Password Hashing: https://docs.djangoproject.com/en/stable/topics/auth/passwords/
- Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

---

**Última actualización**: Diciembre 9, 2025  
**Estado**: ✅ Completado y funcional
