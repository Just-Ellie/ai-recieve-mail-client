#!/usr/bin/env python3
"""
ai-mail.sh sample client — receive-only.

Gives your bot an email address for $0.05/day, no signup, no SDK.
This script demos the whole receive loop: check the inbox, wait for a
verification email, pull out the code, delete the message. No sending.

Setup (one time, by a human or a funded bot):
    1. POST https://ai-mail.sh/inbox/day
       -> 402 with x402 payment instructions (pay $0.05 USDC on Base)
       -> { "address": "k7x2m9qa@ai-mail.sh", "inbox": "<id>",
            "token": "<token>", "expires_at": "...", "messages_left": 10 }
    2. export AI_MAIL_INBOX=<id> AI_MAIL_TOKEN=<token>

Then:
    python3 mail_client.py
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://ai-mail.sh"
INBOX = os.environ.get("AI_MAIL_INBOX")
TOKEN = os.environ.get("AI_MAIL_TOKEN")


class AiMailError(Exception):
    pass


def _req(method, path, http_timeout=30, **params):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url, method=method, headers={"Authorization": f"Bearer {TOKEN}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=http_timeout) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        if e.code == 401:
            raise AiMailError("bad inbox id or token (401)")
        if e.code == 402:
            raise AiMailError(
                "inbox needs funding/extending (402) — "
                "POST /inbox/<id>/day and pay the x402 invoice"
            )
        if e.code == 404:
            raise AiMailError("inbox not found (404)")
        raise AiMailError(f"HTTP {e.code}: {body[:200]}")


def status():
    """Plan, expiry, messages left for this inbox."""
    _, data = _req("GET", f"/inbox/{INBOX}")
    return data or {}


def recent(limit=10):
    """Newest-first list of recent messages (sender, subject, extracted code)."""
    _, data = _req("GET", f"/inbox/{INBOX}/messages")
    return (data or [])[:limit]


def wait_for_code(timeout=120, burn=True):
    """
    Block until the next unseen email arrives, or timeout seconds pass.

    Returns the extracted OTP / verification code (or the verification
    link if there is no numeric code), or None on timeout.

    burn=True appends &delete=1: the message is erased server-side as it
    is returned — read-and-burn. Nothing lingers in storage.
    """
    params = {"timeout": timeout}
    if burn:
        params["delete"] = 1
    code, data = _req(
        "GET", f"/inbox/{INBOX}/wait", http_timeout=timeout + 30, **params
    )
    if code == 204 or not data:
        return None
    return data.get("otp") or data.get("verify_link")


def main():
    if not INBOX or not TOKEN:
        sys.exit("set AI_MAIL_INBOX and AI_MAIL_TOKEN first (see docstring)")
    info = status()
    print(
        f"inbox {info.get('address', INBOX)} — "
        f"{info.get('messages_left', '?')} messages left, "
        f"expires {info.get('expires_at', '?')}"
    )
    print("waiting for a verification email (Ctrl-C to stop)...")
    try:
        code = wait_for_code(timeout=300)
    except KeyboardInterrupt:
        sys.exit("\nstopped.")
    if code:
        print(f"code: {code}   (message deleted on read)")
    else:
        print("timed out — no new mail arrived.")


if __name__ == "__main__":
    main()
