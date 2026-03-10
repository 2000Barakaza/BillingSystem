



import json
from fastapi import APIRouter, Request, HTTPException, status
from svix.webhooks import Webhook, WebhookVerificationError
from backend.app.core.config import settings
from backend.app.core.clerk import clerk

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

PRO_TIER_SLUG = "pro_tier"
FREE_TIER_LIMIT = settings.FREE_TIER_LIMIT
UNLIMITED_LIMIT = 1_000_000

def set_org_member_limit(org_id: str, limit: int):
    clerk.organizations.update(
        organization_id=org_id,
        max_allowed_memberships=limit
    )

def has_active_pro_plan(items: list) -> bool:
    return any(
        item.get("plan", {}).get("slug") == PRO_TIER_SLUG
        and item.get("status") == "active"
        for item in items
    )

@router.post("/clerk")
async def clerk_webhook(request: Request):
    # Clerk inatuma raw body, sio JSON moja kwa moja
    payload = await request.body()
    headers = dict(request.headers)

    print(f"Webhook received! Event: {headers.get('svix-event-type')}")

    if settings.CLERK_WEBHOOK_SECRET:
        try:
            wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
            event = wh.verify(payload, headers)
        except WebhookVerificationError:
            print("Invalid signature")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid signature")
    else:
        event = json.loads(payload)

    event_type = event.get("type")
    data = event.get("data", {})
    org_id = data.get("payer", {}).get("organization_id")

    if event_type in ["subscription.created", "subscription.updated"]:
        if org_id:
            limit = UNLIMITED_LIMIT if has_active_pro_plan(data.get("items", [])) else FREE_TIER_LIMIT
            set_org_member_limit(org_id, limit)
            print(f"UPGRADED org {org_id} to {limit}")

    elif event_type in ["subscription.pastDue", "subscription.deleted", "subscription.cancelled"]:
        if org_id:
            set_org_member_limit(org_id, FREE_TIER_LIMIT)
            print(f"DOWNGRADED org {org_id} to FREE tier (reason: {event_type})")

    return {"received": True}






