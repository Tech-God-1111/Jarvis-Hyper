from fastapi import APIRouter
from core.data_collector import data_collector

router = APIRouter(prefix="/data", tags=["Data"])

@router.get("/weather")
async def get_weather(lat: float = 34.0522, lon: float = -118.2437):
    """Get weather data"""
    return await data_collector.fetch_weather(lat, lon)

@router.get("/news")
async def get_news(limit: int = 5):
    """Get news headlines"""
    return {"news": await data_collector.fetch_news(limit)}

@router.get("/system")
async def get_system():
    """Get system stats"""
    return await data_collector.fetch_system_stats()

@router.get("/all")
async def get_all():
    """Get all data"""
    return await data_collector.collect_all()