from django.shortcuts import render, redirect
import logging

logger = logging.getLogger(__name__)
from .models import Producto, Categoria
from .forms import ProductoForm
from django.contrib import messages
from django.db.models import Q
from usuarios.models import Usuario
from django.http import JsonResponse
from django.conf import settings
from django.templatetags.static import static
from django.contrib.auth.decorators import login_required
from .models import Notification, NotificationRead
from django.views.decorators.http import require_POST
from django.utils import timezone

def catalogo(request):
    """
    Vista del catálogo de productos con filtros por categoría y precio.
    """
    # Obtener todas las categorías para mostrar en el filtro
    categorias = Categoria.objects.all()

    # Obtener todos los productos
    productos = Producto.objects.all()

    # Filtrar por categoría si se pasa en GET
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    # Filtrar por término de búsqueda (nombre o descripción)
    q = request.GET.get('q')
    if q:
        q_clean = q.strip()
        if q_clean:
            # Buscar en nombre o descripción (case-insensitive)
            productos = productos.filter(Q(nombre__icontains=q_clean) | Q(descripcion__icontains=q_clean))

    # Filtrar por rango de precio si se pasa en GET
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    if precio_min and precio_max:
        try:
            productos = productos.filter(precio__gte=float(precio_min), precio__lte=float(precio_max))
        except ValueError:
            messages.error(request, "El rango de precios no es válido.")

    return render(request, "productos/catalogo.html", {
        "productos": productos,
        "categorias": categorias,
        "categoria_id": categoria_id,
        "q": q,
        "precio_min": precio_min,
        "precio_max": precio_max,
    })


def agregar_producto(request):
    """
    Vista para agregar un producto (solo administradores).
    """
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar con commit=False para setear campos adicionales
            producto = form.save(commit=False)
            # Si hay un usuario autenticado, intentar asignarlo como creador
            if request.user.is_authenticated:
                try:
                    usuario = Usuario.objects.filter(email__iexact=request.user.email).first()
                    if usuario:
                        producto.creado_por = usuario
                except Exception:
                    # no bloquear el guardado por errores al buscar usuario
                    pass
            producto.save()
            # Crear una notificación para este nuevo producto
            try:
                n = Notification.objects.create(producto=producto)
                logger.info(f"Notification created (id={n.id}) for producto id={producto.id} by view agregar_producto")
            except Exception:
                # No queremos romper el flujo si algo falla en las notificaciones
                logger.exception("Failed to create Notification in agregar_producto")
                pass
            messages.success(request, f"✅ '{producto.nombre}' agregado correctamente.")
            return redirect("catalogo")
        else:
                # Mostrar errores detallados para depuración
                err = form.errors.as_json() if hasattr(form.errors, 'as_json') else str(form.errors)
                messages.error(request, "Revisa los campos marcados en rojo. Errores: %s" % err)
    else:
        form = ProductoForm()

    return render(request, "productos/agregar_producto.html", {"form": form})


def ultimos_productos(request):
    """Devuelve JSON con los últimos N productos (por defecto 5)."""
    try:
        n = int(request.GET.get('n', 5))
    except ValueError:
        n = 5

    productos = Producto.objects.filter(estado='activo').order_by('-creado_en')[:n]
    data = []
    for p in productos:
        img = p.imagen.url if p.imagen else ''
        data.append({'id': p.id, 'nombre': p.nombre, 'precio': str(p.precio), 'imagen': img})

    return JsonResponse(data, safe=False)


def notifications_unread(request):
    """Devuelve notificaciones no leídas para el usuario autenticado.

    Si el usuario no está autenticado devolvemos una lista vacía (200) para
    simplificar el manejo en el frontend.
    """
    if not request.user.is_authenticated:
        logger.debug('notifications_unread called by anonymous user')
        return JsonResponse({'unread': []})

    user = request.user
    notifs = Notification.objects.order_by('-creado_en')[:20]
    unread = []
    for n in notifs:
        if not NotificationRead.objects.filter(notification=n, user=user).exists():
            unread.append({'id': n.id, 'producto': n.producto.nombre, 'creado_en': n.creado_en.isoformat(), 'producto_id': n.producto.id})
    unread_count = len(unread)
    logger.debug(f'notifications_unread for user={user.username} -> {unread_count} unread')
    return JsonResponse({'unread': unread, 'count': unread_count})


@require_POST
def mark_notification_read(request):
    """Marca una notificación como leída para el usuario autenticado.

    Acepta tanto form-encoded (`notification_id`) como JSON {notification_id}.
    Devuelve JSON {'ok': True, 'count': <unread_count>} cuando se marca.
    """
    if not request.user.is_authenticated:
        logger.debug('mark_notification_read called by anonymous user')
        return JsonResponse({'ok': False, 'error': 'not_authenticated'}, status=401)

    user = request.user
    # soportar body JSON además de form-encoded
    nid = request.POST.get('notification_id')
    if not nid:
        try:
            import json
            payload = json.loads(request.body.decode('utf-8') or '{}')
            nid = payload.get('notification_id')
        except Exception:
            nid = None

    if not nid:
        return JsonResponse({'ok': False, 'error': 'missing_notification_id'}, status=400)

    try:
        n = Notification.objects.get(id=nid)
    except Notification.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'not found'}, status=404)

    NotificationRead.objects.get_or_create(notification=n, user=user, defaults={'read_at': timezone.now()})
    logger.info(f'User {user.username} marked notification {n.id} as read')

    # contar no leídas restantes
    unread_count = Notification.objects.exclude(id__in=NotificationRead.objects.filter(user=user).values_list('notification_id', flat=True)).count()

    return JsonResponse({'ok': True, 'count': unread_count})


# --------- Cupones (Cliente) ---------
@login_required
def validar_cupon(request):
    """
    Valida un código de cupón y retorna la información del descuento.
    Endpoint AJAX que se llama al ingresar un código en el modal de cupones.
    """
    from .models import Cupon
    from django.utils import timezone
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        
        if not codigo:
            return JsonResponse({'valido': False, 'mensaje': 'Ingresa un código de cupón'})
        
        try:
            # Buscar cupón que esté activo y no eliminado
            cupon = Cupon.objects.get(
                codigo=codigo,
                estado='Activo',
                is_deleted=False
            )
            
            # Retornar información del cupón
            return JsonResponse({
                'valido': True,
                'codigo': cupon.codigo,
                'producto_id': cupon.producto.id,
                'producto_nombre': cupon.producto.nombre,
                'porcentaje_descuento': cupon.porcentaje_descuento,
                'precio_original': float(cupon.precio_original),
                'precio_con_descuento': float(cupon.precio_con_descuento),
                'cupon_id': cupon.id
            })
        except Cupon.DoesNotExist:
            return JsonResponse({
                'valido': False,
                'mensaje': 'CODIGO INCORRECTO'
            })
        except Exception as e:
            return JsonResponse({
                'valido': False,
                'mensaje': f'Error: {str(e)}'
            })
    
    return JsonResponse({'valido': False, 'mensaje': 'Método no permitido'})


@login_required
def canjear_cupon(request):
    """
    Canjea un cupón: registra el uso, asigna el usuario y actualiza el estado.
    """
    from .models import Cupon
    from django.utils import timezone
    
    if request.method == 'POST':
        cupon_id = request.POST.get('cupon_id')
        
        try:
            cupon = Cupon.objects.get(id=cupon_id, estado='Activo', is_deleted=False)
            
            # Actualizar el cupón
            cupon.estado = 'Desactivado'
            cupon.fecha_uso = timezone.now()
            
            # Obtener usuario (usuario autenticado)
            try:
                from usuarios.models import Usuario
                usuario = Usuario.objects.get(email=request.user.email)
                cupon.usuario = usuario
            except:
                # Si no existe en usuarios.Usuario, solo dejar el email
                pass
            
            cupon.save()
            
            return JsonResponse({
                'exito': True,
                'mensaje': 'Cupón canjeado exitosamente',
                'codigo': cupon.codigo
            })
        
        except Cupon.DoesNotExist:
            return JsonResponse({
                'exito': False,
                'mensaje': 'El cupón no es válido o ya fue utilizado'
            })
        except Exception as e:
            return JsonResponse({
                'exito': False,
                'mensaje': f'Error al canjear el cupón: {str(e)}'
            })
    
    return JsonResponse({'exito': False, 'mensaje': 'Método no permitido'})


def get_product_stock(request, product_id):
    """
    Endpoint AJAX que devuelve el stock actual de un producto.
    Útil para actualizar el inventario en tiempo real en el catálogo.
    """
    try:
        producto = Producto.objects.get(id=product_id)
        return JsonResponse({
            'exito': True,
            'producto_id': producto.id,
            'nombre': producto.nombre,
            'stock_actual': producto.stock_actual,
            'stock_minimo': producto.stock_minimo,
            'estado': 'agotado' if producto.stock_actual <= 0 else 'disponible'
        })
    except Producto.DoesNotExist:
        return JsonResponse({
            'exito': False,
            'mensaje': 'Producto no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'mensaje': f'Error: {str(e)}'
        }, status=500)
