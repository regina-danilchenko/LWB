import json
import requests
from config import API_KEY, FOLDER_ID

url ='https://translate.api.cloud.yandex.net/translate/v2/translate'

data = {
    "folderId": FOLDER_ID,
    "texts": [],
    "targetLanguageCode": ""
}

headers ={
    "Content-Type": 'application/json',
    "Authorization": f'Api-Key {API_KEY}'
}


def translate(word, language):
    data["texts"].clear()
    data["texts"].append(word)
    data["targetLanguageCode"] = language
    response = requests.post(url, data=json.dumps(data), headers=headers).json()
    return response["translations"][0]["text"], response["translations"][0]["detectedLanguageCode"]