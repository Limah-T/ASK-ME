from django.shortcuts import render, redirect
from .models import Chat
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat
from .form import QuestionNDbotReply
from .wiki_api import wikipedia_api

class ChatBotView(LoginRequiredMixin, View):
    template_name = "chat/chat.html"
    form_class = QuestionNDbotReply

    def get(self, request):
        form = self.form_class()
        chats = Chat.objects.order_by("time_stamp")
        return render(request, self.template_name, {"form": form, "chats": chats})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data.get("user_message")

            # Simulate bot reply (you can replace with real logic)
            # greeting
            if "hello" in user_message.lower():
                bot_reply = "👋 Hello! How can I help you today?"

            elif "any news" in user_message.lower():
                bot_reply = (
                    "Sure! Here's the latest update:\n\n"
                    "- 📰 Our new AI-powered helpdesk feature is now live!\n"
                    "- 🌐 We're working on expanding AskME support to multiple languages.\n"
                    "- 🚀 Stay tuned for our upcoming integration with WhatsApp for seamless chat.\n\n"
                    "For more updates, just ask 'What's new with AskME?' or visit our official blog."
                )
            # Askme purpose
            elif "what is askme" in user_message.lower():
                bot_reply = (
                    "AskME is a simple and intelligent chatbot platform designed to help users get quick, "
                    "relevant answers to their questions. 🤖\n\n"
                    "Whether you're looking for information, assistance with common tasks, or just want to explore what "
                    "a rule-based chatbot can do, AskME is here for you.\n\n"
                    "💡 Built with Django, AskME uses a set of predefined rules and logic to respond to your queries, making it "
                    "fast, lightweight, and easy to expand as needed.\n\n"
                    "Go ahead and try asking questions like:\n"
                    "👉 'How can I contact support?'\n"
                    "👉 'What features does AskME offer?'\n"
                    "👉 'Is AskME open source?'\n\n"
                    "I'm always here to help you explore!"
                )
            # who created askme
            elif "who created" in user_message.lower() or "who built" in user_message.lower():
                bot_reply = "AskME was developed by a talented team of Django developers, the founder named 'Halimah Temitope'. It's designed to be simple, fast, and helpful!"
            # reset password
            elif "reset password" in user_message.lower():
                bot_reply = "To reset your password, please go to the login page and click on 'Forgot Password'. A reset link will be sent to your email."
            # help
            elif "help" in user_message.lower():
                 bot_reply = "Here are a few things you can ask me:\n- What is AskME?\n- How does it work?\n- Any news?\n- Who created AskME?\n- Reset password"

            # thankyou
            elif "thank" in user_message.lower():
                bot_reply = "You're welcome! 😊 Let me know if there's anything else I can help you with."

            else:
                bot_reply = wikipedia_api(user_question=user_message.lower())
                
            # Save chat to DB
            Chat.objects.create(user=request.user, user_message=user_message, bot_reply=bot_reply)

            return redirect("chat:chat")  # Adjust name to match your URL
        chats = Chat.objects.order_by("time_stamp")
        return render(request, self.template_name, {"form": form, "chats": chats})


