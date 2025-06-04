from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from .country_names import COUNTRY_CHOICES, REGISTERED_USER
from .models import CustomUser
from dotenv import load_dotenv
import os
load_dotenv()

class SignupForm(UserCreationForm):
    username = forms.CharField(max_length=100, min_length=3, 
                               widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, 
                                widget=forms.Select(attrs={'class': 'form-select'}))
    password1 = forms.CharField(max_length=255, 
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                               help_text="At least 8 characters, use letters & numbers.", label="Password")
    password2 = forms.CharField(max_length=255, 
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                label="Confirm password")
    
    def clean(self):
        cleaned_data = super().clean()
        cleaned_username = cleaned_data.get("username")
        cleaned_email = cleaned_data.get("email")
        print(cleaned_username, cleaned_email)
        if cleaned_username and cleaned_email:
            cleaned_data['username'] = cleaned_username.lower()
            cleaned_data['email'] = cleaned_email.lower()
        return cleaned_data

    class Meta:
        model = CustomUser
        fields = ["username", "email", "country"]
    

class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))    
    password = forms.CharField(max_length=255, 
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    def clean(self):
        cleaned_data = super().clean()
        cleaned_email = cleaned_data.get("email")
        if cleaned_email:
            cleaned_data['email'] = cleaned_email.lower()
        return cleaned_data
    
class OTPForm(forms.Form):
    code = forms.CharField(max_length=os.getenv("LENGTH"), 
                           label="Enter the OTP code below")

class CustomForgetPasswordForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_email = super().clean()
        email = cleaned_email.get('email')
        if email:
            cleaned_email['email'] = email.lower()
        return cleaned_email
    
class CustomSetPasswordForm(forms.Form):
    new_password = forms.CharField(min_length=8, max_length=255,
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(min_length=8, max_length=255,
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirm password")  

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password')
        password2 = cleaned_data.get('new_password2')
        print(cleaned_data)
        if password1 != password2:
            raise ValidationError('Password do not match')
        cleaned_data.pop('new_password2')
        return cleaned_data
    
class CustomChangePassword(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(min_length=8, max_length=255, 
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="New password")
    new_password2 =forms.CharField(min_length=8, max_length=255, 
                                   widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirm password")
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
            raise ValidationError('Password do not match.')
        cleaned_data.pop('new_password2')
        return cleaned_data
    
class ContactForm(forms.Form):
    name = forms.CharField(min_length=3, max_length=50, 
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(min_length=3, max_length=70, 
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(min_length=5, max_length=255,
                              widget=forms.Textarea(attrs={
                                  'rows': 5,
                                  'placeholder': 'Type in your message',
                                  'class': 'form-control'
                              }))
    registered_user = forms.ChoiceField(choices=REGISTERED_USER, 
                                widget=forms.Select(attrs={'class': 'form-select'})
                            )
    def clean(self):
        cleaned_data = super().clean()
        cleaned_name = cleaned_data.get("name")
        cleaned_email = cleaned_data.get("email")
        if cleaned_name and cleaned_email:
            cleaned_data['name'] = cleaned_name.capitalize()
            cleaned_data['email'] = cleaned_email.lower()
        return cleaned_data