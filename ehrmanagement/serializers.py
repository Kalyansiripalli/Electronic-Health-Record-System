from rest_framework import serializers
from ehrmanagement.models import HospitalList, DoctorHospitalMapping, PatientList
from account.models import User
import random
import string
from ehrmanagement.models import DoctorHospitalMapping, PatientList


class AddHospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalList
        fields = ['name', 'phone_number',
                  'category', 'city', 'address', 'pincode']

    def validate(self, attrs):

        # raise error incase on non-numeric characters in phone number string
        if len(attrs.get('phone_number')) != 10 or not attrs.get('phone_number').isdigit():
            raise serializers.ValidationError(
                "Phone number must be a 10-digit number")

        # raise error incase on non-numeric characters in phone number string
        if len(attrs.get('pincode')) != 6 or not attrs.get('pincode').isdigit():
            raise serializers.ValidationError(
                "picode must be a 6-digit number")

        return attrs

    def create(self, validated_data):
        name = validated_data.pop('name', 'NA').lower()
        category = validated_data.pop('category', 'NA').lower()
        city = validated_data.pop('city', 'NA').lower()
        address = validated_data.pop('address', 'NA').lower()

        return HospitalList.objects.create(**validated_data, name=name, category=category, city=city, address=address)


class AddDoctorSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    hospitalId = serializers.IntegerField()

    def validate(self, attrs):

        # prevent multiple doctor entries
        if User.objects.filter(email=attrs.get('email').lower()).exists():
            raise serializers.ValidationError("email already exists")

        # we can add doctor to existing hospital only
        hospital_id = attrs.get('hospitalId')
        try:
            HospitalList.objects.get(pk=hospital_id).DoesNotExist
        except HospitalList.DoesNotExist:
            raise serializers.ValidationError(
                "Please ensure the current hospital exists before adding doctors.")

        return attrs

    def create(self, validated_data):

        password = self.context.get('password')

        # Create a new User instance for the doctor
        doctor = User.objects.create_user(
            name=validated_data['name'].lower(),
            email=validated_data['email'].lower(),
            role='doctor',
            password=password  # Assign the randomly generated password
        )
        doctor.is_active = True
        doctor.save()

        # Create DoctorHospitalMapping
        DoctorHospitalMapping.objects.create(
            userid=doctor.id, hospital_id=validated_data['hospitalId'])

        return doctor


class AddPatientsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    aadhar_number = serializers.CharField(max_length=20)
    assignedTo = serializers.ListField(child=serializers.IntegerField())

    def validate(self, data):
        if len(data.get('assignedTo')) == 0:
            raise serializers.ValidationError(
                "please provide assigned doctors")

        aadhar = data.get('aadhar_number')
        if len(aadhar) != 12 or not aadhar.isdigit():
            raise serializers.ValidationError(
                "Aadhar number must be 12 digit number")

        # check unique entry constraint using aadharnumber
        duplicateEntry = PatientList.objects.filter(
            aadhar_number=aadhar).first()

        if duplicateEntry:
            raise serializers.ValidationError(
                "patient has already been assigned with doctors")

        # getting all doctors list
        assigned_to_ids = data.get('assignedTo', [])
        if assigned_to_ids:
            # check all doctor's specified exist
            for doctor_id in assigned_to_ids:
                if not User.objects.filter(id=doctor_id, role='doctor').first():
                    raise serializers.ValidationError(
                        f"Invalid doctor-id provided: {doctor_id}")
            flag = 0
            # check all doctor's belongs to same hospital
            for doctor_id in assigned_to_ids:
                doctor = DoctorHospitalMapping.objects.filter(
                    userid=doctor_id).first()
                if flag == 0:
                    flag = doctor.hospital_id
                elif doctor.hospital_id != flag:
                    raise serializers.ValidationError(
                        "You can only assign doctors from the same hospital")
        return data

    def create(self, validated_data):
        assigned_to = validated_data.pop('assignedTo')
        patient = PatientList.objects.create(**validated_data)
        # Convert list of doctor IDs to comma-separated string
        patient.assigned_to = ','.join(map(str, assigned_to))
        patient.save()
        return patient


class DoctorSerializer(serializers.ModelSerializer):
    hospital_name = serializers.SerializerMethodField()
    hospital_address = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['name', 'email', 'hospital_name', 'hospital_address']

    def get_hospital_name(self, obj):
        # Query DoctorHospitalMapping to get the hospital_id for the doctor
        doctor_mapping = DoctorHospitalMapping.objects.filter(
            userid=obj.id).first()
        if doctor_mapping:
            # Query HospitalList to get the hospital name using hospital_id
            hospital = HospitalList.objects.filter(
                id=doctor_mapping.hospital_id).first()
            if hospital:
                return hospital.name
        return None

    def get_hospital_address(self, obj):
        # Query DoctorHospitalMapping to get the hospital_id for the doctor
        doctor_mapping = DoctorHospitalMapping.objects.filter(
            userid=obj.id).first()
        if doctor_mapping:
            # Query HospitalList to get the hospital address using hospital_id
            hospital = HospitalList.objects.filter(
                id=doctor_mapping.hospital_id).first()
            if hospital:
                return hospital.address
        return None


class HospitalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalList
        fields = ['name', 'phone_number',
                  'category', 'city', 'address', 'pincode']


class PatientListSerializer(serializers.ModelSerializer):
    assigned_to_names = serializers.SerializerMethodField()

    class Meta:
        model = PatientList
        fields = ['name', 'aadhar_number', 'assigned_to', 'assigned_to_names']

    def get_assigned_to_names(self, obj):
        # Splitting the assigned_to string into a list of doctor IDs
        assigned_to_ids = obj.assigned_to.split(',')
        doctors = User.objects.filter(id__in=assigned_to_ids)
        return [doctor.name for doctor in doctors]
