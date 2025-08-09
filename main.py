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
