from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"admin/orders", views.AdminOrderViewSet, basename="admin-orders")

app_name = "pharmacy"

urlpatterns = [
    path(
        "categories/",
        view=views.PharmacyCategoryCreateListView.as_view(),
        name="create-pharmacy-category",
    ),
    path(
        "categories/<int:pk>/",
        view=views.PharmacyCategoryDetailView.as_view(),
        name="detail-pharmacy-category",
    ),
    path(
        "products/",
        view=views.PharmacyProductListCreateView.as_view(),
        name="create-pharmacy-product",
    ),
    path(
        "products/<int:pk>/",
        view=views.PharmacyProductDetailView.as_view(),
        name="pharmacy-product-detail",
    ),
    path("catalog/", views.PharmacyCatalogView.as_view(), name="pharmacy-catalog"),
    path("cart/",views.CartView.as_view(), name="pharmacy-cart"),
    path("cart/add/", views.AddToCartView.as_view(), name="pharmacy-cart-add"),
    path("cart/items/<int:pk>/", views.CartItemUpdateDeleteView.as_view(), name="pharmacy-cart-item-update-delete"),

    path("checkout/", views.CheckoutView.as_view(), name="pharmacy-checkout"),

    path("orders/", views.MyOrderListView.as_view(), name="pharmacy-my-orders"),
    path("orders/<int:pk>/", views.MyOrderDetailView.as_view(), name="pharmacy-order-detail"),
    path("orders/<int:pk>/tracking/", views.OrderTrackingView.as_view(), name="pharmacy-order-tracking"),

    path("orders/<int:order_id>/paystack/initialize/", views.InitializePaystackPaymentView.as_view(), name="paystack-initialize"),
    path("orders/<int:order_id>/paystack/verify/", views.VerifyPaystackPaymentView.as_view(), name="paystack-verify"),
    path("payments/callback/", views.PaystackCallbackView.as_view(), name="paystack-callback"),
  

    path("notifications/", views.PharmacyNotificationListView.as_view(), name="pharmacy-notifications"),

    # path("", include(router.urls)),
]
