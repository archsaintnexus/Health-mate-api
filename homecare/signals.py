from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import HomeCareNotification, HomeCareRequest


@receiver(post_save, sender=HomeCareRequest)
def homecare_request_notification(sender, instance, created, **kwargs):
    if created:
        HomeCareNotification.objects.create(
            user=instance.user,
            title="Home Care Request Submitted",
            message=(
                f"Your request for {instance.service.name} on "
                f"{instance.request_date} ({instance.time_slot.label}) has been submitted."
            )
        )
        