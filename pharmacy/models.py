from django.db import models
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField

# Create your models here.

User = get_user_model()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PharmacyCategory(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    image = CloudinaryField("image", folder="pharmacy/categories", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Pharmacy Categories"

    def __str__(self):
        return self.name


class PharmacyProduct(TimeStampedModel):
    category = models.ForeignKey(
        PharmacyCategory,
        on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=255)
    image = CloudinaryField("image",  blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    requires_prescription = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        # If an image is present, adjust its folder dynamically
        if self.image and self.category:
            # Cloudinary stores folder info in the field's options
            self.image.field.folder = f"pharmacy/categories/{self.category.slug}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PharmacyOrder(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pharmacy_orders"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    delivery_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id}"

    def recalculate_total(self):
        total = sum(item.line_total for item in self.items.all())
        self.total_amount = total or Decimal("0.00")
        self.save(update_fields=["total_amount", "updated_at"])


class PharmacyOrderItem(models.Model):
    order = models.ForeignKey(
        PharmacyOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        PharmacyProduct,
        on_delete=models.PROTECT,
        related_name="order_items"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class PharmacyNotification(TimeStampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pharmacy_notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title