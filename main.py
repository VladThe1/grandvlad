from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv
from pathlib import Path

# Charger le fichier .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configurer l'application FastAPI
app = FastAPI()

# Autoriser les requêtes locales (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dossier des templates HTML
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(data: dict):
    message = data.get("message", "")
    if not message:
        return {"response": "Message vide."}

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}],
        project=os.getenv("OPENAI_PROJECT_ID")
    )

    return {"response": completion.choices[0].message.content}

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import os
from pathlib import Path

# Charger la clé et le projet
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")

if not api_key or not project_id:
    raise ValueError("❌ Clé API ou ID de projet manquant dans le fichier .env")

# Initialiser le client avec projet
client = OpenAI(api_key=api_key, project=project_id)

app = FastAPI(title="Assistant Étudiant IA")

class Question(BaseModel):
    message: str

@app.post("/ask")
async def ask_ia(request: Question):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un assistant personnel pour étudiants : organisé, motivant et drôle."},
                {"role": "user", "content": request.message}
            ]
        )
        answer = response.choices[0].message.content
        return {"response": answer}

    except OpenAIError as e:
        return {"error": f"⚠️ Erreur OpenAI : {str(e)}"}

    except Exception as e:
        return {"error": f"⚠️ Erreur inattendue : {str(e)}"}

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import os
from pathlib import Path

# Charger la clé et le projet
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")

if not api_key or not project_id:
    raise ValueError("❌ Clé API ou ID de projet manquant dans le fichier .env")

# Initialiser le client avec projet
client = OpenAI(api_key=api_key, project=project_id)

app = FastAPI(title="Assistant Étudiant IA")

class Question(BaseModel):
    message: str

@app.post("/ask")
async def ask_ia(request: Question):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un assistant personnel pour étudiants : organisé, motivant et drôle."},
                {"role": "user", "content": request.message}
            ]
        )
        answer = response.choices[0].message.content
        return {"response": answer}

    except OpenAIError as e:
        return {"error": f"⚠️ Erreur OpenAI : {str(e)}"}

    except Exception as e:
        return {"error": f"⚠️ Erreur inattendue : {str(e)}"}

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import openai, os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(data: dict):
    message = data.get("message", "")
    if not message:
        return {"response": "Message vide."}
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}],
    )
    return {"response": completion.choices[0].message.content}
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
import uuid, os, openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Dictionnaire pour stocker les conversations par session
conversations = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())  # génère un ID unique
    response = HTMLResponse(open("templates/index.html").read())
    response.set_cookie(key="session_id", value=session_id)
    return response

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    session_id = request.cookies.get("session_id")
    if not session_id:
        return {"response": "Session invalide"}

    if session_id not in conversations:
        conversations[session_id] = []

    conversations[session_id].append({"role": "user", "content": message})

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversations[session_id]
        )
        reply = completion.choices[0].message.content
        conversations[session_id].append({"role": "assistant", "content": reply})
        return {"response": reply}
    except Exception as e:
        print(e)
        return {"response": "⚠️ Erreur avec OpenAI."}
