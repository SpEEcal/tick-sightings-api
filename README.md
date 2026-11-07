# Tick Sightings API

A backend service that imports tick sighting data from the Elanco API,
stores it in a local database, and provides endpoints to search, filter
and analyse it.

## Setup - requires Python 3.10 or newer.
1. Clone the repository and move into it:

        git clone https://github.com/SpEEcal/tick-sightings-api.git
        cd tick-sightings-api

2. Create and activate a virtual environment:

        python -m venv .venv

   Windows (PowerShell):

        .venv\Scripts\activate

   macOS / Linux:

        source .venv/bin/activate

3. Install the dependencies:

        pip install -r requirements.txt

4. Start the server:

        uvicorn main:app --reload

The data is imported automatically on startup.
Interactive docs: http://127.0.0.1:8000/docs

## Project structure

    api.py              fetches data from the Elanco API (with retries)
    database.py         SQLite connection and session
    models.py           Sighting table definition
    services.py         import logic and trend calculation
    routers/analytics.py  analysis endpoints
    main.py             app setup and /sightings endpoint

## Endpoints

- **Filtered list + total:** GET /sightings?location=&species=&date_from=&date_to=  
- **Counts per location:** GET /analytics/by-location                             
- **Trend over time:** GET /analytics/trend?period=monthly|weekly              

## Design choices

- Local SQLite copy of the data therefore endpoints stay fast and keep working
  if the external API is down; the API is only called during import.
- API id as primary key so that re-running the import never creates duplicates.
- Incomplete records are rejected, and the import reports how many.
- Filtering and counting done in SQL, so it scales to larger datasets.
- Trend = linear fit over per-period counts, with empty periods filled
  as zero so each step is exactly one week or month.