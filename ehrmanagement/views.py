from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .renderers import EhrRenderer
from .serializers import AddHospitalSerializer, AddDoctorSerializer, AddPatientsSerializer, DoctorSerializer, HospitalListSerializer, PatientListSerializer
from rest_framework.permissions import IsAuthenticated
from account.models import User
from ehrmanagement.models import HospitalList, PatientList
from .permissions import IsAdminUser
import random
import string
from django.core.mail import send_mail


class AddHospitalView(APIView):
    renderer_classes = [EhrRenderer]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, format=None):
        serializer = AddHospitalSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Hospital added successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddDoctorView(APIView):
    renderer_classes = [EhrRenderer]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, format=None):
        password = ''.join(random.choices(
            string.ascii_letters + string.digits, k=8))
        
        serializer = AddDoctorSerializer(
            data=request.data, context={'request': request,'password': password})

        if serializer.is_valid():
            email = serializer.validated_data['email']
            data=serializer.save()
            send_mail(
                "Your profile has been created by the admin",
                f"your password: {password}",
                "verificmail999@gmail.com",
                [email],
                fail_silently=False,
            )

            return Response({'msg': 'doctor added successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddPatientsView(APIView):
    renderer_classes = [EhrRenderer]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, format=None):
        serializer = AddPatientsSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Patient added and has been assigned to a doctor succesfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllDoctorsView(generics.ListAPIView):
    queryset = User.objects.filter(role='doctor')
    serializer_class = DoctorSerializer


class AllHospitalsView(generics.ListAPIView):
    queryset = HospitalList.objects.all()
    serializer_class = HospitalListSerializer


class AllPatientView(generics.ListAPIView):
    queryset = PatientList.objects.all()
    serializer_class = PatientListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
