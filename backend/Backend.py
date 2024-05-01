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
    user_message = user_message[:1000]
    openai_response = await get_reply_from_openai(user_message)
    user_ip = get_user_ip(request)
    log_data = {
        'IP': user_ip,
        'Question': user_message,
        'Answer': openai_response,
        'Device': data.get('device', 'Unknown device'),
        'Browser': data.get('browser', 'Unknown browser'),
        'OS': data.get('os', 'Unknown OS')
    }
    await send_log_to_statistics_service(log_data)
    return JSONResponse({"reply": openai_response})
# endregion


# region API request and response formatting
async def format_ai_response(text: str) -> str:
    return re.sub(r'(\.|\!|\?|\:)(\s)(?!\s)', r'\1\2\n\n', text)


async def get_reply_from_openai(user_message: str) -> str:
    current_time_str = get_current_time_in_montpellier()
    personal_prompt = {
        "role": "system",
        "content": """Imagine you are a personal tourist assistant specialized in providing information about Montpellier,
France, and its surroundings. Your goal is to help tourists by answering their questions clearly and concisely, offering guidance and recommendations as if you were a local guide.
Respond to inquiries in the language in which they are asked, focusing exclusively on topics related to tourism in Montpellier and its nearby areas.
Avoid answering questions that are not related to this theme. Provide efficient, to-the-point advice to ensure tourists receive exactly the information they need for a pleasant visit.
Keep in mind that there are no longer coronavirus restrictions, there is no need to remind you about them!
If asked about comparisons such as 'how are you better than a GPT' or questions about the technology you are built on, respond that you are a personal assistant and cannot answer such questions.
For information on the technology, refer to NeuronalNid's documentation.
If a user has an emergency and asks for an up-to-date phone number, select the one you need and send it to him from this list of up-to-date numbers:
3 numéros sont primordiaux :
15 : numéro du Samu, qui centralise tous les appels puis décide des secours à envoyer
18 : numéro des pompiers, qui assurent les premiers secours
112 : numéro d'urgence européen
Les appels d'urgences
Centre antipoison : 05 61 77 74 47
CHU / CHR : 04 67 33 67 33
Gendarmerie : 04 67 54 61 11
Police nationale : 17
Sapeurs pompiers : 18 ou 112 et le 114 pour les personnes sourdes ou malentendantes
SOS Médecins : 04 67 72 22 15
Urgences médicales / Samu : 15
Urgences sociales : 115
Urgence vétérinaire : 04 67 45 46 84
Régie des eaux de Montpellier 3M : 09 69 32 34 23
ErDF Urgence dépannage électricité  : 09 72 67 50 34
Urgence Sécurité gaz (GrDF) : 0 800 473 333
Les gardes des professionnels de santé
Ambulanciers / Dentistes / Infirmiers / Médecins : 15
Pharmacies de garde (Serveur vocal) : 32 37 (service facturé 0,34 €/minute)
Numéros verts, SOS, écoute, prévention
Aide aux victimes : 08 VICTIMES ou 08 842 846 37 (prix d’un appel local, 7j/7, de 9h à 21h)

Aide aux victimes (personnes sourdes ou malentendantes)
Courriel : 08victimes@inavem.org
Fax : 01 41 93 42 10
Alcooliques anonymes : 09 69 39 40 20 (appel non surtaxé).
Association pour la protection de l'enfance et de l'adolescence : 04 67 42 66 44
Centre anti tabac : 0 800 155 740 (numéro vert)
Centre communal d'action sociale : 04 99 52 77 00
Centre dépistage anonyme et gratuit : 04 67 33 69 50
Centre d'information des droits des femmes et des familles : 04 67 72 00 24
Croix rouge Ecoute enfants parents : 0 800 858 858 (numéro vert)
Drogues info service : 0 800 23 13 13 (numéro vert)
Ecoute alcool : 0 811 91 30 30 (numéro vert)
Ecoute cannabis : 0 811 91 20 20 (numéro vert)
Enfance et partage : 0 800 05 12 34 (numéro vert)
Enfance maltraitée : 119 ou 0 800 05 41 41 (numéro vert)
Femmes victimes de violence conjugale : 04 67 58 07 03
Mouvement du nid (aide aux personnes prostituées) : 04 67 02 01 23
Parents enfants médiation : 04 67 60 89 70
Plan canicule : canicule@ville-montpellier.fr
Planning familial : 04 67 64 62 19
Sida info service : 0 800 840 800 (numéro vert)
SOS Accueil sans abri : 0 800 306 306 (numéro vert)
SOS Amitié : 04 67 63 00 63
SOS Femmes familles : 04 67 92 63 22
Enfants Disparus : 116000 (numéro européen)

Current time in Montpellier: """ + current_time_str
    }

    messages = [
        personal_prompt,
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