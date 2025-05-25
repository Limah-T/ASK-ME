from rest_framework import serializers
from account.models import CustomUser
from account.country_names import COUNTRY_CHOICES, DEFAULT_ROLE
from django.contrib.auth import authenticate

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
        user = CustomUser.objects.create_user(username=username, email=email, country=country, role=DEFAULT_ROLE, password=password)
        return user
        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)
    password = serializers.CharField(min_length=8, write_only=True, trim_whitespace=True)

    def validate(self, data):
        if not CustomUser.objects.filter(email=data['email']).exists():
            pass
        user = authenticate(email=data['email'], password=data['password'])
        print(user, "user from serializer class")
        if user:
            return user
        raise serializers.ValidationError({'error': 'Email or password is incorrect.'})
         


