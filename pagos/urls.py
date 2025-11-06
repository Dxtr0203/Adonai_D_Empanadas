from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('pago/exito/', views.pago_exito, name='pago_exito'),
    path('pago/error/', views.pago_error, name='pago_error'),
    path('pago/recibo/<str:session_id>/', views.recibo_pdf, name='recibo'),
]
