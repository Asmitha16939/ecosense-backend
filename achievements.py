from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Achievement, ElectricityLog, WaterLog, CleaningLog
from schemas import AchievementsResponse, AchievementOut

router = APIRouter()


def _compute_achievements(db: Session):
    all_achievements = db.query(Achievement).filter(Achievement.is_active == True).all()

    electricity_count = db.query(func.count(ElectricityLog.id)).scalar() or 0
    water_count = db.query(func.count(WaterLog.id)).scalar() or 0
    cleaning_count = db.query(func.count(CleaningLog.id)).scalar() or 0
    total_count = electricity_count + water_count + cleaning_count

    efficient_count = db.query(func.count(ElectricityLog.id)).filter(
        ElectricityLog.efficiency == "Efficient"
    ).scalar() or 0

    good_water_count = db.query(func.count(WaterLog.id)).filter(
        WaterLog.comparison_rating == "Good"
    ).scalar() or 0

    total_carbon = db.query(func.coalesce(func.sum(ElectricityLog.carbon_kg), 0)).scalar() or 0

    # Map badge_key → (current_progress_value)
    progress_map = {
        "first_calc":      total_count,
        "eco_warrior":     electricity_count,
        "water_keeper":    water_count,
        "clean_green":     cleaning_count,
        "efficiency_pro":  efficient_count,
        "water_saver":     good_water_count,
        "carbon_fighter":  float(total_carbon),
        "data_analyst":    total_count,
        "consistent_user": total_count,
        "green_home":      min(3, (1 if electricity_count > 0 else 0) +
                               (1 if water_count > 0 else 0) +
                               (1 if cleaning_count > 0 else 0)),
    }

    result = []
    for ach in all_achievements:
        progress = progress_map.get(ach.badge_key, 0)
        unlocked = progress >= ach.threshold_value
        pct = min(100.0, (progress / ach.threshold_value * 100)) if ach.threshold_value > 0 else 100.0
        result.append(AchievementOut(
            id=ach.id,
            badge_key=ach.badge_key,
            title=ach.title,
            description=ach.description,
            icon=ach.icon,
            category=ach.category,
            threshold_value=ach.threshold_value,
            unlocked=unlocked,
            progress=round(pct, 1),
        ))

    return result


@router.get("", response_model=AchievementsResponse)
def get_achievements(db: Session = Depends(get_db)):
    achievements = _compute_achievements(db)
    unlocked = sum(1 for a in achievements if a.unlocked)
    return AchievementsResponse(
        achievements=achievements,
        unlocked_count=unlocked,
        total_count=len(achievements),
    )
