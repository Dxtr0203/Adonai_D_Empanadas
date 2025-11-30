from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import stripe
import json
import io
import pytz
from decimal import Decimal, ROUND_HALF_UP

from .models import Payment
from productos.models import Producto, Inventario
from ventas.models import Venta, VentaDetalle

# Intentar importar reportlab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def create_venta_from_stripe_session(session_id, amount_bob):
    """
    Crea un registro de Venta y VentaDetalle a partir de una sesión de Stripe completada.
    Se ejecuta cuando el pago es exitoso para registrar la transacción en el dashboard.
    """
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    
    print(f"[CREATE VENTA] Iniciando creación de venta para session: {session_id}")
    
    try:
        # Obtener la sesión de Stripe
        stripe_session = stripe.checkout.Session.retrieve(session_id)
        
        # Obtener los items del carrito desde los metadatos
        cart_items = []
        if stripe_session.get('metadata', {}).get('cart_items'):
            try:
                cart_items = json.loads(stripe_session['metadata']['cart_items'])
                print(f"[CREATE VENTA] Items encontrados: {len(cart_items)} items")
            except Exception as e:
                print(f"[CREATE VENTA] Error parseando metadatos: {e}")
        
        if not cart_items:
            print(f"[CREATE VENTA] No hay items para crear venta")
            return None
        
        # Obtener usuario basado en el email de Stripe
        usuario = None
        customer_email = stripe_session.get('customer_details', {}).get('email')
        customer_name = stripe_session.get('customer_details', {}).get('name')
        
        if customer_email:
            from usuarios.models import Usuario, Rol
            try:
                # Intentar obtener usuario existente por email
                usuario = Usuario.objects.get(email=customer_email)
                print(f"[CREATE VENTA] Usuario encontrado: {usuario.nombre}")
            except Usuario.DoesNotExist:
                # Crear usuario automático si no existe
                print(f"[CREATE VENTA] Creando usuario automático para: {customer_email}")
                try:
                    # Obtener rol Cliente (o crear si no existe)
                    rol_cliente, _ = Rol.objects.get_or_create(nombre='Cliente')
                    
                    # Crear usuario con los datos de Stripe
                    nombre = customer_name or customer_email.split('@')[0]
                    usuario = Usuario.objects.create(
                        email=customer_email,
                        nombre=nombre,
                        rol=rol_cliente,
                        is_active=True
                    )
                    print(f"[CREATE VENTA] Usuario creado automáticamente: {usuario.nombre} ({usuario.email})")
                except Exception as e:
                    print(f"[CREATE VENTA] Error creando usuario automático: {e}")
                    usuario = None
        
        # Crear la Venta (con o sin usuario)
        total_venta = Decimal(str(amount_bob)) if amount_bob else Decimal('0')
        
        venta = Venta.objects.create(
            usuario=usuario,
            total=total_venta,
            metodo_pago='Stripe',
            estado='pagado',  # Siempre pagado porque viene del webhook exitoso
            creado_en=timezone.now()
        )
        
        print(f"[CREATE VENTA] Venta creada: ID={venta.id}, Total={total_venta}, Usuario={usuario.nombre if usuario else 'Anónimo'}")
        
        # Crear VentaDetalle para cada item
        for item in cart_items:
            try:
                product_id = item.get('id')
                product_name = item.get('nombre') or item.get('name')
                quantity = item.get('cantidad') or item.get('quantity', 1)
                price = Decimal(str(item.get('precio', 0)))
                
                # Obtener el producto
                if product_id:
                    producto = Producto.objects.get(id=product_id)
                else:
                    producto = Producto.objects.filter(nombre__icontains=product_name).first()
                
                if producto:
                    subtotal = price * quantity
                    detalle = VentaDetalle.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=quantity,
                        precio_unitario=price,
                        subtotal=subtotal
                    )
                    print(f"[CREATE VENTA] Detalle creado: {producto.nombre} x{quantity} = {subtotal}")
                else:
                    print(f"[CREATE VENTA] Producto no encontrado: {product_name}")
            except Exception as e:
                print(f"[CREATE VENTA] Error creando detalle: {e}")
        
        print(f"[CREATE VENTA] Venta registrada exitosamente: {venta.id}")
        return venta
        
    except Exception as e:
        print(f"[CREATE VENTA] Error en create_venta_from_stripe_session: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_payment_stock(session_id, data_object):
    """
    Procesa la actualización de stock cuando un pago se completa exitosamente.
    Reduce el stock de los productos en la compra y registra el movimiento en Inventario.
    Se ejecuta desde el webhook de Stripe.
    """
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    
    print(f"[WEBHOOK STOCK] Iniciando procesamiento de stock para session: {session_id}")
    
    try:
        # Obtener la sesión de Stripe
        stripe_session = stripe.checkout.Session.retrieve(session_id)
        
        # Obtener los items del carrito desde los metadatos
        cart_items = []
        if stripe_session.get('metadata', {}).get('cart_items'):
            try:
                cart_items = json.loads(stripe_session['metadata']['cart_items'])
                print(f"[WEBHOOK STOCK] Items encontrados en metadatos: {len(cart_items)} items")
            except Exception as e:
                print(f"[WEBHOOK STOCK] Error parseando metadatos: {e}")
        
        # Si no hay metadatos, intentar procesar desde los line items
        if not cart_items:
            print("[WEBHOOK STOCK] Intentando obtener items desde Stripe")
            try:
                li = stripe.checkout.Session.list_line_items(session_id)
                for item in li.data:
                    cart_items.append({
                        'id': getattr(item, 'id', None),
                        'quantity': getattr(item, 'quantity', 1),
                        'nombre': item.description or 'Producto desconocido'
                    })
                print(f"[WEBHOOK STOCK] Items obtenidos desde Stripe: {len(cart_items)} items")
            except Exception as e:
                print(f"[WEBHOOK STOCK] Error obteniendo items: {e}")
        
        if not cart_items:
            print(f"[WEBHOOK STOCK] No hay items para procesar")
            return
        
        # Procesar cada item: reducir stock y registrar en Inventario
        for item in cart_items:
            try:
                product_id = item.get('id')
                quantity = item.get('cantidad') or item.get('quantity', 1)
                product_name = item.get('nombre') or item.get('name')
                
                print(f"[WEBHOOK STOCK] Procesando: ID={product_id}, Nombre={product_name}, Cantidad={quantity}")
                
                # Si no tenemos ID del producto, intentar encontrarlo por nombre
                if not product_id:
                    producto = Producto.objects.filter(nombre__icontains=product_name).first()
                else:
                    producto = Producto.objects.get(id=product_id)
                
                if producto:
                    stock_anterior = producto.stock_actual
                    # Reducir el stock actual
                    producto.stock_actual = max(0, producto.stock_actual - quantity)
                    producto.save(update_fields=['stock_actual'])
                    
                    print(f"[WEBHOOK STOCK] {producto.nombre}: {stock_anterior} -> {producto.stock_actual}")
                    
                    # Registrar el movimiento en Inventario
                    Inventario.objects.create(
                        producto=producto,
                        cantidad=quantity,
                        tipo_movimiento='Salida',
                        observacion='Venta por compra online - Stripe (Webhook)',
                        referencia=session_id,
                        usuario=None  # Sistema automático
                    )
                    print(f"[WEBHOOK STOCK] Inventario registrado para {producto.nombre}")
                else:
                    print(f"[WEBHOOK STOCK] Producto no encontrado: ID={product_id}, Nombre={product_name}")
            except Producto.DoesNotExist:
                print(f"[WEBHOOK STOCK] Producto con ID {product_id} no existe")
            except Exception as e:
                print(f"[WEBHOOK STOCK] Error procesando item: {e}")
                pass
    
    except Exception as e:
        print(f"[WEBHOOK STOCK] Error en process_payment_stock: {e}")
        pass


def checkout_view(request):
    public_key = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    bob_to_usd = getattr(settings, 'STRIPE_BOB_TO_USD_RATE', 0.145)
    return render(request, 'pagos/checkout.html', {
        'stripe_public_key': public_key,
        'bob_to_usd': bob_to_usd
    })


def create_checkout_session(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')

    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    domain = 'http://localhost:8000'

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        payload = {}

    amount_bob = payload.get('amount_bob')
    cart_items = payload.get('cart_items', [])
    
    print(f"[CREATE SESSION] Creando sesión de checkout")
    print(f"[CREATE SESSION] Monto: {amount_bob} BOB")
    print(f"[CREATE SESSION] Items en carrito: {len(cart_items)}")
    if cart_items:
        print(f"[CREATE SESSION] Primer item: {cart_items[0]}")
    
    try:
        amount_bob = Decimal(str(amount_bob)) if amount_bob is not None else None
    except (ValueError, TypeError):
        return JsonResponse({'error': 'amount_bob inválido'}, status=400)

    if amount_bob is None:
        return JsonResponse({'error': 'amount_bob requerido'}, status=400)

    # Usar el monto exacto en BOB sin ajustes
    amount_cents = int(amount_bob * 100)

    if amount_cents <= 0 or amount_cents > 100000000:
        return JsonResponse({'error': 'amount fuera de rango'}, status=400)

    try:
        success_url = domain + '/pago/exito/?session_id={CHECKOUT_SESSION_ID}'
        
        # Serializar los items para guardar en metadatos
        cart_items_json = json.dumps(cart_items)
        print(f"[CREATE SESSION] JSON a enviar: {cart_items_json[:200]}...")
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'bob',  # Usar BOB directamente si Stripe lo permite
                    'product_data': {'name': 'Compra desde Adonai'},
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=domain + '/pago/error/',
            metadata={
                'cart_items': cart_items_json
            }
        )

        print(f"[CREATE SESSION] Sesión creada: {session.id}")

        try:
            Payment.objects.create(
                stripe_session_id=session.id,
                amount_cents=amount_cents,
                currency='bob',  # Usar BOB directamente
                status='created'
            )
        except Exception as e:
            print(f"[CREATE SESSION] Error creando Payment: {e}")
            pass

        return JsonResponse({'id': session.id})
    except Exception as e:
        print(f"[CREATE SESSION] Error creando sesión Stripe: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def process_payment_stock_from_session(session_id):
    """
    Procesa la actualización de stock desde un session_id de Stripe.
    Se ejecuta cuando el usuario llega a la página de éxito.
    """
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    
    try:
        # Obtener la sesión de Stripe
        stripe_session = stripe.checkout.Session.retrieve(session_id)
        
        # Obtener los items del carrito desde los metadatos
        cart_items = []
        if stripe_session.get('metadata', {}).get('cart_items'):
            try:
                cart_items = json.loads(stripe_session['metadata']['cart_items'])
                print(f"[STOCK] Items encontrados en metadatos: {len(cart_items)} items")
            except Exception as e:
                print(f"[STOCK] Error parseando metadatos: {e}")
        
        if not cart_items:
            print(f"[STOCK] No hay items en metadatos para session {session_id}")
            return
        
        # Procesar cada item: reducir stock y registrar en Inventario
        for item in cart_items:
            try:
                product_id = item.get('id')
                quantity = item.get('cantidad') or item.get('quantity', 1)
                product_name = item.get('nombre') or item.get('name')
                
                print(f"[STOCK] Procesando: ID={product_id}, Nombre={product_name}, Cantidad={quantity}")
                
                if not product_id:
                    print(f"[STOCK] Sin ID, buscando por nombre: {product_name}")
                    producto = Producto.objects.filter(nombre__icontains=product_name).first()
                else:
                    producto = Producto.objects.get(id=product_id)
                
                if producto:
                    # Stock anterior
                    stock_anterior = producto.stock_actual
                    
                    # Reducir el stock actual
                    producto.stock_actual = max(0, producto.stock_actual - quantity)
                    producto.save(update_fields=['stock_actual'])
                    
                    print(f"[STOCK] {producto.nombre}: {stock_anterior} -> {producto.stock_actual}")
                    
                    # Registrar el movimiento en Inventario
                    Inventario.objects.create(
                        producto=producto,
                        cantidad=quantity,
                        tipo_movimiento='Salida',
                        observacion='Venta por compra online - Stripe (Session: {})'.format(session_id),
                        referencia=session_id,
                        usuario=None  # Sistema automático
                    )
                    print(f"[STOCK] Inventario registrado para {producto.nombre}")
                else:
                    print(f"[STOCK] Producto no encontrado: ID={product_id}, Nombre={product_name}")
            except Producto.DoesNotExist:
                print(f"[STOCK] Producto con ID {product_id} no existe")
            except Exception as e:
                print(f"[STOCK] Error procesando item: {e}")
                pass
    
    except Exception as e:
        print(f"[STOCK] Error en process_payment_stock_from_session: {e}")
        pass


def pago_exito(request):
    session_id = request.GET.get('session_id')
    
    # Procesar el stock y crear venta cuando el usuario llega a la página de éxito
    if session_id:
        print(f"[EXITO] Procesando pago exitoso para session: {session_id}")
        # Procesar stock
        process_payment_stock_from_session(session_id)
        
        # Obtener cantidad y crear venta
        try:
            stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
            stripe_session = stripe.checkout.Session.retrieve(session_id)
            amount_bob = stripe_session.get('amount_total') or 0
            if amount_bob:
                amount_bob = Decimal(str(amount_bob)) / 100  # Convertir de centavos
            create_venta_from_stripe_session(session_id, amount_bob)
        except Exception as e:
            print(f"[EXITO] Error creando venta: {e}")
    
    return render(request, 'pagos/exito.html', {'session_id': session_id})


def pago_error(request):
    return render(request, 'pagos/error.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            event = json.loads(payload)
    except ValueError:
        return HttpResponseBadRequest('Invalid payload')
    except stripe.error.SignatureVerificationError:
        return HttpResponseBadRequest('Invalid signature')

    event_type = event.get('type') if isinstance(event, dict) else getattr(event, 'type', None)
    data_object = event.get('data', {}).get('object') if isinstance(event, dict) else None

    if event_type == 'checkout.session.completed' and data_object:
        session_id = data_object.get('id') if isinstance(data_object, dict) else None
        if session_id:
            try:
                p = Payment.objects.get(stripe_session_id=session_id)
                p.status = 'paid'
                p.raw_event = json.dumps(event)
                p.save()
                
                # Procesar la actualización de stock después del pago
                process_payment_stock(session_id, data_object)
                
                # Crear venta en el sistema
                try:
                    amount_bob = data_object.get('amount_total') or 0
                    if amount_bob:
                        amount_bob = Decimal(str(amount_bob)) / 100  # Convertir de centavos
                    create_venta_from_stripe_session(session_id, amount_bob)
                except Exception as e:
                    print(f"[WEBHOOK VENTA] Error creando venta: {e}")
            except Payment.DoesNotExist:
                try:
                    Payment.objects.create(
                        stripe_session_id=session_id,
                        amount_cents=1000,
                        currency='usd',
                        status='paid',
                        raw_event=json.dumps(event)
                    )
                    # Procesar la actualización de stock
                    process_payment_stock(session_id, data_object)
                    
                    # Crear venta en el sistema
                    try:
                        amount_bob = data_object.get('amount_total') or 0
                        if amount_bob:
                            amount_bob = Decimal(str(amount_bob)) / 100  # Convertir de centavos
                        create_venta_from_stripe_session(session_id, amount_bob)
                    except Exception as e:
                        print(f"[WEBHOOK VENTA] Error creando venta: {e}")
                except Exception:
                    pass

    return JsonResponse({'received': True})


def recibo_pdf(request, session_id: str):
    """Genera un PDF de recibo con hora local de Bolivia (BOT)."""
    payment = Payment.objects.filter(stripe_session_id=session_id).first()

    bolivia_tz = pytz.timezone('America/La_Paz')
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

    stripe_session = None
    line_items = []
    payment_method_desc = 'Desconocido'
    customer_name = None
    created_dt = timezone.now().astimezone(bolivia_tz)
    amount_cents = None
    currency = 'usd'
    USD_TO_BOB_RATE = Decimal('6.86')

    try:
        stripe_session = stripe.checkout.Session.retrieve(session_id)

        try:
            li = stripe.checkout.Session.list_line_items(session_id)
            for item in li.data:
                name = item.description or (getattr(item, 'description', None)
                                            or getattr(item, 'price', {}).get('product', 'Item'))
                qty = getattr(item, 'quantity', 1)
                line_items.append({
                    'name': name,
                    'quantity': qty,
                    'amount': getattr(item, 'amount_total', None)
                })
        except Exception:
            line_items = []

        pi = None
        try:
            pi_id = stripe_session.get('payment_intent')
            if pi_id:
                pi = stripe.PaymentIntent.retrieve(pi_id)
        except Exception:
            pi = None

        cust = stripe_session.get('customer_details') or {}
        customer_name = cust.get('name') or cust.get('email')

        # ✅ Convertir hora UTC a hora Bolivia
        ts = stripe_session.get('created')
        if ts:
            created_dt = timezone.datetime.fromtimestamp(int(ts), tz=pytz.UTC).astimezone(bolivia_tz)
        else:
            created_dt = timezone.now().astimezone(bolivia_tz)

        amt = stripe_session.get('amount_total') or stripe_session.get('amount_subtotal')
        if amt:
            amount_cents = int(amt)
        currency = stripe_session.get('currency') or currency

        if pi and pi.get('charges') and pi['charges']['data']:
            ch = pi['charges']['data'][0]
            pm = ch.get('payment_method_details', {})
            card = pm.get('card')
            if card:
                payment_method_desc = f"Tarjeta {card.get('brand', '').title()} ****{card.get('last4', '')}"
            else:
                payment_method_desc = ','.join(str(x) for x in stripe_session.get('payment_method_types', [])) or 'Desconocido'
        else:
            payment_method_desc = ','.join(str(x) for x in stripe_session.get('payment_method_types', [])) or 'Desconocido'
    except stripe.error.InvalidRequestError:
        stripe_session = None
    except Exception:
        stripe_session = None

    if not payment and not stripe_session:
        return HttpResponse('Recibo no encontrado', status=404)

    if payment:
        amount_cents = amount_cents or payment.amount_cents
        currency = payment.currency or currency
        if payment.created_at:
            created_dt = payment.created_at.astimezone(bolivia_tz)

    receipt_client = None
    if request.user and request.user.is_authenticated:
        receipt_client = getattr(request.user, 'nombre', None) or \
                         (request.user.get_full_name() if hasattr(request.user, 'get_full_name') else None) or \
                         getattr(request.user, 'username', None)
    receipt_client = receipt_client or customer_name or 'Cliente'

    receipt_items = []
    try:
        if stripe_session and stripe_session.get('metadata', {}).get('cart_items'):
            cart_data = json.loads(stripe_session['metadata']['cart_items'])
            for item in cart_data:
                name = item.get('name', 'Producto')
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                receipt_items.append({
                    'name': name,
                    'quantity': quantity,
                    'price_bob': price
                })
        elif line_items:
            for it in line_items:
                name = it.get('name', 'Producto')
                quantity = it.get('quantity', 1)
                amount = it.get('amount', 0)
                price_bob = Decimal(str(amount)) / 100 * USD_TO_BOB_RATE
                receipt_items.append({
                    'name': name,
                    'quantity': quantity,
                    'price_bob': price_bob
                })
    except Exception:
        receipt_items.append({
            'name': 'Compra desde Adonai',
            'quantity': 1,
            'price_bob': Decimal('0')
        })

    if not REPORTLAB_AVAILABLE:
        return HttpResponse('La generación de PDF requiere la librería reportlab. Instálala con: pip install reportlab', status=500)

    total_bob = Decimal('0')
    for item in receipt_items:
        total_bob += Decimal(str(item['price_bob'])) * Decimal(str(item['quantity']))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont('Helvetica-Bold', 16)
    p.drawString(40, height - 60, 'Recibo de Pago - Adonai')

    p.setFont('Helvetica', 11)
    p.drawString(40, height - 100, f'Cliente: {receipt_client}')
    p.drawString(40, height - 120, f'Número de transacción: {session_id}')

    # ✅ Mostrar hora Bolivia
    fecha_bolivia = created_dt.strftime("%d/%m/%Y %H:%M:%S")
    p.drawString(40, height - 140, f'Fecha: {fecha_bolivia} (BOT)')

    p.drawString(40, height - 170, 'Detalle de productos/servicios:')
    y = height - 190
    for item in receipt_items:
        name = item['name']
        quantity = item['quantity']
        price_bob = Decimal(str(item['price_bob']))
        subtotal = price_bob * Decimal(str(quantity))
        p.drawString(60, y, f'- {name} x {quantity}')
        p.drawString(300, y, f'BOB {subtotal:.2f}')
        y -= 20

    y -= 10
    p.setFont('Helvetica-Bold', 11)
    p.drawString(40, y, 'Monto total pagado:')
    p.drawString(300, y, f'BOB {total_bob:.2f}')
    if amount_cents:
        y -= 20
        usd_amount = amount_cents / 100
        p.drawString(300, y, f'USD {usd_amount:.2f}')

    y -= 20
    p.setFont('Helvetica', 11)
    p.drawString(40, y, f'Medio de pago: {payment_method_desc}')

    p.line(40, 120, width - 40, 120)
    p.setFont('Helvetica', 10)
    y = 100
    p.drawString(40, y, '¡Gracias por tu compra en Adonai!')
    y -= 15
    p.drawString(40, y, 'Valoramos tu preferencia y esperamos que disfrutes de nuestros productos.')
    y -= 15
    p.drawString(40, y, 'Este recibo es tu comprobante oficial de pago. Por favor, consérvalo para tus registros.')
    y -= 15
    p.setFont('Helvetica', 8)
    p.drawString(40, y, 'Aviso legal: Este documento es un comprobante de pago válido emitido por Adonai Delivery.')

    p.showPage()
    p.save()

    buffer.seek(0)
    filename = f'recibo_{session_id}.pdf'
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
