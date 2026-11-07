from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from services import period_series, fit_trend
from typing import Literal

from database import get_db
from models import Sighting

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/by-location")
def get_tick_sightings_by_location(location: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Sighting.location, func.count(Sighting.id).label("count"))
    if location:
        q = q.filter(Sighting.location.ilike(location))
    rows = q.group_by(Sighting.location).order_by(Sighting.location.asc()).all()
    return [{"location": location, "count": count} for location, count in rows]

@router.get("/trends")
def get_the_trends_over_time(period: Literal["weekly", "monthly"] = "monthly", db: Session = Depends(get_db)):
    if period == "weekly":
        bucket = func.date(Sighting.date, "weekday 0", "-6 days")
    else:
        bucket = func.substr(Sighting.date, 1, 7)

    rows = db.query(bucket, func.count()).group_by(bucket).all()
    counts = {b: n for b, n in rows}
    if not counts:
        return {"error": "No data"}

    series = period_series(counts, period)
    result = fit_trend(series, period)
    return result or {"error": "Not enough data to detect a trend"}