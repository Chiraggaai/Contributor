from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Response

from app.schemas.payouts import PayoutSortBy
from app.services.earnings_data import contributor_data
from app.services.payout_receipt_pdf import MINIMAL_PDF

router = APIRouter(prefix="/api/contributor/payouts", tags=["payouts"])


@router.get("")
def list_payouts(
    status: Optional[str] = Query(default=None),
    sort_by: PayoutSortBy = Query(default=PayoutSortBy.DATE),
    sort_dir: Literal["asc", "desc"] = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    return contributor_data.list_payouts(
        status=status,
        sort_by=sort_by.value,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )


@router.get("/{payout_id}/receipt")
def get_payout_receipt(
    payout_id: str,
    format: Literal["pdf"] = Query(default="pdf", alias="format"),
):
    detail = contributor_data.payout_detail(payout_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Payout not found")
    if format != "pdf":
        raise HTTPException(status_code=400, detail="Only format=pdf is supported")
    filename = f"payout-receipt-{detail.reference}.pdf"
    return Response(
        content=MINIMAL_PDF,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{payout_id}")
def get_payout(payout_id: str):
    detail = contributor_data.payout_detail(payout_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Payout not found")
    return detail
