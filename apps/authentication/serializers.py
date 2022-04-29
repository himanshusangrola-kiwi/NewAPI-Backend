from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from apps.authentication.models import User, EmailVerifyToken
from apps.common import app_message
# from django.contrib import auth
# from rest_framework.response import Response


class SignupSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new user using signup form
    """
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        """
        function to match password and confirm password
        :param data: data
        :return: Validated Data or Error
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError(app_message.ERROR_CODE['password']['passwords_match'])
        return data

    def validate_username(self, data):
        """
        Function to validate username uniqueness
        :param data: data
        :return: Validated data or Error
        """
        if User.objects.filter(username=data).exists():
            raise serializers.ValidationError(app_message.ERROR_CODE['username']['username_exist'])
        return data

    def create(self, validated_data):
        """
        Function to make Password Save as Hashed
        :param validated_data: validated_data
        :return: Username and email with hashed password
        """
        if validate_password(validated_data['password']) is None:
            password = make_password(validated_data['password'])
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                password=password
            )
            return user

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']


class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer Class to Upload an Image
    """

    class Meta:
        model = User
        fields = ['photo']


class LoginSerializer(serializers.ModelSerializer):
    """
        Serializer Class to Login with Registered User
    """
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=70, min_length=4, write_only=True)
    username = serializers.CharField(max_length=70, min_length=4, read_only=True)

    def validate(self, data):
        """
        A Function to check if User is a Valid User, an active user or is a verified user
        :param data: data
        :return: Email and Username
        """
        email = data.get('email', '')
        password = data.get('password', '')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError(app_message.ERROR_CODE['user']['wrong_credentials'])
        if not user.is_active:
            raise serializers.ValidationError(app_message.ERROR_CODE['user']['is_active'])
        if not user.is_verified:
            raise serializers.ValidationError(app_message.ERROR_CODE['user']['is_verified'])

        return {
            'email': user.email,
            'username': user.username,
        }

    class Meta:
        model = User
        fields = ['email', 'password', 'username', ]


class EmailVerifyTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailVerifyToken
        fields = '__all__'
