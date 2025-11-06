from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('stripe_session_id', 'status', 'amount_cents', 'currency', 'created_at')
    list_filter = ('status', 'currency')
    readonly_fields = ('created_at', 'updated_at')
