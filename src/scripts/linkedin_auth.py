"""
Re-authorizes LinkedIn OAuth with additional profile reading scopes.

Usage:
    python src/scripts/linkedin_auth.py

Flow:
    1. Opens the authorization link in the terminal / browser.
    2. User clicks and approves on LinkedIn.
    3. The local server captures the callback.
    4. Exchanges the code for a token and saves it in the .env file.
"""

import http.server
import os
import sys
import urllib.parse
import urllib.request
import json
import webbrowser
from pathlib import Path
from dotenv import load_dotenv, set_key

load_dotenv()

REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "openid profile email r_liteprofile w_member_social"

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"

# ─── Callback Server ─────────────────────────────────────────────────────────

captured_code = None

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "error" in params:
            error = params["error"][0]
            desc = params.get("error_description", [""])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                f"<h2>Error: {error}</h2><p>{desc}</p>".encode("utf-8")
            )
            print(f"\n[ERROR] LinkedIn returned: {error} — {desc}")
            return

        code = params.get("code", [None])[0]
        if code:
            captured_code = code
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<h2>&#10003; Authorized!</h2>"
                b"<p>You can close this tab. The token has been saved in your .env file.</p>"
            )
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Parameter 'code' not found.")

    def log_message(self, format, *args):
        pass  # Silence server logs


# ─── OAuth ───────────────────────────────────────────────────────────────────

def build_auth_url(client_id: str, state: str = "linkedin_reauth") -> str:
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
    })
    return f"https://www.linkedin.com/oauth/v2/authorization?{params}"


def exchange_code_for_token(code: str, client_id: str, client_secret: str) -> dict:
    body = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()

    req = urllib.request.Request(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def save_token(token_data: dict):
    access_token = token_data.get("access_token", "")
    set_key(str(ENV_PATH), "LINKEDIN_ACCESS_TOKEN", access_token)
    
    if "refresh_token" in token_data:
        set_key(str(ENV_PATH), "LINKEDIN_REFRESH_TOKEN", token_data["refresh_token"])
        
    scope = token_data.get("scope", "")
    expires_in = int(token_data.get("expires_in", 0))
    days_until_expiration = expires_in // 86400
    
    print(f"  Scopes granted    : {scope}")
    print(f"  Expires in        : {expires_in}s (~{days_until_expiration} days)")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("[ERROR] LINKEDIN_CLIENT_ID or LINKEDIN_CLIENT_SECRET not found in .env")
        sys.exit(1)

    auth_url = build_auth_url(client_id)

    print("\n" + "=" * 60)
    print("  LINKEDIN RE-AUTHORIZATION")
    print("=" * 60)
    print(f"\nRequested scopes: {SCOPES}\n")
    print("Opening browser... If it does not open automatically, access this link:")
    print(f"\n  {auth_url}\n")
    print("Waiting for callback at http://localhost:8888 ...")
    print("=" * 60)

    webbrowser.open(auth_url)

    server = http.server.HTTPServer(("localhost", 8888), CallbackHandler)
    server.timeout = 120  # 2 minutes for the user to approve

    try:
        while captured_code is None:
            server.handle_request()
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user.")
        sys.exit(0)

    if not captured_code:
        print("\n[ERROR] Timeout reached. No code received.")
        sys.exit(1)

    print("\nCode received. Exchanging for token...")

    try:
        token_data = exchange_code_for_token(captured_code, client_id, client_secret)
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Failed to exchange code: HTTP {e.code} — {e.read().decode()}")
        sys.exit(1)

    save_token(token_data)

    print("\n✓ Token successfully saved in .env!")

    # Verify what we can read now
    print("\nTesting profile access...")
    token = token_data["access_token"]

    endpoints = [
        ("userinfo (OpenID)", "https://api.linkedin.com/v2/userinfo"),
        ("liteprofile", "https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,headline,location,summary)"),
    ]

    for name, url in endpoints:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                print(f"\n  ✓ {name}:")
                print(f"    {json.dumps(data, ensure_ascii=False)[:200]}...")
        except urllib.error.HTTPError as e:
            print(f"\n  ✗ {name}: HTTP {e.code} — Lacking specific API permissions for this endpoint.")


if __name__ == "__main__":
    main()