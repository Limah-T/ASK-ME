from rest_framework import views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from .custom_serializers import SignUpSerializer
from account.models import CustomUser
from .sendout import send_token_for_email_verification, decode_token

class SignUpView(views.APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        if len(request.data) > 4 or len(request.data) < 4:
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

    def get(self, request):
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


