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