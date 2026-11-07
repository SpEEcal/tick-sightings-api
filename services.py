from datetime import date, timedelta
import numpy as np

from models import Sighting
from api import get_tick_sightings

REQUIRED = ["id", "date", "location", "species"]
MIN_PERIODS = {"monthly": 12, "weekly": 26}

def is_complete(r):
    return all(isinstance(r.get(f), str) and r[f].strip() for f in REQUIRED)


def import_tick_sightings(db):
    raw_data = get_tick_sightings()
    existing = {row[0] for row in db.query(Sighting.id).all()}

    added = duplicates = 0
    rejected = []

    for r in raw_data:
        if not is_complete(r):
            missing = [f for f in REQUIRED if not (isinstance(r.get(f), str) and r[f].strip())]
            rejected.append({"id": r.get("id"), "missing": missing})
            continue

        if r["id"] in existing:
            duplicates += 1
            continue

        db.add(Sighting(
            id=r["id"].strip(),
            date=r["date"].strip(),
            location=r["location"].strip(),
            species=r["species"].strip(),
            latin_name=(r.get("latinName") or "").strip() or None,
        ))
        existing.add(r["id"])
        added += 1

    db.commit()
    return {
        "fetched": len(raw_data),
        "added": added,
        "duplicates": duplicates,
        "rejected": len(rejected),
    }

def period_series(counts, period):
    labels = sorted(counts)
    series = []

    if period == "weekly":
        current, end = date.fromisoformat(labels[0]), date.fromisoformat(labels[-1])
        while current <= end:
            series.append(counts.get(current.isoformat(), 0))
            current += timedelta(days=7)
    else:
        y, m = map(int, labels[0].split("-"))
        end_y, end_m = map(int, labels[-1].split("-"))
        while (y, m) <= (end_y, end_m):
            series.append(counts.get(f"{y}-{m:02d}", 0))
            m += 1
            if m > 12:
                y, m = y + 1, 1
    return series


def fit_trend(series, period="monthly"):
    if len(series) < MIN_PERIODS[period]:
        return None

    x = np.arange(len(series))
    y = np.array(series, dtype=float)

    mean = float(y.mean())
    if mean == 0:
        return None

    slope, _ = np.polyfit(x, y, 1)
    pct = slope / mean * 100
    direction = "stable" if abs(pct) < 1 else ("increasing" if slope > 0 else "decreasing")

    return {
        "period": period,
        "direction": direction,
        "change_per_period": round(float(slope), 5),
        "percent_change_per_period": round(float(pct), 3),
        "average_per_period": round(mean, 2),
        "periods_analysed": len(series),
    }