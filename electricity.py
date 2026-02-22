from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import ElectricityLog
from schemas import ElectricityRequest, ElectricityResponse

router = APIRouter()

# Appliance wattage map
WATTAGE = {
    "fan": 75,
    "light": 10,
    "ac": 1500,
    "tv": 100,
    "fridge": 150,
    "washer": 500,
    "heater": 2000,
    "geyser": 3000,
}

# Tips per appliance
APPLIANCE_TIPS = {
    "ac": [
        "🌡️ Set AC to 24°C instead of 18°C to save 30% energy",
        "🔄 Use fan along with AC to feel cooler at higher temp settings",
        "🪟 Keep windows and doors closed while AC is running",
    ],
    "fridge": [
        "🧊 Keep refrigerator coils clean and door seals tight",
        "📐 Keep fridge at least 10cm away from the wall for ventilation",
        "🌡️ Set fridge to 3–5°C and freezer to -18°C for optimal efficiency",
    ],
    "washer": [
        "👕 Use cold water for washing clothes — saves 90% energy",
        "🔄 Always run the washing machine with a full load",
        "⏰ Use quick-wash mode for lightly soiled clothes",
    ],
    "light": [
        "💡 Switch to LED bulbs if not already — use 80% less energy",
        "🌞 Use natural light during daytime hours",
        "⚙️ Install motion sensors for corridors and bathrooms",
    ],
    "geyser": [
        "🚿 Install solar water heater — reduces energy use by 70%",
        "⏱️ Set geyser timer: heat water 30 minutes before use",
        "🔥 Lower geyser temperature to 55°C — still safe and saves energy",
    ],
    "heater": [
        "🧥 Wear warmer clothes before switching on the heater",
        "⏰ Use a timer to switch off the heater at night",
        "🪟 Insulate windows and doors to retain room heat",
    ],
}


@router.post("/calculate", response_model=ElectricityResponse)
def calculate_electricity(req: ElectricityRequest, db: Session = Depends(get_db)):
    watts = WATTAGE.get(req.appliance_type)
    if watts is None:
        raise HTTPException(status_code=400, detail=f"Unknown appliance type: {req.appliance_type}")

    days_per_month = (req.days_per_week / 7) * 30
    monthly_kwh = (watts * req.hours * days_per_month * req.count) / 1000
    wasted_kwh = monthly_kwh * (1 - req.occupancy)
    monthly_cost = monthly_kwh * req.tariff
    carbon_kg = monthly_kwh * 0.85  # Indian grid average: 0.85 kg CO2/kWh

    waste_percentage = (1 - req.occupancy) * 100
    if waste_percentage < 20:
        efficiency = "Efficient"
    elif waste_percentage < 50:
        efficiency = "Moderate"
    else:
        efficiency = "Wasteful"

    # Build tips
    tips = []
    if waste_percentage > 30:
        tips.append(f"🔌 Turn off appliances when not in use — save up to ₹{round(wasted_kwh * req.tariff)}/month")
    if req.appliance_type in APPLIANCE_TIPS:
        tips.extend(APPLIANCE_TIPS[req.appliance_type][:2])
    if not tips:
        tips = ["✅ Your usage pattern looks efficient! Keep it up", "📱 Consider smart plugs for automated control"]

    # Save to DB
    log = ElectricityLog(
        appliance_type=req.appliance_type,
        appliance_count=req.count,
        hours_per_day=req.hours,
        days_per_week=req.days_per_week,
        occupancy=req.occupancy,
        tariff=req.tariff,
        monthly_kwh=round(monthly_kwh, 2),
        monthly_cost=round(monthly_cost, 2),
        carbon_kg=round(carbon_kg, 2),
        efficiency=efficiency,
        waste_percentage=round(waste_percentage, 1),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return ElectricityResponse(
        monthly_kwh=round(monthly_kwh, 2),
        monthly_cost=round(monthly_cost, 2),
        carbon_kg=round(carbon_kg, 2),
        efficiency=efficiency,
        waste_percentage=round(waste_percentage, 1),
        wasted_kwh=round(wasted_kwh, 2),
        tips=tips,
        saved_id=log.id,
    )
