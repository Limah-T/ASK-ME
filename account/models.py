from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from .country_names import COUNTRY_CHOICES, DEFAULT_COUNTRY, DEFAULT_ROLE
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, country, role, password=None, **extra_fields):
        if not any([username, email, country]):
            raise ValidationError('This field may not be blank!')
        email = self.normalize_email(email)
        username_exist = self.model.objects.filter(username=username).exists()
        email_exist = self.model.objects.filter(email=email).exists()
        if username_exist:
            raise ValidationError('username is taken!')
        if email_exist:
            raise ValidationError('email already exists!')
        user = self.model(username=username, email=email, country=country, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, country, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        role = "developer"
        return self.create_user(username=username, email=email, country=country, role=role, password=password, **extra_fields)
    
class CustomUser(AbstractUser):
    first_name = None
    last_name = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default=DEFAULT_COUNTRY)
    role = models.CharField(max_length=10, default=DEFAULT_ROLE)
    email_verified = models.BooleanField(default=False)
    token_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "country"]

    def save(self, *args, **kwargs):
        self.username = self.username.strip().lower()
        self.email = self.email.strip().lower()
        self.country = self.country.strip().title()
        self.role = self.role.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


