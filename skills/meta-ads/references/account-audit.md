
# Meta Account Audit

This skill guides you through a comprehensive Meta Ads account audit.

## Step 1: Account Overview

Start by fetching account-level data:

1. Use `meta_get_ad_accounts` to list all ad accounts
2. For each account, note the spend limits, timezone, and currency
3. Check account status and any restrictions

## Step 2: Campaign Structure Review

For each account:

1. Use `meta_get_campaigns` to list all campaigns
2. Group campaigns by objective:
   - Awareness campaigns
   - Traffic campaigns
   - Conversion campaigns
   - Lead generation campaigns
3. Note naming conventions and organization

## Step 3: Performance Analysis

Pull performance data for the last 30 days:

1. Use `meta_get_insights` with date range for account-level metrics
2. Key metrics to capture:
   - Total spend
   - Impressions and reach
   - Click-through rate (CTR)
   - Cost per result (CPR)
   - Return on ad spend (ROAS)

## Step 4: Ad Set Analysis

For top-spending campaigns:

1. Use `meta_get_adsets` to get ad set details
2. Review targeting settings:
   - Audience sizes
   - Age/gender targeting
   - Interest and behavior targeting
   - Lookalike audiences
3. Check budget distribution

## Step 5: Creative Review

For top ad sets:

1. Use `meta_get_ads` to list all ads
2. Review creative types in use:
   - Static images
   - Videos
   - Carousels
   - Dynamic creative
3. Check ad fatigue (frequency > 3)

## Step 6: Recommendations

Based on findings, provide:

1. **Quick Wins**: Changes that can be made immediately
2. **Structural Changes**: Longer-term improvements
3. **Testing Opportunities**: New approaches to try

## Output Format

Create a summary report with:
- Executive summary
- Key metrics table
- Top/bottom performing campaigns
- Prioritized recommendations

Consider using the sandbox to create a visualization dashboard if requested.
