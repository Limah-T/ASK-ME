📘 Project Overview

ChatBotApp API is a RESTful service designed to provide users with a smart and responsive chatbot experience. This API includes user registration, authentication, chatbot interaction powered by Serper API, and conversation history management.

Built using Django Rest Framework, the goal of this project is to offer a robust and secure backend system that is easy to integrate with frontend or mobile applications.

🚀 Features
✅ User Registration, Login & Logout
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

📍 API Endpoints (Overview)
# Endpoint                                Method     Action
/api/v1/signup/	                        POST	   Register new user.
/api/v1/verify-email?token=token        GET        Verifies email via Token.
/api/v1/login/                          POST       Login with valid credentials.
/api/v1/verify-code/                    POST       Verifies OTP code.
/api/v1/forget-password/                POST       Enables password reset,and send code.
/api/v1/verify-reset-code/              GET        Verifies code to reset password.
/api/v1/password-reset/                 POST       Resets and saves new password.
/api/v1/change-password/                POST       Verifies old password & change to new
/api/v1/logout/                         POST       Logout user with valid token.
/api/v1/get-new-token/                  POST       Verifies email and password to get new token
/api/v1/chat-question/                  POST       Enables users to ask the bot questions
/api/v1/chat-history/                   GET       Views users chat history associated to the current user,
                                                   Includes filtering, and pagination settings.
/api/v1/chat-update/                    PUT/PATCH  Updates an existing chat by passing the chat id.
/api/v1/chat/                           GET        Retrieves & Deletes an existing chat by passing the chat id.

# 📝 Signup Endpoint Details
    Endpoint: POST /api/v1/signup/
    Description: Signs in user with validated credentials, then sends email for verification.
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
            "error": "Error occured while sending for verification."
            }
        Action => Verify new user
        📧✅ Email verification required (Token expires in 5mins)
        GET /api/v1/verify-email?token=token
        Query parameter 
            • token – the verification token sent to the user's email
        Responses
            # Success (HTTP 200):
                {
                    "success": "Email verified successfully.",
                    "token": "token-key"
                }
            # Error (HTTP 400): (Code expires after 5mins.)
                {
                    "error": "Invalid or Expired token."
                }

# 📝 Login Endpoint Details
    Endpoint: POST /api/v1/login/
    Description: Validates credentials, then sends OTP Code to email for verification.
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
        📧✅ OTP verification required 
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
            # Error (HTTP 400): (Code expires after 5mins.)
                {
                    "error": "Invalid or Expired token."
                }

# 🔁 Forget password Endpoint Details
    Endpoint: POST /api/v1/forget-password/
    Description: Validates user's email, then sends code to email for verification, verifies and reset password.
        Request Body
                    {
                        "email": "your-email",
                    }
        Responses
        # Success (HTTP 200):
            {
            "message": "Please check you email for confirmation to reset password."
            }
        # Error (HTTP 400):
            {
            "error": "Error occured while sending code to email"
            }

        🔢 Verifies token
        Endpoint: GET /api/v1/verify-reset-code/ 
        Query parameter 
            • token – the verification token sent to the user's email
        Responses
            # Success (HTTP 200):
                {
                'success': 'Token is valid, you can reset your password now.',
                }
            # Error (HTTP 400): (Code expires after 5mins)
                {
                    "error": "Invalid or expired token."
                }

        📧 Reset password
        Endpoint: POST /api/v1/password-reset/
        Request Body
                    {
                        "email": "your-email",
                        "new_password": "your-new-password",
                        "confirm_password": "confirm-password"
                    }
        Responses
            # Success (HTTP 200):
                {
                'success': 'Password has been changed successfully.',
                'token': 'your-token-key'
                }
            # Error (HTTP 400) (timeout after 3mins):
                {
                    "error": "Timeout, request for a new reset token."
                }

# 🔒 Change password Endpoint Details
    Endpoint: POST /api/v1/change-password/
    Description: Validates authenticated user's old and new password, then change to the new password.
        Header
            Authorization: Token <your-auth-token>
        Request Body
                    {
                        "old_password": "your-recent-password",
                        "new_password": "your-new-password",
                        "confirm_password": "confirm-password"
                    }
        Responses
        # Success (HTTP 200):
            {
            "success": "Your password has been changed successfully."
            }
        # Error (HTTP 400):
            {
            "error": "Recent password is incorrect."
            }

# 🔐 Get-new-token Endpoint Details
    Endpoint: POST /api/v1/get-new-token/
    Description: Validates credentials, then sends OTP Code to email for verification.
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
        📧✅ OTP verification required 
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
            # Error (HTTP 400): (Code expires after 5mins.)
                {
                    "error": "Invalid or Expired token."
                }

# 🗨️ Chat Interaction (Q&A) Endpoint Details
    Endpoint: POST /api/v1/chat-question/
    Description: Checks the length of user's question to be more than 7 characters and return bot-reply response.
        Header
            Authorization: Token <your-auth-token>
        Request Body
                    {
                        "question": "your-question",
                    }
        Responses
        # Success (HTTP 200):
            {
            "success": "bot-reply."
            }
        # Error (HTTP 400):
            {
            "error": "Please ask a valid question."
            }

# 🕘💬 Chat history
    Endpoint: POST /api/v1/chat-history/
    Description: Displays chat history between the current user and bot
        Header
            . Authorization: Token <your-auth-token>
        Request Body:
            No data required.
        Query parameters (Optional)
            Parameter key must be either "user_message" or "bot_reply" to get accurate results.
            . Filtering =>  E.g  ?user_message=filter-by-any-existing-word-or-words
                                 OR  
                            bot_reply=any-existing-word-or-words
            . Pagination => E.g ?page=1&page_size=5
             
        Responses:
        # Success (HTTP 200)
            {
                "count": length-of-data-count-returned,
                "next": E.g "https://ask-me-4j4v.onrender.com/api/v1/chat-history/?page=2&page_size=5",
                "previous": null,
                "results": [
                            {   
                                "id": "chat-id",
                                "user_message": "question",
                                "bot_reply": "bot-response",
                                "time_stamp": "chat-time"
                            }
                    ]
            }
        # Error (HTTP 400)
            {
                "error": "Invalid token"
            }    

# Retrieves and Deletes an existing chat.
    Endpoint: GET /api/v1/chat/
    Description: Retrieves an existing chat by passsing the chat id.
        Header
            Authorization: Token <your-auth-token>
        Query parameter
            • pk – The existing chat id
        Request Body:
            No data required.
        Responses:
        # Success (HTTP 200)
            {   
                "success" : "successfully updated prompt."
                "id": "chat-id",
                "user_message": "question",
                "bot_reply": "bot-response",
                "time_stamp": "chat-time"
            }
        # Error (HTTP 400)
            {
                "error": "Id does not exist"
            }

        Endpoint: DELETE /api/v1/chat/
        Description: Deletes an existing chat by passsing the chat id.
        Header
            Authorization: Token <your-auth-token>
        Query parameter
            • pk – The existing chat id
        Request Body:
            No data required.
        Responses:
        # Success (HTTP 200)
            {   
                "success" : "chat deleted successfully."
            }
        # Error (HTTP 400)
            {
                "error": "Id does not exist"
            }
# Update an existing chat.
    Endpoint: PUT/PATCH /api/v1/chat-update/
    Description: Update an existing chat by passsing the chat id.
        Header
            Authorization: Token <your-auth-token>
        Query parameter
            • pk – The existing chat id
        Request Body:
            {
                "question": "your-new-or-edit-question"
            }
        Responses:
        # Success (HTTP 200)
            {   
                "success" : "successfully updated prompt."
                "id": "chat-id",
                "user_message": "question",
                "bot_reply": "bot-response",
                "time_stamp": "chat-time"
            }
        # Error (HTTP 400)
            {
                "error": "Id does not exist"
            } 

# 🔒 Logout Endpoint Details
    Endpoint: POST /api/v1/logout/
    Description: Logs out the authenticated user by pass the valid token in the header.
        Header
            Authorization: Token <your-auth-token>
        Request Body:
            No data required.
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
