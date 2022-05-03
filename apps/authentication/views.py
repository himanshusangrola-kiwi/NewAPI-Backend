import uuid
from apps.common.utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, EmailVerifyToken
from .serializers import SignupSerializer, ImageSerializer, LoginSerializer, EmailVerifyTokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


def get_tokens_for_user(user):
    """
    Function to manually create a token for a user
    :return: Refresh and Access Token
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserViewSet(viewsets.GenericViewSet):
    """
        A class to Register a User
    """
    serializer_class = SignupSerializer
    queryset = User.objects.all()

    def list(self, request):
        """
            Function to list all users
            :param request: wsgi request
            :return: All the Registered Users
        """
        user = User.objects.all()
        serializer = self.serializer_class(user, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
            Function to create a user
            :param request: wsgi request
            :return: Registered user's email and username
        """
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.save()
        token = uuid.uuid4()
        if user_obj:
            params = {
                'token': str(token),
                'user': user_obj.id,
            }
            token_obj = EmailVerifyTokenSerializer(data=params)
            token_obj.is_valid(raise_exception=True)
            token_obj.save()
        current_site = get_current_site(request).domain
        relativeLink = reverse('verify-email')
        abs_url = 'http://' + current_site + relativeLink + '?token=' + str(token)
        email_body = 'Hi ' + user_obj.username + ' Use link below to verify your email \n' + abs_url
        data = {'email_body': email_body, 'to_email': user_obj.email, 'email_subject': 'Verify your email'}
        Util.send_email(data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmailVerify(APIView):
    """
    A class to Activate the Email
    """

    def get(self, request):
        """
        Verify the Token on Email with token saved on Database
        :param request: wsgi request
        :return : Success or Error Messages
        """
        params = request.query_params
        token = params.get('token')
        token_id = EmailVerifyToken.objects.get(token=token)
        if not token:
            return Response({"message": "Wrong Value", "status": False}, status=status.HTTP_400_BAD_REQUEST)
        user_obj = User.objects.get(pk=int(token_id.user.pk))
        if user_obj.is_verified:
            return Response({"message": "User already Verified", "status": True}, status=status.HTTP_200_OK)
        else:
            user_obj.is_verified = True
            user_obj.save()
            return Response({"message": "Activated done", "status": True}, status=status.HTTP_200_OK)


class ImageUploadView(viewsets.GenericViewSet):
    """
    A Class to Upload Image
    """
    parser_classes = [MultiPartParser]
    serializer_class = ImageSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """
        Function to upload an Image File
        :param request: wsgi request
        :return: Image Upload Path or Error Message
        """
        serializer = self.serializer_class(data=request.data, instance=request.user, context={'request': request})
        if serializer.is_valid():
            serializer.save(
                photo=request.data.get('photo')
            )
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(viewsets.GenericViewSet):
    """
    A Class to Login created User
    """
    serializer_class = LoginSerializer

    def create(self, request):
        """
        Login User when Correct Info is Given
        :param request: wsgi request
        :return: Login Success Message with Token or  Wrong Credentials Message
        """
        params = request.data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=params['email'], password=params['password'])
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'msg': 'Login Success', 'token': token}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Wrong Credentials", "status": False}, status=status.HTTP_400_BAD_REQUEST)


# class ChangePassword(viewsets.GenericViewSet):
    # """
    # A class to Change Password of any User
    # """
    # serializer_class = ChangePasswordSerializer
    # permission_classes = [IsAuthenticated]
    # # queryset = User.objects.all()
    #
    # def update(self, request):
    #     """
    #     Change Password of Logged-in User
    #     :param request: wsgi request
    #     :return: Password Change Success Message or Error Message
    #     """
    #     serializer = self.serializer_class(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         if not User.object.(serializer.data.get("password")):
    #             return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
    #         User.object.set_password(serializer.data.get("new_password"))
    #         User.object.save()
    #         return Response("Success.", status=status.HTTP_200_OK)
    #
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)