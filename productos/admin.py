from django.contrib import admin
from .models import Notification, NotificationRead, Cupon


from .models import Promotion
from django.utils import timezone


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ('id', 'producto', 'creado_en')
	readonly_fields = ('creado_en',)


@admin.register(NotificationRead)
class NotificationReadAdmin(admin.ModelAdmin):
	list_display = ('notification', 'user', 'read_at')
	readonly_fields = ('read_at',)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
	list_display = ('id', 'producto', 'status', 'discount_percent', 'promotion_end', 'creado_en')
	list_filter = ('status',)
	actions = ('approve_promotions', 'reject_promotions')
	readonly_fields = ('creado_en',)

	def approve_promotions(self, request, queryset):
		today = timezone.now().date()
		updated = queryset.update(status='approved', promotion_start=today)
		self.message_user(request, f"{updated} promoción(es) aprobada(s).")
	approve_promotions.short_description = 'Approve selected promotions'

	def reject_promotions(self, request, queryset):
		updated = queryset.update(status='rejected')
		self.message_user(request, f"{updated} promoción(es) rechazada(s).")
	reject_promotions.short_description = 'Reject selected promotions'


@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
	list_display = ('codigo', 'producto', 'porcentaje_descuento', 'estado', 'creado_en', 'usuario')
	list_filter = ('estado', 'creado_en', 'is_deleted')
	search_fields = ('codigo', 'producto__nombre')
	readonly_fields = ('codigo', 'creado_en', 'fecha_uso')
	
	fieldsets = (
		('Información del Cupón', {
			'fields': ('codigo', 'producto', 'porcentaje_descuento')
		}),
		('Precios', {
			'fields': ('precio_original', 'precio_con_descuento')
		}),
		('Estado y Uso', {
			'fields': ('estado', 'usuario', 'creado_en', 'fecha_uso')
		}),
		('Administración', {
			'fields': ('is_deleted',)
		}),
	)

