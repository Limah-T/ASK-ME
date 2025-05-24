from django import forms

class QuestionNDbotReply(forms.Form):
    user_message = forms.CharField(
        widget=forms.Textarea(attrs=
                              {'class': 'form-control', 
                               'style': 'height: 80px;',  # adjust the height as needed
                               'row': 3,
                               'placeholder': 'Type your message..'
                               },
                               ), 
                max_length=255, required=True, label="Type your message in the box 👉🏻")




