from fastapi import APIRouter, Query
from models import SummaryResponse
from db.fake_db import get_user

router = APIRouter()

@router.get("/", response_model=SummaryResponse)
def get_summary(user_id: str = Query(...)):
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}

    # Dummy calculation logic
    has_panels = user["has_panels"]
    savings = 1.72 if has_panels else 0.0
    co2 = 1.3 if has_panels else 0.0
    battery = "80% full" if has_panels else "N/A"
    msg = "Nice work! You're in the top 25% this week 🌱" if has_panels else "Install panels to start saving!"

    return SummaryResponse(
        user_id=user_id,
        daily_saving_gbp=savings,
        co2_offset_kg=co2,
        battery_status=battery,
        message=msg
    )
