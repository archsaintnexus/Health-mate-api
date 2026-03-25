from django.db import models
from accounts.models import CompanyUser


# This is the Providers table for customers to get doctors
class Provider(models.Model):
    full_name   = models.CharField(max_length=150)
    specialty   = models.CharField(max_length=100, db_index=True)
    location    = models.CharField(max_length=150, db_index=True)
    bio         = models.TextField(blank=True, null=True) # For the Specialist
    avatar_url  = models.CharField(max_length=300, blank=True, null=True)
    rating      = models.FloatField(default=0.0)
    years_exp   = models.IntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "providers"

    def __str__(self):
        return self.full_name



# This records when they will  be available, the schedules and the ones available for booking
class Availability(models.Model):
    provider    = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="availability")
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    is_booked   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "availability"
        unique_together = ("provider", "start_time")

    def __str__(self):
        return f"{self.provider.full_name} - {self.start_time}"




class Appointment(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    user        = models.ForeignKey(CompanyUser, on_delete=models.CASCADE, related_name="appointments")
    provider    = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="appointments") # This back_tracks to the appointments table to allow 2 way transmission
    slot        = models.OneToOneField(Availability, on_delete=models.CASCADE, related_name="appointment")
    reason      = models.CharField(max_length=500, blank=True, null=True)
    notes       = models.TextField(blank=True, null=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "appointments"

    def __str__(self):
        return f"{self.user.email} - {self.provider.full_name}"