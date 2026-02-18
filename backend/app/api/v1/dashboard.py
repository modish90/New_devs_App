from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", None)
    if tenant_id is None and isinstance(current_user, dict):
        tenant_id = current_user.get("tenant_id")

    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant not resolved for current user")

    if (month is None) ^ (year is None):
        raise HTTPException(status_code=400, detail="Both month and year must be provided together")
    
    revenue_data = await get_revenue_summary(property_id, tenant_id, month=month, year=year)

    total_revenue_decimal = Decimal(revenue_data["total"]).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    total_revenue_float = float(total_revenue_decimal)
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": total_revenue_float,
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count'],
        "month": revenue_data.get("month"),
        "year": revenue_data.get("year"),
        "timezone": revenue_data.get("timezone"),
    }
