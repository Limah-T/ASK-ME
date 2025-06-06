# import requests, re, html
from dotenv import load_dotenv

load_dotenv(override=True)
import cohere, os
def cohere_api(content):

    co = cohere.ClientV2(api_key=os.getenv("CO_API_KEY"))
    response = co.chat(
        model=os.getenv("CO_MODEL_COMMAND"),
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
    )

    print(response.message.content[0].text)
    return response.message.content[0].text

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
# import re

# def organize_snippets(snippets, max_results=100):
#     """Organize snippets into a nicely formatted numbered list."""
#     # Filter out any empty snippets
#     filtered_snippets = [s.strip() for s in snippets if s.strip()]
    
#     # Limit to max_results items
#     bullet_list = []
#     for i, snippet in enumerate(filtered_snippets[:max_results], start=1):
#         bullet_list.append(f"{i}. {snippet}")
    
#     # Join with two newlines between items for readability
#     return "\n\n".join(bullet_list)


# def wikipedia_api(user_question):
#     import os
#     import requests
#     import json

#     url = "https://google.serper.dev/search"
#     # Use an environment variable to set the number of desired results; default to 100 if not set
#     num_results = int(os.getenv('NUMBER_OF_RESULTS', '100'))
#     payload = json.dumps({
#         "q": user_question,
#         "num": num_results
#     })
#     headers = {
#         'X-API-KEY': os.getenv("API_KEY"),
#         'Content-Type': 'application/json'
#     }

#     try:
#         response = requests.post(url, headers=headers, data=payload)
#         data = response.json()

#         # Extract snippets from all organic results (if available)
#         snippets = [item.get('snippet', '') for item in data.get('organic', [])]
        
#         if not snippets:
#             return "Sorry, I couldn't find a clear answer. Could you please be more specific?"

#         # Organize the snippets into a clean, readable list
#         organized_summary = organize_snippets(snippets, max_results=num_results)
#         return organized_summary

#     except Exception as e:
#         print(f"Error: {e}")
#         return "Sorry, something went wrong. Can you ask something different or more specific?"

def action(user_message):
    # Simulate bot reply (you can replace with real logic)
    # greeting
    # AskME basic info and purpose
    if "what is askme" in user_message.lower():
        bot_reply = (
            "AskME is a smart chatbot web app, built with Django, and designed to help users get quick and relevant answers. "
            "It’s simple, fast, and works using both rule-based and AI-powered logic."
        )

    elif "how does askme work" in user_message.lower():
        bot_reply = (
            "AskME works by first checking if your message matches a predefined rule (like help or login issues). "
            "If not, it uses AI to understand and respond. This keeps responses fast, but also smart when needed."
        )

    elif "who created askme" in user_message.lower() or "who developed askme" in user_message.lower() or "who developed this chatbot" in user_message.lower() or "who built askme" in user_message.lower():
        bot_reply = (
            "AskME was developed by Halimah Temitope, a Django backend engineer. "
            "It was created to showcase a hybrid chatbot system using Django, rule-based logic, and AI integration."
        )
    elif "reset my password" in user_message.lower() or "forgot password" in user_message.lower():
        bot_reply = "To reset your password, go to the login page and click on 'Forgot Password'. A reset link will be sent to your email."

    elif "change my password" in user_message.lower():
        bot_reply = "To change your password, log in, click on change password in the navbar section, and update your password."

    # elif "get the api" in user_message.lower() or "api for this chatbot" in user_message.lower() or "access the api" in user_message.lower():
    #     bot_reply = (
    #         "To get the API for this chatbot, please visit the developer section in the dashboard or contact support for access credentials."
    #     )


    elif "who developed askme" in user_message.lower() or "who created this chatbot" in user_message.lower():
        bot_reply = "AskME was developed by Halimah Temitope, a Django backend engineer focused on building intelligent and efficient web tools."

    elif "how does askme work" in user_message.lower():
        bot_reply = (
            "AskME works as a rule-based chatbot. It reads your message and compares it with a set of predefined patterns "
            "to return relevant answers. It’s fast and ideal for answering web app–related questions."
        )

    elif "how do i use askme" in user_message.lower():
        bot_reply = (
            "Using AskME is simple. Just type your question or task in the chat, and the bot will respond with helpful answers. "
           
        )
    elif "who are you" in user_message.lower() or "what are you" in user_message.lower():
        bot_reply = (
        "I'm AskME — a Django-based chatbot designed to help users quickly find answers to common questions on this web app."
    )


    elif "help" in user_message.lower():
        bot_reply = (
            "You can ask me things like:\n"
            "- What is AskME?\n"
            "- Who built AskME?\n"
            "- How do I reset my password?\n"
            "- How do I change my password?\n"
            "- How do I get the API for this chatbot?\n"
            "- How does AskME work?\n"
        )
    else:
        bot_reply = cohere_api(content=user_message)
        
    return bot_reply