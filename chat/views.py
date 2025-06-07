from django.shortcuts import render, redirect, get_object_or_404
from .models import Chat
from django.views import View
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
    

@login_required
def chat_update_view(request, pk):
    chat = get_object_or_404(Chat, id=pk)

    # Only the chat owner should be allowed to update
    if chat.user != request.user:
        messages.error(request, "You are not authorized to update this chat.")
        return redirect("chat-page")  # Replace with your actual chat page name

    # if request.method == "POST":
    form = QuestionNDbotReply(request.POST, instance=chat)
    if form.is_valid():
        form.save()
        messages.success(request, "Chat updated successfully.")
    else:
        form = QuestionNDbotReply(instance=chat)

    chats = Chat.objects.order_by("time_stamp")
    return render(request, "chat/chat.html", {"form": form, "chats": chats})

@login_required(login_url=settings.LOGIN_URL)
def chat_delete_view(request, pk):
    current_user = request.user
    # if request.method != "POST":
    #     messages.error(request, "Invalid request method.")
    #     return redirect("home:home")  # Replace with your actual chat page name
    try:
        chat = Chat.objects.get(id=pk)
        chat_owner = chat.user
    except Chat.DoesNotExist:
        messages.error(request, "Chat does not exist!")
    else:
        if current_user.email_verified and current_user.token_verified:
            if current_user != chat_owner:
                messages.error(request, "Invalid request.")
            else:
                chat.delete()
                messages.success(request, "Chat has been deleted successfully.")
        else:
            messages.error(request, "Your account is not verified.")

    form = QuestionNDbotReply()
    chats = Chat.objects.order_by("time_stamp")
    return render(request, "chat/chat.html", {'form': form, "chats": chats})



