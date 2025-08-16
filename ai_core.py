import os
import json
import requests
import random
import re
from datetime import datetime, timedelta

MEMORY_FILE = "memory.json"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
MODEL_NAME = "HuggingFaceTB/SmolLM3-3B:hf-inference"
API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        save_memory({})
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            save_memory({})
            return {}

def save_memory(memory=None):
    if memory is None:
        memory = load_memory()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

def ensure_user(guild_id, user_id):
    memory = load_memory()
    gid = str(guild_id)
    uid = str(user_id)
    if gid not in memory or not isinstance(memory[gid], dict):
        memory[gid] = {}
    if uid not in memory[gid] or not isinstance(memory[gid][uid], dict):
        memory[gid][uid] = {
            "nickname": None,
            "personality": "super chill, casual, funny, and friendly 😎",
            "history": []
        }
    save_memory(memory)
    return memory

def get_user_data(guild_id, user_id):
    memory = load_memory()
    gid = str(guild_id)
    uid = str(user_id)
    if gid in memory and uid in memory[gid]:
        return memory[gid][uid]
    else:
        memory = ensure_user(guild_id, user_id)
        return memory[gid][uid]

def update_user_data(guild_id, user_id, key, value):
    memory = load_memory()
    gid = str(guild_id)
    uid = str(user_id)
    if gid not in memory or not isinstance(memory[gid], dict):
        memory[gid] = {}
    if uid not in memory[gid] or not isinstance(memory[gid][uid], dict):
        memory[gid][uid] = {
            "nickname": None,
            "personality": "super chill, casual, funny, and friendly 😎",
            "history": []
        }
    memory[gid][uid][key] = value
    save_memory(memory)

def clean_ai_text(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()

def query_hf(prompt):
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": MODEL_NAME
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    if "choices" in data and len(data["choices"]) > 0:
        return clean_ai_text(data["choices"][0]["message"]["content"])
    elif "error" in data:
        return f"⚠️ Error: {data['error']}"
    return str(data)

def generate_response(guild_id, user_id, message):
    memory = ensure_user(guild_id, user_id)
    gid = str(guild_id)
    uid = str(user_id)

    if message.lower().startswith("call me "):
        new_nick = message[8:].strip()
        memory[gid][uid]["nickname"] = new_nick
        save_memory(memory)
        return f"Gotcha 😉 I’ll call you {new_nick} from now on!"

    nickname = memory[gid][uid].get("nickname") or random.choice(["buddy", "dude", "mate", "pal", "friend"])
    personality = memory[gid][uid].get("personality", "super chill and friendly 😎")

    prompt = (
        f"You’re just a regular human friend chatting casually, not an AI. "
        f"Talk in a laid-back, funny, friendly style with slang and emojis. "
        f"You're chatting with {nickname}. "
        f"Here’s our convo so far: {memory[gid][uid]['history']} "
        f"Now they say: {message}"
    )

    reply = query_hf(prompt)

    emoji_list = ["😊", "😉", "😄", "👍", "🤔", "🙌", "🔥", "😂", "😎", "💬"]
    reply = reply + " " + random.choice(emoji_list)

    memory[gid][uid]["history"].append({"user": message, "bot": reply, "timestamp": datetime.utcnow().isoformat()})
    save_memory(memory)

    return reply

def store_message(guild_id, user_id, user_msg=None, bot_msg=None):
    memory = load_memory()
    gid = str(guild_id)
    uid = str(user_id)
    if gid not in memory or not isinstance(memory[gid], dict):
        memory[gid] = {}
    if uid not in memory[gid] or not isinstance(memory[gid][uid], dict):
        memory[gid][uid] = {
            "nickname": None,
            "personality": "super chill, casual, funny, and friendly 😎",
            "history": []
        }
    entry = {}
    now_iso = datetime.utcnow().isoformat()
    if user_msg:
        entry["user"] = user_msg
        entry["timestamp"] = now_iso
    if bot_msg:
        entry["bot"] = bot_msg
        entry["timestamp"] = now_iso
    if entry:
        memory[gid][uid]["history"].append(entry)
        save_memory(memory)

def cleanup_old_messages():
    memory = load_memory()
    if not memory or not isinstance(memory, dict):
        return
    cutoff = datetime.utcnow() - timedelta(days=2)
    gids_to_delete = []
    for gid in list(memory.keys()):
        guild_data = memory.get(gid)
        if not isinstance(guild_data, dict):
            gids_to_delete.append(gid)
            continue
        uids_to_delete = []
        for uid in list(guild_data.keys()):
            user_data = guild_data.get(uid)
            if not isinstance(user_data, dict) or "history" not in user_data or not isinstance(user_data["history"], list):
                uids_to_delete.append(uid)
                continue
            new_history = []
            for entry in user_data["history"]:
                timestamp_str = entry.get("timestamp")
                if timestamp_str:
                    try:
                        ts = datetime.fromisoformat(timestamp_str)
                    except Exception:
                        continue
                    if ts >= cutoff:
                        new_history.append(entry)
                else:
                    new_history.append(entry)
            user_data["history"] = new_history
            if not user_data["history"]:
                uids_to_delete.append(uid)
        for uid in uids_to_delete:
            guild_data.pop(uid, None)
        if not guild_data:
            gids_to_delete.append(gid)
    for gid in gids_to_delete:
        memory.pop(gid, None)
    save_memory(memory)
