# 📸 Mapeo de Imágenes de Productos

## Cómo Funciona

Las imágenes de los productos se cargan **automáticamente** desde `static/img/Imagenes/` sin necesidad de modificar la base de datos.

## Archivos Involucrados

- **`productos/templatetags/producto_tags.py`** - Contiene el mapeo de productos a imágenes
- **`templates/productos/catalogo.html`** - Usa el mapeo para cargar las imágenes

## Agregar una Nueva Imagen

Si quieres agregar una imagen para un producto:

### 1. Copia la imagen a `static/img/Imagenes/`
```bash
cp mi_imagen.png static/img/Imagenes/
```

### 2. Agrega el mapeo en `productos/templatetags/producto_tags.py`

Edita el diccionario `PRODUCTO_IMAGENES`:

```python
PRODUCTO_IMAGENES = {
    'Nombre del Producto': 'img/Imagenes/nombre_archivo.png',
    # ... más productos
}
```

**Importante**: El nombre del producto debe coincidir **exactamente** con el nombre en la BD.

### 3. Haz commit y push

```bash
git add static/img/Imagenes/
git add productos/templatetags/
git commit -m "✨ Agregar imagen para [Producto]"
git push
```

### 4. Tu compañero actualiza

```bash
git pull
```

¡Listo! Las imágenes se cargan automáticamente sin necesidad de migración ni cambios en la BD.

## Orden de Preferencia de Imágenes

La plantilla intenta cargar imágenes en este orden:

1. **Imagen estática** (`static/img/Imagenes/`) - Versionada en Git ✅
2. **Imagen en media** (`media/productos/`) - Subida dinámicamente
3. **Placeholder** - Si no hay imagen

## Ventajas

✅ **Sin cambios en BD** - No necesita migración  
✅ **Versionado en Git** - Las imágenes se sincronizan con el código  
✅ **Fallback automático** - Si no hay imagen estática, usa la que subió el usuario  
✅ **Simple y limpio** - Solo un archivo de configuración  

---

**Última actualización**: Diciembre 2025
