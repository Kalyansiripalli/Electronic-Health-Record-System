from django.db import models
from account.models import User


class DoctorHospitalMapping(models.Model):
    user_id = models.IntegerField(default=0)
    hospital_id = models.IntegerField()

    def __str__(self):
        return str(self.user_id)


class HospitalList(models.Model):
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=10)
    category = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['name', 'pincode']]

    def __str__(self):
        return self.name


class PatientList(models.Model):
    name = models.CharField(max_length=255)
    aadhar_number = models.CharField(max_length=20, unique=True)
    # Storing doctor IDs as a comma-separated string
    assigned_to = models.CharField(max_length=255)

    def __str__(self):
        return self.name
