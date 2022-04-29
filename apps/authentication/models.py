from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
import uuid


class UserManager(BaseUserManager):
    """
    A class to define User Fields and Save User
    """

    def create_user(self, username, email, password=None):
        """
        A function to create a user and Save it
        :param : username, email, password
        :return : user
        """
        if not username:
            raise ValueError('Users must have an username')
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        """
        A function to create a superuser
        :param : username, email, password
        :return : user
        """
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


def img_path(instance, filename):
    """
    function to give the path for the image to upload to
    :param : instance , filename
    :return : Path of Image where it will to upload
    """
    return f"{instance.username}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    """
        A class to create a User table using custom user manager
    """
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True, null=False, blank=False)
    username = models.CharField(max_length=20)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to=img_path, blank=False, null=False)
    is_verified = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """
            A function to tell if the user has special permissions
            :params : perm, obj
            :return : True
        """
        return True


class EmailVerifyToken(models.Model):
    """
    Email Verification Token.
    """
    token = models.CharField(max_length=100, default=uuid.uuid4(), primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
