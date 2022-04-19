from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from apps.authentication.models import User
from apps.common import app_message


# from apps.common.app_message import ERROR_CODE


class SignupSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new user using signup form
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        """
            function to match password and confirm password
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError(app_message.ERROR_CODE['password']['passwords_match'])
        return data

    def validate_username(self, data):
        """
            Function to validate username uniqueness
        """
        if User.objects.filter(username=data).exists():
            raise serializers.ValidationError(app_message.ERROR_CODE['username']['username_exist'])
        return data

    def create(self, validated_data):
        if validate_password(validated_data['password']) is None:
            password = make_password(validated_data['password'])
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                password=password
            )
            return user


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['photo']

