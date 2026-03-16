# crop_logic.py — Rule-based crop recommendation engine

CROP_SEASON_MAP = {
    "kharif": ["Paddy", "Maize", "Jowar", "Bajra", "Cotton", "Sugarcane", "Groundnut", "Soybean", "Turmeric", "Ginger"],
    "rabi":   ["Wheat", "Barley", "Mustard", "Chickpea", "Lentil", "Pea", "Sunflower", "Potato", "Onion"],
    "zaid":   ["Watermelon", "Muskmelon", "Cucumber", "Pumpkin", "Bitter Gourd", "Moong Dal", "Urad Dal"],
}

SOIL_CROP_MAP = {
    "clay":      ["Paddy", "Wheat", "Sugarcane", "Jute"],
    "loamy":     ["Wheat", "Maize", "Soybean", "Cotton", "Groundnut", "Vegetables"],
    "sandy":     ["Groundnut", "Watermelon", "Carrot", "Radish", "Potato"],
    "silt":      ["Paddy", "Sugarcane", "Vegetables", "Wheat"],
    "black":     ["Cotton", "Soybean", "Sunflower", "Jowar", "Wheat"],
    "red":       ["Groundnut", "Potato", "Paddy", "Maize", "Pulses"],
    "laterite":  ["Cashew", "Coconut", "Tea", "Coffee", "Tapioca"],
    "alluvial":  ["Wheat", "Paddy", "Sugarcane", "Maize", "Cotton", "Pulses"],
}

WEATHER_CROP_MAP = {
    "high_rainfall_moderate_temp":     ["Paddy", "Maize", "Sugarcane", "Jute"],
    "low_rainfall_high_temp":          ["Bajra", "Jowar", "Groundnut", "Cotton"],
    "moderate_rainfall_cool_temp":     ["Wheat", "Barley", "Mustard", "Pea"],
    "high_rainfall_high_temp":         ["Paddy", "Banana", "Coconut", "Turmeric"],
    "low_rainfall_cool_temp":          ["Chickpea", "Lentil", "Mustard", "Barley"],
    "moderate_rainfall_moderate_temp": ["Maize", "Soybean", "Cotton", "Sunflower"],
}

DISEASE_SYMPTOM_MAP = {
    "yellow_leaves":       {"disease": "Nitrogen Deficiency / Yellow Mosaic Virus",  "crops": ["Soybean", "Paddy", "Wheat"],    "prevention": "Apply urea fertilizer; remove infected plants; use resistant varieties."},
    "brown_spots":         {"disease": "Leaf Blight / Brown Spot Disease",           "crops": ["Paddy", "Maize"],              "prevention": "Spray Mancozeb or Copper Oxychloride; ensure proper drainage."},
    "white_powder":        {"disease": "Powdery Mildew",                             "crops": ["Wheat", "Pea", "Mustard"],     "prevention": "Spray Sulphur-based fungicide; improve air circulation."},
    "wilting":             {"disease": "Fusarium Wilt / Root Rot",                   "crops": ["Cotton", "Tomato", "Chilli"],  "prevention": "Use Trichoderma; avoid waterlogging; rotate crops."},
    "black_spots":         {"disease": "Anthracnose / Black Scurf",                  "crops": ["Potato", "Mango", "Grapes"],   "prevention": "Use Carbendazim; remove infected debris; practice crop rotation."},
    "holes_in_leaves":     {"disease": "Pest Attack (Caterpillar / Beetles)",        "crops": ["Cotton", "Cabbage", "Paddy"],  "prevention": "Apply Neem oil or Chlorpyrifos; use pheromone traps."},
    "rust_orange_patches": {"disease": "Rust Disease",                               "crops": ["Wheat", "Barley", "Bean"],     "prevention": "Spray Propiconazole; plant resistant varieties."},
    "stunted_growth":      {"disease": "Nutrient Deficiency / Viral Infection",      "crops": ["Paddy", "Maize", "Vegetables"],"prevention": "Soil test; apply micronutrients; remove virus-infected plants."},
}


def get_crops_by_season(season: str) -> dict:
    season = season.lower().strip()
    crops = CROP_SEASON_MAP.get(season, [])
    if not crops:
        return {"error": f"Unknown season '{season}'. Try: kharif, rabi, or zaid."}
    return {"season": season.capitalize(), "recommended_crops": crops, "count": len(crops)}


def get_crops_by_soil(soil_type: str) -> dict:
    soil_type = soil_type.lower().strip()
    crops = SOIL_CROP_MAP.get(soil_type, [])
    if not crops:
        return {"error": f"Unknown soil type. Try: clay, loamy, sandy, silt, black, red, laterite, or alluvial."}
    return {"soil_type": soil_type.capitalize(), "recommended_crops": crops, "count": len(crops)}


def get_crops_by_weather(rainfall: str, temperature: str) -> dict:
    key = f"{rainfall.lower().strip()}_rainfall_{temperature.lower().strip()}_temp"
    crops = WEATHER_CROP_MAP.get(key, [])
    if not crops:
        return {"error": f"No match for rainfall='{rainfall}', temperature='{temperature}'."}
    return {"rainfall": rainfall, "temperature": temperature, "recommended_crops": crops}


def identify_disease(symptom: str) -> dict:
    symptom_key = symptom.lower().replace(" ", "_").strip()
    for key, val in DISEASE_SYMPTOM_MAP.items():
        if key in symptom_key or symptom_key in key:
            return {"symptom": symptom, "disease": val["disease"], "commonly_affects": val["crops"], "prevention": val["prevention"]}
    return {"symptom": symptom, "disease": "Unknown — consult local agricultural expert.", "prevention": "Contact your nearest KVK or agriculture officer."}


def get_all_seasons():
    return list(CROP_SEASON_MAP.keys())

def get_all_soil_types():
    return list(SOIL_CROP_MAP.keys())
