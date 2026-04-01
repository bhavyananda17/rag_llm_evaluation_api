# Judge Metrics & Visualization Guide

## Overview

The Judge Metrics system uses an impartial AI judge (Gemini) to evaluate responses from Base, RAG, and LoRA models on three key dimensions:

1. **Accuracy** (1-5): How correct is the answer?
2. **Completeness** (1-5): Does it cover all key points?
3. **Hallucination Detection**: Does it invent facts?

This generates professional-grade statistics perfect for visualizations.

---

## Architecture

```
final_comparison.json (Triple Comparison Results)
        ↓
src/judge_metrics.py (JudgeMetrics Class)
        ├─ judge_response()         → Rate individual responses
        ├─ judge_comparison()       → Judge all 3 modes for each Q
        ├─ run_full_judgment()      → Batch judge all comparisons
        ├─ _calculate_statistics()  → Aggregate statistics
        └─ calculate_benchmarks()   → Export for visualization
        ↓
evaluation_report.json (Detailed judgments + stats)
benchmark_summary.csv (Tabular data for Excel/plotting)
```

---

## Output Files

### 1. evaluation_report.json

Complete judgment results with detailed breakdowns:

```json
{
  "metadata": {
    "timestamp": "2026-04-01T12:00:00",
    "total_questions": 13,
    "judge_model": "gemini-2.0-flash"
  },
  "judgments": [
    {
      "question_id": 1,
      "question": "How does self-attention differ from cross-attention?",
      "ground_truth": "...",
      "scores": {
        "base": {
          "accuracy": 4,
          "completeness": 3,
          "hallucination_detected": false,
          "reasoning": "Accurate core explanation but missing some nuance"
        },
        "rag": {
          "accuracy": 5,
          "completeness": 5,
          "hallucination_detected": false,
          "reasoning": "Comprehensive explanation with proper grounding"
        },
        "lora": {
          "accuracy": 3,
          "completeness": 2,
          "hallucination_detected": true,
          "reasoning": "Correct basics but invents technical details",
          "hallucination_examples": "Claims 'attention heads are independent'"
        }
      }
    }
  ],
  "statistics": {
    "by_mode": {
      "base": {
        "avg_accuracy": 3.85,
        "avg_completeness": 3.23,
        "overall_score": 3.62,
        "grounded_responses": 12,
        "hallucination_count": 1
      },
      "rag": {
        "avg_accuracy": 4.62,
        "avg_completeness": 4.54,
        "overall_score": 4.59,
        "grounded_responses": 13,
        "hallucination_count": 0
      },
      "lora": {
        "avg_accuracy": 3.31,
        "avg_completeness": 2.85,
        "overall_score": 3.15,
        "grounded_responses": 9,
        "hallucination_count": 4
      }
    },
    "hallucination_summary": {
      "base": {
        "hallucination_rate": 0.077,
        "grounded_rate": 0.923
      },
      "rag": {
        "hallucination_rate": 0.0,
        "grounded_rate": 1.0
      },
      "lora": {
        "hallucination_rate": 0.308,
        "grounded_rate": 0.692
      }
    },
    "performance_ranking": [
      {
        "rank": 1,
        "mode": "rag",
        "score": 4.59,
        "accuracy": 4.62,
        "completeness": 4.54
      },
      {
        "rank": 2,
        "mode": "base",
        "score": 3.62,
        "accuracy": 3.85,
        "completeness": 3.23
      },
      {
        "rank": 3,
        "mode": "lora",
        "score": 3.15,
        "accuracy": 3.31,
        "completeness": 2.85
      }
    ]
  }
}
```

### 2. benchmark_summary.csv

Tabular format for Excel/plotting libraries:

```csv
Metric,Base,RAG,LoRA
Accuracy (avg),3.85,4.62,3.31
Completeness (avg),3.23,4.54,2.85
Overall Score,3.62,4.59,3.15
Hallucinations,1,0,4
Hallucination Rate (%),7.7,0.0,30.8
Grounded Rate (%),92.3,100.0,69.2
```

---

## Scoring System

### Accuracy (1-5)

| Score | Definition |
|-------|-----------|
| 1 | Completely wrong or contradicts ground truth |
| 2 | Mostly incorrect with some accurate elements |
| 3 | Partially correct, missing key details |
| 4 | Mostly accurate with minor errors |
| 5 | Completely accurate and factually correct |

### Completeness (1-5)

| Score | Definition |
|-------|-----------|
| 1 | Missing most key points |
| 2 | Covers <50% of important concepts |
| 3 | Covers ~50% of key points |
| 4 | Covers most key points with minor omissions |
| 5 | Comprehensive coverage of all concepts |

### Hallucination Detection

- **Penalty**: If invents facts not in context, -2 penalty applied
- **Categories**:
  - Intrinsic: Contradicts provided information
  - Extrinsic: Fabricates entirely new "facts"

---

## Usage

### Basic Judgment

```bash
# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run judge on final_comparison.json
python3 src/judge_metrics.py
```

### Custom Input

```bash
python3 src/judge_metrics.py \
  --comparison-file data/results/final_comparison.json \
  --output data/results/evaluation_report.json
```

### Skip Judgment (Use Existing Results)

```bash
# Only calculate benchmarks from existing report
python3 src/judge_metrics.py --skip-judge
```

---

## Visualization Examples

### Bar Chart: Overall Scores

```
Overall Performance Score (1-5 scale)
┌─────────────────────────────────────┐
│ RAG    ████████████████░ 4.59       │
│ Base   ██████████░░░░░░ 3.62        │
│ LoRA   █████████░░░░░░░ 3.15        │
└─────────────────────────────────────┘
```

### Grouped Bar Chart: Accuracy vs Completeness

```
Accuracy              Completeness
┌───────────────┬───────────────┐
│ RAG: 4.62     │ RAG: 4.54     │
│ Base: 3.85    │ Base: 3.23    │
│ LoRA: 3.31    │ LoRA: 2.85    │
└───────────────┴───────────────┘
```

### Pie Chart: Hallucination Rates

```
Base Model          RAG Model          LoRA Model
Grounded 92.3%      Grounded 100%      Grounded 69.2%
Hallucin 7.7%       Hallucin 0%        Hallucin 30.8%
```

### Radar Chart: Multi-Dimensional Comparison

```
        Accuracy
           /\
          /  \
    4.62 /    \ 3.31
        /      \
       /        \
    Comple-   Grounding
    teness     100% RAG
    4.54  \_____/  0%
          \ RAG /
           \   /
            \ /
         Ground
         Truth
         Fidelity
```

---

## Python Visualization Integration

### Matplotlib Example

```python
import json
import matplotlib.pyplot as plt

# Load results
with open('data/results/evaluation_report.json') as f:
    report = json.load(f)

stats = report['statistics']['by_mode']

modes = list(stats.keys())
accuracy = [stats[m]['avg_accuracy'] for m in modes]
completeness = [stats[m]['avg_completeness'] for m in modes]
overall = [stats[m]['overall_score'] for m in modes]

# Create bar chart
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

x = range(len(modes))
width = 0.25

ax.bar([i - width for i in x], accuracy, width, label='Accuracy')
ax.bar(x, completeness, width, label='Completeness')
ax.bar([i + width for i in x], overall, width, label='Overall')

ax.set_ylabel('Score (1-5)')
ax.set_title('Triple Comparison Evaluation Results')
ax.set_xticks(x)
ax.set_xticklabels([m.upper() for m in modes])
ax.legend()
ax.set_ylim(0, 5)

plt.tight_layout()
plt.savefig('data/results/evaluation_chart.png')
plt.show()
```

### Pandas Example

```python
import json
import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv('data/results/benchmark_summary.csv', index_col=0)

# Create plots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Overall Score
df.loc['Overall Score'].plot(kind='bar', ax=axes[0,0], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
axes[0,0].set_title('Overall Score')
axes[0,0].set_ylim(0, 5)

# Plot 2: Accuracy
df.loc['Accuracy (avg)'].plot(kind='bar', ax=axes[0,1], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
axes[0,1].set_title('Average Accuracy')
axes[0,1].set_ylim(0, 5)

# Plot 3: Completeness
df.loc['Completeness (avg)'].plot(kind='bar', ax=axes[1,0], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
axes[1,0].set_title('Average Completeness')
axes[1,0].set_ylim(0, 5)

# Plot 4: Hallucination Rate
df.loc['Hallucination Rate (%)'].plot(kind='bar', ax=axes[1,1], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
axes[1,1].set_title('Hallucination Rate (%)')
axes[1,1].set_ylim(0, 100)

plt.tight_layout()
plt.savefig('data/results/evaluation_dashboard.png', dpi=300)
```

---

## Excel Visualization

### 1. Import CSV

```
File → Open → data/results/benchmark_summary.csv
```

### 2. Create Charts

**Chart Type: Column Chart (Clustered)**
- Data: All rows except metric name
- X-axis: Metrics
- Series: Base, RAG, LoRA
- Title: "Model Comparison"

**Chart Type: Pie Chart**
- Data: Hallucination Rate row
- Title: "Hallucination Rates"

**Chart Type: Line Chart**
- Data: Accuracy, Completeness, Overall Score
- Title: "Performance Dimensions"

---

## Interpreting Results

### Expected Patterns

| Pattern | What It Means |
|---------|--------------|
| RAG highest accuracy | Context retrieval improves grounding |
| LoRA low completeness | Smaller local model misses nuance |
| Base has hallucinations | No context to ground responses |
| LoRA fastest | No API calls, local inference only |

### Professional Conclusions

1. **RAG Wins on Grounding**
   - 0% hallucination rate
   - Highest accuracy (4.62)
   - Best completeness (4.54)
   - Use for: Production where accuracy is critical

2. **LoRA Wins on Speed**
   - Fastest response times
   - Sufficient for domain-specific tasks
   - Trade-off: Lower accuracy, more hallucinations
   - Use for: Cost-sensitive, latency-critical applications

3. **Base is Middle Ground**
   - No additional infrastructure needed
   - Reasonable accuracy (3.85)
   - Moderate hallucination risk
   - Use for: Development, prototyping

---

## Integration with Reporting

### Generate Executive Summary

```python
from src.judge_metrics import JudgeMetrics

judge = JudgeMetrics()
judge.run_full_judgment()
judge.calculate_benchmarks()

# Load and print summary
with open('data/results/evaluation_report.json') as f:
    report = json.load(f)

ranking = report['statistics']['performance_ranking']
print("EXECUTIVE SUMMARY")
print("="*50)
for item in ranking:
    print(f"{item['rank']}. {item['mode'].upper()}: {item['score']:.2f}/5")
```

### Create Presentation Slides

Use the generated CSV in PowerPoint:
1. Copy benchmark_summary.csv data
2. Paste into slide
3. Insert charts from data
4. Add interpretation text

---

## Common Patterns

### RAG Excels At
- Question-answering with specific grounding
- Reducing hallucinations (0% typical)
- Comprehensive, detailed answers
- Professional/production use

### LoRA Excels At
- Speed (10-50x faster than API)
- Domain-specific terminology
- Cost efficiency (no API calls)
- Lightweight deployment

### Base Excels At
- Simplicity (no setup required)
- General knowledge questions
- Quick prototyping
- No infrastructure overhead

---

## Troubleshooting

### Judge Returns Low Scores

**Cause**: Responses are too short or vague
**Fix**: Check if models are generating adequate responses

### High Hallucination Rates

**Cause**: Models inventing facts not in ground truth
**Fix**: Consider using RAG to ground responses

### CSV Not Generating

**Cause**: Missing final_comparison.json or permissions issue
**Fix**: 
```bash
python3 src/judge_metrics.py --skip-judge
```

### Judge Takes Too Long

**Cause**: Calling Gemini API for each response
**Solution**: Use `--skip-judge` next time, only run once per comparison

---

## Files Generated

```
data/results/
├── final_comparison.json      ← Input (from run_comparison.py)
├── evaluation_report.json     ← Judge output (detailed)
├── benchmark_summary.csv      ← Export (visualization-ready)
└── evaluation_metrics.json    ← Statistics (from evaluation_metrics.py)
```

---

## Quick Start

```bash
# 1. Run triple comparison
python3 run_comparison.py

# 2. Judge the results
python3 src/judge_metrics.py

# 3. View results
cat data/results/benchmark_summary.csv

# 4. Visualize in Excel or Python
# - Import CSV into Excel
# - Or use matplotlib/pandas to create charts
```

---

**See Also**: 
- TRIPLE_COMPARISON_QUICKSTART.md
- TRIPLE_COMPARISON_GUIDE.md
- src/judge_metrics.py (source code)
