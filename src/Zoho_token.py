"""
Refactor to support automatic token refresh and retry.
Add helpers to obtain access token using refresh token, make the Leads request, and retry once on 401/invalid token.
Read credentials from environment variables with safe fallbacks to existing values.
Add basic error handling and prints.
"""

import os
import requests
import logging
from livekit.agents import function_tool, RunContext
from numpy import number
import requests
import json

# Config: Prefer environment variables; fallback to current hardcoded values (consider moving these to env vars)
REFRESH_TOKEN = os.getenv("ZCRM_REFRESH_TOKEN", "1000.8b2b6a958ac61db0f6f4060e68f73510.98997cef5924d3138eb1c33ffb90bc4f")
CLIENT_ID = os.getenv("ZCRM_CLIENT_ID", "1000.8560GQVGSJ3HYSQ0QJ1SZ38G1QAYMW")
CLIENT_SECRET = os.getenv("ZCRM_CLIENT_SECRET", "7b00100eeb05eae0060d3f834e4a5e7bc69665d037")
TOKEN_BASE = os.getenv("ZCRM_ACCOUNTS_BASE", "https://accounts.zoho.in")
API_BASE = os.getenv("ZCRM_API_BASE", "https://www.zohoapis.in")
PHONE_TO_SEARCH = os.getenv("ZCRM_TEST_PHONE", "9833220705")

LEADS_SEARCH_URL = f"{API_BASE}/crm/v8/Leads/search?phone={PHONE_TO_SEARCH}"


def get_access_token() -> str:
    """Get a fresh access token using the refresh token."""
    token_url = (
        f"{TOKEN_BASE}/oauth/v2/token"
        f"?refresh_token={REFRESH_TOKEN}"
        f"&client_id={CLIENT_ID}"
        f"&client_secret={CLIENT_SECRET}"
        f"&grant_type=refresh_token"
    )
    resp = requests.post(token_url, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to get access token: {resp.status_code} {resp.text}")
    body = resp.json()
    if "access_token" not in body:
        raise RuntimeError(f"Access token missing in response: {body}")
    return body["access_token"]


def make_leads_request(access_token: str):
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
    }
    return requests.get(LEADS_SEARCH_URL, headers=headers, timeout=30)


def is_auth_error(response: requests.Response) -> bool:
    """Detect if response indicates an expired/invalid token."""
    if response.status_code in (401, 403):
        return True
    # Some APIs return errors in JSON with specific codes/messages
    try:
        body = response.json()
        # Check common fields; adjust if Zoho returns a specific error schema for v8
        if isinstance(body, dict):
            code = str(body.get("code") or body.get("status_code") or "").upper()
            msg = str(body.get("message") or body.get("status") or "").upper()
            if "INVALID_TOKEN" in code or "INVALID_TOKEN" in msg:
                return True
            if "EXPIRED" in code or "EXPIRED" in msg:
                return True
    except Exception:
        pass
    return False


def main():
    try:
        token = get_access_token()
    except Exception as e:
        print("Error obtaining access token:", e)
        return

    # First attempt
    resp = make_leads_request(token)

    # If token invalid/expired, refresh once and retry
    if is_auth_error(resp):
        try:
            token = get_access_token()
        except Exception as e:
            print("Token refresh failed after auth error:", e)
            print("Original response:", resp.status_code, resp.text)
            return
        resp = make_leads_request(token)

    # Handle final response
    if resp.status_code == 200:
        try:
            data = resp.json()
        except Exception:
            print("Success but response is not JSON:")
            print(resp.text)
            return
        # Print the data section if present, else full
        if isinstance(data, dict) and "data" in data:
            print(data["data"])
        else:
            print(data)
        # Also print the access token used (for debugging). Remove in production.
        print("Access token used:", token)
    else:
        print("Error: failed to fetch data")
        print(resp.status_code)
        print(resp.text)


if __name__ == "__main__":
    main()