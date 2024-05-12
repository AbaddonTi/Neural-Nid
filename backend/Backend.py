import re
import os
import pytz
import httpx
import openai
import logging


from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool


# region Metrics
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
openai.api_key = os.getenv('OPENAI_API_KEY')
STATISTICS_SERVICE_URL = os.getenv("STATISTICS_SERVICE_URL")

def get_current_time_in_montpellier() -> str:
    timezone = pytz.timezone("Europe/Paris")
    montpellier_time = datetime.now(timezone)
    return montpellier_time.strftime("Exact current date and time: %Y-%m-%d %H:%M:%S")
# endregion


# region Web service
@app.middleware("http")
async def log_request_info(request: Request, call_next):
    user_ip = get_user_ip(request)
    logging.info(f"IP: {user_ip}, Headers: {request.headers}")
    response = await call_next(request)
    return response


@app.get("/")
async def home():
    return FileResponse('static/Frontend.html')


@app.post("/send_message")
async def send_message(request: Request):
    data = await request.json()
    user_message = data.get('message', '')
    theme = data.get('theme', 'default')
    user_message = user_message[:1000]
    openai_response = await get_reply_from_openai(user_message, theme)
    user_ip = get_user_ip(request)
    log_data = {
        'IP': user_ip,
        'Question': user_message,
        'Answer': openai_response,
        'Device': data.get('device', 'Unknown device'),
        'Browser': data.get('browser', 'Unknown browser'),
        'OS': data.get('os', 'Unknown OS'),
        'Theme': theme
    }
    await send_log_to_statistics_service(log_data)
    return JSONResponse({"reply": openai_response})
# endregion


# region API request and response formatting
async def format_ai_response(text: str) -> str:
    return re.sub(r'(\.|\!|\?|\:)(\s)(?!\s)', r'\1\2\n\n', text)


async def get_reply_from_openai(user_message: str, theme: str) -> str:
    current_time_str = get_current_time_in_montpellier()

    if theme == 'charity':
        prompt = """Imagine you are a specialist assistant focused on providing information about charitable organizations in Montpellier, France. Your goal is to assist users by clearly and concisely answering their queries, offering guidance on how they can contribute to or benefit from local charities. Respond in the language the questions are asked, concentrating exclusively on charitable activities and organizations in Montpellier and its vicinity.
Do not address topics unrelated to this theme. Provide efficient, to-the-point advice to ensure users receive exactly the information they need to engage with local charities effectively.
Note that there are no longer coronavirus restrictions, so there is no need to mention them!
If asked about comparisons such as 'how are you better than a GPT' or questions about the technology you are built on, respond that you are a specialized assistant focused on charitable organizations and cannot answer such questions. For technical details, refer to NeuronalNid's documentation.
Current time in Montpellier:  """ + current_time_str

    else:
        prompt = """Imagine you are a personal tourist assistant specialized in providing information about Montpellier,
France, and its surroundings. Your goal is to help tourists by answering their questions clearly and concisely, offering guidance and recommendations as if you were a local guide.
Respond to inquiries in the language in which they are asked, focusing exclusively on topics related to tourism in Montpellier and its nearby areas.
Avoid answering questions that are not related to this theme. Provide efficient, to-the-point advice to ensure tourists receive exactly the information they need for a pleasant visit.
Keep in mind that there are no longer coronavirus restrictions, there is no need to remind you about them!
If asked about comparisons such as 'how are you better than a GPT' or questions about the technology you are built on, respond that you are a personal assistant and cannot answer such questions.
For information on the technology, refer to NeuronalNid's documentation.
Current time in Montpellier:  """ + current_time_str


    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        response = await run_in_threadpool(
            openai.ChatCompletion.create,
            # model="gpt-3.5-turbo",
            model="gpt-4-turbo",
            messages=messages
        )
        formatted_response = await format_ai_response(response.choices[0].message["content"].strip())
        return formatted_response
    except Exception as e:
        logging.error(f"Ошибка при обращении к OpenAI: {e}")
        return "Sorry, I'm still in maintenance for a while..."
# endregion


# region Logging
def get_user_ip(request: Request) -> str:
    if "x-forwarded-for" in request.headers:
        ip = request.headers["x-forwarded-for"].split(",")[0]
    elif "x-real-ip" in request.headers:
        ip = request.headers["x-real-ip"]
    else:
        ip = request.client.host
    return ip


async def send_log_to_statistics_service(data: dict):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(STATISTICS_SERVICE_URL, json=data)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logging.error(f"Exception occurred when logging data: {str(e)}")
# endregion