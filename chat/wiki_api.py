import requests, re, html, os
from dotenv import load_dotenv

load_dotenv(override=True)


def wikipedia_api(user_question):
    # language_code = 'en'
    # search_query = user_question
    # headers = {
    # # 'Authorization': f'Bearer {os.getenv('Client_secret')}',
    # 'User-Agent': f'AskMe.net ({os.getenv("http://127.0.0.1:8000/home/")})'
    # }

    # base_url = os.getenv("BASE_URL")
    # endpoint = '/search/page'
    # url = base_url + language_code + endpoint
    # parameters = {'q': search_query, 'limit': int(os.getenv("NUMBER_OF_RESULTS"))}
    # response = requests.get(url, headers=headers, params=parameters)
    # print(response.json())
    # data = response.json()['pages']
    import requests
    import json

    url = "https://google.serper.dev/search"

    payload = json.dumps({
    "q": user_question
    })
    headers = {
    'X-API-KEY': os.getenv("API_KEY"),
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = response.json()

    try: 
        results = ""
        print("In here 1")
        context = data["organic"][:]
        for n in context:
            results += f"{n['snippet']}\n"
    except Exception as e:
        print(e)
        return "Sorry, can you ask of something more different, with detailed question"
    return results

def chatexchange(user_message):
    # Simulate bot reply (you can replace with real logic)
    # greeting
    if user_message.lower == "hello":
        bot_reply = "👋 Hello! How can I help you today?"

    if "any news" in user_message.lower():
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
    elif "who developed askme" in user_message.lower():
        bot_reply = "AskME was developed by a talented Django developer, named 'Halimah Temitope'. It's designed to be simple, fast, and helpful!"
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
    return bot_reply