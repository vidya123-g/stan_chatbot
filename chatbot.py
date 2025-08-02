import requests
import os

# Put your OpenRouter API key here
OPENROUTER_API_KEY = "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"  # ← replace with your real key

def generate_reply(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://openrouter.ai",  # Required
        "Content-Type": "application/json"
    }

    data = {
        "model": "anthropic/claude-3-haiku",
        "messages": [
            {"role": "system", "content": "You are a friendly emotional assistant that remembers the user's preferences and always responds in a human-like tone."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error] Failed to get response: {str(e)}"
