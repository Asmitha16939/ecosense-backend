from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import ElectricityLog, WaterLog, CleaningLog
from schemas import AnalysisHistoryResponse, AnalysisSummaryResponse, ElectricityHistoryItem, WaterHistoryItem

router = APIRouter()


@router.get("/history", response_model=AnalysisHistoryResponse)
def get_history(db: Session = Depends(get_db)):
    electricity = db.query(ElectricityLog).order_by(ElectricityLog.created_at.desc()).limit(30).all()
    water = db.query(WaterLog).order_by(WaterLog.created_at.desc()).limit(30).all()
    return AnalysisHistoryResponse(
        electricity=[ElectricityHistoryItem.model_validate(e) for e in electricity],
        water=[WaterHistoryItem.model_validate(w) for w in water],
        total_records=len(electricity) + len(water),
    )


@router.get("/summary", response_model=AnalysisSummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    e = db.query(
        func.coalesce(func.sum(ElectricityLog.monthly_kwh), 0).label("total_kwh"),
        func.coalesce(func.sum(ElectricityLog.monthly_cost), 0).label("total_cost"),
        func.coalesce(func.sum(ElectricityLog.carbon_kg), 0).label("total_carbon"),
        func.count(ElectricityLog.id).label("count"),
    ).one()

    w = db.query(
        func.coalesce(func.sum(WaterLog.monthly_liters), 0).label("total_liters"),
        func.coalesce(func.sum(WaterLog.monthly_cost), 0).label("total_cost"),
        func.count(WaterLog.id).label("count"),
    ).one()

    cleaning_count = db.query(func.count(CleaningLog.id)).scalar()

    return AnalysisSummaryResponse(
        total_electricity_kwh=round(float(e.total_kwh), 2),
        total_electricity_cost=round(float(e.total_cost), 2),
        total_carbon_kg=round(float(e.total_carbon), 2),
        total_water_liters=round(float(w.total_liters), 2),
        total_water_cost=round(float(w.total_cost), 2),
        electricity_count=e.count,
        water_count=w.count,
        cleaning_count=cleaning_count or 0,
    )
