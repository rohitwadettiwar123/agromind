# app.py — AgroMind Flask Backend Server
import os
import json
from datetime import datetime, UTC
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from logic.crop_logic import (
    get_crops_by_season, get_crops_by_soil, get_crops_by_weather,
    identify_disease, get_all_seasons, get_all_soil_types
)

from logic.fertilizer_logic import (
    calculate_npk_dosage, get_organic_recommendations,
    get_soil_health_advice, list_available_crops
)

from logic.weather_logic import (
    get_irrigation_schedule, get_season_weather_advice,
    get_sustainable_practices, classify_weather_risk
)

from groq_agent import chat_with_agromind, detect_intent

load_dotenv()
app = Flask(__name__)
CORS(app)

# In-memory conversation store (per session_id)
conversation_store: dict = {}


def get_history(session_id: str) -> list:
    return conversation_store.get(session_id, [])

def update_history(session_id: str, role: str, content: str):
    if session_id not in conversation_store:
        conversation_store[session_id] = []
    conversation_store[session_id].append({"role": role, "content": content})
    # Keep last 20 messages
    if len(conversation_store[session_id]) > 20:
        conversation_store[session_id] = conversation_store[session_id][-20:]


# ─────────────────────────────────────────────
# MAIN CHAT ENDPOINT
# ─────────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_message = data.get("message", "").strip()
        session_id   = data.get("session_id", "default")

        if not user_message:
            return jsonify({"error": "Message cannot be empty."}), 400
        if len(user_message) > 2000:
            return jsonify({"error": "Message too long. Please keep it under 2000 characters."}), 400

        intent = detect_intent(user_message)
        context_data = None

        # ── Auto-enrich with structured data based on intent ──
        msg_lower = user_message.lower()

        if intent == "crop":
            for season in ["kharif", "rabi", "zaid"]:
                if season in msg_lower:
                    context_data = get_crops_by_season(season)
                    break
            if not context_data:
                for soil in get_all_soil_types():
                    if soil in msg_lower:
                        context_data = get_crops_by_soil(soil)
                        break

        elif intent == "fertilizer":
            for crop in list_available_crops():
                if crop.lower() in msg_lower:
                    # Default to 1 hectare if not specified
                    area = 1.0
                    import re
                    area_match = re.search(r"(\d+\.?\d*)\s*(hectare|ha|acre)", msg_lower)
                    if area_match:
                        area = float(area_match.group(1))
                        if "acre" in area_match.group(2):
                            area = area * 0.405
                    context_data = calculate_npk_dosage(crop, area)
                    break

        elif intent == "disease":
            symptoms = ["yellow_leaves", "brown_spots", "white_powder", "wilting",
                        "black_spots", "holes_in_leaves", "rust_orange_patches", "stunted_growth"]
            for sym in symptoms:
                sym_readable = sym.replace("_", " ")
                if any(w in msg_lower for w in sym.split("_")):
                    context_data = identify_disease(sym_readable)
                    break

        elif intent == "irrigation":
            for crop in list(get_irrigation_schedule.__globals__['IRRIGATION_SCHEDULE'].keys() if hasattr(get_irrigation_schedule, '__globals__') else []):
                if crop.lower() in msg_lower:
                    context_data = get_irrigation_schedule(crop)
                    break

        elif intent == "weather":
            for season in ["kharif", "rabi", "zaid"]:
                if season in msg_lower:
                    context_data = get_season_weather_advice(season)
                    break

        history = get_history(session_id)
        bot_reply = chat_with_agromind(user_message, history, context_data)

        update_history(session_id, "user",      user_message)
        update_history(session_id, "assistant", bot_reply)

        return jsonify({
            "reply":      bot_reply,
            "intent":     intent,
            "context":    context_data,
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": session_id,
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ─────────────────────────────────────────────
# CROP ADVICE ENDPOINT
# ─────────────────────────────────────────────
@app.route("/crop-advice", methods=["POST"])
def crop_advice():
    try:
        data     = request.get_json(force=True)
        season   = data.get("season", "").strip()
        soil     = data.get("soil_type", "").strip()
        rainfall = data.get("rainfall", "").strip()
        temp     = data.get("temperature", "").strip()

        result = {}
        if season:
            result["by_season"] = get_crops_by_season(season)
        if soil:
            result["by_soil"] = get_crops_by_soil(soil)
        if rainfall and temp:
            result["by_weather"] = get_crops_by_weather(rainfall, temp)

        if not result:
            return jsonify({"error": "Provide at least one of: season, soil_type, or rainfall+temperature."}), 400

        return jsonify({"status": "success", "data": result, "timestamp": datetime.now(UTC).isoformat()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# FERTILIZER CALCULATOR ENDPOINT
# ─────────────────────────────────────────────
@app.route("/fertilizer-calculator", methods=["POST"])
def fertilizer_calculator():
    try:
        data  = request.get_json(force=True)
        crop  = data.get("crop", "").strip()
        area  = float(data.get("area_hectare", 1.0))
        organic_only = data.get("organic_only", False)

        if not crop:
            return jsonify({"error": "Crop name is required.", "available_crops": list_available_crops()}), 400

        if organic_only:
            result = get_organic_recommendations("N")
        else:
            result = calculate_npk_dosage(crop, area)

        return jsonify({"status": "success", "data": result, "timestamp": datetime.now(UTC).isoformat()})
    except ValueError:
        return jsonify({"error": "area_hectare must be a number."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# WEATHER TIPS ENDPOINT
# ─────────────────────────────────────────────
@app.route("/weather-tips", methods=["POST"])
def weather_tips():
    try:
        data    = request.get_json(force=True)
        season  = data.get("season", "").strip()
        temp    = data.get("temperature_c")
        rain    = data.get("rainfall_mm")
        crop    = data.get("crop", "").strip()

        result = {}
        if season:
            result["season_advice"] = get_season_weather_advice(season)
        if temp is not None and rain is not None:
            result["risk_assessment"] = classify_weather_risk(float(temp), float(rain))
        if crop:
            result["irrigation"] = get_irrigation_schedule(crop)
        result["sustainable_practices"] = get_sustainable_practices(4)

        return jsonify({"status": "success", "data": result, "timestamp": datetime.now(UTC).isoformat()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# HEALTH & INFO ENDPOINTS
# ─────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "agent": "AgroMind", "version": "1.0.0", "timestamp": datetime.now(UTC).isoformat()})

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "AgroMind API",
        "description": "AI Smart Farming Assistant",
        "endpoints": ["/chat", "/crop-advice", "/fertilizer-calculator", "/weather-tips", "/health"],
        "powered_by": "Groq LLaMA3 + Python Rule Engine"
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    print(f"\n🌱 AgroMind Server starting on http://localhost:{port}")
    print("📋 Open frontend/index.html in your browser to start chatting!\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
