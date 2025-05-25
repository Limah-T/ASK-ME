📘 Project Overview

ChatBotApp API is a RESTful service designed to provide users with a smart and responsive chatbot experience. This API includes user registration, authentication, chatbot interaction powered by Serper API, and conversation history management.

Built using Django Rest Framework, the goal of this project is to offer a robust and secure backend system that is easy to integrate with frontend or mobile applications.

🚀 Features

✅ User Registration & Login
✅ JWT Authentication
✅ Smart Chatbot Interaction via Serper API
✅ Input Validation & Error Handling
✅ Country Detection & Normalization
✅ Chat History Tracking
✅ Modular & Extensible Design

🛠️ Tech Stack

Backend Framework: Django + Django REST Framework
External APIs: Serper API
Authentication: JSON Web Token (JWT) for Email Verification
Database: MySQL
Others: Custom DRF Serializers, Validation

📦 Installation (for developers)
git clone https://github.com/Limah-T/ASK-ME.git
cd ASK-ME
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
pip install -r requirements.txt (check the requirements.txt file)

🔐 Environment Variables

SECRET_KEY=your-django-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
SERPER_API_KEY=your-serper-api-key

📍 API Endpoints (Overview)
Endpoint                                Method     Action
/api/v1/signup/	                        POST	   Register new user
/api/v1/verify-email?token=token        GET        Verify email via Token
/api/v1/login/                          POST       Login with valid credentials
/api/v1/verify-code/                    POST       Verify OTP code
/api/v1/logout/                         POST       Logout with valid token place in the header


# 📝 Signup Endpoint Details
Endpoint: POST /api/v1/signup/
Description:
Signs in user with validated credentials, then sends email for verification.
    Request Body  {
                    "email": "your-email",
                    "username": "your-email",
                    "country": "your-country",
                    "password": "your-password"
                }
    Responses
    # Success (HTTP 200):
        {
        "message": "Registration successful. Please check your email to verify your account."
        }
    # Error (HTTP 400):
        {
        "error": "detail will be displayed here."
        }
    Action => Verify new user
    📧✅ Email verification required (Token expires in 5mins time)
    GET /api/v1/verify-email?token=token
    Query parameter 
        • token – the verification token sent to the user's email
    Responses
        # Success (HTTP 200):
            {
                "success": "Email verified successfully.",
                "token": "token-key"
            }
        # Error (HTTP 400):
            {
                "error": "Invalid or Expired token."
            }

# 📝 Login Endpoint Details
Description:
Validates credentials, then sends OTP Code to email for verification.
Endpoint: POST /api/v1/login/
    Request Body
                {
                    "email": "your-email",
                    "password": "your-password"
                }
    Responses
    # Success (HTTP 200):
        {
        "message": "Please check your email for an OTP code."
        }
    # Error (HTTP 400):
        {
        "error": "Email or password is incorrect."
        }
    Action => Verify OTP Code
    📧✅ OTP verification required (Code expires in 5mins time)
    POST /api/v1/verify-code/
    Request Body
                {
                    "email": "your-email",
                    "code": "code-sent-to-email"
                }
    Responses
        # Success (HTTP 200):
            {
                "success": "Code Accepted.",
                "token": "token-key"
            }
        # Error (HTTP 400):
            {
                "error": "Invalid or Expired token."
            }

# 🔒 Logout Endpoint Details
Endpoint: POST /api/v1/logout/

Description:
Logs out the authenticated user by pass the valid token in the header.

    Header
        Authorization: Bearer <your-auth-token>
    Request Body:
        No body required.
    Responses:
        # Success (HTTP 200)
            {
                "success": "Successfully logged out."
            }
        # Error (HTTP 400)
            {
                "error": "Authentication credentials were not provided."
            }

🧪 Testing
python manage.py test

✍️ Author
Halimah Temitope
• LinkedIn - https://www.linkedin.com/in/limah-temitope/
• GitHub - https://github.com/Limah-T/
• Email - limahtechnology@yahoo.com

