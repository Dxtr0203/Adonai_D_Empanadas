from django import forms
from django.core.exceptions import ValidationError
from .models import Producto, Categoria

MAX_IMG_MB = 2
ALLOWED_IMG_TYPES = {"image/jpeg", "image/png", "image/webp"}

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["categoria", "nombre", "descripcion", "precio", "stock_minimo", "stock_actual", "imagen"]
        widgets = {
            "categoria": forms.Select(attrs={"class": "form-select", "required": True}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "required": True, "minlength": 2, "maxlength": 120}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "maxlength": 500}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "required": True, "min": "0.1", "step": "0.01"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control", "required": True, "min": "0", "step": "1"}),
            "stock_actual": forms.NumberInput(attrs={"class": "form-control", "required": True, "min": "0", "step": "1"}),
            # Asegúrate de que el campo de imagen tenga las extensiones adecuadas
            "imagen": forms.FileInput(attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png,.webp"}),
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
        return data

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'maxlength': 100}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 500}),
        }