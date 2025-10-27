from django.contrib import admin
from .models import Notification, NotificationRead


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ('id', 'producto', 'creado_en')
	readonly_fields = ('creado_en',)


@admin.register(NotificationRead)
class NotificationReadAdmin(admin.ModelAdmin):
	list_display = ('notification', 'user', 'read_at')
	readonly_fields = ('read_at',)
