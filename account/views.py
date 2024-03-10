from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import UserRegistrationSerializer, UserLoginSerializer
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .models import User

from .serializers import UserConfirmationSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            # Save user with is_active=False
            user = serializer.save()

            # Send confirmation email to user
            confirmation_link = f"http://example.com/api/user/confirm-registration/{
                user.id}/"
            send_mail(
                "Confirm your registration",
                f"Please click the following link to confirm your registration: {
                    confirmation_link}",
                "verificmail999@gmail.com",
                [user.email],
                fail_silently=False,
            )

            return Response({'msg': 'Confirmation email sent'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserRegistrationConfirmation(APIView):
    def patch(self, request, user_id, format=None):
        user = get_object_or_404(User, id=user_id)
        serializer = UserConfirmationSerializer(instance=user, data={'is_active': True}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'User activated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email').lower()
        password = serializer.validated_data.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Email or Password is not valid")
        token = get_tokens_for_user(user)
        return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
