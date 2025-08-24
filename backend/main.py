from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from routes import onboarding, summary, tips, solar

app = FastAPI(title="SolarPal MVP API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])
app.include_router(summary.router, prefix="/summary", tags=["Summary"])
app.include_router(tips.router, prefix="/tips", tags=["Tips"])
app.include_router(solar.router, prefix="/solar", tags=["Solar"])  # forecast + weather

@app.get("/")
def root():
    return {"message": "SolarPal API running 🚀"}
