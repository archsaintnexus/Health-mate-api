from rest_framework import serializers
from .models import Provider, Availability, Appointment



# This is the Serializer to validate schemas against Django field translators
class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = [
            'id', 'full_name', 'specialty', 'location',
            'bio', 'avatar_url', 'rating', 'years_exp', 'is_active'
        ]


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['id', 'provider_id', 'start_time', 'end_time', 'is_booked']


class AppointmentCreateSerializer(serializers.Serializer):
    provider_id = serializers.IntegerField()
    slot_id     = serializers.IntegerField()
    reason      = serializers.CharField(required=False, allow_null=True) # This isn't necessary by default for me.
    notes       = serializers.CharField(required=False, allow_null=True)


# Django actually automatically reads my ORM values against it's serializers, lol, kinda disciplined.
class AppointmentOutputSerializer(serializers.ModelSerializer):
    provider = ProviderSerializer(read_only=True)
    slot     = SlotSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'user_id', 'provider_id', 'slot_id',
            'reason', 'notes', 'status', 'created_at',
            'provider', 'slot'
        ]