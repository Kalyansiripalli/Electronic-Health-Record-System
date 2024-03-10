from django.urls import path, include
from account.views import UserRegistrationView, UserLoginView, UserRegistrationConfirmation

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('confirm-registration/<int:user_id>/',
         UserRegistrationConfirmation.as_view(), name='user_registration_confirm'),
    path('login/', UserLoginView.as_view(), name='login'),

]
