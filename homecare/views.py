from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions

from .models import HomeCareService, HomeCareRequest
from .permissions import IsOwnerOrAdmin
from .serializers import (
    HomeCareServiceSerializer,
    HomeCareRequestSerializer,
    HomeCareNotificationSerializer,
)


class HomeCareServiceListView(generics.ListAPIView):
    queryset = HomeCareService.objects.filter(is_active=True)
    serializer_class = HomeCareServiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class HomeCareRequestCreateView(generics.CreateAPIView):
    serializer_class = HomeCareRequestSerializer
    permission_classes = [permissions.IsAuthenticated]


class HomeCareRequestListView(generics.ListAPIView):
    serializer_class = HomeCareRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return HomeCareRequest.objects.select_related("service", "user").all()
        return HomeCareRequest.objects.select_related("service").filter(user=self.request.user)