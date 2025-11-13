from django import forms
from django.core.exceptions import ValidationError
from .models import Producto, Categoria, Empleado
from django.forms import ModelForm
from .models import Promotion


class PromotionForm(ModelForm):
    class Meta:
        model = Promotion
        # Expose editable fields; producto shown but disabled in template
        fields = ['producto', 'tipo', 'discount_percent', 'recommended_reason', 'promotion_start', 'promotion_end', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make producto readonly in the form (show only)
        if 'producto' in self.fields:
            self.fields['producto'].disabled = True
        # Configure discount field to be integer-only in the form
        if 'discount_percent' in self.fields:
            self.fields['discount_percent'].widget.attrs.update({'step': '1'})

MAX_IMG_MB = 2
ALLOWED_IMG_TYPES = {"image/jpeg", "image/png", "image/webp"}

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["categoria", "nombre", "descripcion", "precio", "stock_minimo", "stock_actual", "imagen", "fecha_vencimiento"]
        widgets = {
            "categoria": forms.Select(attrs={"class": "form-select", "required": True}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "required": True, "minlength": 2, "maxlength": 120}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "maxlength": 500}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "required": True, "min": "0.1", "step": "0.01"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control", "required": True, "min": "0", "step": "1"}),
            "stock_actual": forms.NumberInput(attrs={"class": "form-control", "required": True, "min": "0", "step": "1"}),
            # Asegúrate de que el campo de imagen tenga las extensiones adecuadas
            "imagen": forms.FileInput(attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png,.webp"}),
            "fecha_vencimiento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if any(c in nombre for c in ["<", ">", "{", "}"]):
            raise ValidationError("El nombre contiene caracteres inválidos.")
        return nombre

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio is None or precio <= 0:
            raise ValidationError("El precio debe ser mayor a 0.")
        return precio

    def clean_stock_minimo(self):
        sm = self.cleaned_data["stock_minimo"]
        if sm is None or sm < 0:
            raise ValidationError("El stock mínimo no puede ser negativo.")
        return sm

    def clean_stock_actual(self):
        sa = self.cleaned_data["stock_actual"]
        if sa is None or sa < 0:
            raise ValidationError("El stock actual no puede ser negativo.")
        return sa

    def clean_imagen(self):
        img = self.cleaned_data.get("imagen")
        if not img:
            return img  # opcional (permitir sin imagen)
        # tipo mime
        if getattr(img, "content_type", None) not in ALLOWED_IMG_TYPES:
            raise ValidationError("Solo se permiten imágenes JPG/PNG/WEBP.")
        # tamaño
        size_mb = img.size / (1024 * 1024)
        if size_mb > MAX_IMG_MB:
            raise ValidationError(f"La imagen supera {MAX_IMG_MB} MB.")
        return img

    def clean(self):
        data = super().clean()
        sm = data.get("stock_minimo")
        sa = data.get("stock_actual")
        if sm is not None and sa is not None and sm > sa:
            # puedes hacer warning, pero mejor forzar
            self.add_error("stock_minimo", "El stock mínimo no puede ser mayor que el stock actual.")
        # Validación simple de fecha de vencimiento: si existe, puede ser futura o pasada según negocio
        # (Dejar sin validación estricta aquí; ajustar si se requiere que sea >= hoy)
        return data

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'maxlength': 100}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 500}),
        }

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'email', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'maxlength': 45}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 200}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) > 45:
            self.add_error('nombre', "El nombre no puede superar los 45 caracteres.")
        return nombre

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not email or '@' not in email:
            self.add_error('email', "Ingrese un correo electrónico válido.")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono'].strip()
        if not telefono.isdigit():
            self.add_error('telefono', "El teléfono debe contener solo números.")
        elif len(telefono) != 8:
            self.add_error('telefono', "El teléfono debe tener exactamente 8 dígitos.")
        elif not telefono.startswith(('6', '7')):
            self.add_error('telefono', "El teléfono debe comenzar con 6 o 7.")
        return telefono

    def clean_direccion(self):
        direccion = self.cleaned_data['direccion'].strip()
        if len(direccion) > 200:
            self.add_error('direccion', "La dirección no puede superar los 200 caracteres.")
        return direccion

    def clean(self):
        data = super().clean()
        # Add any additional cross-field validation here if needed
        return data
