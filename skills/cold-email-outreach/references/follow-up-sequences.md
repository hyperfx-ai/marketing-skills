# Follow-Up Sequences

The reply rate on the first touch is the floor, not the ceiling. Most positive replies in cold outbound come on touches 2–4. The follow-up sequence is where the campaign is won or lost.

## The non-negotiables

1. **Each follow-up adds something new.** A different angle, fresh proof, a useful resource. "Just checking in" is a tax on the reader's attention with no payoff — it nukes reply rates and trains the prospect to ignore you.
2. **Each email stands alone.** Don't assume the prospect read the previous touches. A follow-up that only makes sense if you read touch 1 has already lost.
3. **Always reply in the original thread.** Use `gmail_reply_to_message` with the `thread_id` from touch 1 (saved from the `gmail_messages_send` response). Threading preserves context and helps deliverability — Gmail treats threaded replies more favorably than fresh sends to the same address.
4. **Widen the gaps as the sequence goes.** First gap is short, last gap is long. Hammering on a tight cadence reads as desperate and trips spam filters.
5. **Honor the breakup.** If the breakup email is "closing your file unless I hear back," actually close the file. Sending a sneaky "actually one more thing" after a breakup nukes credibility.

## Default cadence (5 touches over 21 days)

| Touch | Day | Gap | Angle | Subject pattern | Tool |
| --- | --- | --- | --- | --- | --- |
| 1 | 0 | — | Initial framework (Observation / Question / Trigger / Story) | Short and lowercase | `gmail_messages_send` |
| 2 | +3 | 3d | Same angle, sharpened — add a one-line specific proof | Reply (no subject change) | `gmail_reply_to_message` |
| 3 | +7 | 4d | *Different* angle from touch 1 | Reply | `gmail_reply_to_message` |
| 4 | +14 | 7d | Useful free resource (case study, calculator, teardown) | Reply | `gmail_reply_to_message` |
| 5 | +21 | 7d | Breakup. "Closing your file." | Reply | `gmail_reply_to_message` |

Adjust to context: a high-stakes enterprise campaign might run 7 touches over 6 weeks; a SMB volume play might run 3 touches in 7 days. Five touches over 21 days is the sane default.

## Angle rotation — what "different angle" actually means

If touch 1 was Observation → Problem → Proof → Ask, then touch 3 needs to *not* be a sharper observation. Rotate.

| Touch 1 angle | Touch 3 angle (good) | Touch 3 angle (bad — same shape) |
| --- | --- | --- |
| Observation (what you noticed) | Question (force them to answer one in their head) | Another observation about a different page on their site |
| Question (what's going on with X) | Story (similar customer's outcome) | Variant of the same question |
| Trigger (recent event) | Mechanism (specifically how you'd help) | Same trigger restated |
| Story (customer A's outcome) | Question (does this map to your situation?) | Customer B's story |

The point of rotating is to give the prospect *new information* — a new way to evaluate whether you're worth a reply.

## Touch-by-touch templates (Observation framework example)

### Touch 1 — initial

See [`frameworks.md`](./frameworks.md) for the full Observation example. It opens the thread.

### Touch 2 (+3 days) — sharpened proof

```
Touch 2 (reply in same thread, no subject change)

Quick follow-up — forgot to mention: the result with Notion was on a 
team your size (12 SDRs). They cut their per-prospect research time 
from 90s to 8s in the first 2 weeks.

Worth seeing how?

— Sam
```

Two sentences. Adds a *new* concrete data point (team size match → makes the proof more credible for *this* reader). Same ask.

### Touch 3 (+7 days) — different angle (Question)

```
Touch 3 (same thread)

Different angle — out of curiosity, are you running prospect research
in-house, with an agency, or with one of the prefab tools?

Asking because the play we use only really clicks if you're in one of
the first two camps.

— Sam
```

Now you're qualifying. Many prospects who didn't reply to touch 1–2 will reply to a question because it's a low-cost answer. And the answer routes the rest of the conversation.

### Touch 4 (+14 days) — useful resource

```
Touch 4 (same thread)

Switching gears — wrote up the Ramp onboarding teardown I mentioned in
[short link]. Five-min read, no signup. Even if we're not a fit, the
section on the 90-day SDR ramp curve is probably useful.

Holler if anything resonates.

— Sam
```

The resource has to be genuinely useful and *related to the problem* — not a sales deck dressed up as a "guide." If you don't have a real piece, skip touch 4 and go straight to the breakup.

### Touch 5 (+21 days) — breakup

```
Touch 5 (same thread)

Going to close the file on my end since the timing's clearly off.

If outbound prospect research moves up the priority list later, my
inbox is open — no follow-up from me until then.

— Sam
```

Two sentences. No "one last thing" pitch. The breakup email is your last touch — honor it. Conventional wisdom (and most data) says breakup emails get the second-highest reply rate after touch 1. They work *because* you mean it.

## Pruning prospects mid-sequence

Stop sending immediately if any of these happen:

| Signal | Action | Tool |
| --- | --- | --- |
| Reply (any classification — interested, objection, not now, unsubscribe) | Stop sequence. Apply classification label. | `gmail_labels_add` (and `gmail_labels_remove` if removing) |
| Hard bounce | Remove from sequence. Mark email as bad in Apollo (don't enrich again). | (manual) |
| Soft bounce 2x in a row | Pause sequence. Investigate (mailbox full, vacation auto-reply). | (manual) |
| OOO / vacation auto-reply | Pause sequence, resume after the OOO end date in the message body. | `gmail_messages_list(query="is:oof from:<email>")` |
| "Wrong contact, talk to X" | Stop sequence to original contact. Start a new (1-touch) sequence to X. | New `apollo_people_match` + `gmail_messages_send` |

The single biggest reason cold-email campaigns get blocked: continuing to email people who replied "remove me" because the operator didn't classify the reply correctly. Build the label discipline early.

## How to actually run the cadence

The Hyper MCP doesn't have a native cron — the agent / user has to drive the schedule. Two patterns:

### Pattern A — Daily checkin (recommended for ≤200 prospects)

Once a day the user says: "Run the cold-email cadence — send any due touches and pull replies."

```
1. gmail_messages_list(query="label:cold/<campaign> is:unread newer_than:1d")
   → process replies, apply classification labels, prune sequence
2. For each prospect with no reply and last touch > N days ago:
     - gmail_reply_to_message(thread_id=..., body=<next angle>)
     - gmail_labels_add(message_id=..., label_ids=["cold/<campaign>/touch-N"])
3. Report: X sent, Y replied, breakdown by classification.
```

The agent maintains state via Gmail labels — no external scheduler needed.

### Pattern B — Per-touch single-prompt

The user prompts each touch separately:

> "Send touch 2 to anyone in `cold/q3-growth-leads` who got touch 1 ≥ 3 days ago and hasn't replied."

Same toolchain, just on-demand instead of daily. Useful for low-volume / high-stakes outreach where the user wants to eyeball the list each time.

## Subject lines on follow-ups

Don't change the subject line on follow-ups — keeping the same subject preserves threading and signals to Gmail that this is conversational, not promotional. The `gmail_reply_to_message` tool handles this automatically (it uses `Re:` if Gmail's UI does).

If a thread goes very long (10+ messages), Gmail clients sometimes collapse it. At that point a fresh send with a slightly different subject is fine — but you've already lost the thread.

## What never to do in follow-ups

- **"Bumping this to the top of your inbox."** Performative and annoying.
- **"In case you missed it."** They didn't miss it, they ignored it. Don't make them feel bad.
- **"My boss is asking about you."** Manipulative; reads as fake urgency.
- **"Last chance!"** There is no last chance for a cold email.
- **Adding new recipients to the thread (CC'ing the boss).** Aggressive and reads as escalation. Don't.
- **Sending the same email twice with a different subject line.** Gmail / spam filters spot this immediately and the prospect notices.

## Volume math (so the campaign doesn't run you over)

5 touches × N prospects × cadence = total sends. Plan around your daily cap:

| Prospects | Sends in the 21-day window | Sends/day (if spread evenly) |
| --- | --- | --- |
| 50 | 250 | ~12 |
| 200 | 1,000 | ~48 |
| 500 | 2,500 | ~120 |
| 1,000 | 5,000 | ~240 |

A consumer Gmail account caps at ~500/day; a Workspace account at ~2,000/day. Campaigns above 1,000 prospects need either a warmed dedicated sending account or a bigger time window. See [`deliverability.md`](./deliverability.md) for warming and pacing.
