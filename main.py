from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from chatbot import generate_reply

app = FastAPI()

# Mount folders
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Memory file
MEMORY_FILE = "memory_store.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def generate_prompt(user_id, user_message, memory):
    user_data = memory.get(user_id, {})
    name = user_data.get("name", "there")
    facts = user_data.get("facts", [])

    facts_text = "- " + "\n- ".join(facts) if facts else "None yet"
    lowered_msg = user_message.lower().strip()

    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]

    if lowered_msg in greetings:
        return f"Reply casually and friendly to the user named {name}, who just greeted you by saying \"{user_message}\"."

    base_prompt = f"""
You are an emotionally intelligent chatbot named Claude.
Speak warmly and like a caring human friend.

The user's name is {name}.
Only use facts that the user has shared previously — do not guess.

Here are known facts about the user:
{facts_text}

Now, the user says: "{user_message}"
Respond in a short, kind, human-like way. Avoid repetition.
""".strip()

    return base_prompt


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "default_user")
    user_message = data["message"]

    memory = load_memory()
    user_data = memory.setdefault(user_id, {})

    # Name handling
    if "my name is" in user_message.lower():
        name = user_message.lower().split("my name is")[-1].strip().split()[0].capitalize()
        user_data["name"] = name

    # Semantic fact storage: store any sentence that includes "I", "my", or "me"
    facts = user_data.setdefault("facts", [])
    lowered = user_message.lower()

    if any(keyword in lowered for keyword in ["i ", "my ", "me"]):
        facts.append(user_message.strip())

    user_data["facts"] = list(set(facts))  # remove duplicates
    memory[user_id] = user_data
    save_memory(memory)

    prompt = generate_prompt(user_id, user_message, memory)
    response_text = generate_reply(prompt)

    return JSONResponse({"response": response_text})
