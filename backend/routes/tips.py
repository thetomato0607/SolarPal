from fastapi import APIRouter, Query
from db.fake_db import get_user

router = APIRouter()

@router.get("/")
def get_tip(user_id: str = Query(...)):
    user = get_user(user_id)

    if not user:
        return {"tip": "Please complete onboarding first."}

    has_panels = user["has_panels"]
    goal = user["goal"]

    # Very basic tip logic
    if not has_panels:
        return {"tip": "Did you know installing solar could save you up to £500/year? I can help you plan it!"}

    if goal == "save_money":
        return {"tip": "Try running your dishwasher during the day to use more solar and less grid electricity."}
    elif goal == "help_environment":
        return {"tip": "You're already saving CO₂ every day! Want to go further? Consider adding a battery system."}
    else:
        return {"tip": "Want to optimise your solar output? Tap the 'Improve My Setup' button on your dashboard."}
