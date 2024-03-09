from django.urls import path,include
from ehrmanagement.views import AddHospitalView,AddDoctorView,AddPatientsView,AllDoctorsView,AllHospitalsView,AllPatientView

urlpatterns = [
    path('addhospital/',AddHospitalView.as_view(), name='addhospital'),
    path('adddoctor/',AddDoctorView.as_view(), name='adddoctor'),
    path('addpatient/',AddPatientsView.as_view(), name='adddoctor'),
    path('viewalldoctors/',AllDoctorsView.as_view(), name='alldoctorview'),
    path('viewallhospitals/',AllHospitalsView.as_view(), name='allhospitalview'),
    path('viewallpatients/',AllPatientView.as_view(), name='allpatientsview'),
]

