import httpx, time

BASE_URL = "https://dev-task.elancoapps.com/"

def fetch(path, retries=3):
    for attempt in range(retries):
        try:
            response = httpx.get(BASE_URL + path, timeout=5)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError):
            if attempt == retries - 1:
                raise
            time.sleep(2**attempt)
    return None

def get_tick_sightings():
    return fetch("/data/tick-sightings")