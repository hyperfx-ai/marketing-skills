---
name: Tool Chaining
description: Use this reference for bulk data collection, multi-step tool pipelines, and code-driven tool orchestration inside the sandbox.
---

## When to Use This

Use in-sandbox tool chaining when:

- You need to call the same tool many times in a loop (bulk scraping, enrichment, batch queries).
- You need to process tool results with Python before passing them to the next tool.
- The workflow has 3+ sequential steps that depend on each other's output.
- You want to collect data from one API, transform it, and store it in the database or export as a file.

Do NOT use in-sandbox tool chaining for:

- Single tool calls. Use normal agent tool calls instead.
- Tools that require user approval (`requires_approval` / `sensitive_operation`). Call those directly as agent tool calls.

## Critical File Boundary Rule

Sandbox Python can only open files that exist inside `/home/user/...`.

- `/files/...` and `/skills/...` are different backends.
- Do NOT do this inside Python:
  - `open("/files/result.json")`
  - `pd.read_csv("/files/data.csv")`
- If a normal tool returns a VFS file path such as `/files/tmp/...json`, either:
  - inspect it with `read_file(path="/files/tmp/...json")`
  - copy it into `/home/user/...` with `copy_files(...)` before opening it in Python
  - or call the upstream tool directly from Python with `call_tool(...)` / `call_tool_sync(...)` when bulk orchestration is actually needed

## Imports

Inside `python(code)` blocks, the sandbox has a lightweight RPC client pre-installed:

```python
python("""
from seti.sandbox import call_tool_sync

result = call_tool_sync("web_search", queries=["AI agents 2025"], num_results=5)
print(result)
""")
```

Two calling styles are available:

**Direct (recommended for clarity):**

```python
from seti.sandbox import call_tool_sync

result = call_tool_sync("tool_name", arg1="value", arg2=123)
```

**Async (when running in an async context):**

```python
from seti.sandbox import call_tool

result = await call_tool("tool_name", arg1="value", arg2=123)
```

## Common Tools for Chaining

| Tool | Purpose | Example args |
|------|---------|--------------|
| `web_search` | Search the web | `queries=["..."], num_results=5, mode="summary"` |
| `web_scrape_page` | Scrape a single URL | `url="https://..."` |
| `hyper_data_save` | Save data to a database table | `table="leads", data=[{...}], mode="append"` |
| `hyper_data_sql` | Query a database table | `sql="SELECT * FROM leads"` |
| `hyper_data_list_tables` | List existing tables | (no required args) |
| `firecrawl_scrape_url` | Scrape with Firecrawl | `url="https://..."` |
| `analyze_website` | Analyze a website | `url="https://..."` |

## Pattern: Search → Process → Save to Database

```python
python("""
from seti.sandbox import call_tool_sync

# 1. Search
result = call_tool_sync("web_search", queries=["top SaaS companies 2025"], num_results=10, mode="summary")

# 2. Process into rows
rows = []
for search in result.get("searches", []):
    for item in search.get("results", []):
        rows.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", "")[:300],
        })

print(f"Found {len(rows)} results")

# 3. Save to database
save_result = call_tool_sync("hyper_data_save", table="saas_research", data=rows, mode="replace")
print(save_result.get("message"))
""")
```

## Pattern: Bulk Scrape → CSV → PDF Report with Charts

```python
python("""
import json
import csv
from seti.sandbox import call_tool_sync

# 1. Search multiple queries
all_results = []
queries = ["AI automation tools", "no-code AI platforms", "enterprise AI agents"]

for query in queries:
    result = call_tool_sync("web_search", queries=[query], num_results=5, mode="summary")
    for search in result.get("searches", []):
        for item in search.get("results", []):
            all_results.append({
                "query": query,
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", "")[:200],
            })

# 2. Write CSV
csv_path = "/home/user/data/research.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["query", "title", "url", "snippet"])
    writer.writeheader()
    writer.writerows(all_results)

print(f"Saved {len(all_results)} results to CSV")
""")
```

Then generate a chart and PDF in a follow-up block:

```python
python("""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Load data
df = pd.read_csv("/home/user/data/research.csv")

# Chart: results per query
counts = df["query"].value_counts()
fig, ax = plt.subplots(figsize=(8, 4))
counts.plot(kind="barh", ax=ax, color="#4f46e5")
ax.set_xlabel("Results")
ax.set_title("Search Results by Query")
plt.tight_layout()
chart_path = "/home/user/data/chart.png"
fig.savefig(chart_path, dpi=150)

# Build PDF
pdf_path = "/home/user/data/report.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=A4)
styles = getSampleStyleSheet()
elements = []

elements.append(Paragraph("Research Report", styles["Title"]))
elements.append(Spacer(1, 12))
elements.append(Paragraph(f"Total results: {len(df)}", styles["Normal"]))
elements.append(Spacer(1, 12))
elements.append(Image(chart_path, width=400, height=200))
elements.append(Spacer(1, 12))

# Table of top results
table_data = [["Query", "Title", "URL"]]
for _, row in df.head(10).iterrows():
    table_data.append([row["query"][:30], row["title"][:40], row["url"][:50]])

t = Table(table_data, colWidths=[100, 150, 200])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 7),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
]))
elements.append(t)
doc.build(elements)
print(f"PDF report saved to {pdf_path}")
""")
```

Then export and display:

```python
copy_files(sources=["/home/user/data/report.pdf"], destination="/files/report.pdf")
display_file(path="/files/report.pdf")
```

## Pattern: Scrape → Enrich → Database

```python
python("""
from seti.sandbox import call_tool_sync

urls = [
    "https://example.com/company-a",
    "https://example.com/company-b",
    "https://example.com/company-c",
]

enriched = []
for url in urls:
    analysis = call_tool_sync("analyze_website", url=url)
    enriched.append({
        "url": url,
        "title": analysis.get("title", ""),
        "description": analysis.get("description", ""),
        "tech_stack": str(analysis.get("technologies", [])),
    })
    print(f"Analyzed: {url}")

# Save to Hyper database
call_tool_sync("hyper_data_save", table="competitor_analysis", data=enriched, mode="replace")
print(f"Saved {len(enriched)} rows to competitor_analysis")
""")
```

Then query the data:

```python
python("""
from seti.sandbox import call_tool_sync

result = call_tool_sync("hyper_data_sql", sql="SELECT * FROM competitor_analysis ORDER BY title")
for row in result.get("data", []):
    print(f"{row['title']} — {row['url']}")
""")
```

## Error Handling

Tool calls can fail. Always handle errors in loops to avoid losing partial progress:

```python
python("""
from seti.sandbox import call_tool_sync

results = []
errors = []

for query in queries:
    try:
        result = call_tool_sync("web_search", queries=[query], num_results=5)
        results.append(result)
    except RuntimeError as e:
        errors.append({"query": query, "error": str(e)})
        print(f"Failed: {query} — {e}")

print(f"Completed: {len(results)}, Failed: {len(errors)}")
""")
```

## Rules

1. All `call_tool_sync` / `call_tool` calls go through the Seti backend via RPC. They are real tool executions with full authentication.
2. Keep each `python(code)` block focused on one phase. Chain multiple blocks rather than writing a 200-line monolith.
3. Write intermediate results to files (`/home/user/data/...`) between blocks so progress is recoverable.
4. For files you want to show the user: copy to `/files/` first, then call `display_file(path="/files/...")`.
5. For database persistence: use `hyper_data_save` to store structured data, `hyper_data_sql` to query it back.
6. Do not use `call_tool_sync` for tools that require user approval. Use normal agent tool calls for those.
