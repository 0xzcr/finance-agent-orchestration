"""
Zerodha Kite Connect authentication flow.

Kite Connect uses OAuth-style login:
1. User is redirected to Kite login page
2. After login, Kite redirects back with a `request_token`
3. We exchange request_token for an `access_token`
4. access_token is used for all subsequent API calls (valid for one trading day)
"""

import os
from app.config import settings


def get_login_url() -> str:
    """Generate the Zerodha login URL for the user to authenticate."""
    if not settings.KITE_API_KEY:
        raise ValueError("KITE_API_KEY not configured.")

    return f"https://kite.zerodha.com/connect/login?v=3&api_key={settings.KITE_API_KEY}"


def generate_access_token(request_token: str) -> dict:
    """
    Exchange request_token for access_token after user completes Kite login.

    Args:
        request_token: Token received from Kite redirect callback

    Returns:
        Dict with access_token and user info
    """
    try:
        from kiteconnect import KiteConnect
    except ImportError:
        raise ImportError("kiteconnect not installed. Run: pip install kiteconnect")

    kite = KiteConnect(api_key=settings.KITE_API_KEY)

    data = kite.generate_session(
        request_token=request_token,
        api_secret=settings.KITE_API_SECRET,
    )

    access_token = data["access_token"]

    # Store in environment for the current session
    os.environ["KITE_ACCESS_TOKEN"] = access_token

    return {
        "access_token": access_token,
        "user_id": data.get("user_id", ""),
        "user_name": data.get("user_name", ""),
        "email": data.get("email", ""),
    }


def is_authenticated() -> bool:
    """Check if we have a valid Kite access token."""
    token = os.environ.get("KITE_ACCESS_TOKEN", settings.KITE_ACCESS_TOKEN)
    return bool(token)
