import json
import requests
import time
import jwt

def get_iam_token(service_account_key_path):
    with open(service_account_key_path, 'r') as f:
        obj = f.read()
        obj = json.loads(obj)
        key_id = obj['id']
        service_account_id = obj['service_account_id']
        private_key = obj['private_key']

    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 3600
    }

    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )

    # Запись ключа в файл
    with open('jwt_token.txt', 'w') as j:
        j.write(encoded_token)

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'jwt': encoded_token
    }

    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()['iamToken']
    else:
        print("Ошибка при получении токена:", response.text)

API_URL = "https://translate.api.cloud.yandex.net/translate/v2/translate"
IAM_TOKEN = get_iam_token('translator_key.json')

def yandex_translate(text, source_lang, target_lang):
    headers = {
        "Authorization": f"Bearer {IAM_TOKEN}"
    }

    data = {
        "texts": [text],
        "sourceLanguageCode": source_lang,
        "targetLanguageCode": target_lang
    }

    response = requests.post(API_URL, json=data, headers=headers)

    if response.status_code == 200:
        translations = response.json().get("translations", [])
        if translations:
            return translations[0]["text"]
        else:
            return "Ошибка: пустой ответ от сервиса перевода"
    else:
        raise Exception(f"Ошибка API Яндекс Переводчика: {response.text}")