from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import WaterLog
from schemas import WaterRequest, WaterResponse

router = APIRouter()

# Benchmark liters per session (based on Indian averages)
BENCHMARKS = {
    "shower":    60,
    "bath":      20,
    "dishwash":  35,
    "laundry":   70,
    "gardening": 150,
    "cooking":   8,
    "flushing":  9,
    "cleaning":  50,
}

ACTIVITY_TIPS = {
    "shower": [
        "🚿 Reduce shower time by 2 minutes — saves up to 16L per shower",
        "💧 Install a low-flow showerhead — reduces water use by 40%",
    ],
    "bath": [
        "🪣 Use a smaller bucket — a 10L bucket is enough for a bath",
        "♻️ Reuse bath water for mopping or gardening",
    ],
    "dishwash": [
        "🧼 Use a bucket for dishwashing instead of a running tap — saves 50%",
        "🍽️ Soak dishes first to reduce scrubbing water",
    ],
    "laundry": [
        "👕 Run washing machine only with a full load — saves 40L per cycle",
        "🔄 Use the economy or quick-wash setting when possible",
    ],
    "gardening": [
        "🌱 Water plants early morning or evening — reduces evaporation by 30%",
        "🪣 Use drip irrigation or a watering can instead of a pipe",
    ],
    "cooking": [
        "🥦 Reuse water from washing vegetables for plants",
        "🍳 Use the minimum water needed when boiling food",
    ],
    "flushing": [
        "💡 Install a dual-flush toilet — saves up to 50% flush water",
        "🪣 Place a water displacement device in the cistern",
    ],
    "cleaning": [
        "🧹 Use a mop with a wringer to reuse water multiple times",
        "♻️ Collect rinse water and reuse for preliminary mopping",
    ],
}


@router.post("/calculate", response_model=WaterResponse)
def calculate_water(req: WaterRequest, db: Session = Depends(get_db)):
    liters_per_session = req.flow_rate * req.duration
    daily_liters = liters_per_session * req.sessions
    days_per_month = (req.days_per_week / 7) * 30
    monthly_liters = daily_liters * days_per_month
    monthly_cost = (monthly_liters / 1000) * req.water_rate

    benchmark = BENCHMARKS.get(req.activity, 50)
    benchmark_per_day = benchmark * req.sessions
    ratio = daily_liters / benchmark_per_day if benchmark_per_day > 0 else 1.0

    if ratio < 1.2:
        comparison_rating = "Good"
        comparison_desc = "Within recommended range 👍"
    elif ratio < 1.8:
        comparison_rating = "Average"
        comparison_desc = f"{round((ratio - 1) * 100)}% above benchmark"
    else:
        comparison_rating = "High"
        comparison_desc = f"{round((ratio - 1) * 100)}% above — improvement needed"

    # Build tips
    tips = []
    if ratio > 1.3:
        excess = daily_liters - benchmark_per_day
        tips.append(f"💧 Reduce {req.activity} time by 2–3 min — save ~{round(excess)}L/day")
    if req.flow_rate > 8 and req.activity in ("shower", "dishwash"):
        tips.append("🚿 Install a tap aerator — reduces flow by 50% without losing pressure")
    tips.extend(ACTIVITY_TIPS.get(req.activity, [])[:2])
    if not tips:
        tips = ["✅ Great job! Your water usage is efficient", "💡 Check for leaking taps — a drip wastes 20L/day"]

    # Save to DB
    log = WaterLog(
        activity_type=req.activity,
        flow_rate=req.flow_rate,
        duration_minutes=req.duration,
        sessions_per_day=req.sessions,
        days_per_week=req.days_per_week,
        water_rate=req.water_rate,
        daily_liters=round(daily_liters, 2),
        monthly_liters=round(monthly_liters, 2),
        monthly_cost=round(monthly_cost, 2),
        comparison_rating=comparison_rating,
        ratio=round(ratio, 2),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return WaterResponse(
        daily_liters=round(daily_liters, 2),
        monthly_liters=round(monthly_liters, 2),
        monthly_cost=round(monthly_cost, 2),
        comparison_rating=comparison_rating,
        comparison_desc=comparison_desc,
        ratio=round(ratio, 2),
        tips=tips,
        saved_id=log.id,
    )
