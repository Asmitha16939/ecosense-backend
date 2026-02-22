from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import CleaningLog
from schemas import CleaningRequest, CleaningResponse

router = APIRouter()

# Chemical hazard scores (0-10, higher = more toxic)
PRODUCT_SCORES = {
    "bleach":        2,   # very toxic — score is eco_score (low = bad)
    "ammonia":       2,
    "acid_cleaner":  1,
    "disinfectant":  3,
    "detergent":     5,
    "soap":          7,
    "vinegar":       9,
    "baking_soda":   10,
    "lemon":         10,
    "eco_cleaner":   9,
    "steam":         10,
}

ALTERNATIVES = {
    "bleach":        ["White vinegar + water spray", "Hydrogen peroxide (3%)", "Castile soap solution"],
    "ammonia":       ["Baking soda paste", "Vinegar + dish soap", "Commercial eco-cleaner"],
    "acid_cleaner":  ["Lemon juice + salt", "Baking soda scrub", "Citric acid (natural)"],
    "disinfectant":  ["Tea tree oil spray", "Hydrogen peroxide", "Boiling water steam"],
    "detergent":     ["Plant-based dish soap", "Castile soap", "Eco-certified detergent"],
    "soap":          ["Castile soap", "Natural bar soap", "Current choice is good!"],
    "vinegar":       ["Current choice is great!", "Lemon juice", "Baking soda"],
    "baking_soda":   ["Current choice is excellent!", "Lemon + salt"],
    "lemon":         ["Current choice is excellent!", "Vinegar + water"],
    "eco_cleaner":   ["Current choice is great!", "DIY: vinegar + baking soda"],
    "steam":         ["Current choice is the best!", "Hot water + microfiber cloth"],
}

PRODUCT_TIPS = {
    "bleach":        ["Never mix bleach with ammonia or vinegar — toxic fumes", "Dilute bleach 1:10 with water for cleaning"],
    "ammonia":       ["Ventilate the room well when using ammonia-based cleaners", "Wear gloves and avoid skin contact"],
    "detergent":     ["Use only the recommended amount — excess doesn't clean better", "Choose phosphate-free formulas"],
    "vinegar":       ["Vinegar kills 82% of bacteria and is safe for family and pets", "Don't use on marble or granite surfaces"],
    "baking_soda":   ["Mix with vinegar for a powerful, natural effervescent cleaner", "Great for deodorizing refrigerators"],
}


@router.post("/analyze", response_model=CleaningResponse)
def analyze_cleaning(req: CleaningRequest, db: Session = Depends(get_db)):
    base_score = PRODUCT_SCORES.get(req.product_type, 5)

    # Penalize for high frequency
    frequency_penalty = {"daily": 0, "weekly": 1, "monthly": 2, "rarely": 3}
    penalty = frequency_penalty.get(req.usage_frequency, 0)

    eco_score = min(10, max(1, base_score + penalty - (req.rooms // 5)))

    if eco_score >= 8:
        chemical_load = "Low"
        rating = "Excellent — very eco-friendly! 🌿"
    elif eco_score >= 5:
        chemical_load = "Medium"
        rating = "Good — some improvements possible"
    else:
        chemical_load = "High"
        rating = "Needs improvement — high chemical load ⚠️"

    alternatives = ALTERNATIVES.get(req.product_type, ["Try plant-based cleaners", "Use microfiber cloths with water"])
    tips = PRODUCT_TIPS.get(req.product_type, [
        "🌿 Ventilate rooms after cleaning",
        "♻️ Buy cleaners in concentrated form to reduce plastic waste",
    ])
    tips.append(f"🏠 {req.rooms} rooms need ~{req.rooms * 500}ml of cleaner per session — buy in bulk to save")

    # Save to DB
    log = CleaningLog(
        product_type=req.product_type,
        usage_frequency=req.usage_frequency,
        rooms=req.rooms,
        eco_score=eco_score,
        chemical_load=chemical_load,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return CleaningResponse(
        eco_score=eco_score,
        chemical_load=chemical_load,
        rating=rating,
        alternatives=alternatives,
        tips=tips,
        saved_id=log.id,
    )
