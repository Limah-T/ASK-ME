from django.shortcuts import render, redirect
from .models import Chat
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat
from .form import QuestionNDbotReply
from .wiki_api import chatexchange


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

            bot_reply = chatexchange(user_message=user_message)
                
            # Save chat to DB
            Chat.objects.create(user=request.user, user_message=user_message, bot_reply=bot_reply)

            return redirect("chat:chat")  # Adjust name to match your URL
        chats = Chat.objects.order_by("time_stamp")
        return render(request, self.template_name, {"form": form, "chats": chats})


