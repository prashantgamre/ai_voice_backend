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
REFRESH_TOKEN = os.getenv("ZCRM_REFRESH_TOKEN", "1000.64736e2f23724d4b8a0443a2ccb640ff.8375d82c3b7ce9c4247d1ebb8b23ef98")
CLIENT_ID = os.getenv("ZCRM_CLIENT_ID", "1000.6D6TQVEON9AP86IEIA5DUDETZ6PZPJ")
CLIENT_SECRET = os.getenv("ZCRM_CLIENT_SECRET", "6e9db45c0ec9a3dac6f4404f5ed6e27b424d14a65c")
TOKEN_BASE = os.getenv("ZCRM_ACCOUNTS_BASE", "https://accounts.zoho.in")
API_BASE = os.getenv("ZCRM_API_BASE", "https://www.zohoapis.in")
PHONE_TO_SEARCH = os.getenv("ZCRM_TEST_PHONE", "9833220705")
PRODUCTS_TO_SEARCH = os.getenv("ZCRM_TEST_PRODUCTS", "Iphon17 pro")

LEADS_SEARCH_URL = f"{API_BASE}/crm/v8/Leads/search?phone={PHONE_TO_SEARCH}"

Products_url = f"{API_BASE}/crm/v8/Products?fields=Product_Name={PRODUCTS_TO_SEARCH},Unit_Price,Product_Name,Color,Storage"

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

def make_products_request(access_token: str):
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
    }
    return requests.get(Products_url, headers=headers, timeout=30)

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
    products_response = make_products_request(token)

    # If token invalid/expired, refresh once and retry
    if is_auth_error(resp):
        try:
            token = get_access_token()
        except Exception as e:
            print("Token refresh failed after auth error:", e)
            print("Original response:", resp.status_code, resp.text)
            return
        resp = make_leads_request(token)
        products_response = make_products_request(token)

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


    # Handle final Products response
    if products_response.status_code == 200:
        try:
            data = products_response.json()
        except Exception:
            print("Success but response is not JSON:")
            print(products_response.text)
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
        print(products_response.status_code)
        print(products_response.text)


if __name__ == "__main__":
    main()