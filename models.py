from pydantic import BaseModel

class OnboardingRequest(BaseModel):
    user_id: str
    location: str
    has_panels: bool
    energy_bill: str
    goal: str

class SummaryResponse(BaseModel):
    user_id: str
    daily_saving_gbp: float
    co2_offset_kg: float
    battery_status: str
    message: str
