from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─────────────────────────────────────────────────
# Electricity
# ─────────────────────────────────────────────────
class ElectricityRequest(BaseModel):
    appliance_type: str = Field(..., example="ac")
    count: int = Field(1, ge=1, le=20)
    hours: float = Field(..., ge=0, le=24)
    days_per_week: int = Field(7, ge=1, le=7)
    occupancy: float = Field(1.0, ge=0, le=1)
    tariff: float = Field(6.0, ge=1, le=50)


class ElectricityResponse(BaseModel):
    monthly_kwh: float
    monthly_cost: float
    carbon_kg: float
    efficiency: str
    waste_percentage: float
    wasted_kwh: float
    tips: List[str]
    saved_id: Optional[int] = None


# ─────────────────────────────────────────────────
# Water
# ─────────────────────────────────────────────────
class WaterRequest(BaseModel):
    activity: str = Field(..., example="shower")
    flow_rate: float = Field(..., ge=1, le=100)
    duration: float = Field(..., ge=1, le=120)
    sessions: int = Field(1, ge=1, le=20)
    days_per_week: int = Field(7, ge=1, le=7)
    water_rate: float = Field(10.0, ge=1, le=200)


class WaterResponse(BaseModel):
    daily_liters: float
    monthly_liters: float
    monthly_cost: float
    comparison_rating: str
    comparison_desc: str
    ratio: float
    tips: List[str]
    saved_id: Optional[int] = None


# ─────────────────────────────────────────────────
# Cleaning
# ─────────────────────────────────────────────────
class CleaningRequest(BaseModel):
    product_type: str = Field(..., example="bleach")
    usage_frequency: str = Field(..., example="daily")
    rooms: int = Field(1, ge=1, le=20)


class CleaningResponse(BaseModel):
    eco_score: int
    chemical_load: str
    rating: str
    alternatives: List[str]
    tips: List[str]
    saved_id: Optional[int] = None


# ─────────────────────────────────────────────────
# Analysis
# ─────────────────────────────────────────────────
class ElectricityHistoryItem(BaseModel):
    id: int
    appliance_type: str
    monthly_kwh: float
    monthly_cost: float
    carbon_kg: float
    efficiency: str
    created_at: datetime

    class Config:
        from_attributes = True


class WaterHistoryItem(BaseModel):
    id: int
    activity_type: str
    daily_liters: float
    monthly_liters: float
    monthly_cost: float
    comparison_rating: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisHistoryResponse(BaseModel):
    electricity: List[ElectricityHistoryItem]
    water: List[WaterHistoryItem]
    total_records: int


class AnalysisSummaryResponse(BaseModel):
    total_electricity_kwh: float
    total_electricity_cost: float
    total_carbon_kg: float
    total_water_liters: float
    total_water_cost: float
    electricity_count: int
    water_count: int
    cleaning_count: int


# ─────────────────────────────────────────────────
# Achievements
# ─────────────────────────────────────────────────
class AchievementOut(BaseModel):
    id: int
    badge_key: str
    title: str
    description: str
    icon: str
    category: str
    threshold_value: float
    unlocked: bool
    progress: float

    class Config:
        from_attributes = True


class AchievementsResponse(BaseModel):
    achievements: List[AchievementOut]
    unlocked_count: int
    total_count: int
