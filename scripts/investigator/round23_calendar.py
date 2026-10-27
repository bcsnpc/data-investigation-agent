"""Owner's explicit live start date; offline fixtures never contact a provider."""
from datetime import datetime,timezone

LIVE_START=datetime(2026,10,26,tzinfo=timezone.utc)


def require_live_window(now=None):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:raise ValueError('UTC_DATE_REQUIRED')
    if now<LIVE_START:raise RuntimeError('ROUND23_OFFLINE_ONLY_BEFORE_OWNER_APPROVAL_2026_10_26')
