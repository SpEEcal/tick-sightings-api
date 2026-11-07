from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, Base, get_db, SessionLocal
from models import Sighting
from routers import analytics
from services import import_tick_sightings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tick Sightings API")


@asynccontextmanager
async def lifespan(app: FastAPI): # runs once when the server starts
    db = SessionLocal()
    try:
        print("Import on startup:", import_tick_sightings(db))
    except Exception as e:
        print("Startup import failed, using existing data:", e)
    finally:
        db.close()
    yield

@app.get("/tick-sightings", tags=["Tick Sightings"])
def total_tick_sightings(
    date_from: str | None = None,
    date_to: str | None = None,
    location: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Sighting)

    if date_from:
        q = q.filter(Sighting.date >= date_from)
    if date_to:
        q = q.filter(Sighting.date <= date_to + "T23:59:59")
    if location:
        q = q.filter(Sighting.location.ilike(location))

    results = q.order_by(Sighting.date.desc()).all()
    return {"total": len(results), "results": results}

app.include_router(analytics.router)