from django.urls import path

from .views import (
    HomeCareServiceListView,
    HomeCareRequestCreateView,
    HomeCareRequestListView
)

urlpatterns = [
    path("services/", HomeCareServiceListView.as_view(), name="homecare-services"),
    path("requests/", HomeCareRequestCreateView.as_view(), name="homecare-request-create"),
    path("requests/list/", HomeCareRequestListView.as_view(), name="homecare-request-list"),

]
