# weather_logic.py — Weather-based crop planning & irrigation logic

IRRIGATION_SCHEDULE = {
    "Paddy":     {"interval_days": 3,  "method": "Flood / SRI",          "water_mm": 1200, "critical_stages": ["Tillering", "Flowering", "Grain Filling"]},
    "Wheat":     {"interval_days": 10, "method": "Furrow / Sprinkler",   "water_mm": 450,  "critical_stages": ["CRI (21 days)", "Tillering", "Jointing", "Grain Filling"]},
    "Maize":     {"interval_days": 7,  "method": "Furrow / Drip",        "water_mm": 500,  "critical_stages": ["Knee-high", "Tasseling", "Silking"]},
    "Cotton":    {"interval_days": 10, "method": "Furrow / Drip",        "water_mm": 700,  "critical_stages": ["Squaring", "Flowering", "Boll Development"]},
    "Sugarcane": {"interval_days": 7,  "method": "Drip / Furrow",        "water_mm": 1500, "critical_stages": ["Grand Growth Period (3-5 months)"]},
    "Potato":    {"interval_days": 5,  "method": "Sprinkler / Drip",     "water_mm": 500,  "critical_stages": ["Tuber Initiation", "Tuber Bulking"]},
    "Tomato":    {"interval_days": 4,  "method": "Drip",                 "water_mm": 400,  "critical_stages": ["Flowering", "Fruit Setting", "Fruit Development"]},
    "Groundnut": {"interval_days": 10, "method": "Sprinkler / Furrow",   "water_mm": 500,  "critical_stages": ["Pegging", "Pod Development"]},
    "Soybean":   {"interval_days": 10, "method": "Furrow / Sprinkler",   "water_mm": 450,  "critical_stages": ["Flowering (R1)", "Pod Filling (R5)"]},
    "Onion":     {"interval_days": 5,  "method": "Drip / Sprinkler",     "water_mm": 350,  "critical_stages": ["Bulb Formation", "Maturity"]},
}

SEASON_WEATHER_ADVICE = {
    "kharif": {
        "months": "June – October",
        "rainfall": "High (700-1200 mm)",
        "temperature": "25-35°C",
        "tips": [
            "Ensure proper drainage to avoid waterlogging.",
            "Apply fungicides preventively during high humidity.",
            "Use short-duration varieties to avoid late monsoon risk.",
            "Prepare bunds to retain rainwater in paddy fields.",
        ]
    },
    "rabi": {
        "months": "November – March",
        "rainfall": "Low (100-300 mm)",
        "temperature": "10-25°C",
        "tips": [
            "Rely on irrigation — plan canal or groundwater schedule.",
            "Protect crops from frost in December-January.",
            "Use mulching to conserve soil moisture.",
            "Night temperatures below 5°C can damage flowering — use foggers.",
        ]
    },
    "zaid": {
        "months": "March – May",
        "rainfall": "Very Low (<100 mm)",
        "temperature": "30-45°C",
        "tips": [
            "Irrigate frequently — every 3-5 days for most crops.",
            "Use shade nets for vegetable crops in peak summer.",
            "Avoid mid-day irrigation — water early morning or evening.",
            "Mulch heavily to reduce soil temperature and water loss.",
        ]
    }
}

SUSTAINABLE_PRACTICES = [
    {"practice": "Drip Irrigation",       "benefit": "Saves 40-60% water vs flood irrigation",        "suitable_for": "Vegetables, Fruits, Cotton, Sugarcane"},
    {"practice": "Sprinkler Irrigation",  "benefit": "Uniform distribution; saves 25-35% water",      "suitable_for": "Wheat, Groundnut, Potato, Onion"},
    {"practice": "Crop Rotation",         "benefit": "Breaks pest cycles; improves soil fertility",    "suitable_for": "All crops"},
    {"practice": "Cover Cropping",        "benefit": "Prevents erosion; adds nitrogen (legumes)",      "suitable_for": "Inter-season periods"},
    {"practice": "Mulching",              "benefit": "Conserves moisture; suppresses weeds",           "suitable_for": "All crops — especially in dry seasons"},
    {"practice": "Integrated Pest Mgmt",  "benefit": "Reduces chemical use; eco-friendly pest control","suitable_for": "All crops"},
    {"practice": "Vermicomposting",       "benefit": "Improves soil structure; provides balanced nutrition","suitable_for": "All crops"},
    {"practice": "Zero Tillage",          "benefit": "Saves fuel; protects soil structure",            "suitable_for": "Wheat after Paddy (Happy Seeder)"},
]


def get_irrigation_schedule(crop: str) -> dict:
    crop_title = crop.strip().title()
    info = IRRIGATION_SCHEDULE.get(crop_title)
    if not info:
        return {"error": f"Irrigation data not available for '{crop}'.", "available_crops": list(IRRIGATION_SCHEDULE.keys())}
    return {
        "crop": crop_title,
        "irrigation_interval": f"Every {info['interval_days']} days",
        "recommended_method": info["method"],
        "total_water_requirement": f"{info['water_mm']} mm per crop season",
        "critical_irrigation_stages": info["critical_stages"],
        "tip": "Never skip irrigation at critical stages — yield loss can be 30-50%."
    }


def get_season_weather_advice(season: str) -> dict:
    season = season.lower().strip()
    info = SEASON_WEATHER_ADVICE.get(season)
    if not info:
        return {"error": f"Unknown season '{season}'. Try: kharif, rabi, or zaid."}
    return {"season": season.capitalize(), **info}


def get_sustainable_practices(count: int = 5) -> list:
    return SUSTAINABLE_PRACTICES[:count]


def classify_weather_risk(temperature: float, rainfall_mm: float) -> dict:
    risk = "Low"
    concerns = []

    if temperature > 40:
        risk = "High"
        concerns.append("Extreme heat — risk of heat stress, flower drop, and yield reduction.")
    elif temperature > 35:
        risk = "Medium"
        concerns.append("High temperature — monitor water stress; irrigate more frequently.")
    elif temperature < 5:
        risk = "High"
        concerns.append("Frost risk — protect with smoke screens, wind breakers, or foggers.")
    elif temperature < 10:
        risk = "Medium"
        concerns.append("Cool temperatures — crops may develop slowly; watch for frost.")

    if rainfall_mm > 100:
        risk = "High" if risk != "High" else risk
        concerns.append("Heavy rainfall — risk of waterlogging, fungal diseases, and soil erosion.")
    elif rainfall_mm > 50:
        concerns.append("Moderate-high rain — ensure drainage; apply protective fungicide.")
    elif rainfall_mm < 5:
        concerns.append("Very low rainfall — irrigation needed immediately.")

    if not concerns:
        concerns.append("Conditions look favorable for most crops.")

    return {
        "temperature_c": temperature,
        "rainfall_mm": rainfall_mm,
        "risk_level": risk,
        "concerns": concerns,
        "action": "Take immediate preventive action." if risk == "High" else "Monitor regularly."
    }
