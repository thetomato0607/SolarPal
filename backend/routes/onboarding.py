from fastapi import APIRouter
from models import OnboardingRequest
from db.fake_db import save_user

router = APIRouter()

@router.post("/")
def onboarding(data: OnboardingRequest):
    save_user(data.user_id, data.dict())
    return {
        "message": f"Welcome {data.user_id}! We've saved your setup and will guide you step by step ☀️"
    }
