# fertilizer_logic.py — NPK dosage calculator & fertilizer recommendation engine

# NPK requirements per crop (kg/hectare): [Nitrogen, Phosphorus, Potassium]
CROP_NPK_REQUIREMENTS = {
    "Paddy":       {"N": 120, "P": 60,  "K": 60,  "stage_split": [40, 30, 30]},
    "Wheat":       {"N": 120, "P": 60,  "K": 40,  "stage_split": [50, 25, 25]},
    "Maize":       {"N": 150, "P": 75,  "K": 50,  "stage_split": [40, 35, 25]},
    "Cotton":      {"N": 100, "P": 50,  "K": 50,  "stage_split": [33, 33, 34]},
    "Sugarcane":   {"N": 250, "P": 100, "K": 120, "stage_split": [30, 40, 30]},
    "Soybean":     {"N": 30,  "P": 60,  "K": 40,  "stage_split": [50, 50, 0]},
    "Groundnut":   {"N": 25,  "P": 50,  "K": 75,  "stage_split": [50, 50, 0]},
    "Potato":      {"N": 180, "P": 90,  "K": 150, "stage_split": [40, 30, 30]},
    "Tomato":      {"N": 120, "P": 60,  "K": 80,  "stage_split": [33, 33, 34]},
    "Mustard":     {"N": 80,  "P": 40,  "K": 40,  "stage_split": [50, 50, 0]},
    "Chickpea":    {"N": 20,  "P": 50,  "K": 25,  "stage_split": [50, 50, 0]},
    "Onion":       {"N": 100, "P": 50,  "K": 75,  "stage_split": [40, 30, 30]},
    "Banana":      {"N": 200, "P": 60,  "K": 300, "stage_split": [33, 33, 34]},
}

# Commercial fertilizer nutrient content (%)
FERTILIZER_NUTRIENT = {
    "Urea":               {"N": 46, "P": 0,  "K": 0},
    "DAP":                {"N": 18, "P": 46, "K": 0},
    "MOP":                {"N": 0,  "P": 0,  "K": 60},
    "SSP":                {"N": 0,  "P": 16, "K": 0},
    "NPK 10-26-26":       {"N": 10, "P": 26, "K": 26},
    "NPK 12-32-16":       {"N": 12, "P": 32, "K": 16},
    "Ammonium Sulphate":  {"N": 21, "P": 0,  "K": 0},
}

# Organic alternatives
ORGANIC_FERTILIZERS = {
    "N_source": ["Compost (1-2% N)",  "Farm Yard Manure (0.5% N)", "Neem Cake (5% N)", "Vermicompost (1.5% N)"],
    "P_source": ["Rock Phosphate",    "Bone Meal (3% P)", "Fish Meal", "Green Manure"],
    "K_source": ["Wood Ash (5-10% K)","Banana Peel Compost", "Kelp Meal", "Granite Dust"],
    "general":  ["Vermicompost", "Farm Yard Manure (FYM)", "Green Manure (Dhaincha)", "Bio-fertilizers (Rhizobium, Azotobacter)"],
}

SOIL_HEALTH_TIPS = {
    "acidic":   "Apply Agricultural Lime (2-3 tonnes/hectare) to raise pH. Add well-decomposed FYM.",
    "alkaline": "Apply Gypsum (500 kg/hectare) or Sulphur to lower pH. Use acidifying fertilizers.",
    "neutral":  "Maintain with organic matter. Use balanced NPK. Practice crop rotation.",
    "saline":   "Leach excess salts with irrigation. Apply Gypsum. Grow salt-tolerant crops.",
}


def calculate_npk_dosage(crop: str, area_hectare: float) -> dict:
    crop_title = crop.strip().title()
    if crop_title not in CROP_NPK_REQUIREMENTS:
        available = list(CROP_NPK_REQUIREMENTS.keys())
        return {"error": f"Crop '{crop}' not found.", "available_crops": available}

    req = CROP_NPK_REQUIREMENTS[crop_title]
    area = max(0.1, min(area_hectare, 1000))  # clamp

    total_N = round(req["N"] * area, 1)
    total_P = round(req["P"] * area, 1)
    total_K = round(req["K"] * area, 1)

    # Calculate fertilizer quantities
    urea_kg   = round((total_N / 46) * 100, 1)
    dap_kg    = round((total_P / 46) * 100, 1)
    mop_kg    = round((total_K / 60) * 100, 1)

    split = req["stage_split"]
    split_schedule = [
        {"stage": "Basal (At sowing)",        "percent": split[0], "N_kg": round(total_N * split[0] / 100, 1)},
        {"stage": "1st Top Dress (20-25 days)","percent": split[1], "N_kg": round(total_N * split[1] / 100, 1)},
        {"stage": "2nd Top Dress (40-45 days)","percent": split[2], "N_kg": round(total_N * split[2] / 100, 1)},
    ]

    return {
        "crop": crop_title,
        "area_hectare": area,
        "npk_requirement": {"N_kg": total_N, "P_kg": total_P, "K_kg": total_K},
        "fertilizer_quantities": {
            "Urea (46% N)": f"{urea_kg} kg",
            "DAP (46% P)": f"{dap_kg} kg",
            "MOP (60% K)": f"{mop_kg} kg",
        },
        "split_application": split_schedule,
        "organic_alternatives": ORGANIC_FERTILIZERS["general"][:3],
        "precautions": [
            "Avoid applying fertilizers before heavy rain.",
            "Apply in the evening to reduce evaporation losses.",
            "Always do a soil test before application.",
            "Do not exceed recommended doses — it causes soil & water pollution.",
        ]
    }


def get_organic_recommendations(nutrient_deficiency: str) -> dict:
    nutrient = nutrient_deficiency.upper().strip()
    key_map = {"N": "N_source", "P": "P_source", "K": "K_source"}
    key = key_map.get(nutrient, "general")
    return {
        "nutrient": nutrient_deficiency,
        "organic_sources": ORGANIC_FERTILIZERS.get(key, ORGANIC_FERTILIZERS["general"]),
        "tip": "Combine 2-3 organic sources for best results. Add compost 2-3 weeks before sowing."
    }


def get_soil_health_advice(soil_ph_type: str) -> dict:
    ph = soil_ph_type.lower().strip()
    advice = SOIL_HEALTH_TIPS.get(ph, "Conduct a soil test first. Maintain organic matter above 1.5%.")
    return {"soil_condition": ph, "advice": advice}


def list_available_crops():
    return list(CROP_NPK_REQUIREMENTS.keys())
