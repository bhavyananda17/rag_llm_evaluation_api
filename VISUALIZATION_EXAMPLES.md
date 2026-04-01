# Judge Metrics Visualization - Complete Examples & Guide

## Overview

This guide shows how to create professional visualizations from the Judge Metrics output. The system generates:
- **evaluation_report.json** - Detailed judge data with all scores
- **benchmark_summary.csv** - Visualization-ready summary

---

## Method 1: Excel Visualization

### Step 1: Import CSV File
1. Open Microsoft Excel
2. Click `File` → `Open`
3. Navigate to `data/results/benchmark_summary.csv`
4. Click Open

### Step 2: Create Bar Chart (Overall Performance)
1. Select cells A1:D1 (headers: Metric, Base, RAG, LoRA)
2. Select the row with "Overall Score": A8:D8
3. Click `Insert` → `Chart` → `Column Chart`
4. Customize title: "Model Performance Comparison"
5. Add data labels showing values

**Expected Chart**:
```
Overall Score Comparison
5.0 |
4.5 | ░░░
4.0 | ░░░
3.5 | ░░░ ░░░
3.0 | ░░░ ░░░ ░░░
    +---+---+---
    Base RAG LoRA
```

### Step 3: Create Multi-Series Bar Chart (All Metrics)
1. Select columns A:D and all data rows (A1:D9)
2. Click `Insert` → `Chart` → `Column Chart`
3. Configure as grouped column chart
4. Title: "Comprehensive Model Evaluation"

**Shows**:
- Accuracy, Completeness, Overall Score, Hallucinations, Rates side-by-side
- Easy comparison across all metrics

### Step 4: Create Pie Charts (Hallucination Rates)
1. Create one pie chart per model
2. Data: Total responses vs Hallucinations
3. Titles: "Base Hallucination Rate (7.7%)" etc.

**Example for RAG**:
```
    ■ Grounded (100%)
    ■ Hallucinations (0%)
```

### Step 5: Format for Presentation
1. Add borders and colors
2. Use consistent color scheme:
   - Base: Blue
   - RAG: Green
   - LoRA: Orange
3. Export as PNG for presentation

---

## Method 2: Python Matplotlib Visualization

### Installation
```bash
source venv/bin/activate
pip install matplotlib seaborn
```

### Complete Visualization Script

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

# Load data
df = pd.read_csv('data/results/benchmark_summary.csv', index_col=0)

# Create figure with subplots
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('Judge Evaluation - Triple Comparison Analysis', fontsize=16, fontweight='bold')

# Color palette
colors = ['#1f77b4', '#2ca02c', '#ff7f0e']  # Blue, Green, Orange

# 1. Overall Score (Bar Chart)
ax1 = axes[0, 0]
overall_data = df.loc['Overall Score']
bars1 = ax1.bar(overall_data.index, overall_data.values, color=colors, edgecolor='black', linewidth=1.5)
ax1.set_ylabel('Score (out of 5)', fontweight='bold')
ax1.set_title('Overall Performance Score', fontweight='bold')
ax1.set_ylim([0, 5])
ax1.axhline(y=3, color='red', linestyle='--', alpha=0.3, label='Acceptable Threshold')
for i, (idx, val) in enumerate(overall_data.items()):
    ax1.text(i, val + 0.1, f'{val:.2f}', ha='center', fontweight='bold')
ax1.legend()

# 2. Accuracy Comparison (Bar Chart)
ax2 = axes[0, 1]
accuracy_data = df.loc['Accuracy (avg)']
bars2 = ax2.bar(accuracy_data.index, accuracy_data.values, color=colors, edgecolor='black', linewidth=1.5)
ax2.set_ylabel('Score (out of 5)', fontweight='bold')
ax2.set_title('Accuracy Comparison', fontweight='bold')
ax2.set_ylim([0, 5])
for i, (idx, val) in enumerate(accuracy_data.items()):
    ax2.text(i, val + 0.1, f'{val:.2f}', ha='center', fontweight='bold')

# 3. Completeness Comparison (Bar Chart)
ax3 = axes[0, 2]
completeness_data = df.loc['Completeness (avg)']
bars3 = ax3.bar(completeness_data.index, completeness_data.values, color=colors, edgecolor='black', linewidth=1.5)
ax3.set_ylabel('Score (out of 5)', fontweight='bold')
ax3.set_title('Completeness Comparison', fontweight='bold')
ax3.set_ylim([0, 5])
for i, (idx, val) in enumerate(completeness_data.items()):
    ax3.text(i, val + 0.1, f'{val:.2f}', ha='center', fontweight='bold')

# 4. Hallucination Count (Bar Chart)
ax4 = axes[1, 0]
hall_count = df.loc['Hallucinations']
bars4 = ax4.bar(hall_count.index, hall_count.values, color=colors, edgecolor='black', linewidth=1.5)
ax4.set_ylabel('Count', fontweight='bold')
ax4.set_title('Hallucination Count', fontweight='bold')
for i, (idx, val) in enumerate(hall_count.items()):
    ax4.text(i, val + 0.05, f'{int(val)}', ha='center', fontweight='bold')

# 5. Hallucination Rate (Pie Charts)
ax5 = axes[1, 1]
models = ['Base', 'RAG', 'LoRA']
hall_rates = [7.7, 0.0, 30.8]
sizes = [hall_rates, [100-r for r in hall_rates]]  # Hallucinations vs Grounded

# Create stacked data for grouped pie
explode = (0.05, 0.05, 0.05)
ax5.pie(hall_rates, labels=models, autopct='%1.1f%%', startangle=90,
        colors=colors, explode=explode, textprops={'fontweight': 'bold'})
ax5.set_title('Hallucination Rate (%)', fontweight='bold')

# 6. Performance Ranking (Horizontal Bar Chart)
ax6 = axes[1, 2]
ranking_data = [
    ('RAG', 4.59),
    ('Base', 3.62),
    ('LoRA', 3.15)
]
models_ranked = [x[0] for x in ranking_data]
scores_ranked = [x[1] for x in ranking_data]
rank_colors = [colors[1], colors[0], colors[2]]  # Green, Blue, Orange

bars6 = ax6.barh(models_ranked, scores_ranked, color=rank_colors, edgecolor='black', linewidth=1.5)
ax6.set_xlabel('Overall Score', fontweight='bold')
ax6.set_title('Performance Ranking', fontweight='bold')
ax6.set_xlim([0, 5])
for i, (model, score) in enumerate(ranking_data):
    ax6.text(score + 0.1, i, f'#{i+1} - {score:.2f}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('judge_evaluation_visualization.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved: judge_evaluation_visualization.png")
plt.show()
```

### Create Individual Comparison Charts

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('data/results/benchmark_summary.csv', index_col=0)

# 1. Side-by-side accuracy and completeness
fig, ax = plt.subplots(figsize=(10, 6))

x = range(3)
width = 0.35
models = ['Base', 'RAG', 'LoRA']

accuracy = [3.85, 4.62, 3.31]
completeness = [3.23, 4.54, 2.85]

ax.bar([i - width/2 for i in x], accuracy, width, label='Accuracy', color='#1f77b4')
ax.bar([i + width/2 for i in x], completeness, width, label='Completeness', color='#ff7f0e')

ax.set_ylabel('Score (out of 5)', fontweight='bold')
ax.set_title('Accuracy vs Completeness Comparison', fontweight='bold', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.legend(fontsize=12)
ax.set_ylim([0, 5])
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('accuracy_vs_completeness.png', dpi=300, bbox_inches='tight')
print("✓ Saved: accuracy_vs_completeness.png")
plt.show()

# 2. Hallucination comparison (pie chart comparison)
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Hallucination Analysis Across Models', fontsize=14, fontweight='bold')

hallucination_data = [
    {'grounded': 12, 'hallucinations': 1},  # Base
    {'grounded': 13, 'hallucinations': 0},  # RAG
    {'grounded': 9, 'hallucinations': 4}    # LoRA
]

labels = ['Base', 'RAG', 'LoRA']
colors_pie = [['#2ca02c', '#d62728'], ['#2ca02c', '#d62728'], ['#2ca02c', '#d62728']]

for idx, (ax, data, label) in enumerate(zip(axes, hallucination_data, labels)):
    sizes = [data['grounded'], data['hallucinations']]
    labels_pie = ['Grounded', 'Hallucinations']
    ax.pie(sizes, labels=labels_pie, autopct='%1.1f%%', startangle=90,
           colors=['#2ca02c', '#d62728'])
    ax.set_title(label, fontweight='bold', fontsize=12)

plt.tight_layout()
plt.savefig('hallucination_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: hallucination_comparison.png")
plt.show()
```

### Save as High-Resolution Images

```python
# Export with high DPI for presentations
plt.savefig('visualization.png', dpi=300, bbox_inches='tight')
plt.savefig('visualization.pdf', format='pdf', bbox_inches='tight')  # For printing

# Create web-ready version
plt.savefig('visualization_web.png', dpi=72, bbox_inches='tight')
```

---

## Method 3: Python Plotly (Interactive)

### Installation
```bash
pip install plotly
```

### Interactive Visualizations

```python
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load data
df = pd.read_csv('data/results/benchmark_summary.csv', index_col=0)

# Create subplots
fig = make_subplots(
    rows=2, cols=3,
    subplot_titles=('Overall Score', 'Accuracy', 'Completeness',
                    'Hallucination Count', 'Hallucination Rate', 'Performance Ranking'),
    specs=[[{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}],
           [{'type': 'bar'}, {'type': 'pie'}, {'type': 'bar'}]]
)

models = ['Base', 'RAG', 'LoRA']
colors = ['#1f77b4', '#2ca02c', '#ff7f0e']

# Overall Score
overall = df.loc['Overall Score']
fig.add_trace(
    go.Bar(x=models, y=overall.values, name='Overall Score', 
           marker_color=colors),
    row=1, col=1
)

# Accuracy
accuracy = df.loc['Accuracy (avg)']
fig.add_trace(
    go.Bar(x=models, y=accuracy.values, name='Accuracy',
           marker_color=colors),
    row=1, col=2
)

# Completeness
completeness = df.loc['Completeness (avg)']
fig.add_trace(
    go.Bar(x=models, y=completeness.values, name='Completeness',
           marker_color=colors),
    row=1, col=3
)

# Hallucination Count
hallucinations = df.loc['Hallucinations']
fig.add_trace(
    go.Bar(x=models, y=hallucinations.values, name='Hallucinations',
           marker_color=colors),
    row=2, col=1
)

# Hallucination Rate (Pie)
hall_rate = [7.7, 0.0, 30.8]
fig.add_trace(
    go.Pie(labels=models, values=hall_rate, name='Hallucination Rate'),
    row=2, col=2
)

# Performance Ranking
ranking_scores = [4.59, 3.62, 3.15]
fig.add_trace(
    go.Bar(x=models, y=ranking_scores, name='Performance',
           marker_color=colors),
    row=2, col=3
)

# Update layout
fig.update_layout(
    height=800,
    showlegend=False,
    title_text='Judge Evaluation - Triple Comparison Dashboard'
)

fig.write_html('judge_evaluation_interactive.html')
print("✓ Interactive visualization saved: judge_evaluation_interactive.html")
fig.show()
```

---

## Method 4: JSON-based Web Visualization

### Using D3.js Template

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Judge Evaluation Dashboard</title>
    <script src="https://d3js.org/d3.v6.min.js"></script>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .chart { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
        .bar { fill: steelblue; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Judge Evaluation - Triple Comparison Analysis</h1>
        
        <div class="chart">
            <div class="title">Overall Performance Score</div>
            <svg id="overall-chart" width="800" height="400"></svg>
        </div>
        
        <div class="chart">
            <div class="title">Accuracy vs Completeness</div>
            <svg id="comparison-chart" width="800" height="400"></svg>
        </div>
    </div>

    <script>
        // Load evaluation data
        fetch('data/results/evaluation_report.json')
            .then(r => r.json())
            .then(data => {
                const stats = data.statistics.by_mode;
                
                // Chart 1: Overall Score
                const svg1 = d3.select('#overall-chart');
                const models = Object.keys(stats);
                const scores = models.map(m => stats[m].overall_score);
                
                const x = d3.scaleBand().domain(models).range([0, 800]);
                const y = d3.scaleLinear().domain([0, 5]).range([400, 0]);
                
                svg1.selectAll('.bar')
                    .data(scores)
                    .enter()
                    .append('rect')
                    .attr('x', (d, i) => x(models[i]))
                    .attr('y', d => y(d))
                    .attr('width', x.bandwidth())
                    .attr('height', d => 400 - y(d))
                    .attr('class', 'bar');
            });
    </script>
</body>
</html>
```

---

## Method 5: Pandas Data Analysis

### Load and Analyze

```python
import pandas as pd
import json

# Load CSV
df = pd.read_csv('data/results/benchmark_summary.csv', index_col=0)

# Display summary
print("\n" + "="*60)
print("JUDGE EVALUATION SUMMARY")
print("="*60)
print(df)
print("\n")

# Load JSON for detailed analysis
with open('data/results/evaluation_report.json', 'r') as f:
    report = json.load(f)

stats = report['statistics']

# Print detailed statistics
print("="*60)
print("DETAILED STATISTICS BY MODE")
print("="*60)

for mode, stat in stats['by_mode'].items():
    print(f"\n{mode.upper()}:")
    print(f"  Accuracy:        {stat['avg_accuracy']:.2f}/5")
    print(f"  Completeness:    {stat['avg_completeness']:.2f}/5")
    print(f"  Overall Score:   {stat['overall_score']:.2f}/5")
    print(f"  Hallucinations:  {stat['hallucination_count']}")
    print(f"  Grounded:        {stat['grounded_responses']}")

print("\n" + "="*60)
print("PERFORMANCE RANKING")
print("="*60)

for rank_item in stats['performance_ranking']:
    print(f"{rank_item['rank']}. {rank_item['mode'].upper():6} - {rank_item['score']:.2f}/5")
```

---

## Method 6: Export to Other Formats

### Export to Excel with Formatting

```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

# Load data
df = pd.read_csv('data/results/benchmark_summary.csv', index_col=0)

# Create Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "Judge Evaluation"

# Write headers
ws.append(['Metric', 'Base', 'RAG', 'LoRA'])

# Write data with formatting
for idx, row in df.iterrows():
    ws.append([idx] + list(row.values))

# Apply formatting
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF")

for cell in ws[1]:
    cell.fill = header_fill
    cell.font = header_font

# Set column widths
ws.column_dimensions['A'].width = 25
for col in ['B', 'C', 'D']:
    ws.column_dimensions[col].width = 15

wb.save('Judge_Evaluation_Report.xlsx')
print("✓ Excel file created: Judge_Evaluation_Report.xlsx")
```

### Export to LaTeX Table

```python
import pandas as pd

df = pd.read_csv('data/results/benchmark_summary.csv', index_col=0)

# Generate LaTeX
latex = df.to_latex()
print(latex)

# Save to file
with open('evaluation_table.tex', 'w') as f:
    f.write(latex)

print("✓ LaTeX table saved: evaluation_table.tex")
```

---

## Visualization Best Practices

### 1. Color Scheme
Use consistent colors for models:
- **Base**: Blue (#1f77b4)
- **RAG**: Green (#2ca02c)
- **LoRA**: Orange (#ff7f0e)

### 2. Chart Types
- **Overall Score**: Vertical bar chart (easy comparison)
- **Accuracy/Completeness**: Side-by-side bars
- **Hallucination**: Pie chart (shows percentage)
- **Ranking**: Horizontal bar (shows order)

### 3. Labels & Titles
- Include units (out of 5, percentage, count)
- Show actual values on bars
- Use clear, descriptive titles
- Include legend when needed

### 4. For Presentations
- Use high DPI (300+)
- Keep text readable from 10+ feet away
- Use consistent fonts
- Add grid lines for reference

### 5. For Reports
- Include data table with visualization
- Add interpretation/insights
- Show methodology
- Include timestamp and source

---

## Expected Visualizations

### Chart 1: Overall Performance
```
Performance Score Comparison
5  ┌─────┐
4  │ ░░░ │ RAG: 4.59
3  │ ░░░ │ Base: 3.62
2  │ ░░░ │
1  │ ░░░ │ LoRA: 3.15
0  └─────┘
   Base RAG LoRA
```

### Chart 2: Accuracy Distribution
```
Accuracy (out of 5)
5  ┌─────┐
4  │ ░░░ │
3  │ ░░░ │
2  │ ░░░ │
   └─────┘
   Base RAG LoRA
```

### Chart 3: Hallucination Rate
```
RAG Mode - Hallucination Rate
┌─────────────┐
│ ■ Grounded  │
│   (100%)    │
│             │
│ ■ Halluc    │
│   (0%)      │
└─────────────┘
```

---

## Summary

Use these methods to create professional visualizations:

1. **Excel**: Easiest, built-in tools, office-ready
2. **Matplotlib**: Publication quality, customizable
3. **Plotly**: Interactive, web-ready
4. **D3.js**: Advanced interactive visualizations
5. **JSON/Web**: Integration with other tools

All methods use the same source data files:
- `benchmark_summary.csv` (primary visualization source)
- `evaluation_report.json` (detailed data source)

**Recommended for Most Users**: Excel + Matplotlib combination
- Import CSV into Excel for quick dashboards
- Use Matplotlib for publication-quality charts
- Export both as PNG for presentations

---

**Generated**: April 1, 2026  
**System**: Triple Comparison Judge Metrics  
**Version**: 1.0
