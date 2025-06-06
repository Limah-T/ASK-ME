from django.shortcuts import render, redirect
from .models import Chat
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat
from .form import QuestionNDbotReply
from .external_search_api import action
import markdown

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
            # bot_reply_raw = wikipedia_api(user_message)
            # Converts markdown to html
            bot_reply_raw = action(user_message=user_message)
            bot_reply = markdown.markdown(bot_reply_raw)

            Chat.objects.create(user=request.user, user_message=user_message, bot_reply=bot_reply)

            return redirect("chat:chat") 
        chats = Chat.objects.order_by("time_stamp")
        return render(request, self.template_name, {"form": form, "chats": chats})


