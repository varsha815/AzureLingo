from flask import Flask, render_template, request
from azure_secrets import KEY, ENDPOINT, LOCATION
import requests, uuid


def translate_text(original_text, target_language):
    path = '/translate?api-version=3.0'
    target_language_parameter = '&to=' + target_language
    constructed_url = ENDPOINT + path + target_language_parameter

    # Set up the header information, which includes our subscription key
    headers = {
        'Ocp-Apim-Subscription-Key': KEY,
        'Ocp-Apim-Subscription-Region': LOCATION,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    body = [{'text': original_text}]
    translator_request = requests.post(constructed_url, headers=headers, json=body)
    translator_response = translator_request.json()
    translated_text = translator_response[0]['translations'][0]['text']

    return translated_text


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/translate", methods=['GET', 'POST'])
def translate():
    if request.method == 'POST':
        original_text = request.form.get('original-text')
        selected_language = request.form.get('color-select')
        translation = translate_text(original_text, selected_language)
        return render_template('translate.html', translation=translation, original_text=original_text)
    else:
        return render_template('translate.html')


if __name__ == '__main__':
    app.run(debug=True, port=815)
