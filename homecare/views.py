from datetime import date

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import mixins
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import (
    HomeCareNotification,
    HomeCareRequest,
    HomeCareService,
    HomeCareTimeSlot,
)
from .permissions import IsAdminUserOnly, IsOwnerOrAdmin
from .serializers import (
    CreateHomeCareRequestSerializer,
    HomeCareNotificationSerializer,
    HomeCareRequestSerializer,
    HomeCareServiceSerializer,
    HomeCareTimeSlotSerializer,
    UpdateHomeCareRequestStatusSerializer,
)


class HomeCareServiceListView(generics.ListAPIView):
    serializer_class = HomeCareServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = HomeCareService.objects.filter(is_active=True)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        return queryset


class HomeCareServiceDetailView(generics.RetrieveAPIView):
    queryset = HomeCareService.objects.filter(is_active=True)
    serializer_class = HomeCareServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    # lookup_field = "slug"



class HomeCareTimeSlotListView(generics.ListAPIView):
    serializer_class = HomeCareTimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

 
    def get_queryset(self):
        queryset = HomeCareTimeSlot.objects.select_related("service").filter(
            is_active=True,
            service__is_active=True,
        )

        service_id = self.request.query_params.get("service")
        if service_id:
            queryset = queryset.filter(service_id=service_id)

        return queryset



class AvailableHomeCareTimeSlotView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    @extend_schema(
        summary="Get available home care time slots",
        description="Returns available time slots for a given service and date.",
        parameters=[
            OpenApiParameter(
                name="service",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Home care service ID",
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Requested booking date in YYYY-MM-DD format",
            ),
        ],
        responses={200: HomeCareTimeSlotSerializer(many=True)},
    )
    def get(self, request):
        service_id = request.query_params.get("service")
        request_date = request.query_params.get("date")

        if not service_id:
            return Response(
                {"detail": "service query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request_date:
            return Response(
                {"detail": "date query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        slots = HomeCareTimeSlot.objects.select_related("service").filter(
            service_id=service_id,
            is_active=True,
            service__is_active=True,
        )

        booked_slot_ids = HomeCareRequest.objects.filter(
            service_id=service_id,
            request_date=request_date,
            status__in=[
                HomeCareRequest.Status.PENDING,
                HomeCareRequest.Status.CONFIRMED,
                HomeCareRequest.Status.IN_PROGRESS,
            ],
        ).values_list("time_slot_id", flat=True)

        available_slots = slots.exclude(id__in=booked_slot_ids)
        serializer = HomeCareTimeSlotSerializer(available_slots, many=True)
        return Response(serializer.data)


@extend_schema_view(post=extend_schema(
            request=CreateHomeCareRequestSerializer,
            responses=HomeCareRequestSerializer
    ))
class HomeCareRequestCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def post(self, request):
        serializer = CreateHomeCareRequestSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        homecare_request = serializer.save()
        return Response(
            HomeCareRequestSerializer(homecare_request).data,
            status=status.HTTP_201_CREATED,
        )


class MyHomeCareRequestListView(generics.ListAPIView):
    serializer_class = HomeCareRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HomeCareRequest.objects.select_related("service", "time_slot").filter(
            user=self.request.user
        )


class MyHomeCareRequestDetailView(generics.RetrieveAPIView):
    serializer_class = HomeCareRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return HomeCareRequest.objects.select_related("service", "time_slot", "user").all()
        return HomeCareRequest.objects.select_related("service", "time_slot").filter(
            user=self.request.user
        )


class CancelHomeCareRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        homecare_request = get_object_or_404(
            HomeCareRequest,
            pk=pk,
            user=request.user
        )

        if homecare_request.status in [
            HomeCareRequest.Status.COMPLETED,
            HomeCareRequest.Status.CANCELLED,
        ]:
            return Response(
                {"detail": "This request cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        homecare_request.status = HomeCareRequest.Status.CANCELLED
        homecare_request.save(update_fields=["status", "updated_at"])

        return Response(HomeCareRequestSerializer(homecare_request).data)


class HomeCareNotificationListView(generics.ListAPIView):
    serializer_class = HomeCareNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HomeCareNotification.objects.filter(user=self.request.user)


class AdminHomeCareRequestViewSet(mixins.RetrieveModelMixin,
                                  mixins.ListModelMixin,
                                    viewsets.GenericViewSet):
    queryset = HomeCareRequest.objects.select_related("service", "time_slot", "user").all()
    permission_classes = [permissions.IsAuthenticated, IsAdminUserOnly]

    def get_serializer_class(self):
        if self.action in ["partial_update", "update"]:
            return UpdateHomeCareRequestStatusSerializer
        return HomeCareRequestSerializer

    @action(detail=True, methods=["patch"], url_path="update-status")
    def update_status(self, request, pk=None):
        homecare_request = self.get_object()
        serializer = UpdateHomeCareRequestStatusSerializer(
            homecare_request,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(HomeCareRequestSerializer(homecare_request).data)