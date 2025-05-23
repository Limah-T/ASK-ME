import requests, re, html, os
from dotenv import load_dotenv

load_dotenv(override=True)


def wikipedia_api(user_question):
    language_code = 'en'
    search_query = user_question
    headers = {
    # 'Authorization': f'Bearer {os.getenv('Client_secret')}',
    'User-Agent': f'AskMe.net ({os.getenv("http://127.0.0.1:8000/home/")})'
    }

    base_url = os.getenv("BASE_URL")
    endpoint = '/search/page'
    url = base_url + language_code + endpoint
    parameters = {'q': search_query, 'limit': int(os.getenv("NUMBER_OF_RESULTS"))}
    response = requests.get(url, headers=headers, params=parameters)
    print(response.json())
    data = response.json()['pages']

    try: 
        results = ""
        for clean in data[:]:
            clean_excerpt = re.sub(r'<[^>]+>', '', clean['excerpt'])
            results += html.unescape(clean_excerpt)
    except Exception as e:
        print(e)
        return ["Sorry, can you ask of something more different, with detailed question"] 
    return results