from pydantic import BaseModel

class SummaryResponse(BaseModel):
    user_id: str
    daily_saving_gbp: float
    co2_offset_kg: float
    battery_status: str
    message: str
