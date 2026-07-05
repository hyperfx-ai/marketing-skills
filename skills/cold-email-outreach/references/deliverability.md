# Deliverability

The single biggest reason cold-email campaigns fail is not the copy — it's that the emails don't make it to the inbox. Send infrastructure is the part most operators ignore until they're already burned. Read this *before* the first send.

## The mental model

Inbox providers (Gmail, Outlook, Apple Mail) decide whether to deliver, spam-folder, or block your mail based on three signals:

1. **Identity** — Can the provider verify the sender is who they claim to be? (SPF, DKIM, DMARC.)
2. **Reputation** — How does this domain / IP behave? (Bounce rate, spam complaints, engagement, age.)
3. **Content** — Does this email *look* like spam? (Spammy words, too many links, image-heavy, fake `Re:` prefixes, "no-reply" sender, unsubscribe nags.)

Cold outreach lives or dies on identity + reputation. The Hyper MCP can't fix either for you — they're DNS / inbox-level concerns. But it *can* avoid making them worse.

## Hard rules — never break these

1. **Never cold-send from your primary work domain.** If your real email is `you@yourcompany.com`, do not run cold outbound from that mailbox. One spam complaint trains Gmail to send your *internal* mail to spam too. Use a dedicated sending domain (e.g., `you@yourcompany-sales.com` or `you@get-yourcompany.com`).
2. **Never start a cold campaign from a fresh-zero-day mailbox.** A brand-new Gmail / Workspace account that suddenly sends 100 emails on day 1 will be flagged within 24 hours. Warm for at least 2–4 weeks first.
3. **Never include images, HTML formatting, or more than 1 link in a cold email.** Plain text reads as human; rich formatting reads as marketing.
4. **Never use fake `Re:` or `Fwd:` subject prefixes.** Provider filters spot this and Gmail explicitly penalizes it.
5. **Never email purchased lists or scraped emails you can't verify.** Apollo's verified emails (with `reveal_personal_emails=True`) have far lower bounce rates than `firstname@domain.com` guesses.
6. **Never let bounce rate exceed 5% on a campaign.** Above that, the inbox provider will start spam-foldering you. Above 10%, you're at risk of getting suspended. See [List hygiene](#list-hygiene) below.

## Sending limits

Gmail's published soft limits (per account, per 24h rolling window):

| Account type | Sends/day | Recipients/day (across all sends) |
| --- | --- | --- |
| Free Gmail | ~500 | ~500 |
| Google Workspace (Business Starter / Standard) | ~2,000 | ~2,000 |
| Google Workspace (Business Plus / Enterprise) | ~2,000 | ~10,000 |

These are *soft* — Gmail throttles before they suspend, but if you hit the throttle the campaign stalls. Plan to use 50–70% of the cap so you have headroom for follow-ups.

For new / cold sending accounts, start at **20–40 sends/day** and ramp gradually (see warming below). The cap is the limit; the actual safe volume on a fresh account is much lower.

## Sender warming (the 2–4 week setup)

Skip warming and you'll burn the domain before the campaign clears Phase 4.

### Week 1 — establish a real-mail baseline (20 sends/day)

- Send and reply to real human conversations from the new mailbox. Not bots — actual people.
- Subscribe to 3–5 newsletters (Stratechery, Lenny's, your industry's daily). Open and click sometimes.
- Don't send any cold mail.

### Week 2 — small-batch warm sends (40 sends/day)

- Start sending real, opted-in mail (e.g., to existing customers, partners, internal team) to build positive engagement signal.
- Add the new sender's email signature to other mailboxes you control so people send mail *to* it (incoming mail = positive reputation).

### Week 3 — first cold sends (50 sends/day)

- Begin Phase 4 sends in batches of 50 or fewer.
- Monitor: bounce rate < 3%, no spam complaints. If you cross either, pause and diagnose.

### Week 4+ — scale to target volume

- Increase by ~25% per day if metrics stay clean.
- Cap at 70% of Gmail's daily limit (so ~350/day for free, ~1,400/day for Workspace).

There are also paid services (Mailwarm, Lemwarm, Warmup Inbox) that automate the warming bot-traffic. They speed things up but the inbox providers are getting better at detecting bot warming — manual + real correspondence is more durable.

## DNS — SPF, DKIM, DMARC

These three records on the *sending domain's* DNS tell inbox providers "yes, this server / service is allowed to send mail as this domain."

| Record | What it does | Where to set |
| --- | --- | --- |
| **SPF** | Lists the IPs / services authorized to send as this domain | DNS TXT record |
| **DKIM** | Cryptographic signature on the email proving it wasn't tampered with in transit | DNS TXT record (key provided by Google Workspace) |
| **DMARC** | Tells receivers what to do if SPF or DKIM fail (allow / quarantine / reject) and reports to you | DNS TXT record (`_dmarc.yourdomain.com`) |

### Minimum config for cold sending from Google Workspace

```
# SPF — TXT record on yourdomain.com
v=spf1 include:_spf.google.com ~all

# DKIM — get the actual key from Workspace Admin → Apps → Google Workspace → Gmail → Authenticate email
google._domainkey.yourdomain.com  TXT  "v=DKIM1; k=rsa; p=MIGfMA0GCSqG..."

# DMARC — TXT record on _dmarc.yourdomain.com
v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@yourdomain.com; pct=100
```

Start with `p=quarantine` (failed mail goes to spam, not rejected). Move to `p=reject` only after a few weeks of clean DMARC reports.

The Hyper MCP doesn't manage DNS — these have to be set on the registrar / DNS host. Verify them with `dig` or [mxtoolbox.com](https://mxtoolbox.com) before the first send.

## List hygiene

Bad addresses tank deliverability faster than bad copy. Before adding a prospect to a campaign:

1. **Use Apollo's verified emails.** Pass `reveal_personal_emails=True` on `apollo_people_bulk_match` — Apollo flags verified vs guessed.
2. **Skip the role-based addresses for cold outbound.** `info@`, `sales@`, `hello@` rarely reply and often hit shared inboxes that spam-flag everything.
3. **Honor Apollo's `email_status`.** If status is `unverified` or `bounced`, drop the prospect — don't try to email anyway.
4. **Drop prospects who have ever replied "remove me / unsubscribe / not interested" — across any campaign in the workspace.** Maintain a global `unsubscribed` Gmail label and check against it before each campaign:

```
gmail_messages_list(query="label:unsubscribed to:<prospect-email>")
```

If anything comes back, do not send.

## Pacing inside the day

Don't dump 100 sends in 5 minutes. Spread them out:

- **Time of day:** 8–11am and 1–3pm in the *recipient's* time zone get the highest open rates.
- **Per-minute cap:** Stay under 1 send per 6 seconds. Faster = bot-like.
- **Per-hour cap:** Stay under 30–50 sends/hour from a single mailbox.
- **Day of week:** Tuesday–Thursday outperform Monday and Friday for B2B. Avoid sends on weekends.

Implementation: run the send loop over a `gmail_messages_send` call, sleep ~15–60 seconds between sends, batch ~30 sends per hour. The agent can drive this directly.

## Monitoring — what to check after every campaign day

| Metric | Target | How to check | What it means if bad |
| --- | --- | --- | --- |
| Bounce rate | < 3% | Apollo + Gmail bounce notifications | List quality is poor — re-enrich or pause |
| Spam complaint rate | < 0.1% | Gmail Postmaster Tools | Copy reads as spam, or list is wrong-target |
| Reply rate | > 2% | `gmail_messages_list(query="label:cold/<campaign> to:me newer_than:7d")` | Copy / targeting is off, or list is dead |
| Open rate | If tracked: 40%+ | (open tracking pixels are detectable and hurt deliverability — generally skip) | Subject line is weak |

[Gmail Postmaster Tools](https://postmaster.google.com) is the single most useful free dashboard. Set it up the day you set up the sending domain. It shows your domain's reputation directly.

## When you've already been blocked or spam-foldered

Signals you're in trouble:

- Replies suddenly stop (without copy changes).
- Test sends from the cold mailbox to your *own* personal Gmail land in spam.
- Your sending IP shows up on a public blocklist (check at [mxtoolbox.com](https://mxtoolbox.com)).

Recovery playbook:

1. **Stop the campaign immediately.** Continuing makes it worse.
2. **Diagnose:** Bounce rate? Spam complaints? Sudden volume jump? Bad list?
3. **Wait 2–4 weeks** before sending any cold mail from that domain again.
4. **Restart warming from week 1** — yes, all the way back.
5. **Move to a *new* sending sub-domain** (e.g., from `get-yourcompany.com` to `try-yourcompany.com`) if reputation damage is severe.

The fastest way to recover from a deliverability problem is *not* to be in one in the first place. Spend the 2–4 weeks on warming up front; the math works out.

## Compliance — quick legal checklist

Cold outbound is legal in most jurisdictions, but with rules. Mostly common-sense:

- **CAN-SPAM (US):** Include a real physical address in the email footer. Honor opt-outs within 10 business days. Don't use deceptive subject lines.
- **GDPR (EU):** Cold B2B outreach is generally allowed under "legitimate interest" if (a) the email is on the prospect's published professional channels, (b) the message is relevant to their job, and (c) they have a clear way to opt out. Don't email EU consumers without explicit opt-in.
- **CASL (Canada):** Stricter — generally requires implied or express consent. Be careful with Canadian prospects.
- **PIPL / CCPA / state privacy laws:** Mostly affect data storage, not the cold-send itself, but worth verifying for your jurisdiction.

The skill defaults assume B2B outbound to professional contacts based on Apollo-verified data, with a clear opt-out, a real footer, and unsubscribe enforcement via the global `unsubscribed` label. That's compliant in most cases — but if you're operating in a high-risk jurisdiction or industry, get legal sign-off before scaling.
