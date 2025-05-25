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


# 📝 Signup Endpoint Details
POST /api/v1/signup/
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

🧪 Testing
python manage.py test

✍️ Author
Halimah Temitope
• LinkedIn - https://www.linkedin.com/in/limah-temitope/
• GitHub - https://github.com/Limah-T/
• Email - limahtechnology@yahoo.com

