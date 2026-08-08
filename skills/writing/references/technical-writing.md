# Technical writing systems

Structures for documents that must be acted on correctly: docs, procedures, specs, UI copy. The shared contract: the reader is mid-task, possibly frustrated, and reads to do — not to appreciate. Ambiguity here is not a style problem; it is a defect.

## Plain language

**Use for:** anything a non-specialist must act on — help center articles, policies, onboarding, billing and legal explanations.

**Hard rules:**

1. Address the reader as "you." Name the actor in every sentence.
2. Common words: "use" not "utilize," "help" not "facilitate," "end" not "terminate."
3. Sentences average under 20 words. One idea each.
4. No double negatives, no "unless...except" chains. Rewrite as positive conditions.
5. Define a necessary technical term at first use, in one sentence, then use only that term (no elegant-variation synonyms).
6. Headings are questions or tasks the reader actually has ("Cancel your subscription"), not nouns ("Cancellation policy").

**Before:**

> Termination of the subscription may be effectuated by the user at any time via the account management interface, whereupon a pro-rata refund shall be issued, except in cases where usage thresholds have been exceeded.

**After:**

> You can cancel your subscription at any time from Settings → Billing. We refund the unused part of your month. Exception: if you used more than your plan's included volume this month, that usage is billed first.

---

## Diátaxis — the four documentation modes

**Use for:** structuring any docs set, and diagnosing why an existing page fails.

Every docs page is exactly one of four things. Mixing modes on one page is the root cause of most bad documentation.

| Mode | Reader's situation | The page's job | Failure smell |
| --- | --- | --- | --- |
| **Tutorial** | New, learning by doing | A guaranteed-success first journey | Detours into options and theory |
| **How-to guide** | Competent, mid-task, has a goal | The steps for this one goal | Teaching basics the reader has |
| **Reference** | Knows what they need, wants facts | Complete, accurate, findable description | Chatty prose, opinions |
| **Explanation** | Curious, off-task | Why it works this way | Step-by-step instructions creeping in |

**Hard rules:**

1. Declare the mode before writing. One page, one mode.
2. Tutorials promise and deliver success: tested end-to-end, zero forks ("if you prefer X..."), visible result at each stage.
3. How-to guides start from a named starting condition and assume competence. Numbered steps, one action per step, each step verifiable.
4. Reference pages are structured like the thing they describe, exhaustive, and free of advice. Advice links out to explanation.
5. When a page fights you, check its mode first: a "tutorial" full of options is a how-to wearing the wrong clothes.

---

## Controlled technical English

**Use for:** procedures where misreading has a cost — operator instructions, runbooks, safety steps, checklists. Inspired by the ASD-STE100 controlled-language standard.

**Hard rules:**

1. One instruction per sentence. Sentences of 20 words or fewer.
2. Imperative mood for every instruction: "Press the button." Never "The button should be pressed."
3. One meaning per word, one word per meaning, everywhere in the document. If "close" means "shut the valve," it never also means "nearly."
4. State the condition before the instruction: "If the light is red, stop the pump" — never "Stop the pump if the light is red" (the reader may act before reading the condition).
5. Warnings come before the step they concern, never after.
6. No pronouns where a noun can repeat. "Remove the filter. Clean the filter." — not "clean it."

**Before:**

> The system should be restarted after configuration changes have been applied, though it's usually fine to wait until the end of a batch, unless changes were made to auth, which need an immediate restart.

**After:**

> If you changed auth settings: restart the system now.
> For all other changes: restart the system at the end of the current batch.

---

## RFC requirement keywords

**Use for:** specs, API contracts, integration requirements — documents where "should" being read as "must" (or the reverse) causes real disputes.

**Hard rules:**

1. Use the keywords with their standard meanings: **MUST** (absolute requirement), **MUST NOT** (absolute prohibition), **SHOULD** (do it unless you have a good, understood reason), **MAY** (truly optional).
2. Capitalize the keywords so they read as defined terms.
3. State the keyword definitions once at the top of the document.
4. Never use lowercase "should"/"must" loosely elsewhere in the spec — pick the keyword or rewrite the sentence.
5. Every MUST is testable. If you cannot write the check, you cannot write the MUST.

**Example:**

> Webhook consumers MUST respond with a 2xx within 5 seconds. Consumers SHOULD process payloads asynchronously and respond before processing. Consumers MAY request a replay of events up to 7 days old. Consumers MUST NOT treat event ordering as guaranteed.

---

## UX microcopy

**Use for:** buttons, error messages, empty states, confirmations, tooltips — the words inside the product.

**Hard rules:**

1. Buttons are verb-first and name the outcome: "Save changes," "Send invoice" — never "OK," "Submit," "Yes."
2. Every error message answers three questions in order: what happened, why (if known), what to do next.
3. Never blame the user. "That code has expired" — not "You entered an invalid code."
4. Empty states sell the next action, not the emptiness: what this screen will show, and the one button that starts it.
5. Confirmations for destructive actions name the object and the consequence: "Delete 'Q3 Report'? This cannot be undone." The confirming button repeats the verb ("Delete report"), never "Yes."
6. Sentence case everywhere. No exclamation points. No "Oops."

**Before:**

> Error: Invalid input. Please try again!

**After:**

> That email address is missing an "@". Check it and resend — or use SSO if your company uses Google Workspace.
