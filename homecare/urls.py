from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminHomeCareRequestViewSet,
    AvailableHomeCareTimeSlotView,
    CancelHomeCareRequestView,
    HomeCareNotificationListView,
    HomeCareRequestCreateView,
    HomeCareServiceDetailView,
    HomeCareServiceListView,
    HomeCareTimeSlotListView,
    MyHomeCareRequestDetailView,
    MyHomeCareRequestListView,
)

router = DefaultRouter()
router.register(r"admin/requests", AdminHomeCareRequestViewSet, basename="admin-homecare-requests")

urlpatterns = [
    path("services/", HomeCareServiceListView.as_view(), name="homecare-services"),
    path("services/<int:pk>/", HomeCareServiceDetailView.as_view(), name="homecare-service-detail"),

    path("time-slots/", HomeCareTimeSlotListView.as_view(), name="homecare-time-slots"),
    path("available-slots/", AvailableHomeCareTimeSlotView.as_view(), name="homecare-available-slots"),

    path("requests/", HomeCareRequestCreateView.as_view(), name="homecare-request-create"),
    path("requests/list/", MyHomeCareRequestListView.as_view(), name="homecare-request-list"),
    path("requests/<int:pk>/", MyHomeCareRequestDetailView.as_view(), name="homecare-request-detail"),
    path("requests/<int:pk>/cancel/", CancelHomeCareRequestView.as_view(), name="homecare-request-cancel"),

    path("notifications/", HomeCareNotificationListView.as_view(), name="homecare-notifications"),

    path("", include(router.urls)),
]
