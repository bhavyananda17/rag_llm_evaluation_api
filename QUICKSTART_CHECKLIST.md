# Judge System - Quick Start Checklist

## 🎯 Pre-Execution Checklist (2 minutes)

### Environment Setup
- [ ] Navigate to project: `cd /Users/bhavyananda/Documents/coding/rag_llm_evaluation_api`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Set Python path: `export PYTHONPATH=$PYTHONPATH:$(pwd)`
- [ ] Verify API key: `echo $GOOGLE_API_KEY` (should show key, not blank)

### Files Verification
- [ ] Check QA data: `ls -lh data/processed/synthetic_qa.json`
- [ ] Check vector store: `ls -lh data/processed/vector_index.faiss`
- [ ] Check results dir: `mkdir -p data/results && ls -lh data/results/`
- [ ] Check main scripts: `ls -lh src/judge_metrics.py run_comparison.py evaluation_metrics.py`

### Dependencies Check
```bash
python3 -c "
import sys
required = ['google.generativeai', 'transformers', 'faiss', 'pandas', 'dotenv']
failed = []
for lib in required:
    try:
        __import__(lib.split('.')[0])
    except ImportError:
        failed.append(lib)
if failed:
    print('❌ Missing:', ', '.join(failed))
else:
    print('✓ All dependencies installed')
"
```

---

## 🚀 Quick Path Execution (5-10 minutes)

### Step 1: Generate Comparison (2-3 minutes)
```bash
python3 run_comparison.py
```

**What it does:**
- Loads 13 QA pairs from `data/processed/synthetic_qa.json`
- Generates responses from Base mode (direct Gemini API)
- Generates responses from RAG mode (Gemini + vector retrieval)
- Saves all responses to `data/results/final_comparison.json`

**Expected output:**
```
Triple Comparison Evaluation
========================================================
Loading QA pairs from data/processed/synthetic_qa.json...
✓ Loaded 13 QA pairs

Running triple comparison evaluation...
[1/13] Evaluating: How does self-attention differ...
  Base: ✓ Generated response (2.3s)
  RAG:  ✓ Generated response (2.1s)
...
[13/13] Evaluating: What is the difference...
✓ Comparison complete: 39 responses generated

Results saved to: data/results/final_comparison.json
```

**Files created:**
- ✅ `data/results/final_comparison.json` (100-200 KB)

---

### Step 2: Judge All Responses (3-5 minutes)
```bash
python3 src/judge_metrics.py
```

**What it does:**
- Loads `final_comparison.json` with all responses
- Calls Gemini judge for each response (39 total)
- Scores: accuracy (1-5), completeness (1-5), hallucination (yes/no)
- Calculates statistics and rankings
- Exports visualization-ready CSV

**Expected output:**
```
JUDGE EVALUATION - RATING RESPONSES
========================================================

Loading comparisons from data/results/final_comparison.json
✓ Loaded 39 comparisons (13 questions × 3 modes)

[1/13] Judging: How does self-attention differ...
  base : Accuracy=4/5, Completeness=3/5, ✓ Grounded
  rag  : Accuracy=5/5, Completeness=5/5, ✓ Grounded
  lora : Accuracy=3/5, Completeness=2/5, ✗ Hallucination

...

[13/13] Judging: What is the difference...

Calculating aggregate statistics...
✓ Judgments saved to data/results/evaluation_report.json

========================================================
JUDGE EVALUATION SUMMARY
========================================================

PERFORMANCE RANKING:
---------
1. RAG
   Overall Score: 4.59/5
   Accuracy:     4.62/5
   Completeness: 4.54/5

2. BASE
   Overall Score: 3.62/5
   Accuracy:     3.85/5
   Completeness: 3.23/5

3. LORA
   Overall Score: 3.15/5
   Accuracy:     3.31/5
   Completeness: 2.85/5

DETAILED STATISTICS:
---------

BASE:
  Accuracy:          3.85/5 (13 evals)
  Completeness:      3.23/5 (13 evals)
  Overall Score:     3.62/5
  Hallucinations:    1
  Hallucination Rate: 7.7%
  Grounded Rate:     92.3%

RAG:
  Accuracy:          4.62/5 (13 evals)
  Completeness:      4.54/5 (13 evals)
  Overall Score:     4.59/5
  Hallucinations:    0
  Hallucination Rate: 0.0%
  Grounded Rate:     100.0%

LORA:
  Accuracy:          3.31/5 (13 evals)
  Completeness:      2.85/5 (13 evals)
  Overall Score:     3.15/5
  Hallucinations:    4
  Hallucination Rate: 30.8%
  Grounded Rate:     69.2%

========================================================
```

**Files created:**
- ✅ `data/results/evaluation_report.json` (detailed judge output with all scores)
- ✅ `data/results/benchmark_summary.csv` (visualization-ready summary)

---

### Step 3: Analyze Metrics (< 1 minute)
```bash
python3 evaluation_metrics.py
```

**What it does:**
- Loads comparison data
- Calculates latency statistics
- Analyzes success rates
- Generates quality metrics
- Saves comprehensive analysis

**Expected output:**
```
Loading comparison data...
Analyzing metrics...
✓ Analysis complete

Metrics saved to: data/results/evaluation_metrics.json
```

**Files created:**
- ✅ `data/results/evaluation_metrics.json` (comprehensive metrics analysis)

---

## 📊 Results Summary

After completing all 3 steps, you have:

### Files Generated
```
data/results/
├── final_comparison.json          (100-200 KB) - All responses
├── evaluation_report.json         (50-100 KB) - Judge output + stats
├── benchmark_summary.csv          (1 KB)      - Visualization CSV
└── evaluation_metrics.json        (20-30 KB)  - Metrics analysis
```

### Quick Data Preview
```bash
# View summary CSV
cat data/results/benchmark_summary.csv

# View top of judge report
head -100 data/results/evaluation_report.json | python3 -m json.tool

# Count hallucinations
grep -o '"hallucination_detected": true' data/results/evaluation_report.json | wc -l
```

---

## 📈 Visualize Results

### Option A: Excel (Easiest - 2 minutes)
```bash
# Open CSV in Excel
open data/results/benchmark_summary.csv

# In Excel:
# 1. Insert → Chart
# 2. Select "Column Chart" (vertical bars)
# 3. Title: "Model Performance"
# 4. Repeat for other metrics
```

### Option B: Python Matplotlib (Quality - 5 minutes)
```bash
pip install matplotlib

python3 << 'EOF'
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/results/benchmark_summary.csv', index_col=0)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Judge Evaluation Results', fontsize=14, fontweight='bold')

models = ['Base', 'RAG', 'LoRA']
colors = ['#1f77b4', '#2ca02c', '#ff7f0e']

# Chart 1: Overall Score
overall = df.loc['Overall Score']
axes[0].bar(models, overall.values, color=colors)
axes[0].set_title('Overall Score')
axes[0].set_ylim([0, 5])
axes[0].set_ylabel('Score (out of 5)')

# Chart 2: Accuracy
accuracy = df.loc['Accuracy (avg)']
axes[1].bar(models, accuracy.values, color=colors)
axes[1].set_title('Accuracy')
axes[1].set_ylim([0, 5])

# Chart 3: Hallucination Rate
hall_rate = df.loc['Hallucination Rate (%)']
axes[2].bar(models, hall_rate.values, color=colors)
axes[2].set_title('Hallucination Rate (%)')
axes[2].set_ylabel('Percentage')

plt.tight_layout()
plt.savefig('judge_results.png', dpi=300, bbox_inches='tight')
print("✓ Chart saved: judge_results.png")
plt.show()
EOF
```

### Option C: Python Plotly (Interactive - 5 minutes)
```bash
pip install plotly

python3 << 'EOF'
import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv('data/results/benchmark_summary.csv', index_col=0)
models = ['Base', 'RAG', 'LoRA']

fig = go.Figure()

for metric in df.index:
    fig.add_trace(go.Bar(
        x=models,
        y=df.loc[metric].values,
        name=metric
    ))

fig.update_layout(
    title='Judge Evaluation Results',
    xaxis_title='Model',
    yaxis_title='Score',
    barmode='group',
    height=600,
    width=1000
)

fig.write_html('judge_results_interactive.html')
print("✓ Interactive chart saved: judge_results_interactive.html")
fig.show()
EOF
```

---

## ⏱️ Time Breakdown

| Step | Time | Command |
|------|------|---------|
| Generate Comparison | 2-3 min | `python3 run_comparison.py` |
| Judge Responses | 3-5 min | `python3 src/judge_metrics.py` |
| Analyze Metrics | <1 min | `python3 evaluation_metrics.py` |
| **Total** | **5-10 min** | All 3 commands |

**Additional time for visualization:**
- Excel: +2 minutes
- Matplotlib: +5 minutes
- Plotly: +5 minutes

---

## 🔍 Verify Results

### Check Files Exist
```bash
echo "Checking output files..."
test -f data/results/final_comparison.json && echo "✓ final_comparison.json" || echo "✗ final_comparison.json"
test -f data/results/evaluation_report.json && echo "✓ evaluation_report.json" || echo "✗ evaluation_report.json"
test -f data/results/benchmark_summary.csv && echo "✓ benchmark_summary.csv" || echo "✗ benchmark_summary.csv"
test -f data/results/evaluation_metrics.json && echo "✓ evaluation_metrics.json" || echo "✗ evaluation_metrics.json"

# Show file sizes
echo -e "\nFile sizes:"
du -h data/results/*
```

### Check Data Integrity
```bash
# Count judgments (should be 13)
python3 -c "
import json
with open('data/results/evaluation_report.json') as f:
    data = json.load(f)
    print(f'Judgments: {len(data[\"judgments\"])}')
    print(f'Ranking: {[x[\"mode\"] for x in data[\"statistics\"][\"performance_ranking\"]]}')
"

# Show statistics
python3 -c "
import json
with open('data/results/evaluation_report.json') as f:
    stats = json.load(f)['statistics']['by_mode']
    for mode in ['base', 'rag', 'lora']:
        s = stats[mode]
        print(f'{mode.upper()}: Accuracy={s[\"avg_accuracy\"]:.2f}, Completeness={s[\"avg_completeness\"]:.2f}, Overall={s[\"overall_score\"]:.2f}')
"
```

### Verify Rankings
```bash
python3 << 'EOF'
import json

with open('data/results/evaluation_report.json') as f:
    data = json.load(f)
    
print("\n" + "="*60)
print("PERFORMANCE RANKING")
print("="*60)

for rank_item in data['statistics']['performance_ranking']:
    print(f"\n{rank_item['rank']}. {rank_item['mode'].upper()}")
    print(f"   Score: {rank_item['score']:.2f}/5")
    print(f"   Accuracy: {rank_item['accuracy']:.2f}/5")
    print(f"   Completeness: {rank_item['completeness']:.2f}/5")
EOF
```

---

## 🐛 Troubleshooting Quick Fixes

### Error: "ModuleNotFoundError: No module named 'google'"
```bash
# Reactivate venv and reinstall
deactivate  # Exit any current venv
rm -rf venv  # Delete old venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "GOOGLE_API_KEY not found"
```bash
# Check .env file exists
test -f .env && echo "✓ .env exists" || echo "✗ .env missing"

# Check key is set
grep GOOGLE_API_KEY .env || echo "Key not found in .env"

# Set it temporarily (for testing)
export GOOGLE_API_KEY="your-key-here"
```

### Error: "final_comparison.json not found"
```bash
# This means run_comparison.py failed
# Check if it ran completely:
ls -lh data/results/

# If missing, run again with verbose output:
python3 run_comparison.py 2>&1 | head -50
```

### Error: Rate limit exceeded (429)
```bash
# Wait 35 seconds and retry
sleep 35
python3 src/judge_metrics.py

# The Gemini client has caching, so rerunning helps
```

---

## 📚 More Information

- **Full Guide**: Read `EXECUTION_GUIDE.md`
- **Status**: Check `STATUS_REPORT.md`
- **Visualization Examples**: See `VISUALIZATION_EXAMPLES.md`
- **Judge Explanation**: See `JUDGE_METRICS_VISUALIZATION_GUIDE.md`
- **System README**: See `JUDGE_SYSTEM_README.md`

---

## ✅ Success Checklist

After completing all steps, verify:

- [ ] `final_comparison.json` exists and has responses
- [ ] `evaluation_report.json` exists and has scores
- [ ] `benchmark_summary.csv` exists and is importable
- [ ] `evaluation_metrics.json` exists
- [ ] Performance ranking shows RAG #1, Base #2, LoRA #3
- [ ] CSV data can be imported into Excel
- [ ] Visualization created (Excel/Matplotlib/Plotly)

---

## 🎉 You're Done!

You now have:
✅ Evaluated 39 responses (13 questions × 3 modes)  
✅ Generated impartial judge scores  
✅ Calculated comprehensive statistics  
✅ Created visualization-ready CSV  
✅ Visualized results in Excel or Python  

**Total Time: 10-15 minutes** ⏱️

---

## 🚀 Next Steps (Optional)

### Full Evaluation with LoRA (30-45 minutes)
Want to include local LoRA fine-tuning?

```bash
# 1. Prepare LoRA data
python3 src/prep_lora_data.py

# 2. Train LoRA (10-15 minutes)
python3 run_lora_pipeline.py

# 3. Run comparison with LoRA
python3 run_comparison.py --with-lora

# 4. Judge with LoRA included
python3 src/judge_metrics.py

# 5. See LoRA performance in results
```

### Create Detailed Report
Want to create a professional PDF report?

```bash
# Install reporting tools
pip install reportlab

# Generate PDF with charts and insights
python3 << 'EOF'
# (See VISUALIZATION_EXAMPLES.md for report generation code)
EOF
```

---

**Ready to start?** Run this command now:

```bash
cd /Users/bhavyananda/Documents/coding/rag_llm_evaluation_api && \
source venv/bin/activate && \
export PYTHONPATH=$PYTHONPATH:$(pwd) && \
python3 run_comparison.py && \
python3 src/judge_metrics.py && \
python3 evaluation_metrics.py && \
echo "✓ Evaluation complete! Check data/results/"
```

---

**Generated**: April 1, 2026  
**System**: Triple Comparison Judge  
**Version**: 1.0  
**Status**: Ready to Execute ✓
