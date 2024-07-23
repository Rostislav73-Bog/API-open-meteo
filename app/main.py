from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from datetime import datetime, timedelta

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/weather", response_class=HTMLResponse)
async def get_weather(request: Request, city: str, date: str):
    geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    async with httpx.AsyncClient() as client:
        geocode_response = await client.get(geocode_url)
        if geocode_response.status_code != 200:
            raise HTTPException(status_code=geocode_response.status_code, detail="Ошибка получения данных геокодирования")

        geocode_data = geocode_response.json()
        if "results" not in geocode_data or len(geocode_data["results"]) == 0:
            raise HTTPException(status_code=404, detail="Город не найден")

        lat = geocode_data["results"][0]["latitude"]
        lon = geocode_data["results"][0]["longitude"]

    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&start_date={date}&end_date={date}"
    async with httpx.AsyncClient() as client:
        weather_response = await client.get(weather_url)
        if weather_response.status_code != 200:
            raise HTTPException(status_code=weather_response.status_code, detail="Ошибка получения данных о погоде")

        weather_data = weather_response.json()

    # Получение данных для указанной даты и формирование почасовых данных
    date_time_obj = datetime.strptime(date, '%Y-%m-%d')
    hourly_temps = weather_data.get('hourly', {}).get('temperature_2m', [])
    hourly_times = [date_time_obj + timedelta(hours=i) for i in range(24)]

    return templates.TemplateResponse("weather.html", {
        "request": request,
        "city": city,
        "date": date,
        "latitude": lat,
        "longitude": lon,
        "weather": list(zip(hourly_times, hourly_temps))
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)