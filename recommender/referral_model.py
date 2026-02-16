import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import os

# ======================================================
# LOAD DATA
# ======================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'BD_200_Hospital_Facility_Dataset - Sheet1.csv')

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Dataset not found at: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)

# Clean text columns (VERY IMPORTANT)
for col in ["upazila", "district", "division"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.lower().str.strip()

# ======================================================
# LOCATION RESOLVER (BANGLADESH SAFE)
# ======================================================

def get_location_from_upazila(place_name):
    """
    Resolve patient location using:
    1) Upazila (partial)
    2) District (fallback)
    3) Division (fallback)
    """

    if not place_name:
        return None, None

    key = place_name.lower().strip()

    # 1️⃣ Upazila match
    subset = df[df["upazila"].str.contains(key, na=False)]

    # 2️⃣ District fallback - try full key or first word
    if subset.empty:
        subset = df[df["district"].str.contains(key, na=False)]
        if subset.empty and len(key.split()) > 1:
            first_word = key.split()[0]
            subset = df[df["district"].str.contains(first_word, na=False)]

    # 3️⃣ Division fallback
    if subset.empty and "division" in df.columns:
        subset = df[df["division"].str.contains(key, na=False)]
        if subset.empty and len(key.split()) > 1:
            first_word = key.split()[0]
            subset = df[df["division"].str.contains(first_word, na=False)]

    if subset.empty:
        return None, None

    return subset["latitude"].mean(), subset["longitude"].mean()

# ======================================================
# DEPARTMENT MAP
# ======================================================

DEPT_MAP = {
    'medicine':'dept_medicine',
    'cardiology':'dept_cardiology',
    'neurology':'dept_neurology',
    'gastroenterology':'dept_gastroenterology',
    'pulmonology':'dept_pulmonology',
    'nephrology':'dept_nephrology',
    'orthopedics':'dept_orthopedics',
    'surgery':'dept_surgery',
    'ent':'dept_ent',
    'obgyn':'dept_obgyn',
    'pediatrics':'dept_pediatrics',
    'dermatology':'dept_dermatology',
    'ophthalmology':'dept_ophthalmology',
    'psychiatry':'dept_psychiatry'
}

# ======================================================
# DISTANCE
# ======================================================

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# ======================================================
# MAIN REFERRAL MODEL
# ======================================================

def referral_model(
    department,
    patient_lat,
    patient_lon,
    emergency_level_required=0,
    top_n=3
):
    data = df.copy()

    # RULE ENGINE
    data = data[data.get(DEPT_MAP[department], 0) == 1]
    data = data[data["accepting_referrals"] == 1]

    if emergency_level_required > 0:
        data = data[data["has_emergency"] == 1]
        data = data[data["emergency_level"] >= emergency_level_required]
        if emergency_level_required >= 2:
            data = data[data["available_icu_beds"] > 0]

    if data.empty:
        return []

    # DISTANCE
    data["distance_km"] = data.apply(
        lambda r: haversine_km(
            patient_lat, patient_lon,
            r["latitude"], r["longitude"]
        ),
        axis=1
    )

    # BANGLADESH SAFE LIMIT
    max_dist = 40 if emergency_level_required > 0 else 60
    data = data[data["distance_km"] <= max_dist]

    if data.empty:
        return []

    # PRIORITY
    data["distance_priority"] = np.where(
        data["distance_km"] <= (25 if emergency_level_required > 0 else 30),
        1.0, 0.6
    )

    # FEATURES
    data["vacant_norm"] = data["vacant_beds"] / (data["total_beds"] + 1)
    data["icu_norm"] = data["available_icu_beds"] / (data["icu_beds"] + 1)

    # WEIGHTS
    if emergency_level_required >= 2:
        w = {'dist':0.6, 'vac':0.1, 'icu':0.3}
    elif emergency_level_required == 1:
        w = {'dist':0.55, 'vac':0.25, 'icu':0.2}
    else:
        w = {'dist':0.5, 'vac':0.35, 'icu':0.15}

    data["score"] = (
        w["dist"] * data["distance_priority"] +
        w["vac"]  * data["vacant_norm"] +
        w["icu"]  * data["icu_norm"]
    )

    ranked = data.sort_values("score", ascending=False).head(top_n)

    return [
        {
            "hospital": r["hospital_name"],
            "district": r["district"].title(),
            "distance_km": round(r["distance_km"], 2),
            "score": round(r["score"], 4),
            "why": f"{department} | {r['distance_km']:.1f}km | ICU {r['available_icu_beds']} | Vacant {r['vacant_beds']}"
        }
        for _, r in ranked.iterrows()
    ]
