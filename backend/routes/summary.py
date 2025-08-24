from fastapi import APIRouter, Query
from models import SummaryResponse
from db.fake_db import get_user

router = APIRouter()

@router.get("/", response_model=SummaryResponse)
def get_summary(user_id: str = Query(...)):
    user = get_user(user_id)
    if not user:
        return {"error": "User not found"}

    # Example logic using stored info
    has_panels = user.get("has_panels", False)
    bill = float(user.get("energy_bill", 100))  # default £100 bill
    goal = user.get("goal", "savings")

    daily_saving_gbp = round(bill * 0.25 / 30, 2) if has_panels else 0.0
    co2_offset_kg = round(bill * 0.1 / 30, 2) if has_panels else 0.0
    battery_status = "80% full" if has_panels else "N/A"

    if goal == "sustainability":
        msg = "🌱 You're cutting CO₂ emissions like a pro!"
    elif goal == "savings":
        msg = "💰 Great! You're saving big on energy costs."
    else:
        msg = "☀️ Solar power is powering your goals!"

    return SummaryResponse(
        user_id=user_id,
        daily_saving_gbp=daily_saving_gbp,
        co2_offset_kg=co2_offset_kg,
        battery_status=battery_status,
        message=msg
    )
