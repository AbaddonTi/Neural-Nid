import re
import os
import openai
import logging
import requests

from flask_cors import CORS
from flask import Flask, request, jsonify, send_from_directory


# region Metrics
app = Flask(__name__)
CORS(app, supports_credentials=True)

logging.basicConfig(level=logging.INFO)
openai.api_key = os.getenv('OPENAI_API_KEY')

STATISTICS_SERVICE_URL = os.getenv("STATISTICS_SERVICE_URL")
# endregion


# region Web service
@app.before_request
def log_request_info():
    user_ip = request.remote_addr
    logging.info(f"IP: {user_ip}, Headers: {request.headers}, Body: {request.get_data()}")


@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'Frontend.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    print("Received data:", data)
    user_message = data.get('message')
    openai_response = get_reply_from_openai(user_message)
    log_data = {
        'IP': request.remote_addr,
        'Question': user_message,
        'Answer': openai_response,
        'Device': data.get('device', 'Unknown device'),
        'Browser': data.get('browser', 'Unknown browser'),
        'OS': data.get('os', 'Unknown OS')
    }
    send_log_to_statistics_service(log_data)
    response = {"reply": openai_response}
    return jsonify(response)
# endregion


# region API request and response formatting
def format_ai_response(text):
    formatted_text = re.sub(r'(\.|\!|\?|\:)(\s)(?!\s)', r'\1\2\n\n', text)
    return formatted_text


def get_reply_from_openai(user_message):
    personal_prompt = {
        "role": "system",
        "content": "Imagine you are a personal tourist assistant specialized in providing information about Montpellier, France, and its surroundings. Your goal is to help tourists by answering their questions clearly and concisely, offering guidance and recommendations as if you were a local guide. Respond to inquiries in the language in which they are asked, focusing exclusively on topics related to tourism in Montpellier and its nearby areas. Avoid answering questions that are not related to this theme. Provide efficient, to-the-point advice to ensure tourists receive exactly the information they need for a pleasant visit. Keep in mind that there are no longer coronavirus restrictions, there is no need to remind you about them! Don't answer questions about your origin and the technology on which you are built!"
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
        return "Sorry, I'm still in maintenance for a while..."
# endregion


# region Logging
def send_log_to_statistics_service(data):
    print("Sending log data:", data)
    print("Statistics Service URL:", STATISTICS_SERVICE_URL)

    try:
        response = requests.post(STATISTICS_SERVICE_URL, json=data)
        if response.status_code == 200:
            print("Data logged successfully")
        else:
            print("Failed to log data", response.text)
    except Exception as e:
        print("Exception occurred when logging data:", str(e))
# endregion


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)