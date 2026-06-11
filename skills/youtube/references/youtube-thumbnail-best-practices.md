# YouTube thumbnail best practices

Channel-agnostic packaging guidance the agent should apply when designing
a thumbnail or critiquing one. Pair with `composition-tips.md`, which
covers the visual mechanics.

## CTR-driven mindset

The thumbnail's only job is to win the click against ~12 sibling thumbnails
on the suggested feed. Every design decision should be evaluated against:

> "Does this make a viewer pause and click *instead* of the next video?"

If the answer is "it looks nice", the thumbnail is failing.

## The packaging unit

A thumbnail never works alone. It must form a coherent **packaging unit**
with the title:

- **Curiosity gap** between thumbnail visual and title text — the visual
  raises a question the title partially answers.
- **No redundancy** — never use the same words on the thumbnail and in the
  title. Wasted real estate.
- **Tone match** — sober thumbnail + clickbait title = trust collapse.

When in doubt, write the title first, then design the thumbnail to create
tension with it.

## Hook archetypes that consistently work

Use these as a checklist when generating concepts:

1. **Transformation / before-after** — clearly show two states.
2. **Big number** — "$10K", "100×", "Day 47". Numbers must look hand-set,
   not auto-rendered.
3. **Contrarian claim** — visually contradict the audience's prior.
4. **Curiosity gap** — show the *outcome* but obscure the *cause*.
5. **Authority** — recognisable expert / celebrity / brand on screen.
6. **Reaction shot** — strong emotion at something the viewer can't see.
7. **Comparison / vs.** — two subjects with a divider.
8. **Process reveal** — peek inside something normally hidden.
9. **Risk / stakes** — implied danger, deadline, or scarcity.
10. **Pattern interrupt** — visually breaks the niche's convention.

Always pick one primary hook per thumbnail. Stacking hooks dilutes them.

## Niche conventions

Quickly check the top results for the user's search term (use
`research_top_thumbnails`) and note the niche convention before designing.
Common conventions:

- **Tech / coding** — code editor screenshots, dark backgrounds, neon
  highlights, expressive faces pointing at things.
- **Finance** — green/red, large numbers, charts going up-and-to-the-right.
- **Lifestyle / vlog** — bright outdoor shots, full body in frame, warm
  colour grade.
- **Educational / explainer** — diagrams, arrows, isolated subject on a
  flat background.

You can either follow the convention (safer, blends into the feed) or
intentionally break it (riskier, but a strong differentiator). Tell the
user which strategy you're using and why.

## Title best practices

- **Length** — keep under 70 characters so it never truncates on mobile or
  the suggested feed.
- **Keyword early** — primary keyword in the first 50 characters helps
  search ranking.
- **Avoid clickbait that misleads.** YouTube's ranking model penalises
  high-CTR-but-low-watch-time videos harder than low-CTR ones.
- **Test variants.** When the user asks for titles, give them 10 stylistic
  variants (handled by `generate_seo_titles.py`) — they should A/B test.

## Description best practices

The first 1-2 lines show in search snippets and above the fold; everything
else is for the algorithm.

- **Hook line** — first line restates the value prop, includes the primary
  keyword.
- **Summary** — 2-3 sentences, keyword-natural, no stuffing.
- **Key takeaways** — bulleted, scannable.
- **Timestamps** — if you have them, include them. They both help retention
  and unlock chapters.
- **CTA** — single, specific call-to-action. "Subscribe for more" is dead;
  "Get the template at <link>" works.
- **Hashtags** — 3-5 relevant hashtags at the very end. The first 3 show
  above the title.

`generate_seo_description.py` produces this whole structure plus a
`flattened` field the user can paste straight into YouTube.

## Iteration loop

When the user is iterating on a thumbnail:

1. Generate 1 thumbnail at a time. Don't dump 4 variants without comment.
2. After each generation, name the **specific** thing you'd change next
   ("the text is competing with the face — move it lower", not "we could
   try variations").
3. Stop iterating after 3 attempts on the same concept. If it isn't working
   after 3 tries, the concept is wrong; go back to
   `analyze_thumbnail_concepts.py` for a different angle.
