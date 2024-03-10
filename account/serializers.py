from rest_framework import serializers
from account.models import User
from ehrmanagement.models import DoctorHospitalMapping, HospitalList


class UserRegistrationSerializer(serializers.ModelSerializer):

    ConfirmPassword = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)
    role = serializers.CharField(max_length=100, write_only=True)
    is_admin = serializers.BooleanField(default=False, read_only=True)
    hospitalId = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'name', 'password',
                  'ConfirmPassword', 'role', 'is_admin', 'hospitalId']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_admin': {'read_only': True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hospitalId'].required = False

    def validate(self, attrs):
        print("kalyam")
        email = attrs.get('email').lower()
        print("kadaa")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("email already exists")

        password = attrs.get('password')
        ConfirmPassword = attrs.get('ConfirmPassword')
        if password != ConfirmPassword:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match")

        role = attrs.get('role').lower()

        if role != 'doctor' and role != 'admin':
            raise serializers.ValidationError(
                "role must be either admin or doctor")
        if role == 'doctor' and 'hospitalId' not in attrs:
            raise serializers.ValidationError(
                "Hospital ID is required for doctor role")
        if role == 'doctor':
            hospital_id = attrs.get('hospitalId')
            if not HospitalList.objects.filter(id=hospital_id).exists():
                raise serializers.ValidationError(
                    "Currently we don't offer services in this hospital. Please reach out to the admin to add this hospital.")

        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role', 'NA').lower()
        email = validated_data.pop('email', 'NA').lower()
        hospital_id = validated_data.pop('hospitalId', None)
        user = User.objects.create_user(
            **validated_data, email=email, role=role)

        if role == 'admin':
            user.is_admin = True
            user.save()

        # Create Doctor entry
        if role == 'doctor':
            DoctorHospitalMapping.objects.create(
                userid=user.id, hospital_id=hospital_id)

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                "Email and Password are required")

        return attrs
