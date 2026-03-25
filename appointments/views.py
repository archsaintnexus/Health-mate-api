from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Provider, Availability, Appointment
from .serializers import (
    ProviderSerializer,
    SlotSerializer,
    AppointmentCreateSerializer,
    AppointmentOutputSerializer
) # I will be using this to map with the views created here
from accounts.firebase import verify_id_token
from accounts.models import CompanyUser


class FirebaseAuthentication:
    #Reusable method to verify Firebase token and get user
    def get_user(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None, Response(
                {'detail': 'Invalid Authentication Credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        token = auth_header[len('Bearer '):] #I'm adding 'Bearer ' header to how the token is being verified here
        decoded = verify_id_token(token)
        if not decoded:
            return None, Response(
                {'detail': 'Invalid or expired token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        email = decoded.get('email')
        try:
            user = CompanyUser.objects.get(email=email)
            return user, None
        except CompanyUser.DoesNotExist:
            return None, Response(
                {'detail': 'User not found'},
                status=status.HTTP_401_UNAUTHORIZED
            )


# PROVIDER VIEWS, this uses restframework apiview
class ProviderSearchView(APIView):
    def get(self, request):
        specialty = request.query_params.get('specialty')
        location  = request.query_params.get('location')

        providers = Provider.objects.filter(is_active=True)
        if specialty:
            providers = providers.filter(specialty__icontains=specialty) # This filters and search if the specialty exists
        if location:
            providers = providers.filter(location__icontains=location)

        serializer = ProviderSerializer(providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProviderDetailView(APIView):
    def get(self, request, provider_id):
        try:
            provider = Provider.objects.get(id=provider_id, is_active=True)
        except Provider.DoesNotExist:
            return Response(
                {'detail': 'Provider not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProviderSerializer(provider)
        return Response(serializer.data, status=status.HTTP_200_OK)


#AVAILABILITY VIEWS 
class ProviderSlotsView(APIView):
    def get(self, request, provider_id):
        try:
            Provider.objects.get(id=provider_id, is_active=True) # This checks against the boolean values 
        except Provider.DoesNotExist:
            return Response(
                {'detail': 'Provider not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        slots = Availability.objects.filter(
            provider_id=provider_id,
            is_booked=False
        )
        serializer = SlotSerializer(slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# APPOINTMENT VIEWS 
class BookAppointmentView(FirebaseAuthentication, APIView):
    def post(self, request):
        user, error = self.get_user(request)
        if error:
            return error

        serializer = AppointmentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            with transaction.atomic():
                # Lock the slot
                slot = Availability.objects.select_for_update().get(
                    id=data['slot_id']
                )
                if slot.is_booked:
                    return Response(
                        {'detail': 'Slot is already booked'},
                        status=status.HTTP_409_CONFLICT
                    )

                slot.is_booked = True
                slot.save()

                appointment = Appointment.objects.create(
                    user=user,
                    provider_id=data['provider_id'],
                    slot=slot,
                    reason=data.get('reason'),
                    notes=data.get('notes'),
                )

        except Availability.DoesNotExist:
            return Response(
                {'detail': 'Slot not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        output = AppointmentOutputSerializer(appointment)
        return Response(output.data, status=status.HTTP_201_CREATED)


class MyAppointmentsView(FirebaseAuthentication, APIView):
    def get(self, request):
        user, error = self.get_user(request) # Allows the user to check for appointments they booked
        if error:
            return error

        appointments = Appointment.objects.filter(
            user=user
        ).select_related('provider', 'slot')

        serializer = AppointmentOutputSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AppointmentDetailView(FirebaseAuthentication, APIView):
    def get(self, request, appointment_id):
        user, error = self.get_user(request)
        if error:
            return error

        try:
            appointment = Appointment.objects.select_related(
                'provider', 'slot'
            ).get(id=appointment_id, user=user)
        except Appointment.DoesNotExist:
            return Response(
                {'detail': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AppointmentOutputSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)



# My delete endpoints
class CancelAppointmentView(FirebaseAuthentication, APIView):
    def delete(self, request, appointment_id):
        user, error = self.get_user(request)
        if error:
            return error

        try:
            appointment = Appointment.objects.select_related('slot').get(
                id=appointment_id,
                user=user
            )
        except Appointment.DoesNotExist:
            return Response(
                {'detail': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        appointment.status = 'cancelled'
        appointment.slot.is_booked = False
        appointment.slot.save()
        appointment.save()

        serializer = AppointmentOutputSerializer(appointment) # This uses the output serializer to map out what the appointment provides as response.
        return Response(serializer.data, status=status.HTTP_200_OK)