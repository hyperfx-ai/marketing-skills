---
name: Data Analysis
description: Use this reference for data analysis, chart creation, file processing, and report generation in the sandbox.
---

## Getting Files Into the Sandbox

Use `copy_files(...)` to move input data into the sandbox explicitly:

```python
copy_files(sources=["/files/input.csv"], destination="/home/user/data/input.csv")
```
Sandbox Python only sees `/home/user/...`. Persistent files stay in `/files/...` until you copy them over.

## Running Analysis

The sandbox Python venv has pre-installed libraries:

```python
python("""
import pandas as pd
import numpy as np

df = pd.read_csv('/home/user/data/input.csv')
summary = df.describe()
print(summary)
""")
```

Available libraries: pandas, numpy, scipy, matplotlib, seaborn, plotly, openpyxl, httpx.

## Creating Charts

Use normal plotting libraries directly in `python(code)`. Native sandbox results now surface logs, structured chart JSON, and file artifacts in the UI:

```python
python("""
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('/home/user/data/input.csv')
fig, ax = plt.subplots(figsize=(10, 6))
df.plot(kind='bar', ax=ax)
plt.tight_layout()
plt.savefig('/home/user/data/chart.png', dpi=150)
print('Chart saved')
""")
```

For Plotly, prefer returning the figure or writing HTML/PNG files when needed:

```python
python("""
import pandas as pd
import plotly.express as px

df = pd.read_csv('/home/user/data/input.csv')
fig = px.bar(df, x='category', y='value', title='Category totals')
fig
""")
```

## Showing Results to the User

Default behavior:
- Let `python(code)` return its native results first. The sandbox UI now shows console output, rendered charts, and file artifacts automatically.
- Use `display_file(path=...)` only for files already copied into `/files/...`.
- If the file was created in the sandbox VM under `/home/user/...`, copy it into `/files/...` first. No exceptions.

Example:

```python
copy_files(sources=["/home/user/data/chart.png"], destination="/files/chart.png")
display_file(path="/files/chart.png")
```

## Exporting Files

Use `copy_files(...)` to persist files outside the sandbox, then `display_file(path="/files/...")` when you want to attach them in chat:

```python
copy_files(sources=["/home/user/data/report.csv"], destination="/files/report.csv")
display_file(path="/files/report.csv")
```

## PDF Report Generation

ReportLab is pre-installed for generating professional PDF reports:

```python
python("""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

c = canvas.Canvas('/home/user/data/report.pdf', pagesize=A4)
c.drawString(72, 750, 'Analysis Report')
c.save()
print('PDF saved')
""")
```

## Workflow Pattern

1. Copy/prepare input data with `copy_files(...)`
2. Analyze with `python(code)` using pandas/numpy
3. Create visualizations with matplotlib/seaborn/plotly
4. Let the native sandbox results UI render logs/charts/files
5. Use `display_file(path=...)` for explicit chat attachments
6. Export with `sandbox_download_file(path)` or `copy_files(...)` when needed
