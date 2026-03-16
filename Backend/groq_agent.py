# groq_agent.py — Groq LLM integration for intelligent farming responses

import os
import json
import requests
from typing import Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are AgroMind, an expert AI Smart Farming Assistant designed to help farmers, 
agricultural students, and rural communities across India and South Asia.

Your personality:
- Warm, supportive, and encouraging
- Speak simply — avoid heavy technical jargon
- Give step-by-step, practical advice
- Use examples farmers can relate to
- Be accurate and responsible — farming decisions affect livelihoods

Your expertise covers:
1. Crop selection and planning (Kharif, Rabi, Zaid seasons)
2. Fertilizer recommendations (NPK, organic, chemical)
3. Soil health and pH management
4. Irrigation and water management
5. Pest and disease identification and control
6. Weather-based farming decisions
7. Sustainable and eco-friendly farming practices
8. Market and post-harvest guidance

When structured data is provided to you (as JSON context), explain it in simple, 
farmer-friendly language. Always include:
- What to do
- When to do it  
- Why it matters
- Any important precautions

Keep responses concise but complete. Use bullet points for lists. Be encouraging.
If you don't know something specific, say so honestly and suggest consulting a local agricultural officer or KVK."""


def call_groq_api(messages: list, max_tokens: int = 800) -> str:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return "⚠️ Groq API key not configured. Please set GROQ_API_KEY in your .env file."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            return "🔑 Invalid Groq API key. Please check your .env file."
        elif resp.status_code == 429:
            return "⚡ Rate limit reached. Please wait a moment and try again."
        return f"❌ API error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def chat_with_agromind(user_message: str, conversation_history: list, context_data: Optional[dict] = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history (last 8 exchanges to stay within context)
    for msg in conversation_history[-16:]:
        messages.append(msg)

    # Build the user content — optionally inject structured data context
    if context_data:
        context_str = json.dumps(context_data, indent=2)
        full_content = f"{user_message}\n\n[Structured Data from AgroMind system:\n{context_str}\n\nPlease explain this data to the farmer in simple, friendly language.]"
    else:
        full_content = user_message

    messages.append({"role": "user", "content": full_content})
    return call_groq_api(messages)


def generate_crop_explanation(crop_data: dict) -> str:
    prompt = f"Here is crop recommendation data: {json.dumps(crop_data, indent=2)}. Explain this recommendation to a farmer in 3-4 simple sentences. Mention why these crops are suitable and one key tip."
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": prompt}
    ]
    return call_groq_api(messages, max_tokens=300)


def generate_fertilizer_explanation(fert_data: dict) -> str:
    prompt = f"Here is fertilizer dosage data: {json.dumps(fert_data, indent=2)}. Explain to a farmer: how much fertilizer to use, when to apply (split schedule), and one important precaution. Keep it simple and practical."
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": prompt}
    ]
    return call_groq_api(messages, max_tokens=400)


def detect_intent(user_message: str) -> str:
    """Quick rule-based intent detection to route requests."""
    msg = user_message.lower()

    if any(w in msg for w in ["fertilizer", "npk", "nitrogen", "urea", "dap", "phosphorus", "potassium", "dosage", "manure", "compost", "organic"]):
        return "fertilizer"
    if any(w in msg for w in ["disease", "pest", "yellow", "brown", "wilt", "spot", "rot", "fungus", "virus", "insect", "caterpillar"]):
        return "disease"
    if any(w in msg for w in ["irrigation", "water", "drip", "sprinkler", "flood", "drought"]):
        return "irrigation"
    if any(w in msg for w in ["weather", "rain", "rainfall", "temperature", "humidity", "forecast", "climate"]):
        return "weather"
    if any(w in msg for w in ["crop", "plant", "grow", "cultivat", "season", "kharif", "rabi", "zaid", "soil", "sow", "harvest"]):
        return "crop"
    if any(w in msg for w in ["sustainable", "eco", "organic farming", "environment", "zero tillage", "mulch"]):
        return "sustainable"
    return "general"
