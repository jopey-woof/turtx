# analytics_routes.py - Analytics API Endpoints

from fastapi import APIRouter
import sqlite3
from datetime import datetime, timedelta

router = APIRouter()

DATABASE_PATH = "/home/shrimp/turtx/turtle-monitor/api/data/turtle_monitor.db"

AGGREGATION_MAP = {
    "2h": "2 seconds",
    "12h": "1 minute",
    "24h": "5 minutes",
    "3d": "15 minutes",
    "1w": "1 hour",
    "1m": "4 hours"
}

def period_to_timedelta(period):
    mapping = {
        "2h": {"hours": 2},
        "12h": {"hours": 12},
        "24h": {"days": 1},
        "3d": {"days": 3},
        "1w": {"days": 7},
        "1m": {"days": 30}
    }
    return timedelta(**mapping.get(period, {"days": 1}))

@router.get("/analytics/temperature/{zone}")
async def temperature_analytics(zone: str, period: str = "24h", aggregation: str = None):
    agg = aggregation or AGGREGATION_MAP.get(period, "5 minutes")
    return await get_aggregated_data("temperature", zone, period, agg)

@router.get("/analytics/humidity/{zone}")
async def humidity_analytics(zone: str, period: str = "24h", aggregation: str = None):
    agg = aggregation or AGGREGATION_MAP.get(period, "5 minutes")
    return await get_aggregated_data("humidity", zone, period, agg)

async def get_aggregated_data(metric, zone, period, agg):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    end_time = datetime.now()
    start_time = end_time - period_to_timedelta(period)

    # Simple aggregation for demonstration; adjust for exact interval grouping
    query = f"""
    SELECT timestamp, AVG({metric}) as avg_value
    FROM sensor_readings
    WHERE sensor_id = ? AND timestamp BETWEEN ? AND ?
    GROUP BY strftime('%Y-%m-%d %H:%M', timestamp)
    ORDER BY timestamp
    """
    cursor.execute(query, (zone, start_time, end_time))
    results = cursor.fetchall()

    conn.close()
    return [{"time": row[0], "value": row[1]} for row in results]

# Add other endpoints as needed