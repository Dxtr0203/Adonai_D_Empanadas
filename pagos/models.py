from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    stripe_session_id = models.CharField(max_length=255, unique=True)
    amount_cents = models.PositiveIntegerField(default=1000)
    currency = models.CharField(max_length=10, default='usd')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    raw_event = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.stripe_session_id} ({self.get_status_display()})"
