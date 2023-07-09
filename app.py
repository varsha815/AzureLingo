import uuid
import requests
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, url_for, redirect
from azure_secrets import KEY, ENDPOINT, LOCATION


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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///translations.db'
db = SQLAlchemy(app)


class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.String(200))
    translated_text = db.Column(db.String(200))


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/translate", methods=['GET', 'POST'])
def translate():
    if request.method == 'POST':
        original_text = request.form.get('original-text')
        selected_language = request.form.get('language-select')
        translation = translate_text(original_text, selected_language)
        '''
        # Save the translation to the database
        new_translation = Translation(original_text=original_text, translated_text=translation)
        db.session.add(new_translation)
        db.session.commit()
        '''
        # Retrieve the history from the database, sorted by ID in descending order
        history = Translation.query.order_by(Translation.id.desc()).all()

        return render_template('translate.html', translation=translation, original_text=original_text, history=history)
    else:
        # Retrieve the history from the database, sorted by ID in descending order
        history = Translation.query.order_by(Translation.id.desc()).all()
        return render_template('translate.html', history=history)


@app.route("/save_translation", methods=['POST'])
def save_translation():
    original_text = request.form.get('original-text')
    translated_text = request.form.get('translated-text')

    if len(translated_text) > 2:
        translation_entry = Translation(original_text=original_text, translated_text=translated_text)
        db.session.add(translation_entry)
        db.session.commit()

    return redirect(url_for('translate'))


if __name__ == '__main__':
    app.run(debug=True, port=815)
