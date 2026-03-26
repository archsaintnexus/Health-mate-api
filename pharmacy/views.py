from django.shortcuts import render, get_object_or_404, redirect
import hashlib
import hmac
import json
from django.conf import settings
from django.utils import timezone


from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView, RetrieveAPIView
)
from rest_framework.views import APIView
from rest_framework import permissions, status, generics, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from drf_spectacular.utils import extend_schema_view, extend_schema

from .permissions import IsOwnerOrAdmin, IsAdminUserOnly

from .models import ( Cart,
    CartItem,
    OrderTrackingEvent,
    PharmacyCategory,
    PharmacyNotification,
    PharmacyOrder,
    PharmacyProduct)

from .serializers import (
    AddToCartSerializer,
    CartSerializer,
    CheckoutSerializer,
    PharmacyCategorySerializer,
    PharmacyNotificationSerializer,
    PharmacyOrderSerializer,
    PharmacyProductSerializer,
    UpdateCartItemSerializer,
    UpdateOrderStatusSerializer,
)
from .paystack import PaystackAPIError, initialize_transaction, verify_transaction



# Create your views here.


## Create CRUD for catagories
class PharmacyCategoryCreateListView(ListCreateAPIView):
    queryset = PharmacyCategory.objects.all()
    serializer_class = PharmacyCategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return []


class PharmacyCategoryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = PharmacyCategory.objects.all()
    serializer_class = PharmacyCategorySerializer
    permission_classes = [permissions.IsAdminUser]


## Create CRUD for  products
class PharmacyProductListCreateView(ListCreateAPIView):
    queryset = PharmacyProduct.objects.all()
    serializer_class = PharmacyProductSerializer
    permission_classes = [permissions.IsAdminUser]


class PharmacyProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = PharmacyProduct.objects.all()
    serializer_class = PharmacyProductSerializer
    permission_classes = [permissions.IsAdminUser]


# Pharmacy catalog
class PharmacyCatalogView(ListAPIView):
    queryset = PharmacyProduct.objects.filter(is_active=True)
    serializer_class = PharmacyProductSerializer
    permission_classes = [permissions.IsAuthenticated]


# Order creation

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)


@extend_schema_view(
    post=extend_schema(
        request= AddToCartSerializer,
        responses=CartSerializer
    )
)
class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        cart = serializer.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        request= UpdateCartItemSerializer,
        responses=CartSerializer
    )
)
class CartItemUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        serializer = UpdateCartItemSerializer(cart_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CartSerializer(cart_item.cart).data)

    def delete(self, request, pk):
        cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        cart = cart_item.cart
        cart_item.delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


@extend_schema_view( post=extend_schema(
                        request=CheckoutSerializer,
                        responses=PharmacyOrderSerializer
                    ))
class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(PharmacyOrderSerializer(order).data, status=status.HTTP_201_CREATED)




# Order  tracking
class MyOrderListView(generics.ListAPIView):
    serializer_class = PharmacyOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PharmacyOrder.objects.prefetch_related("items__product", "tracking_events").filter(
            user=self.request.user
        )


class MyOrderDetailView(generics.RetrieveAPIView):
    serializer_class = PharmacyOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PharmacyOrder.objects.prefetch_related("items__product", "tracking_events").all()
        return PharmacyOrder.objects.prefetch_related("items__product", "tracking_events").filter(
            user=self.request.user
        )


class OrderTrackingView(generics.RetrieveAPIView):
    serializer_class = PharmacyOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PharmacyOrder.objects.prefetch_related("tracking_events", "items__product").all()
        return PharmacyOrder.objects.prefetch_related("tracking_events", "items__product").filter(
            user=self.request.user
        )



class AdminOrderViewSet(viewsets.ModelViewSet):
    queryset = PharmacyOrder.objects.prefetch_related("items__product", "tracking_events").all()
    permission_classes = [permissions.IsAuthenticated, IsAdminUserOnly]

    def get_serializer_class(self):
        if self.action in ["partial_update", "update"]:
            return UpdateOrderStatusSerializer
        return PharmacyOrderSerializer

    @action(detail=True, methods=["patch"], url_path="update-status")
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PharmacyOrderSerializer(order).data)
    


# Payments
class InitializePaystackPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(PharmacyOrder, id=order_id, user=request.user)

        if order.payment_status == PharmacyOrder.PaymentStatus.PAID:
            return Response(
                {"detail": "This order has already been paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payer_email = order.email or getattr(request.user, "email", "")
        if not payer_email:
            return Response(
                {"detail": "An email address is required to initialize payment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            response_data = initialize_transaction(
                email=payer_email,
                amount=int(order.total_amount * 100),
                reference=order.payment_reference,
                callback_url=settings.PAYSTACK_CALLBACK_URL,
                channels=["card", "bank_transfer", "ussd"],
                metadata={
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "user_id": request.user.id,
                },
            )
        except PaystackAPIError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Payment initialized successfully.",
                "authorization_url": response_data.get("authorization_url"),
                "access_code": response_data.get("access_code"),
                "reference": response_data.get("reference"),
                "order": PharmacyOrderSerializer(order).data,
            },
            status=status.HTTP_200_OK,
        )


class VerifyPaystackPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(PharmacyOrder, id=order_id, user=request.user)
        reference = request.data.get("reference") or order.payment_reference

        try:
            payment_data = verify_transaction(reference)
        except PaystackAPIError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        gateway_status = payment_data.get("status")

        if gateway_status == "success":
            if order.payment_status != PharmacyOrder.PaymentStatus.PAID:
                order.payment_status = PharmacyOrder.PaymentStatus.PAID
                order.status = PharmacyOrder.Status.CONFIRMED
                order.save(update_fields=["payment_status", "status", "updated_at"])

                for item in order.items.select_related("product").all():
                    item.product.stock_quantity -= item.quantity
                    item.product.save(update_fields=["stock_quantity", "updated_at"])

                OrderTrackingEvent.objects.create(
                    order=order,
                    status=PharmacyOrder.Status.CONFIRMED,
                    title="Payment Confirmed",
                    note="Your payment was confirmed successfully.",
                    event_time=timezone.now(),
                )

                PharmacyNotification.objects.create(
                    user=order.user,
                    title="Payment Successful",
                    message=f"Payment for order {order.order_number} was confirmed successfully.",
                )

                cart = Cart.objects.filter(user=order.user).first()
                if cart:
                    cart.items.all().delete()

            return Response(
                {
                    "message": "Payment verified successfully.",
                    "gateway_status": gateway_status,
                    "order": PharmacyOrderSerializer(order).data,
                },
                status=status.HTTP_200_OK,
            )

        if gateway_status in ["failed", "abandoned", "reversed"]:
            order.payment_status = PharmacyOrder.PaymentStatus.FAILED
            order.save(update_fields=["payment_status", "updated_at"])

        return Response(
            {
                "message": "Payment not successful.",
                "gateway_status": gateway_status,
                "order": PharmacyOrderSerializer(order).data,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PaystackCallbackView(APIView):
    permission_classes = []

    def get(self, request):
        reference = request.query_params.get("reference")
        if not reference:
            return Response({"detail": "Missing reference."}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(PharmacyOrder, payment_reference=reference)

        try:
            payment_data = verify_transaction(reference)
        except PaystackAPIError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if payment_data.get("status") == "success":
            if order.payment_status != PharmacyOrder.PaymentStatus.PAID:
                order.payment_status = PharmacyOrder.PaymentStatus.PAID
                order.status = PharmacyOrder.Status.CONFIRMED
                order.save(update_fields=["payment_status", "status", "updated_at"])

                for item in order.items.select_related("product").all():
                    item.product.stock_quantity -= item.quantity
                    item.product.save(update_fields=["stock_quantity", "updated_at"])

                OrderTrackingEvent.objects.create(
                    order=order,
                    status=PharmacyOrder.Status.CONFIRMED,
                    title="Payment Confirmed",
                    note="Your payment was confirmed successfully.",
                    event_time=timezone.now(),
                )

                PharmacyNotification.objects.create(
                    user=order.user,
                    title="Payment Successful",
                    message=f"Payment for order {order.order_number} was confirmed successfully.",
                )

                cart = Cart.objects.filter(user=order.user).first()
                if cart:
                    cart.items.all().delete()

            return redirect(f"{settings.FRONTEND_ORDER_SUCCESS_URL}{order.id}")

        return redirect(f"{settings.FRONTEND_PAYMENT_FAILED_URL}{order.id}")


@method_decorator(csrf_exempt, name="dispatch")
class PaystackWebhookView(View):
    def post(self, request, *args, **kwargs):
        secret = settings.PAYSTACK_WEBHOOK_SECRET
        signature = request.headers.get("x-paystack-signature", "")

        if secret:
            computed = hmac.new(
                secret.encode("utf-8"),
                request.body,
                hashlib.sha512
            ).hexdigest()

            if computed != signature:
                return HttpResponse(status=400)

        payload = json.loads(request.body.decode("utf-8"))
        event = payload.get("event")
        data = payload.get("data", {})
        reference = data.get("reference")

        if not reference:
            return HttpResponse(status=200)

        try:
            order = PharmacyOrder.objects.get(payment_reference=reference)
        except PharmacyOrder.DoesNotExist:
            return HttpResponse(status=200)

        if event == "charge.success":
            if order.payment_status != PharmacyOrder.PaymentStatus.PAID:
                order.payment_status = PharmacyOrder.PaymentStatus.PAID
                order.status = PharmacyOrder.Status.CONFIRMED
                order.save(update_fields=["payment_status", "status", "updated_at"])

                for item in order.items.select_related("product").all():
                    item.product.stock_quantity -= item.quantity
                    item.product.save(update_fields=["stock_quantity", "updated_at"])

                OrderTrackingEvent.objects.create(
                    order=order,
                    status=PharmacyOrder.Status.CONFIRMED,
                    title="Payment Confirmed",
                    note="Your payment was confirmed via webhook.",
                    event_time=timezone.now(),
                )

                PharmacyNotification.objects.create(
                    user=order.user,
                    title="Payment Successful",
                    message=f"Payment for order {order.order_number} was confirmed.",
                )

                cart = Cart.objects.filter(user=order.user).first()
                if cart:
                    cart.items.all().delete()

        return HttpResponse(status=200)
    

class PharmacyNotificationListView(generics.ListAPIView):
    serializer_class = PharmacyNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PharmacyNotification.objects.filter(user=self.request.user)
    