from django.urls import path, include
from ehrmanagement.views import AddHospitalView, AddDoctorView, AddPatientsView, AllDoctorsView, AllHospitalsView, \
    AllPatientView

urlpatterns = [
    path('add-hospital/', AddHospitalView.as_view(), name='addhospital'),
    path('add-doctor/', AddDoctorView.as_view(), name='adddoctor'),
    path('add-patient/', AddPatientsView.as_view(), name='addpatient'),
    path('doctor/all/', AllDoctorsView.as_view(), name='alldoctorview'),
    path('hospital/all/', AllHospitalsView.as_view(), name='allhospitalview'),
    path('patient/all/', AllPatientView.as_view(), name='allpatientsview'),
]
