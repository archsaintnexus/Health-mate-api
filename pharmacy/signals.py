from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PharmacyNotification, PharmacyOrder


@receiver(post_save, sender=PharmacyOrder)
def pharmacy_order_created_notification(sender, instance, created, **kwargs):
    if created:
        PharmacyNotification.objects.create(
            user=instance.user,
            title="Order Created",
            message=f"Your order {instance.order_number} has been created successfully."
        )
        