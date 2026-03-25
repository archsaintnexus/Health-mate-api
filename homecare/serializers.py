from rest_framework import serializers

from .models import HomeCareService, HomeCareRequest, HomeCareNotification


class HomeCareServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeCareService
        fields = ["id", "name", "description", "price", "is_active"]


class HomeCareRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeCareRequest
        fields = [
            "id",
            "service",
            "preferred_time",
            "address",
            "phone_number",
            "status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        return HomeCareRequest.objects.create(user=request.user, **validated_data)


class HomeCareNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeCareNotification
        fields = ["id", "title", "message", "is_read", "created_at"]