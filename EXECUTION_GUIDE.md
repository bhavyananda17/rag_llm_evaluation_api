# Triple Comparison Judge System - Complete Execution Guide

## Overview

This guide provides step-by-step instructions for executing the complete Triple Comparison Judge System. The system evaluates AI responses from three models:

1. **Base**: Direct Gemini API calls (baseline)
2. **RAG**: Gemini API with vector store context retrieval
3. **LoRA**: Local inference with LoRA-adapted model (optional)

The judge uses impartial evaluation criteria to rate responses on accuracy, completeness, and hallucination detection, generating professional-grade reports suitable for visualization.

---

## Quick Start (5-10 minutes)

### Prerequisites
- Python 3.8+
- Virtual environment activated: `source venv/bin/activate`
- Dependencies installed: `pip install -r requirements.txt`
- `.env` file with `GOOGLE_API_KEY` set
- `data/processed/synthetic_qa.json` exists (13 QA pairs)
- Vector store index exists: `data/processed/vector_index.faiss`

### Step 1: Generate Comparison Data
```bash
cd /Users/bhavyananda/Documents/coding/rag_llm_evaluation_api
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run Base and RAG comparison (no LoRA)
python3 run_comparison.py --output data/results/final_comparison.json
```

**Expected Output:**
- `data/results/final_comparison.json` - Contains responses from Base and RAG modes for all 13 questions
- Console output shows progress: `[1/13] Evaluating...` through `[13/13]`
- ~2-3 minutes to complete

### Step 2: Run Judge Evaluation
```bash
# Judge all responses and calculate benchmarks
python3 src/judge_metrics.py
```

**Expected Output:**
- `data/results/evaluation_report.json` - Detailed judgment with scores
- `data/results/benchmark_summary.csv` - Visualization-ready summary
- Console output shows:
  - Judgment progress: `[1/13] Judging...` through `[13/13]`
  - Performance ranking (RAG expected #1)
  - Detailed statistics for each mode

### Step 3: Analyze Metrics
```bash
# Generate comprehensive metrics analysis
python3 evaluation_metrics.py
```

**Expected Output:**
- `data/results/evaluation_metrics.json` - Detailed statistical analysis
- Console output shows latency analysis, success rates, quality metrics

### Step 4: Export for Visualization
The CSV file `data/results/benchmark_summary.csv` is now ready for:
- **Excel**: Import CSV and create charts
- **Python**: Use Pandas/Matplotlib to create visualizations
- **Web**: JSON file ready for D3.js or Plotly

---

## Complete Execution (30-45 minutes)

For full evaluation including LoRA mode:

### Step 1: Prepare LoRA Data
```bash
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)

python3 src/prep_lora_data.py
```

### Step 2: Train LoRA Adapter
```bash
# Fine-tune with LoRA (10-15 minutes)
python3 run_lora_pipeline.py
```

### Step 3: Generate Full Comparison
```bash
# Include all three modes: Base, RAG, LoRA
python3 run_comparison.py --with-lora --output data/results/final_comparison.json
```

### Step 4-6: Same as Quick Start
- Run judge evaluation
- Analyze metrics
- Export for visualization

---

## Output Files

### Primary Outputs

#### 1. `data/results/evaluation_report.json`
Contains detailed judgment data with structure:
```json
{
  "metadata": {
    "timestamp": "2026-04-01T...",
    "source_file": "data/results/final_comparison.json",
    "total_questions": 13,
    "judge_model": "gemini-1.5-flash"
  },
  "judgments": [
    {
      "question_id": 1,
      "question": "How does self-attention...",
      "ground_truth": "...",
      "scores": {
        "base": {
          "accuracy": 4,
          "completeness": 3,
          "hallucination_detected": false,
          "reasoning": "..."
        },
        "rag": {
          "accuracy": 5,
          "completeness": 5,
          "hallucination_detected": false,
          "reasoning": "..."
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
        "hallucination_count": 1,
        "grounded_responses": 12
      }
    },
    "performance_ranking": [
      {
        "rank": 1,
        "mode": "rag",
        "score": 4.59,
        "accuracy": 4.62,
        "completeness": 4.54
      }
    ]
  }
}
```

#### 2. `data/results/benchmark_summary.csv`
Visualization-ready summary:
```csv
Metric,Base,RAG,LoRA
Accuracy (avg),3.85,4.62,3.31
Completeness (avg),3.23,4.54,2.85
Overall Score,3.62,4.59,3.15
Hallucinations,1,0,4
Hallucination Rate (%),7.7,0.0,30.8
Grounded Rate (%),92.3,100.0,69.2
```

#### 3. `data/results/evaluation_metrics.json`
Statistical analysis with latency metrics, success rates, quality analysis.

#### 4. `data/results/final_comparison.json`
Raw comparison data with all responses from each model.

---

## Scoring System

### Accuracy (1-5)
- **1**: Completely wrong or contradicts ground truth
- **2**: Mostly incorrect with some accurate elements
- **3**: Partially correct, but misses key details
- **4**: Mostly accurate with minor errors
- **5**: Completely accurate and factually correct

### Completeness (1-5)
- **1**: Missing most key points
- **2**: Covers less than 50% of important concepts
- **3**: Covers about 50% of key points
- **4**: Covers most key points with minor omissions
- **5**: Comprehensive coverage of all key concepts

### Hallucination Detection
- **YES**: Response invents facts not in the context → -2 penalty applied to accuracy
- **NO**: Response stays grounded → No penalty

### Overall Score Calculation
```
Overall Score = (Accuracy × 0.6) + (Completeness × 0.4)
```

**Example:**
- Accuracy: 4/5, Completeness: 3/5
- Overall Score = (4 × 0.6) + (3 × 0.4) = 2.4 + 1.2 = **3.6/5**

---

## Expected Results

Based on system design:

### Expected Rankings
1. **RAG** (Expected #1): ~4.5-4.6/5
   - Best performance with context retrieval
   - Highest accuracy and completeness
   - Minimal hallucinations (0-1)

2. **Base** (Expected #2): ~3.6-3.8/5
   - Direct API without context
   - Moderate accuracy and completeness
   - Some hallucinations (1-2)

3. **LoRA** (Expected #3): ~3.1-3.4/5
   - Local inference with fine-tuned adapter
   - Lower completeness without context
   - Higher hallucination rate (3-5)

### Hallucination Summary
| Mode | Hallucinations | Rate |
|------|---|---|
| Base | 1-2 | 7.7-15.4% |
| RAG | 0-1 | 0-7.7% |
| LoRA | 3-5 | 23.1-38.5% |

---

## Command Reference

### Full Execution Commands

```bash
# Navigate to project directory
cd /Users/bhavyananda/Documents/coding/rag_llm_evaluation_api

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# === QUICK PATH (10 minutes) ===

# 1. Generate Base+RAG comparison
python3 run_comparison.py

# 2. Judge responses
python3 src/judge_metrics.py

# 3. Analyze metrics
python3 evaluation_metrics.py

# === FULL PATH (40 minutes) ===

# 1. Prepare LoRA data
python3 src/prep_lora_data.py

# 2. Train LoRA adapter
python3 run_lora_pipeline.py

# 3. Generate Base+RAG+LoRA comparison
python3 run_comparison.py --with-lora

# 4. Judge responses
python3 src/judge_metrics.py

# 5. Analyze metrics
python3 evaluation_metrics.py
```

### Useful Options

```bash
# Custom output file
python3 run_comparison.py --output /path/to/custom_output.json

# Custom QA file
python3 run_comparison.py --qa-file /path/to/custom_qa.json

# Skip RAG mode
python3 run_comparison.py --skip-rag

# Skip judge evaluation (only calculate benchmarks)
python3 src/judge_metrics.py --skip-judge

# Custom comparison file for judge
python3 src/judge_metrics.py --comparison-file /path/to/comparison.json
```

---

## Visualization Guide

### Option 1: Excel Visualization

1. Open Excel
2. File → Open → Select `data/results/benchmark_summary.csv`
3. Create charts:
   - **Bar Chart**: Overall Score, Accuracy, Completeness
   - **Pie Chart**: Hallucination rates
   - **Line Chart**: Performance comparison

### Option 2: Python Visualization

```python
import pandas as pd
import matplotlib.pyplot as plt

# Read CSV
df = pd.read_csv('data/results/benchmark_summary.csv', index_col=0)

# Create subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Overall Score
df.loc['Overall Score'].plot(kind='bar', ax=axes[0, 0], title='Overall Score')

# Accuracy
df.loc['Accuracy (avg)'].plot(kind='bar', ax=axes[0, 1], title='Accuracy')

# Completeness
df.loc['Completeness (avg)'].plot(kind='bar', ax=axes[1, 0], title='Completeness')

# Hallucination Rate
df.loc['Hallucination Rate (%)'].plot(kind='bar', ax=axes[1, 1], title='Hallucination Rate (%)')

plt.tight_layout()
plt.savefig('evaluation_summary.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Option 3: JSON for Web Visualization

The `evaluation_report.json` is ready for:
- D3.js visualizations
- Plotly charts
- Custom dashboards
- Integration with reporting tools

---

## Troubleshooting

### Issue: "GOOGLE_API_KEY not found"
**Solution:** 
- Check `.env` file exists in project root
- Verify `GOOGLE_API_KEY=your_key` is set
- Run: `source .env` before executing

### Issue: "Vector store not found"
**Solution:**
- Ensure `data/processed/vector_index.faiss` exists
- If missing, the system will skip RAG mode
- Use `--skip-rag` flag to run without RAG

### Issue: "LoRA model not found"
**Solution:**
- LoRA is optional; system continues without it
- For full evaluation: `python3 src/prep_lora_data.py && python3 run_lora_pipeline.py`

### Issue: "Rate limit exceeded"
**Solution:**
- Wait ~35 seconds before retrying
- Use API cache: Gemini client automatically caches responses
- Run comparison again: `python3 run_comparison.py`

### Issue: JSON parsing error in judge
**Solution:**
- System has fallback error handling
- Check if `final_comparison.json` was generated correctly
- Re-run: `python3 run_comparison.py`

---

## Performance Metrics

### Execution Time

| Step | Quick Path | Full Path |
|------|---|---|
| Generate Comparison | 2-3 min | 5-8 min |
| Judge Evaluation | 3-5 min | 3-5 min |
| Metrics Analysis | <1 min | <1 min |
| **Total** | **5-10 min** | **30-45 min** |

### API Costs

- **Base Mode**: ~39 requests (13 questions)
- **RAG Mode**: ~39 requests (13 questions with retrieval)
- **LoRA Mode**: Local inference (no API cost)
- **Judge**: ~13 requests (1 per question)

**Free Tier**: Typically sufficient for this workload (~100 requests/month included)

---

## File Structure

```
rag_llm_evaluation_api/
├── src/
│   ├── judge_metrics.py          ← Judge system
│   ├── evaluator.py               ← Model evaluator
│   ├── model_client.py            ← Gemini client
│   ├── vector_db.py               ← Vector store
│   ├── config.py                  ← Configuration
│   └── ...
├── run_comparison.py              ← Comparison orchestrator
├── evaluation_metrics.py           ← Metrics analyzer
├── requirements.txt               ← Dependencies
├── .env                           ← API key
├── data/
│   ├── processed/
│   │   ├── synthetic_qa.json      ← Input QA pairs (13)
│   │   ├── vector_index.faiss     ← Vector store index
│   │   └── vector_index_metadata.json
│   └── results/
│       ├── final_comparison.json  ← Comparison output
│       ├── evaluation_report.json ← Judge output
│       ├── benchmark_summary.csv  ← Visualization CSV
│       └── evaluation_metrics.json ← Metrics output
└── EXECUTION_GUIDE.md             ← This file
```

---

## Next Steps

1. **Execute Quick Path** (5-10 minutes)
   - Run comparison: `python3 run_comparison.py`
   - Judge responses: `python3 src/judge_metrics.py`
   - Analyze metrics: `python3 evaluation_metrics.py`

2. **Review Results**
   - Open `data/results/evaluation_report.json`
   - Check `data/results/benchmark_summary.csv`
   - Review console output for insights

3. **Visualize Data**
   - Import CSV into Excel
   - Create charts and dashboards
   - Generate reports

4. **Analyze Findings**
   - Compare model performance
   - Identify hallucination patterns
   - Make recommendations

5. **Optional: Full Evaluation**
   - Include LoRA mode for complete comparison
   - Provides insights on local fine-tuning effectiveness
   - Takes additional 30-35 minutes

---

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review console output for error messages
3. Check file existence: `ls -lh data/results/`
4. Verify API key: `echo $GOOGLE_API_KEY`
5. Test imports: `python3 -c "from src.judge_metrics import JudgeMetrics"`

---

## Summary

The Triple Comparison Judge System provides:
- ✅ Impartial evaluation across three model modes
- ✅ Professional-grade scoring system
- ✅ Comprehensive statistical analysis
- ✅ Visualization-ready output formats
- ✅ Detailed hallucination detection
- ✅ Performance ranking and comparison

**Ready to execute: YES** ✓

Start with the Quick Start path for fastest results, or follow the Complete Execution path for comprehensive evaluation including LoRA mode.
