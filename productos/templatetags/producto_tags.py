from django import template
from pathlib import Path
from django.conf import settings

register = template.Library()

# Mapeo de nombres de productos a imágenes estáticas
# Agrega aquí los productos que tengan imágenes en static/img/Imagenes/
PRODUCTO_IMAGENES = {
    'Alimento Perro Cachorro 2kg': 'img/Imagenes/Comida de cachorro .png',
    'Alimento Perro Adulto 3kg': 'img/Imagenes/Comida de perro adulto .png',
    'Alimento Gato Adulto 2kg': 'img/Imagenes/Comida de gato adulto .png',
    'Alimento Gato Senior 1.5kg': 'img/Imagenes/Comida de gato senior.png',
    'Snack Perro Hueso 500g': 'img/Imagenes/Snack perro hueso 500g.png',
    'Snack Gato 300g': 'img/Imagenes/snack gato 300g.png',
    'Alimento Pez Tropical 1kg': 'img/Imagenes/Alimento Pez tropical.png',
    'Pelota de Tenis Perro': 'img/Imagenes/Pelota de tenis para perro.png',
    'Ratón con Plumas': 'img/Imagenes/Raton con plumas.png',
    'Hueso de Goma Grande': 'img/Imagenes/Hueso de goma grande.png',
    'Juguete Interactivo Gato': 'img/Imagenes/Juguete interactivo gato.png',
    'Cuerda de Saltar Perro': 'img/Imagenes/Cuerda de saltar para perro .png',
    'Pluma con Varita': 'img/Imagenes/Pluma con varita para gato.png',
    'Pelota de Goma con Sonido': 'img/Imagenes/Pelota de goma con Sonida.png',
    'Cama Perro Pequeño': 'img/Imagenes/cama perro pequeño.jpg',
    'Collar Perro Pequeño': 'img/Imagenes/Collar perro Pequeño .png',
    'Arnés Gato': 'img/Imagenes/Arnes de Gato.png',
    'Comedero Perro Automático': 'img/Imagenes/Comedero Perro Automatico.png',
    'Bebedero Gato Automático': 'img/Imagenes/Bebedero Gato Automatico.png',
    'Correa Extensible Perro': 'img/Imagenes/Correa Extensible Perro .png',
    'Transportadora Gato Pequeña': 'img/Imagenes/Transportadora Gato Pequeña.png',
    'Antipulgas Perro': 'img/Imagenes/Antipulgas Perro .png',
    'Vitamina Gato Adulto': 'img/Imagenes/Vitamina Gato Adulto.png',
    'Shampoo Perro': 'img/Imagenes/Shampoo Perro.png',
    'Spray Calmante Gato': 'img/Imagenes/Spray Calmante Gato.png',
    'Pastillas Digestivas Perro': 'img/Imagenes/Pastillas Digestivas Perro.png',
    'Arena Gato Premium 15kg': 'img/Imagenes/Arena Gato Premium 15kg.png',
    'Cepillo Perro': 'img/Imagenes/Cepillo Perro.png',
    'Toallitas Higiénicas Gato': 'img/Imagenes/Toallitas Higienicas Gato .png',
    'Shampoo Gato': 'img/Imagenes/Shampoo Gato.png',
    'Desinfectante Jaulas': 'img/Imagenes/Desinfectante Jaulas.png',
    'Disfraz Pirata Perro': 'img/Imagenes/Disfraz Pirata Perro .png',
    'Disfraz Princesa Gato': 'img/Imagenes/Disfraz Princesa Gato .png',
    'Suéter Perro Invierno': 'img/Imagenes/Sueter Perro Invierno.png',
    'Transportadora Perro Mediano': 'img/Imagenes/Transportadora Perro Mediano.png',
    'Mochila Gato': 'img/Imagenes/Mochila Gato.png',
    'Clicker Básico': 'img/Imagenes/Clicker Basico.png',
    'Silbato Entrenamiento Perro': 'img/Imagenes/Silbato Entrenamiento Perro .png',
    'Alfombra Olfativa': 'img/Imagenes/Alfombra Olfativa.png',
    'Cono de Agilidad': 'img/Imagenes/Cono de agilidad .png',
    'Clicker Avanzado': 'img/Imagenes/Clicker Avanzado.png',
    'huesito de goma rojo': 'img/Imagenes/Huesito de goma rojo.png',
}


@register.filter
def get_imagen_producto(producto_nombre):
    """
    Filter que obtiene la ruta de la imagen estática para un producto.
    Uso en plantilla: {{ p.nombre|get_imagen_producto }}
    """
    ruta = PRODUCTO_IMAGENES.get(producto_nombre)
    
    if ruta:
        # Verificar que el archivo realmente exista
        archivo = Path(settings.BASE_DIR) / "static" / ruta
        if archivo.exists():
            return ruta
    
    return None
