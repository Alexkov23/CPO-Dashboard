"""Google OAuth2 authentication for accessing private Google Docs.

Handles the OAuth2 flow:
1. /api/auth/google -> redirects user to Google consent screen
2. /api/auth/google/callback -> exchanges code for tokens, stores them
3. Tokens are persisted to disk and reused across restarts
"""

import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

_credentials_dir = Path(os.getenv("CREDENTIALS_DIR", "/data"))
_token_path = _credentials_dir / "google_token.json"
_client_secret_path = _credentials_dir / "client_secret.json"

_cached_creds: Credentials | None = None
_pending_flow: Flow | None = None


def get_client_config() -> dict | None:
    if _client_secret_path.exists():
        with open(_client_secret_path) as f:
            return json.load(f)
    env_val = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
    if env_val:
        return json.loads(env_val)
    return None


def save_client_config(config: dict) -> None:
    _credentials_dir.mkdir(parents=True, exist_ok=True)
    with open(_client_secret_path, "w") as f:
        json.dump(config, f)


def get_credentials() -> Credentials | None:
    global _cached_creds
    if _cached_creds and _cached_creds.valid:
        return _cached_creds

    if _cached_creds and _cached_creds.expired and _cached_creds.refresh_token:
        from google.auth.transport.requests import Request

        _cached_creds.refresh(Request())
        _save_token(_cached_creds)
        return _cached_creds

    if _token_path.exists():
        creds = Credentials.from_authorized_user_file(str(_token_path), SCOPES)
        if creds and creds.valid:
            _cached_creds = creds
            return creds
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request

            creds.refresh(Request())
            _cached_creds = creds
            _save_token(creds)
            return creds

    return None


def _save_token(creds: Credentials) -> None:
    _credentials_dir.mkdir(parents=True, exist_ok=True)
    with open(_token_path, "w") as f:
        f.write(creds.to_json())


def create_auth_flow(redirect_uri: str) -> tuple[Flow, str] | None:
    global _pending_flow
    config = get_client_config()
    if not config:
        return None

    flow = Flow.from_client_config(
        config, scopes=SCOPES, redirect_uri=redirect_uri
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline", prompt="consent"
    )
    _pending_flow = flow
    return flow, authorization_url


def exchange_code(code: str, redirect_uri: str) -> Credentials | None:
    global _cached_creds, _pending_flow

    if _pending_flow:
        flow = _pending_flow
        flow.redirect_uri = redirect_uri
        _pending_flow = None
    else:
        config = get_client_config()
        if not config:
            return None
        flow = Flow.from_client_config(
            config, scopes=SCOPES, redirect_uri=redirect_uri
        )

    flow.fetch_token(code=code)

    creds = flow.credentials
    _cached_creds = creds
    _save_token(creds)
    return creds


def is_authenticated() -> bool:
    return get_credentials() is not None
