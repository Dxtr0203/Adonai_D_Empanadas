from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
import json

from .models import Payment


def checkout_view(request):
    public_key = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    return render(request, 'pagos/checkout.html', {'stripe_public_key': public_key})


def create_checkout_session(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')

    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    domain = 'http://localhost:8000'
    # Leer el body JSON para obtener amount_cents (en centavos)
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        payload = {}

    amount_cents = payload.get('amount_cents')
    try:
        amount_cents = int(amount_cents) if amount_cents is not None else 1000
    except (ValueError, TypeError):
        return JsonResponse({'error': 'amount_cents inválido'}, status=400)

    # Simple validación para evitar montos negativos/excesivos (10,000 USD max)
    if amount_cents <= 0 or amount_cents > 1000000:
        return JsonResponse({'error': 'amount_cents fuera de rango'}, status=400)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Compra desde Adonai'},
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=domain + '/pago/exito/',
            cancel_url=domain + '/pago/error/',
        )

        # Guardar registro del pago (si la tabla existe)
        try:
            Payment.objects.create(stripe_session_id=session.id, amount_cents=amount_cents, currency='usd', status='created')
        except Exception:
            pass

        return JsonResponse({'id': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def pago_exito(request):
    return render(request, 'pagos/exito.html')


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
            except Payment.DoesNotExist:
                try:
                    Payment.objects.create(stripe_session_id=session_id, amount_cents=1000, currency='usd', status='paid', raw_event=json.dumps(event))
                except Exception:
                    pass

    return JsonResponse({'received': True})
