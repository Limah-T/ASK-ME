from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django_otp.models import Device
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPRecipientsRefused, SMTPSenderRefused, SMTPDataError, SMTPException
from dotenv import load_dotenv
from datetime import timedelta
from .country_names import COUNTRY_CHOICES, DEFAULT_COUNTRY, DEFAULT_ROLE
import uuid, os, socket

load_dotenv(override=True)

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

class EmailOTP(Device):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="otp")
    otp_code = models.CharField(max_length=int(os.getenv("LENGTH")), null=False, blank=False)
    valid_until = models.DateTimeField(null=False, blank=False)
    
    def save(self, *args, **kwargs):
        self.otp_code = get_random_string(length=int(os.getenv("LENGTH")), 
                                          allowed_chars=os.getenv("CHARACTERS"))
        self.valid_until = timezone.now() + timedelta(
                                                minutes=int(os.getenv("EXPIRATION_TIME"))
                                                )
        super().save(*args, **kwargs)

    def send_otp_to_email(self, app_name):
        SUBJECT = "OTP Code"
        OTP = self.otp_code
        print(OTP, "otp")
        html_content = render_to_string(
                                template_name=f"{app_name}/otp_email.html",
                                context={
                                    "OTP":OTP,
                                    "subject":SUBJECT
                                }
                            )
        msg = EmailMultiAlternatives(
            subject=SUBJECT,
            from_email=os.getenv("EMAIL_HOST_USER"),
            to=[self.user.email]
        )
        msg.attach_alternative(content=html_content, mimetype="text/html")

        try:
            msg.send()
            print("sent")
            return True
        except SMTPAuthenticationError:
            print("SMTP Authentication failed. Check your email credentials.")
            return None
        except SMTPConnectError:
            print("Failed to connect to the SMTP server. Is it reachable?")
            return None
        except SMTPRecipientsRefused:
            print("Recipient address was refused by the server.")
            return None
        except SMTPSenderRefused:
            print("Sender address was refused by the server.")
            return None
        except SMTPDataError:
            print("SMTP server replied with an unexpected error code (data issue).")
            return None
        except SMTPException as e:
            print(f"SMTP error occurred: {e}")
            return None
        except socket.gaierror:
            print("Network error: Unable to resolve SMTP server.")
            return None
        except socket.timeout:
            print("Network error: SMTP server timed out.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
        
    def verify_otp(self):
        now = timezone.now()
        print(self.valid_until)
        if now > self.valid_until:
            return False
        return True