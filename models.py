from sqlalchemy import Column, Integer, String, Float, Boolean, Text, TIMESTAMP
from sqlalchemy.sql import func
from database import Base


class ElectricityLog(Base):
    __tablename__ = "electricity_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    appliance_type = Column(String(50), nullable=False)
    appliance_count = Column(Integer, nullable=False, default=1)
    hours_per_day = Column(Float, nullable=False)
    days_per_week = Column(Integer, nullable=False)
    occupancy = Column(Float, nullable=False, default=1.0)
    tariff = Column(Float, nullable=False, default=6.0)
    monthly_kwh = Column(Float, nullable=False)
    monthly_cost = Column(Float, nullable=False)
    carbon_kg = Column(Float, nullable=False)
    efficiency = Column(String(20), nullable=False)
    waste_percentage = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_type = Column(String(50), nullable=False)
    flow_rate = Column(Float, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    sessions_per_day = Column(Integer, nullable=False)
    days_per_week = Column(Integer, nullable=False)
    water_rate = Column(Float, nullable=False, default=10.0)
    daily_liters = Column(Float, nullable=False)
    monthly_liters = Column(Float, nullable=False)
    monthly_cost = Column(Float, nullable=False)
    comparison_rating = Column(String(20), nullable=False)
    ratio = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class CleaningLog(Base):
    __tablename__ = "cleaning_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_type = Column(String(100), nullable=False)
    usage_frequency = Column(String(50), nullable=False)
    rooms = Column(Integer, nullable=False, default=1)
    eco_score = Column(Integer, nullable=False)
    chemical_load = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    badge_key = Column(String(50), unique=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(10), nullable=False)
    category = Column(String(30), nullable=False)
    threshold_value = Column(Float, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
