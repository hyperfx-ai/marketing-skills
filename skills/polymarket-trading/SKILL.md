---
name: polymarket-trading
description: Trade on Polymarket prediction markets with a safe workflow and risk management. Use when the user wants to browse markets, check prices, place or close positions on Polymarket, or review their prediction-market portfolio.
use_cases:
  - Trade on Polymarket
  - Find prediction markets
  - Check Polymarket portfolio
  - Analyze market odds
  - Buy/sell prediction shares
triggers:
  - polymarket
  - prediction market
  - betting
  - market odds
requires_toolkits:
  - polymarket_toolkit
suggested_toolkits:
  - system_web_toolkit
icon: polymarket
short_description: Research Polymarket prediction markets and manage positions and orders.
---

# Polymarket Trading

Guide for trading on Polymarket prediction markets. Polymarket is a decentralized prediction market on Polygon.

## Requirements

- **Hyper MCP installed and connected.** [https://app.hyperfx.ai/mcp](https://app.hyperfx.ai/mcp)
- **Polymarket toolkit** enabled at [https://app.hyperfx.ai/integrations](https://app.hyperfx.ai/integrations).

## Important: Time Sensitivity

**Prediction markets are time-sensitive!**
- Check if market end_date has passed or is imminent
- Consider how much time remains for events to occur
- Markets about past events have already been resolved
- Always verify current date context

## Getting Fresh News

For news-driven trading, ALWAYS use real-time sources:
1. **Web Search** - Use `web_search` with time filters like "last hour" or "today"
2. **X/Twitter** - Check trending topics and breaking news
3. Cross-reference multiple sources for accuracy
4. Be skeptical of cached/old results

## Tool Categories

### Market Discovery (Read-Only)

| Tool | Use Case |
|------|----------|
| `polymarket_trending_markets_get` | Find what's hot RIGHT NOW (volume in last N minutes) |
| `polymarket_events_search` | Find events by topic (events contain related markets) |
| `polymarket_events_get` | Get specific event by ID or URL slug |
| `polymarket_markets_search` | Find individual markets by keyword |
| `polymarket_markets_list` | Browse top markets by liquidity/volume |
| `polymarket_markets_get` | Get details for specific market by ID |
| `polymarket_markets_get_by_slug` | Get market directly by URL slug |

**Events vs Markets:**
- **Events** are top-level objects (e.g., "Super Bowl 2026")
- **Markets** are individual outcomes within events (e.g., "Will Chiefs win?")
- Use `search_events` first for discovery, then explore markets within events

### Trading Analysis

| Tool | Use Case |
|------|----------|
| `polymarket_order_books_get` | See bid/ask depth for a token |
| `polymarket_prices_get` | Get current price (BUY or SELL side) |

### Portfolio Management (Authenticated)

| Tool | Use Case |
|------|----------|
| `polymarket_balances_get` | Check USDC balance |
| `polymarket_positions_list` | View current holdings with P&L |
| `polymarket_orders_get` | List open orders |
| `polymarket_trades_get` | View trade history |

### Trading (Authenticated)

| Tool | Use Case |
|------|----------|
| `polymarket_markets_buy` | Buy shares at market price |
| `polymarket_markets_sell` | Sell shares at market price |
| `polymarket_orders_create` | Place limit order at specific price |
| `polymarket_orders_cancel` | Cancel a specific order |
| `polymarket_orders_cancel_all` | Cancel all open orders |

## Optimal Trading Workflow

### Finding Good Markets
1. Use search tools - defaults filter out resolved, expired, and low liquidity markets
2. Best markets have:
   - Liquidity > $50,000
   - Price between 20-80%
   - End date in the future
   - Recent volume

### Before Trading - ALWAYS Check:
```python
# 1. Verify funds
polymarket_balances_get()

# 2. Check spread and liquidity
polymarket_order_books_get(token_id=token_id)

# 3. Get actual execution price
polymarket_prices_get(token_id=token_id, side="BUY")
```

### Executing a Buy
```python
# 1. Get market details to find token_id
market = polymarket_markets_get(market_id)
# token_ids are in market.clob_token_ids - first is YES, second is NO

# 2. Check order book
book = polymarket_order_books_get(token_id=yes_token_id)

# 3. Execute market buy
result = polymarket_markets_buy(token_id=yes_token_id, amount=10)  # $10 USDC
```

## Token ID Rules

### Binary Markets (Yes/No)
- `clob_token_ids[0]` = YES token
- `clob_token_ids[1]` = NO token
- Buying YES = betting event WILL happen
- Buying NO = betting event WON'T happen

### Token ID Format
- Token IDs are VERY long integers (76+ digits)
- ALWAYS pass as strings to avoid truncation

## Understanding Prices & Odds

| Price | Probability | Interpretation |
|-------|-------------|----------------|
| 0.10 | 10% | Unlikely to happen |
| 0.50 | 50% | Coin flip |
| 0.80 | 80% | Likely to happen |
| 0.95 | 95% | Very likely (near certainty) |

**Payout Calculation:**
- Buy YES at $0.40, event happens → Win $1.00 per share (profit: $0.60)
- Buy YES at $0.40, event doesn't happen → Lose $0.40 per share

## Common Patterns

### "What's happening on Polymarket RIGHT NOW?"
```python
polymarket_trending_markets_get(minutes=5, limit=10)
# Returns markets with most volume in last 5 minutes
```

### "Find events about X"
```python
polymarket_events_search(query="Ukraine ceasefire", limit=5)
# Returns events sorted by volume
```

### "Buy $10 of X at current price"
```python
polymarket_markets_buy(token_id="...", amount=10)
# Executes immediately at best available price
```

### "What's my current portfolio?"
```python
polymarket_positions_list()
# Shows all holdings with P&L
```

## Error Handling

| Error | Solution |
|-------|----------|
| Cloudflare 403 | VPN/geo issue - check network |
| Insufficient balance | Deposit USDC on Polygon |
| Market closed | Cannot trade closed markets |
| Order rejected | Check spread, may need better price |
