from django.shortcuts import render, get_object_or_404
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView, RetrieveAPIView
)
from rest_framework.views import APIView
from rest_framework import permissions, status, generics, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action


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

from .permissions import IsOwnerOrAdmin, IsAdminUserOnly

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


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        cart = serializer.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


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