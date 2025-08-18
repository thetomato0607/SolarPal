from fastapi import FastAPI
from routes import onboarding, summary, tips

app = FastAPI(title="SolarPal MVP API")

# Include routers
app.include_router(onboarding.router, prefix="/onboarding")
app.include_router(summary.router, prefix="/summary")
app.include_router(tips.router, prefix="/tips")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/summary")
def get_summary(
    location: str = Query(..., description="City or 'lat,lon'"),
    system_size: float = Query(..., gt=0, description="kW")
):
    # TODO: replace with your real logic
    est = round(system_size * 4.5, 2)
    return {"summary": {"location": location, "system_size_kw": system_size, "estimated_daily_kwh": est},
            "tip": "Tilt panels roughly to your latitude."}
