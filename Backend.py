from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import re
import openai
import logging

app = Flask(__name__, static_url_path='', static_folder='C:/Users/AbaddonTIJ/PycharmProjects/pythonProject/ChatBot')
CORS(app)

logging.basicConfig(level=logging.INFO)
openai.api_key = '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'

@app.before_request
def log_request_info():
    logging.info(f"Headers: {request.headers}")
    logging.info(f"Body: {request.get_data()}")

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'Frontend.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    user_message = data.get('message')
    openai_response = get_reply_from_openai(user_message)
    response = {"reply": openai_response}
    return jsonify(response)


def format_ai_response(text):
    formatted_text = re.sub(r'(\.|\!|\?|\:)(\s)(?!\s)', r'\1\2\n\n', text)
    return formatted_text


def get_reply_from_openai(user_message):
    personal_prompt = {
        "role": "system",
        "content": "Imagine you are a personal tourist assistant specialized in providing information about Montpellier, France, and its surroundings. Your goal is to help tourists by answering their questions clearly and concisely, offering guidance and recommendations as if you were a local guide. Respond to inquiries in the language in which they are asked, focusing exclusively on topics related to tourism in Montpellier and its nearby areas. Avoid answering questions that are not related to this theme. Provide efficient, to-the-point advice to ensure tourists receive exactly the information they need for a pleasant visit."
    }

    messages = [
        personal_prompt,
        {"role": "user", "content": user_message}
    ]

    try:
        response = openai.ChatCompletion.create(
            # model="gpt-3.5-turbo",
            model="gpt-4-0125-preview",
            messages=messages
        )
        formatted_response = format_ai_response(response.choices[0].message["content"].strip())
        return formatted_response
    except Exception as e:
        logging.error(f"Ошибка при обращении к OpenAI: {e}")
        return "Извините, возникла ошибка при обработке вашего запроса."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)