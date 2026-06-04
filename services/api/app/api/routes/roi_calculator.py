from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.domains.calculator.service import calculate_roi

router = APIRouter()


class RoiCalculatorRequest(BaseModel):
    users: int = Field(ge=0)
    tokens_per_user: int = Field(ge=0)
    provider: str
    infrastructure_cost: float = Field(ge=0)
    employees: int = Field(ge=0)
    subscription_price: float = Field(ge=0)


@router.post("/roi-calculator")
def roi_calculator(payload: RoiCalculatorRequest) -> dict[str, float | int]:
    return calculate_roi(**payload.model_dump())
