import requests, re, html, os
from dotenv import load_dotenv

load_dotenv(override=True)


# def wikipedia_api(user_question):
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
    # import requests
    # import json

    # url = "https://google.serper.dev/search"

    # payload = json.dumps({
    # "q": user_question
    # })
    # headers = {
    # 'X-API-KEY': os.getenv("API_KEY"),
    # 'Content-Type': 'application/json'
    # }

    # response = requests.request("POST", url, headers=headers, data=payload)

    # data = response.json()

    # try: 
    #     results = ""
    #     print("In here 1")
    #     context = data["organic"][:]
    #     for n in context:
    #         results += f"{n['snippet']}\n"
    # except Exception as e:
    #     print(e)
    #     return "Sorry, can you ask of something more different, with detailed question"
    # return results
import re

def summarize_snippets(snippets, max_sentences=20):
    # Collect sentences from snippets
    sentences = []
    for snippet in snippets:
        # Split snippet into sentences using simple regex
        sents = re.split(r'(?<=[.!?])\s+', snippet.strip())
        for sent in sents:
            # Clean sentence
            clean_sent = sent.strip()
            if clean_sent and clean_sent not in sentences:
                sentences.append(clean_sent)
            if len(sentences) >= max_sentences:
                break
        if len(sentences) >= max_sentences:
            break
    
    # Join selected sentences with space or line breaks
    return " ".join(sentences)


def wikipedia_api(user_question):
    import os
    import requests
    import json

    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": user_question,
                          "num": 100
                        })
    headers = {
        'X-API-KEY': os.getenv("API_KEY"),
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()

        # Extract snippets from top organic results (limit 3)
        snippets = [item.get('snippet', '') for item in data.get('organic', [])[:3]]
        summary = summarize_snippets(snippets)

        if not summary:
            return "Sorry, I couldn't find a clear answer. Could you please be more specific?"

        return summary

    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, something went wrong. Can you ask something different or more specific?"


def chatexchange(user_message):
    # Simulate bot reply (you can replace with real logic)
    # greeting
    if user_message.lower == "hello":
        bot_reply = "👋 Hello! How can I help you today?"

    if "any news" in user_message.lower():
        bot_reply = (
            "Sure! Here's the latest update:\n\n"
            "- Our new AI-powered helpdesk feature is now live!\n"
            "- 🌐 We're working on expanding AskME support to multiple languages.\n"
            "- Stay tuned for our upcoming integration with WhatsApp for seamless chat.\n\n"
        
        )
    # Askme purpose
    elif "what is askme" in user_message.lower():
        bot_reply = (
            "AskME is a simple and intelligent chatbot platform designed to help users get quick, "
            "relevant answers to their questions.\n\n"
            "Whether you're looking for information, assistance with common tasks, or just want to explore what "
            "a rule-based chatbot can do, AskME is here for you.\n\n"
            "Built with Django, AskME uses a set of predefined rules and logic to respond to your queries, making it "
            "fast, lightweight, and easy to expand as needed.\n\n"

        )
    # who created askme
    elif "who developed askme" in user_message.lower(): 
        bot_reply = "AskME was developed by a talented Django developer, named 'Halimah Temitope'. It's designed to be simple, fast, and helpful!"

    elif "who developed this chatbot?" in user_message.lower():
        bot_reply = "AskME was developed by Halimah Temitope, a talented Django developer. It’s designed to be simple, fast, and helpful!"

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