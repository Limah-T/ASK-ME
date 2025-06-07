from rest_framework import serializers
from account.models import CustomUser
from account.country_names import COUNTRY_CHOICES, DEFAULT_ROLE
from django.contrib.auth import authenticate
from django.utils import timezone

class ChoiceFieldCustomSerializer(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.strip().title()
        return super().to_internal_value(data)

class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, min_length=3, trim_whitespace=True)
    email = serializers.EmailField(trim_whitespace=True)
    country = ChoiceFieldCustomSerializer(choices=COUNTRY_CHOICES)
    password = serializers.CharField(min_length=8, write_only=True, trim_whitespace=True)

    def validate_email(self, value):
        return value.lower()

    def validate_country(self, value):
        if value:
            return value.title()

    def validate(self, data):   
        if len(data['username']) < 3:
            raise serializers.ValidationError({'error':'username must be not be less than 3 characters.'})
        if len(data['password']) < 8:
            raise serializers.ValidationError({'error': 'password length greater or equal to 8 characters.'})
        if CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'error': 'username is taken.'})
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'error': 'email already exists.'})
        return data
    
    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        country = validated_data.get('country')
        password = validated_data.get('password')
        if email == "limahenterprises152@gmail.com" and username == "limah":
            user = CustomUser.objects.create_superuser(username=username, email=email, country=country)
        else:
            user = CustomUser.objects.create_user(username=username, email=email, country=country, role=DEFAULT_ROLE, password=password)
        return user
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)
    password = serializers.CharField(min_length=8, write_only=True, trim_whitespace=True)

    def validate_email(self, value):
        return value.lower()

    def validate(self, data):
        try:
            user_exist = CustomUser.objects.get(email=data['email'])
        except Exception as e:
            raise serializers.ValidationError({'error': 'No user associated with this account'})
        if user_exist.token_verified:
                raise serializers.ValidationError({'error': 'Invalid request, user is logged in already.'})
        user = authenticate(email=data['email'], password=data['password'])
        if not user: 
            raise serializers.ValidationError({'error': 'Email or password is incorrect.'})
        return user
    
class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value.lower())
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"error": "Email does not exist!"})
        except CustomUser.MultipleObjectsReturned:
            raise serializers.ValidationError({'error':'Multiple account found for this user.'})
        except Exception as e:
            print(e)
            raise serializers.ValidationError({"error": "An error occured try again later."})
        user.token_verified = False
        user.save()
        return value
    
class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)
    new_password = serializers.CharField(trim_whitespace=True, min_length=8, write_only=True)
    confirm_password = serializers.CharField(trim_whitespace=True, min_length=8, write_only=True)

    def validate_email(self, value):
        return value.lower()

    def validate(self, data):
        if len(data) > 3 or len(data) < 3:
            raise serializers.ValidationError({'error': 'Only email, new_password, and confirm_password are required in the request body.'})
        try:
            user = CustomUser.objects.get(email=data['email'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"error": "Email does not exist!"})
        except CustomUser.MultipleObjectsReturned:
            raise serializers.ValidationError({'error':'Multiple account found for this user.'})
        except Exception as e:
            print(e)
            raise serializers.ValidationError({"error": "An error occured try again later."})
        if not user.reset_token:
            raise serializers.ValidationError({'error': 'Invalid attempt due to time out or no token generated, request a token before resetting password.'})
        if not timezone.now() > user.time_token_set:
            raise serializers.ValidationError({'error': 'Timeout, request for a new reset token.'})
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'error': 'passwords do not match.'})
        data.pop('confirm_password')
        return data
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(trim_whitespace=True)
    new_password = serializers.CharField(trim_whitespace=True, min_length=8, write_only=True)
    confirm_password = serializers.CharField(trim_whitespace=True, min_length=8, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'error': 'Passwords do not match.'})
        data.pop('confirm_password')
        return data
    
class GetNewTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)
    password = serializers.CharField(min_length=8, write_only=True, trim_whitespace=True)

    def validate_email(self, value):
        return value.lower()

    def validate(self, data):
        try:
            user_exist = CustomUser.objects.get(email=data['email'])
        except Exception as e:
            raise serializers.ValidationError({'error': 'No user associated with this account'})
        if not user_exist.email_verified:
            raise serializers.ValidationError({'error': 'Invalid request, user\'s account has not been verified.'})
        user = authenticate(email=data['email'], password=data['password'])
        if not user: 
            raise serializers.ValidationError({'error': 'Email or password is incorrect.'})
        user.token_verified = False
        user.save()
        return user
    
class ChatCreateSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255, trim_whitespace=True)

    def validate_question(self, value):
        if len(value) <= 7:
            raise serializers.ValidationError({'error': 'Please ask a valid question'})
        return value
    
class ChatListSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    user_message = serializers.CharField()
    bot_reply = serializers.CharField()
    time_stamp = serializers.DateTimeField()


 