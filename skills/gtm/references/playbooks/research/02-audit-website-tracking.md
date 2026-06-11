# Audit Website Tracking

Check what tracking pixels, CMS, and performance infrastructure a site has. Determines paid campaign readiness and SEO baseline.

## When to use

Read this in the `research/foundation` group, immediately after `01-scrape-brand-profile.md`. Its output (Meta Pixel present? GA4 connected? CMS = Webflow?) gates several downstream choices: whether `paid-ads/meta` is plausible, whether `playbooks/organic-content/16-publish-to-webflow.md` will work, and whether the gtm decision layer should flag missing tracking as an `open_question`.

## What You Get

- **Tracking pixels** — Meta Pixel ID, GTM ID, LinkedIn Insight Tag, Twitter Pixel, TikTok Pixel, Hotjar
- **Tech stack** — framework, CMS, hosting
- **Page speed** — performance score, LCP, FCP, CLS
- **Launch readiness** — paid ready (has pixel), SEO ready (speed score >= 60), tracking score

## Tool Calls

Run in parallel:

```
analyze_website(url="https://{DOMAIN}")
hyperseo_pagespeed(url="https://{DOMAIN}", strategy="mobile")
```

`analyze_website` returns tracking pixels (Meta Pixel, GTM, LinkedIn, Twitter/X, TikTok, Hotjar), CMS, detected technologies (frameworks like Next.js, Tailwind), quality signals (SSL, mobile viewport, clear CTA, contact info, social links), and a tracking score.

Most sites redirect apex to www (or vice versa), so both calls return the same data. Only call both variants if the first one returns no pixels and you suspect a redirect issue.

## Failure Modes

- **Both variants return no pixels:** Could be GTM loading pixels dynamically after page render. Note it, ask the user to confirm their pixel setup manually.
- **Page speed returns null:** Domain might be behind a WAF or CDN that blocks Lighthouse. Note "unable to measure" rather than guessing.
- **CMS not detected:** Common for custom builds (Next.js, Nuxt, etc.). Report the framework instead.

