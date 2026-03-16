"""Azure AD token validation."""

from __future__ import annotations

import json
import logging
import urllib.request

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from app.config.settings import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()

_azure_keys: list = []


def _fetch_azure_keys() -> list:
    """Download the Microsoft signing keys (executed once at import)."""
    if not settings.AZURE_TENANT_ID:
        return []
    url = f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/discovery/v2.0/keys"
    try:
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read())["keys"]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not fetch Azure keys: %s", exc)
        return []


_azure_keys = _fetch_azure_keys()


def validate_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Validate the Azure AD Bearer token and return the decoded payload."""
    token = credentials.credentials

    if not settings.AZURE_TENANT_ID or not _azure_keys:
        raise HTTPException(
            status_code=401,
            detail="Azure AD is not configured. Set AZURE_TENANT_ID and AZURE_CLIENT_ID.",
        )

    # ── Decode header to find signing key ──────────────────────────────
    try:
        unverified = jwt.get_unverified_header(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token header")

    rsa_key: dict = {}
    for key in _azure_keys:
        if key["kid"] == unverified.get("kid"):
            rsa_key = {k: key[k] for k in ("kty", "kid", "use", "n", "e")}
            break

    if not rsa_key:
        raise HTTPException(status_code=401, detail="Signing key not found")

    # ── Verify signature, then validate audience & issuer ──────────────
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=settings.AZURE_CLIENT_ID,
            options={"verify_iss": False},
        )

        # Validate issuer (support both v1 and v2 endpoints)
        valid_issuers = [
            f"https://sts.windows.net/{settings.AZURE_TENANT_ID}/",
            f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/v2.0",
        ]
        token_issuer = payload.get("iss", "")
        if token_issuer not in valid_issuers:
            logger.error("Invalid issuer: %s", token_issuer)
            raise HTTPException(status_code=401, detail="Invalid token issuer")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTClaimsError as e:
        logger.error("Invalid claims: %s", e)
        raise HTTPException(status_code=401, detail="Invalid token claims")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token verification failed: %s", e)
        raise HTTPException(status_code=401, detail="Token verification failed")
