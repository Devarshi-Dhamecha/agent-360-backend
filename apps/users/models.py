# apps/users/models.py

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Profile(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Profiles'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return self.name


class UserRole(models.Model):
    id = models.CharField(max_length=18, primary_key=True)
    name = models.CharField(max_length=255)
    parent_role = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='child_roles',
        db_column='ParentRoleId'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'UserRoles'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, email, password, **extra_fields)


class Users(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=18, primary_key=True)
    username = models.CharField(max_length=80, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False)
    profile = models.ForeignKey(
        Profile, on_delete=models.PROTECT,
        db_column='ProfileId', db_index=True
    )
    user_role = models.ForeignKey(
        UserRole, on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='UserRoleId'
    )
    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='direct_reports',
        db_column='ManagerId', db_index=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True, db_index=True)
    last_modified_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='modified_users',
        db_column='LastModifiedById'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'Users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.name
