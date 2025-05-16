from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trip_plans = relationship("TripPlan", back_populates="user")

class TripPlan(Base):
    __tablename__ = "trip_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    preferences = Column(ARRAY(String), nullable=False)
    duration = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trip_plans")
    routes = relationship("Route", back_populates="trip_plan")
    weather_forecasts = relationship("WeatherForecast", back_populates="trip_plan")
    pois = relationship("POI", back_populates="trip_plan")
    ai_summaries = relationship("AISummary", back_populates="trip_plan")

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_plan_id = Column(Integer, ForeignKey("trip_plans.id"))
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    distance = Column(String(50))
    duration = Column(String(50))
    steps = Column(ARRAY(Text))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trip_plan = relationship("TripPlan", back_populates="routes")

class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_plan_id = Column(Integer, ForeignKey("trip_plans.id"))
    location = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    condition = Column(String(50))
    humidity = Column(Integer)
    wind_speed = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trip_plan = relationship("TripPlan", back_populates="weather_forecasts")

class POI(Base):
    __tablename__ = "pois"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_plan_id = Column(Integer, ForeignKey("trip_plans.id"))
    name = Column(String(200), nullable=False)
    category = Column(String(50))
    rating = Column(Float)
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(Text)
    price_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trip_plan = relationship("TripPlan", back_populates="pois")

class AISummary(Base):
    __tablename__ = "ai_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_plan_id = Column(Integer, ForeignKey("trip_plans.id"))
    summary = Column(Text, nullable=False)
    recommendations = Column(Text)
    tips = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trip_plan = relationship("TripPlan", back_populates="ai_summaries")
