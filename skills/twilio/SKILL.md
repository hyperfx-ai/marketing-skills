---
name: twilio
description: Twilio messaging, voice, phone number management, and verification workflows. Use when the user wants to send SMS or WhatsApp messages, make voice calls, buy or configure phone numbers, or run OTP verification.
use_cases:
  - Send SMS messages
  - Send WhatsApp messages
  - Make phone calls
  - Manage Twilio phone numbers
  - Build OTP verification flows
triggers:
  - twilio
  - sms
  - whatsapp
  - phone verification
  - otp
  - send message
requires_toolkits:
  - twilio_toolkit
suggested_toolkits:
  - file_manager
---

# Twilio Communications

Use this skill for all Twilio tasks including SMS, WhatsApp, voice calls, and verification.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Twilio integration** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## WhatsApp Sandbox Setup (Required for Testing)

Before sending WhatsApp messages in sandbox/testing mode, users must join the sandbox:

1. User goes to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. They find their unique join code (e.g., "join happy-turtle")
3. They send that message from WhatsApp to **+14155238886**
4. Once confirmed, use `twilio_send_whatsapp` with `from_number` set to `"+14155238886"`

**If WhatsApp message fails with "not a valid WhatsApp-enabled number" or similar:**
- The user likely hasn't joined the sandbox yet
- Guide them through the steps above

## Tool Quick Reference

### Messaging
- `twilio_send_sms` - Send SMS/MMS messages
- `twilio_send_whatsapp` - Send WhatsApp messages (sandbox: use +14155238886 as from_number)
- `twilio_list_messages` - List message history
- `twilio_check_delivery_status` - Check if message was delivered

### Voice Calls
- `twilio_make_call` - Initiate outbound call (requires TwiML URL or inline TwiML)
- `twilio_list_calls` - List call history
- `twilio_list_recordings` - List call recordings

### Phone Numbers
- `twilio_list_phone_numbers` - List numbers in account (use to find valid from_number)
- `twilio_lookup_phone` - Validate phone number and get carrier info

### Verification (OTP)
- `twilio_create_verification_service` - Create verification service first
- `twilio_send_verification` - Send OTP code
- `twilio_check_verification` - Verify user's code

## Common Patterns

**Before sending SMS/WhatsApp:** Call `twilio_list_phone_numbers` first to find a valid sender number.

**WhatsApp sandbox flow:**
1. Confirm user has joined sandbox (provide instructions if not)
2. Call `twilio_send_whatsapp` with:
```json
{
  "to": "+1XXXXXXXXXX",
  "body": "Hello from the assistant",
  "from_number": "+14155238886"
}
```

**Phone verification flow:**

Step 1 -- Call `twilio_create_verification_service` with:
```json
{
  "friendly_name": "My App"
}
```

Step 2 -- Call `twilio_send_verification` with:
```json
{
  "service_sid": "<service_sid_from_step_1>",
  "to": "+1XXXXXXXXXX",
  "channel": "sms"
}
```

Step 3 -- Call `twilio_check_verification` with:
```json
{
  "service_sid": "<service_sid>",
  "to": "+1XXXXXXXXXX",
  "code": "<user_provided_code>"
}
```

## Safety Rules

- Never assume a valid sender number; always verify with `twilio_list_phone_numbers`.
- Do not continue silently after failures; report exact error and ask user how to proceed.
- For verification flows, keep service SIDs and code checks explicit and auditable.
