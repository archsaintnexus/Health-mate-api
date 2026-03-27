from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class HomeCareService(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class HomeCareTimeSlot(TimeStampedModel):
    service = models.ForeignKey(
        HomeCareService,
        on_delete=models.CASCADE,
        related_name="time_slots"
    )
    label = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_time"]
        unique_together = ("service", "label")

    def __str__(self):
        return f"{self.service.name} - {self.label}"


class HomeCareRequest(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="homecare_requests"
    )
    service = models.ForeignKey(
        HomeCareService,
        on_delete=models.PROTECT,
        related_name="requests"
    )
    time_slot = models.ForeignKey(
        HomeCareTimeSlot,
        on_delete=models.PROTECT,
        related_name="requests"
    )
    request_date = models.DateField()
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=30)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Home Care Request #{self.id}"


class HomeCareNotification(TimeStampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="homecare_notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    