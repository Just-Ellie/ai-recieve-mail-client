# mail-client

A minimal sample client for [ai-mail.sh](https://ai-mail.sh) — an email address your bot can rent for $0.05/day. Receive-only: no sending, no spam, no signup. Pay with x402 (USDC on Base).

## The idea

Your agent needs an email address to receive a signup code. You don't want to run mail infrastructure, and you don't want a mailbox that lives forever.

Buy an address for a day. Use it. Let it lapse — it costs nothing while lapsed, and it's still yours when you come back months later. Whoever holds the key owns the address; addresses are never reassigned.

## Quickstart

**1. Buy an inbox:**

```
POST https://ai-mail.sh/inbox/day
→ 402 with x402 payment instructions → pay $0.05 USDC on Base
→ { "address": "k7x2m9qa@ai-mail.sh", "inbox": "<id>", "token": "<token>", ... }
```

**2. Export the credentials:**

```
export AI_MAIL_INBOX=<id> AI_MAIL_TOKEN=<token>
```

**3. Run the sample:**

```
python3 mail_client.py
```

The script prints the inbox status, then waits for the next verification email, pulls out the code, and deletes the message as it's returned (`&delete=1` — read-and-burn). Nothing lingers.

Prefer MCP? Point any MCP client at `https://ai-mail.sh/mcp` with header `Authorization: Bearer <token>`.

## What the script shows

- `status()` — plan, expiry, messages left (`GET /inbox/:id`)
- `wait_for_code()` — long-poll for the next unseen message (`GET /inbox/:id/wait?timeout=60`), returns the extracted OTP or verification link
- `recent()` — list recent messages (`GET /inbox/:id/messages`)
- Error handling for 401 (bad credentials), 402 (inbox needs funding), 404 (not found)

Full API docs: https://ai-mail.sh

## Privacy

Delete means delete. Message content lives only in object storage and is erased immediately on delete, otherwise 7 days after arrival. The database never holds mail content. No names, no accounts, no cookies, no tracking. Full notes: https://ai-mail.sh/privacy

## No support, by design

Lose your key or token and the inbox is gone. It's $0.05 — get another.
