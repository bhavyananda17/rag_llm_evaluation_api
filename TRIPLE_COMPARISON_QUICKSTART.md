# Triple Comparison Evaluation - Quick Start

## TL;DR

```bash
# 1. Setup environment
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 2. Run comparison (base + RAG modes)
python3 run_comparison.py

# 3. Add LoRA mode (if adapters exist)
python3 run_comparison.py --with-lora

# 4. Analyze results
python3 evaluation_metrics.py

# 5. View results
cat data/results/final_comparison.json      # Detailed responses
cat data/results/evaluation_metrics.json    # Statistics
```

## What Gets Generated

### 1. **final_comparison.json** (13 questions × 3 modes)

Contains side-by-side comparison:
- Question & ground truth
- Response from Base, RAG, and LoRA
- Latency for each mode
- Success/failure status

**Size**: ~250KB  
**Location**: `data/results/final_comparison.json`

### 2. **evaluation_metrics.json** (Statistical analysis)

Contains:
- Latency statistics (min/max/mean/stdev)
- Success rates
- Response quality metrics
- Performance by difficulty

**Size**: ~15KB  
**Location**: `data/results/evaluation_metrics.json`

## Expected Latencies

| Mode | Expected | Notes |
|------|----------|-------|
| Base | 0.3-0.9s | Gemini API call |
| RAG | 0.8-2.3s | Retrieval + API |
| LoRA | 0.04-0.2s | Local inference |

## Mode Comparison

### Base Mode
```
Question → Gemini API → Response
```
- **Pros**: Reliable, no setup needed
- **Cons**: Slowest, requires API key
- **Use for**: Baseline comparison

### RAG Mode
```
Question → Vector Search → Context + Gemini API → Response
```
- **Pros**: Context-aware, good quality
- **Cons**: Slower (2-phase), needs vector store
- **Use for**: Quality with context

### LoRA Mode
```
Question → Local LoRA Model → Response
```
- **Pros**: Fastest, no API calls
- **Cons**: Requires training, memory hungry
- **Use for**: Speed/cost optimization

## File Locations

```
project_root/
├── run_comparison.py           # Main script (start here)
├── evaluation_metrics.py       # Results analyzer
│
├── src/
│   └── evaluator.py           # Core evaluation class
│
├── data/
│   ├── processed/
│   │   └── synthetic_qa.json  # 13 test questions
│   └── results/
│       ├── final_comparison.json      # Main output
│       └── evaluation_metrics.json    # Analysis output
│
└── models/
    └── lora_adapters/         # LoRA weights (if available)
```

## Common Commands

### Run with all modes
```bash
python3 run_comparison.py --with-lora
```

### Run specific modes only
```bash
# Base only (fast, no dependencies)
python3 run_comparison.py --skip-rag

# RAG only (skip LoRA if not trained)
python3 run_comparison.py --skip-lora
```

### Custom files
```bash
# Use different questions
python3 run_comparison.py --qa-file path/to/questions.json

# Save to custom location
python3 run_comparison.py --output path/to/results.json
```

### Analyze existing results
```bash
# Default: analyze final_comparison.json
python3 evaluation_metrics.py

# Custom file
python3 evaluation_metrics.py --results path/to/comparison.json
```

## Output Examples

### Sample final_comparison.json Entry
```json
{
  "question_id": 1,
  "question": "How does self-attention differ from cross-attention?",
  "ground_truth": "Self-attention attends to the same sequence...",
  "base": {
    "response": "Self-attention is a mechanism where...",
    "latency": 0.523,
    "success": true
  },
  "rag": {
    "response": "Based on context: Self-attention...",
    "latency": 1.245,
    "retrieval_time": 0.352,
    "context_count": 3,
    "success": true
  },
  "lora": {
    "response": "Self-attention is a key component...",
    "latency": 0.087,
    "success": true
  }
}
```

### Sample evaluation_metrics.json Summary
```json
{
  "latency_analysis": {
    "base": {
      "count": 13,
      "mean": 0.523,
      "median": 0.501,
      "stdev": 0.187
    },
    "rag": {
      "count": 13,
      "mean": 1.245,
      "median": 1.123,
      "stdev": 0.412
    },
    "lora": {
      "count": 12,
      "mean": 0.087,
      "median": 0.082,
      "stdev": 0.038
    }
  },
  "success_analysis": {
    "base": {"successful": 13, "success_rate": 1.0},
    "rag": {"successful": 13, "success_rate": 1.0},
    "lora": {"successful": 12, "success_rate": 0.923}
  }
}
```

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | `export PYTHONPATH=$PYTHONPATH:$(pwd)` |
| "Vector store not found" | `python3 src/build_index.py` |
| "LoRA model not initialized" | `pip install peft transformers` |
| "GOOGLE_API_KEY not found" | Add key to `.env` file |
| "Out of memory" | Run with `--skip-lora` |

## Performance Tips

### Speed Up Evaluation
```bash
# Skip slow modes
python3 run_comparison.py --skip-rag --skip-lora  # Base only

# Or run in parallel (manual)
python3 run_comparison.py > results_1.json &
python3 run_comparison.py > results_2.json &
wait
```

### Reduce Memory Usage
```bash
# Modify src/evaluator.py _get_lora_answer():
max_length=128,  # Reduce from 256
num_beams=1      # Greedy decoding
```

### Cache Results
```python
# Already enabled by default
evaluator = ModelEvaluator(use_cache=True)
```

## Interpreting Results

### Latency Comparison
- **Lower is better** for latency
- Base: ~500ms (API overhead)
- RAG: ~1.2s (retrieval + API)
- LoRA: ~87ms (local only)

### Success Rate
- **Higher is better**
- Target: 100% success
- Check `error` field for failures

### Response Quality
- **Longer responses** often more detailed
- **LoRA** may be shorter (local model limits)
- **RAG** context usually improves quality

## Next Steps

1. ✅ Run `python3 run_comparison.py`
2. ✅ Run `python3 evaluation_metrics.py`
3. ✅ Review `final_comparison.json`
4. ✅ Read TRIPLE_COMPARISON_GUIDE.md for details
5. ✅ Optimize based on results

---

**See Also**:
- `TRIPLE_COMPARISON_GUIDE.md` - Full documentation
- `src/evaluator.py` - Implementation details
- `run_comparison.py` - Main script
- `evaluation_metrics.py` - Analysis script
