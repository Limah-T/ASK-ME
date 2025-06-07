from rest_framework import views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import logout, authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from datetime import timedelta
from dotenv import load_dotenv
from .custom_serializers import SignUpSerializer, LoginSerializer, ForgetPasswordSerializer, SetPasswordSerializer, ChangePasswordSerializer, ChatCreateSerializer, ChatListSerializer, GetNewTokenSerializer
from account.models import CustomUser, EmailOTP
from .sendout import send_token_for_email_verification, decode_token, send_token_for_password_reset
from chat.external_search_api import action
from chat.models import Chat
import os
load_dotenv()

def customexceptionhandler(request, exception):
    if request.path.startswith('/api/'):
        return JsonResponse({'detail': 'Not found'}, status=400)
    return render(request, '404.html', status=404)

class SignUpView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        length_of_data = len(request.data)
        if length_of_data > 4 or length_of_data < 4:
            return Response(data={'error': 'only \"username\", \"email\", \"country\", and \"password\" are required'}, status=status.HTTP_400_BAD_REQUEST)
        CustomUser.objects.all().delete()
        try:
            user = CustomUser.objects.get(email=request.data.get("email").strip().lower())
            if  user.username == request.data.get("username").strip().lower():
                pass
            if not user.email_verified:
                pass
            user.delete()
        except CustomUser.DoesNotExist:
            pass
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if send_token_for_email_verification(user=user.email):
            return Response(data={'message': ' If this email is registered, you’ll receive further instructions shortly for verification.'}, status=status.HTTP_200_OK)
        return Response(data={'error': 'Error occured while sending for verification.'}, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyEmailView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
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
            return Response(data={'error': 'Error occured while sending code to email'}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(data={'error':'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(data={'error': 'New password password to similar.'}, status=status.HTTP_400_BAD_REQUEST)
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
    
class ChangePasswordView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def post(self, request):
        email_verified = request.user.email_verified
        token_verified = request.user.token_verified
        if not email_verified and not token_verified:
            return Response(data={'error': 'Invalid request, user\'s email has not been verified'}, status=status.HTTP_400_BAD_REQUEST)
        length_of_data = len(request.data)
        if length_of_data > 3 or length_of_data < 3:
            return Response(data={'error': 'Only old_password, new_password, and confirm_password are required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')
        user = request.user
        if not authenticate(email=user.email, password=old_password):
            return Response(data={'error': 'Recent password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        if authenticate(email=user.email, password=new_password):
            return Response(data={'error': 'New password is too similar to the old password.'}, status=status.HTTP_400_BAD_REQUEST)
        user.password = make_password(password=new_password)
        user.save()
        return Response(data={'success': 'Your password has been changed successfully.'}, status=status.HTTP_200_OK)
    
class GetNewTokenView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request):
        length_of_data = len(request.data)
        if length_of_data > 2 or length_of_data < 2:
            return Response(
                data={'error': 'Only email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = GetNewTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if EmailOTP.objects.filter(user=user).exists():
            EmailOTP.objects.filter(user=user).delete()
        get_otp = EmailOTP.objects.create(user=user)
        if get_otp.send_otp_to_email(app_name="api"):
            return Response(data={'message': 'Please check your email for OTP code.'}, status=status.HTTP_200_OK)
        return Response(data={'error': 'Error occured while sending OTP to email'}, status=status.HTTP_400_BAD_REQUEST)
    
class ChatCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        email_verified = request.user.email_verified
        token_verified = request.user.token_verified
        if not email_verified and not token_verified:
            return Response(data={'error': 'Invalid request, user\'s email has not been verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ChatCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_question = serializer.validated_data.get('question')
        bot_reply = action(user_message=user_question)
        exchange = Chat.objects.create(user=request.user, user_message=user_question,
                                       bot_reply=bot_reply)
        return Response(data={
                        'you': user_question,
                        'bot': bot_reply,
                        'time': exchange.time_stamp
                        }, status=status.HTTP_200_OK
                )

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'count': len(data),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
    
class CustomSearchFilter(SearchFilter):
    def get_search_fields(self, view, request):
        if request.query_params.get("user_message"):
            return ['user_message']
        if request.query_params.get("bot_reply"):
            print("here2")
            return ['bot_reply']
        return super().get_search_fields(view, request)

class ChatListView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]
    serializer_class = ChatListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [CustomSearchFilter, OrderingFilter]
    ordering_fields = ["-time_stamp"]
    search_fields = ["user_message", "bot_reply"]
    
    def get_queryset(self):
        # Fitering against current user
        email_verified = self.request.user.email_verified
        token_verified = self.request.user.token_verified
        if not email_verified and not token_verified:
            return Response(data={'error': 'Invalid request, user\'s email has not been verified'}, status=status.HTTP_400_BAD_REQUEST)
        base_query = Chat.objects.filter(user=self.request.user).order_by("-time_stamp")
        date_time_query = self.request.query_params.get("time_stamp", None)
        if date_time_query:
            base_query = base_query.filter(time_stamp=date_time_query)
        return base_query

    def get(self, request, *args, **kwargs):
        email_verified = request.user.email_verified
        token_verified = request.user.token_verified
        if not email_verified and not token_verified:
            return Response(data={'error': 'Invalid request, user\'s email has not been verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        length_of_data = len(request.data)
        if length_of_data:
            return Response(
                data={'error': 'No data is required in the body parameters.'},  status=status.HTTP_400_BAD_REQUEST
            )
        return super().get(request, *args, **kwargs)
    
class ChatDetailView(generics.RetrieveDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "delete"]
    serializer_class = ChatListSerializer

    def get_queryset(self):
        email_verified = self.request.user.email_verified
        token_verified = self.request.user.token_verified
        if not email_verified and not token_verified:
            return Response(data={'error': 'Invalid request, user\'s email has not been verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Chat.objects.filter(user=self.request.user)

    def get(self, request):
        email_verified = request.user.email_verified
        token_verified = request.user.token_verified
        if not email_verified and not token_verified:
            return Response(data={'error': 'Invalid request, user\'s email has not been verified'}, status=status.HTTP_400_BAD_REQUEST)
        pk = request.query_params.get('pk', None)
        try:
            chat_exist = Chat.objects.get(id=pk)
        except Chat.DoesNotExist:
            return Response(data={'error': 'Id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except Chat.MultipleObjectsReturned:
            return Response(data={'error': 'Multiple chat found with this id.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={'error': 'Invalid ID.'}, status=status.HTTP_400_BAD_REQUEST)
            
        length_of_data = len(request.data)
        if length_of_data:
            return Response(
                data={'error': 'No data is required in the body parameters.'},  status=status.HTTP_400_BAD_REQUEST
            )
        return Response(data={
                            'id': chat_exist.id,
                            'user_message': chat_exist.user_message,
                            'bot_reply': chat_exist.bot_reply,
                            'time_stamp': chat_exist.time_stamp.date()
                        },status=status.HTTP_200_OK
                )
    
    def delete(self, request):
        email_verified = request.user.email_verified
        token_verified = request.user.token_verified
        if not email_verified and not token_verified:
            return Response(data={'error': 'Invalid request, user\'s email has not been verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        pk = request.query_params.get('pk', None)
        try:
            chat_exist = Chat.objects.get(id=pk)
        except Chat.DoesNotExist:
            return Response(data={'error': 'Id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except Chat.MultipleObjectsReturned:
            return Response(data={'error': 'Multiple chat found with this id.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={'error': 'Invalid ID.'}, status=status.HTTP_400_BAD_REQUEST)
            
        length_of_data = len(request.data)
        if length_of_data:
            return Response(
                data={'error': 'No data is required in the body parameters.'},  status=status.HTTP_400_BAD_REQUEST
            )
        chat_exist.delete()
        return Response(data={'success': 'chat deleted successfully.'}, status=status.HTTP_200_OK)
    
class ChatUpdateView(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch", "put"]

    def get_queryset(self):
        if not self.request.user.email_verified:
            return Response(data={'error': 'Invalid request, user\'s email has not been verified'}, status=status.HTTP_400_BAD_REQUEST)
        return Chat.objects.filter(user=self.request.user)

    def put(self, request, *args, **kwargs): 
        chat_id = request.query_params.get("pk", None)
        if not chat_id:
            return Response(data={'error': 'Pk is missing in query paramater.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            chat_exists = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response(data={'error': 'id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except Chat.MultipleObjectsReturned:
            return Response(data={'error': 'multiple chat found with this id.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={'error': 'an error occured when searching for the chat id'}, status=status.HTTP_400_BAD_REQUEST)
        length_of_data = len(request.data)
        if length_of_data > 1 or length_of_data < 1:
            return Response(data={'error': 'only question is allowed in the request body.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ChatCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data.get('question')
        bot_reply = action(user_message=question)
        chat_exists.user_message = question
        chat_exists.bot_reply = bot_reply
        chat_exists.save()

        return Response(data={
                        'sucesss': 'successfully updated prompt.',
                        'id': chat_exists.id,
                        'user_messsage': chat_exists.user_message,
                        'bot_reply': chat_exists.bot_reply,
                        },status=status.HTTP_200_OK
                )
    
    def patch(self, request, *args, **kwargs):
        chat_id = request.query_params.get("pk", None)
        if not chat_id:
            return Response(data={'error': 'Pk is missing in query paramater.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            chat_exists = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response(data={'error': 'id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except Chat.MultipleObjectsReturned:
            return Response(data={'error': 'multiple chat found with this id.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={'error': 'an error occured when searching for the chat id'}, status=status.HTTP_400_BAD_REQUEST)
        length_of_data = len(request.data)
        if length_of_data > 1 or length_of_data < 1:
            return Response(data={'error': 'only question is allowed in the request body.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ChatCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data.get('question')
        bot_reply = action(user_message=question)
        chat_exists.user_message = question
        chat_exists.bot_reply = bot_reply
        chat_exists.save()

        return Response(data={
                        'sucesss': 'successfully updated prompt.',
                        'id': chat_exists.id,
                        'user_messsage': chat_exists.user_message,
                        'bot_reply': chat_exists.bot_reply,
                        },status=status.HTTP_200_OK
                )
        
class LogoutView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request):
        email_verified = request.user.email_verified
        token_verified = request.user.token_verified
        if not email_verified and not token_verified:
            return Response(data={'error': 'Invalid request, user\'s email has not been verified'}, status=status.HTTP_400_BAD_REQUEST)
        Token.objects.filter(user=request.user).delete()
        request.user.token_verified = False
        request.user.save()
        logout(request)
        return Response(data={'success': 'Successfully logged out.'}, status=status.HTTP_200_OK)
