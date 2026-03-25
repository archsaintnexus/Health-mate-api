from decimal import Decimal

from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

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
    image = CloudinaryField("image", folder="pharmacy/products", blank=True, null=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    pack_size = models.CharField(max_length=100, blank=True, default="24 Tablets")
    strength = models.CharField(max_length=100, blank=True, default="500mg")
    stock_quantity = models.PositiveIntegerField(default=0)
    requires_prescription = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock_quantity > 0


class Cart(TimeStampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="pharmacy_cart"
    )

    def __str__(self):
        return f"{self.user} Cart"

    @property
    def subtotal(self):
        total = sum(item.line_total for item in self.items.select_related("product").all())
        return total or Decimal("0.00")

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        PharmacyProduct,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.product.price * self.quantity


class PharmacyOrder(TimeStampedModel):
    class DeliveryMethod(models.TextChoices):
        SHIP = "ship", "Ship"
        PICKUP = "pickup", "Pick Up"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pharmacy_orders"
    )
    order_number = models.CharField(max_length=30, unique=True)

    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=30)
    alternate_phone_number = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    delivery_method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.SHIP
    )
    delivery_address = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    order_instructions = models.TextField(blank=True)

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_reference = models.CharField(max_length=150, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    estimated_delivery_start = models.DateTimeField(null=True, blank=True)
    estimated_delivery_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.order_number}"

    def recalculate_total(self):
        subtotal = sum(item.line_total for item in self.items.all())
        self.subtotal = subtotal or Decimal("0.00")
        self.total_amount = (self.subtotal or Decimal("0.00")) + (self.shipping_fee or Decimal("0.00"))
        self.save(update_fields=["subtotal", "total_amount", "updated_at"])


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


class OrderTrackingEvent(TimeStampedModel):
    order = models.ForeignKey(
        PharmacyOrder,
        on_delete=models.CASCADE,
        related_name="tracking_events"
    )
    status = models.CharField(max_length=30, choices=PharmacyOrder.Status.choices)
    title = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    event_time = models.DateTimeField()

    class Meta:
        ordering = ["event_time"]

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


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