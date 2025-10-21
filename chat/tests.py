import json
from django.test import TestCase, Client
from django.urls import reverse


class ChatEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_send_message_requires_post(self):
        url = reverse('chat:send')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 405)

    def test_send_message_empty(self):
        url = reverse('chat:send')
        resp = self.client.post(url, data='{}', content_type='application/json')
        self.assertEqual(resp.status_code, 400)

    def test_send_message_greeting(self):
        url = reverse('chat:send')
        resp = self.client.post(url, data='{"message":"hola"}', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertTrue(payload.get('ok'))
        # reply should not be empty
        self.assertTrue(payload.get('reply'))

    def test_send_message_option_without_user(self):
        url = reverse('chat:send')
        data = { 'option': 'Consultar estado de pedido' }
        resp = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertTrue(payload.get('ok'))

    def test_products_and_top_sold(self):
        # Crear categoría y productos
        from productos.models import Categoria, Producto
        from ventas.models import Venta, VentaDetalle

        # Intentamos crear datos; si fallan (managed=False tables), la vista debe manejarlo y devolver ok
        created = True
        try:
            cat = Categoria.objects.create(nombre='Prueba')
            p1 = Producto.objects.create(categoria=cat, nombre='Prod A', precio=10, stock_actual=5, estado='activo')
            p2 = Producto.objects.create(categoria=cat, nombre='Prod B', precio=5, stock_actual=2, estado='activo')

            venta = Venta.objects.create(usuario_id=None, total=25, metodo_pago='Efectivo', estado='pagado')
            VentaDetalle.objects.create(venta=venta, producto=p1, cantidad=3, precio_unitario=10)
            VentaDetalle.objects.create(venta=venta, producto=p2, cantidad=1, precio_unitario=5)
        except Exception:
            created = False

        url = reverse('chat:send')
        resp = self.client.post(url, data=json.dumps({'message':'lo mas vendido'}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertTrue(payload.get('ok'))
        # Si no pudimos crear datos, el endpoint aún debe responder OK; si creamos, sugeridas debe contener algo
        if created:
            self.assertTrue(payload.get('suggested'))
from django.test import TestCase

# Create your tests here.
