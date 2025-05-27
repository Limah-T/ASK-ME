from rest_framework import views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from django.contrib.auth import logout, authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from dotenv import load_dotenv
from .custom_serializers import SignUpSerializer, LoginSerializer, ForgetPasswordSerializer, SetPasswordSerializer
from account.models import CustomUser, EmailOTP
from .sendout import send_token_for_email_verification, decode_token, send_token_for_password_reset
import os
load_dotenv()

class SignUpView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        length_of_data = len(request.data)
        if length_of_data > 4 or length_of_data < 4:
            return Response(data={'error': 'only \"username\", \"email\", \"country\", and \"password\" are required'}, status=status.HTTP_400_BAD_REQUEST)
        CustomUser.objects.all().delete()
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        print(user)
        if send_token_for_email_verification(user=user.email):
            return Response(data={'message': 'Registration successful. Please check your email to verify your account.'}, status=status.HTTP_200_OK)
        return Response(data={'error': 'Error occured while sending email'}, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyEmailView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    http_method_names = ['get']

    def get(self, request):
        length_of_data = len(request.data)
        if length_of_data:
            return Response(data={'error': 'No data is required in the request body'}, status=status.HTTP_400_BAD_REQUEST)
        token_recieved = request.query_params.get('token')
        if not token_recieved:
            return Response(data={'error': 'Token is missing from the query params.'}, status=status.HTTP_400_BAD_REQUEST)
        decoded_token = decode_token(token=token_recieved)
        if not decoded_token:
            return Response(data={'error': "Invalid or Expired token."}, status=status.HTTP_400_BAD_REQUEST)
        
        email = decoded_token['sub']
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(data={'error': 'User with this account does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.MultipleObjectsReturned:
            return Response(data={'error':'Multiple account found with this email.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={'error': 'An error occurred when verifying this account.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.token_verified:
            return Response(data={'error': 'This account has been verified before now.'}, status=status.HTTP_400_BAD_REQUEST)
        user.email_verified = True
        token = Token.objects.create(user=user)
        user.token_verified = True
        user.save()
        return Response(data={  'success': 'Email verified successfully.',
                                'token': token.key
                                }, 
                        status=status.HTTP_200_OK)
    
class LoginView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        length_of_data = len(request.data)
        if length_of_data > 2 or length_of_data < 2:
            return Response(data={'error': 'only  \"email\", and \"password\" are required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if EmailOTP.objects.filter(user=user).exists():
            EmailOTP.objects.filter(user=user).delete()
        get_otp = EmailOTP.objects.create(user=user)
        if get_otp.send_otp_to_email(app_name="api"):
            return Response(data={'message': 'Please check your email for OTP code.'}, status=status.HTTP_200_OK)
        return Response(data={'error': 'Error occured while sending OTP to email'}, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyOtpView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        length_of_data = len(request.data)
        if length_of_data > 2 or length_of_data < 2:
            return Response(data={'error': 'Only email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            email = request.data['email']
            code = request.data['code']
        except KeyError:
            return Response(data={'error': 'Email and code are required.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={'error': 'Email and code are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email.strip())
        except CustomUser.DoesNotExist:
            return Response(data={'error': 'User with this account does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.MultipleObjectsReturned:
            return Response(data={'error':'Multiple account found with this email.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={'error': 'An error occurred when verifying this account.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.email_verified:
            return Response(data={'error': 'User with the account does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.token_verified:
            return Response(data={'error': 'User code has been verified before now'}, status=status.HTTP_400_BAD_REQUEST)

        if not EmailOTP.objects.filter(user=user).exists():
            return Response(data={'error': 'No code generated for this user yet.'}, status=status.HTTP_400_BAD_REQUEST)
        user_code = EmailOTP.objects.get(user=user)
        if code != user_code.otp_code:
            return Response(data={'error': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_code.verify_otp():
            return Response(data={'error': 'Code has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        user.token_verified = True
        user.save()
        EmailOTP.objects.filter(user=user).delete()
        if Token.objects.filter(user=user).exists():
            Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        return Response(data={
                            'success': 'Code Accepted',
                            'token': token.key
                            }, status=status.HTTP_200_OK)

class ForgetPasswordView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        length_of_data = len(request.data)
        if length_of_data > 1 or length_of_data < 1:
            return Response(data={'error': 'Only email is required in the data body.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        if not send_token_for_password_reset(user=email):
            return Response(data={'error': 'Error occured while sending OTP to email'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Please check you email for confirmation to reset password.'}, status=status.HTTP_200_OK)

class VerifyPasswordResetToken(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['get']

    def get(self, request):
        length_of_data = len(request.data)
        if length_of_data:
            return Response(data={'error': 'No data is required in the request body'}, status=status.HTTP_400_BAD_REQUEST)
        token = request.query_params.get('token')
        if not token:
            return Response(data={'error': 'Token is missing from the query params.'}, status=status.HTTP_400_BAD_REQUEST)
        decoded_token = decode_token(token=token)
        if not decoded_token:
            return Response(data={'error':'Invalid or Expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        email = decoded_token['sub']
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(data={'error': 'User with this account does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.MultipleObjectsReturned:
            return Response(data={'error':'Multiple account found with this email.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={'error': 'An error occurred when verifying this account.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.email_verified:
            return Response(data={'error': 'Email has not been verified.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.token_verified:
            return Response(data={'error':'Token has been used, request for a new one.'}, status=status.HTTP_400_BAD_REQUEST)
        user.token_verified = True
        user.reset_token = True
        user.time_token_set = timezone.now() + timedelta(minutes=int(os.getenv('RESET_PASSWORD_TIME')))
        user.save()
        return Response(data={'success': 'Token is valid, you can reset your password now.'}, status=status.HTTP_200_OK)
    
class ResetPasswordView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        length_of_data = len(request.data)
        if length_of_data > 3 or length_of_data < 3:
            return Response(data={'error': 'Only email, new_password, and confirm_password are required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('new_password')
        user = CustomUser.objects.get(email=email)
        if authenticate(email=user.email, password=password):
            return Response(data={'error': 'New password cannot be thesame as old.'}, status=status.HTTP_400_BAD_REQUEST)
        user.password = make_password(password=password)
        user.reset_token = False
        user.save()
        # If token exist for user
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        return Response(data={
                                'success': 'Password has been changed successfully.',
                                'token': token.key
                            }, status=status.HTTP_200_OK)

class LogoutView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        request.user.token_verified = False
        request.user.save()
        logout(request)
        return Response(data={'success': 'Successfully logged out.'}, status=status.HTTP_200_OK)
