from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import require_api_key
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
def roi_calculator(
    payload: RoiCalculatorRequest,
    _: dict[str, str | int | None] = Depends(require_api_key),
) -> dict[str, float | int]:
    return calculate_roi(**payload.model_dump())
