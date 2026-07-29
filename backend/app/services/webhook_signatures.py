"""Webhook signature verification utilities.

Provides HMAC-based signature verification for external webhook sources.
All verifications use constant-time comparison to prevent timing attacks.
Ported from IncidentFox's production ``signatures.py``.

Supported services:
- GitHub:    HMAC-SHA256 with ``sha256=`` prefix
- Slack:     HMAC-SHA256 with ``v0=`` prefix
- PagerDuty: HMAC-SHA256 with ``v1=`` prefix
"""

from __future__ import annotations

import hashlib
import hmac
import time


class SignatureVerificationError(Exception):
    """Raised when webhook signature verification fails."""

    def __init__(self, reason: str, service: str):
        self.reason = reason
        self.service = service
        super().__init__(f"{service} signature verification failed: {reason}")


def verify_github_signature(
    *,
    secret: str,
    signature_header: str | None,
    raw_body: bytes,
) -> None:
    """Verify a GitHub webhook request signature.

    GitHub uses HMAC-SHA256 and sends the signature in the
    ``X-Hub-Signature-256`` header with a ``sha256=`` prefix.

    Args:
        secret: The webhook secret configured in GitHub.
        signature_header: Value of the ``X-Hub-Signature-256`` header.
        raw_body: The raw request body bytes.

    Raises:
        SignatureVerificationError: If verification fails.
    """
    if not secret:
        raise SignatureVerificationError("missing_webhook_secret", "github")
    if not signature_header:
        raise SignatureVerificationError("missing_signature_header", "github")

    if not signature_header.startswith("sha256="):
        raise SignatureVerificationError("invalid_signature_format", "github")

    expected_sig = signature_header[7:]  # Strip "sha256=" prefix
    computed = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, computed):
        raise SignatureVerificationError("signature_mismatch", "github")


def verify_slack_signature(
    *,
    signing_secret: str,
    timestamp: str | None,
    signature: str | None,
    raw_body: str,
    max_age_seconds: int = 300,
) -> None:
    """Verify a Slack webhook request signature.

    Slack uses HMAC-SHA256 with format:
    - Base string: ``v0:{timestamp}:{body}``
    - Signature header: ``v0={hex_digest}``

    Args:
        signing_secret: Slack app signing secret.
        timestamp: ``X-Slack-Request-Timestamp`` header.
        signature: ``X-Slack-Signature`` header.
        raw_body: Raw request body as string.
        max_age_seconds: Max age of request (default 5 minutes).

    Raises:
        SignatureVerificationError: If verification fails.
    """
    if not signing_secret:
        raise SignatureVerificationError("missing_signing_secret", "slack")
    if not timestamp:
        raise SignatureVerificationError("missing_timestamp_header", "slack")
    if not signature:
        raise SignatureVerificationError("missing_signature_header", "slack")

    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        raise SignatureVerificationError("invalid_timestamp", "slack")

    # Replay protection
    age = abs(time.time() - ts)
    if age > max_age_seconds:
        raise SignatureVerificationError(
            f"request_too_old ({age:.0f}s > {max_age_seconds}s)", "slack"
        )

    base_string = f"v0:{timestamp}:{raw_body}"
    computed = (
        "v0="
        + hmac.new(
            signing_secret.encode("utf-8"),
            base_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(signature, computed):
        raise SignatureVerificationError("signature_mismatch", "slack")


def verify_pagerduty_signature(
    *,
    secret: str,
    signature_header: str | None,
    raw_body: bytes,
) -> None:
    """Verify a PagerDuty V3 webhook signature.

    PagerDuty uses HMAC-SHA256 with a ``v1=`` prefix.

    Args:
        secret: PagerDuty webhook signing secret.
        signature_header: Value of ``X-PagerDuty-Signature`` header.
        raw_body: The raw request body bytes.

    Raises:
        SignatureVerificationError: If verification fails.
    """
    if not secret:
        raise SignatureVerificationError("missing_webhook_secret", "pagerduty")
    if not signature_header:
        raise SignatureVerificationError("missing_signature_header", "pagerduty")

    # PagerDuty may send multiple signatures separated by commas
    signatures = [s.strip() for s in signature_header.split(",")]
    computed = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    for sig in signatures:
        if sig.startswith("v1="):
            if hmac.compare_digest(sig[3:], computed):
                return

    raise SignatureVerificationError("signature_mismatch", "pagerduty")
