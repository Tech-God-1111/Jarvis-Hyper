import aiohttp
import psutil
from datetime import datetime


class DataCollector:
    async def fetch_weather(self, lat: float = 34.0522, lon: float = -118.2437):
        """Fetch current weather"""
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return data.get('current_weather', {})
        except:
            return {}

    async def fetch_news(self, limit: int = 5):
        """Fetch latest news"""
        try:
            url = f"https://api.thenewsapi.com/v1/news/top?locale=us&limit={limit}"
            # Note: This API might need a key, using a free alternative
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return data.get('data', [])
        except:
            return []

    async def fetch_system_stats(self):
        """Fetch system stats"""
        return {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent if psutil.disk_usage('/') else 0
        }

    async def collect_all(self):
        """Collect all data"""
        return {
            'system': await self.fetch_system_stats(),
            'timestamp': datetime.now().isoformat()
        }


data_collector = DataCollector()