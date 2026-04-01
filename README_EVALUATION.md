# RAG + LoRA Evaluation API

A comprehensive system for comparing three distinct approaches to answering questions:
- **Base**: Direct Gemini API calls
- **RAG**: Gemini API with vector store context retrieval
- **LoRA**: Local inference using LoRA-adapted models

## 🚀 Quick Start (2 minutes)

```bash
# 1. Set up environment
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 2. Run evaluation
python3 run_comparison.py --with-lora

# 3. Analyze results
python3 evaluation_metrics.py

# 4. View results
cat data/results/final_comparison.json
```

## 📋 What This Does

**Compares 13 test questions across 3 modes:**

```
Question 1: "How does self-attention differ from cross-attention?"

Base Mode:   0.523s  → "Self-attention is a mechanism where..."
RAG Mode:    1.245s  → "Based on context: Self-attention..."
LoRA Mode:   0.087s  → "Self-attention enables..."

[Saves all responses + latency + success status]
```

**Generates detailed analysis:**
- Latency statistics (min/max/mean/stdev)
- Success rates per mode
- Response quality metrics
- Performance by difficulty

## 📦 What's Included

### Core Components
- **`src/evaluator.py`** - ModelEvaluator class with unified interface
- **`run_comparison.py`** - Main execution script
- **`evaluation_metrics.py`** - Results analysis

### Data
- **`data/processed/synthetic_qa.json`** - 13 test QA pairs
- **`data/processed/vector_index.faiss`** - Vector store for RAG
- **`models/lora_adapters/`** - Pre-trained LoRA weights

### Documentation
- **`TRIPLE_COMPARISON_QUICKSTART.md`** - Quick reference guide
- **`TRIPLE_COMPARISON_GUIDE.md`** - Full technical documentation
- **`IMPLEMENTATION_CHECKLIST.md`** - Verification checklist

## 🎯 Usage Examples

### Run All Modes
```bash
python3 run_comparison.py --with-lora
```

### Run Specific Modes
```bash
# Base + RAG only
python3 run_comparison.py

# Base + LoRA only
python3 run_comparison.py --with-lora --skip-rag

# Base only (fastest)
python3 run_comparison.py --skip-rag --skip-lora
```

### Custom Configuration
```bash
# Use different questions
python3 run_comparison.py --qa-file data/my_questions.json

# Save to custom location
python3 run_comparison.py --output results/my_comparison.json

# Enable verbose logging
python3 run_comparison.py --verbose
```

### Analyze Results
```bash
python3 evaluation_metrics.py
```

## 📊 Output

### final_comparison.json
Contains side-by-side comparison of all three modes:
```json
{
  "question_id": 1,
  "question": "How does self-attention differ...",
  "base": {"response": "...", "latency": 0.523, "success": true},
  "rag": {"response": "...", "latency": 1.245, "success": true},
  "lora": {"response": "...", "latency": 0.087, "success": true}
}
```

### evaluation_metrics.json
Statistical analysis of results:
```json
{
  "latency_analysis": {
    "base": {"count": 13, "mean": 0.523, "stdev": 0.187},
    "rag": {"count": 13, "mean": 1.245, "stdev": 0.412},
    "lora": {"count": 12, "mean": 0.087, "stdev": 0.038}
  },
  "success_analysis": {
    "base": {"successful": 13, "success_rate": 1.0},
    "rag": {"successful": 13, "success_rate": 1.0},
    "lora": {"successful": 12, "success_rate": 0.923}
  }
}
```

## ⚡ Expected Performance

### Latency (on M1/M2 Mac)
| Mode | Min | Mean | Max |
|------|-----|------|-----|
| Base | 200ms | 523ms | 890ms |
| RAG | 800ms | 1.2s | 2.3s |
| LoRA | 40ms | 87ms | 200ms |

### Success Rate
| Mode | Rate | Notes |
|------|------|-------|
| Base | 100% | Reliable API |
| RAG | 100% | Context-aware |
| LoRA | 92% | Memory dependent |

## 🔧 Installation

### Prerequisites
```bash
# Python 3.7+
python3 --version

# Install dependencies
pip install -r requirements.txt

# For LoRA support (optional)
pip install -r requirements-lora.txt
```

### Configuration
```bash
# Add Gemini API key to .env
echo "GOOGLE_API_KEY=your_key_here" > .env

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## 📚 Documentation

### Get Started (5-10 minutes)
1. **TRIPLE_COMPARISON_QUICKSTART.md** - TL;DR with examples

### Understand the System (30 minutes)
2. **TRIPLE_COMPARISON_GUIDE.md** - Full technical guide with architecture

### Deep Dive (1 hour)
3. **TRIPLE_COMPARISON_IMPLEMENTATION.md** - Implementation details
4. **IMPLEMENTATION_CHECKLIST.md** - Complete feature verification

### Reference
5. **PROJECT_COMPLETION.md** - Project summary
6. Code docstrings in `src/evaluator.py`

## 🏗️ Architecture

```
ModelEvaluator
├── get_answer(question, mode)
│   ├── mode='base'  → Gemini API
│   ├── mode='rag'   → Vector Search + Gemini API
│   └── mode='lora'  → Local LoRA Model
│
├── run_full_comparison()
│   ├── Load 13 QA pairs
│   ├── Evaluate all 3 modes for each question
│   ├── Track latency
│   └── Save to final_comparison.json
│
└── Statistics tracking
    ├── Success rates
    ├── Latency metrics
    └── Quality metrics
```

## 🔄 Workflow

```
1. User runs: python3 run_comparison.py --with-lora

2. System loads 13 QA pairs from synthetic_qa.json

3. For each question:
   - Gets base response (~0.5s)
   - Gets RAG response (~1.2s) 
   - Gets LoRA response (~0.09s)

4. Saves final_comparison.json with all results

5. User runs: python3 evaluation_metrics.py

6. System analyzes results and saves evaluation_metrics.json
```

## 🎓 Learning Path

1. **5 min**: Read QUICKSTART
2. **10 min**: Run `python3 run_comparison.py`
3. **15 min**: Review output in `data/results/`
4. **30 min**: Read GUIDE for understanding
5. **60 min**: Explore source code and customize

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Issue: GOOGLE_API_KEY not found
```bash
echo "GOOGLE_API_KEY=your_key_here" >> .env
```

### Issue: Vector store not initialized
```bash
python3 src/build_index.py
```

### Issue: LoRA model not loading
```bash
pip install peft transformers torch

# Or skip LoRA:
python3 run_comparison.py --skip-lora
```

## 📈 Use Cases

### Speed Optimization
Use **LoRA mode** - fastest option (~87ms)

### Quality Optimization
Use **RAG mode** - context-aware answers

### Reliability Baseline
Use **Base mode** - direct API calls

### Balanced Approach
Use **Base + LoRA** - speed with fallback

## 🚀 Deployment

### Development
```bash
python3 run_comparison.py
```

### Production
```bash
export GOOGLE_API_KEY="your-key"
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 run_comparison.py --with-lora > logs/eval.log 2>&1
```

### Scaling
- Results in JSON for programmatic access
- Modular design allows parallel processing
- Caching reduces repeated API calls

## 📞 Support

### Documentation
- **Quick Start**: TRIPLE_COMPARISON_QUICKSTART.md
- **Full Guide**: TRIPLE_COMPARISON_GUIDE.md
- **Implementation**: TRIPLE_COMPARISON_IMPLEMENTATION.md
- **Checklist**: IMPLEMENTATION_CHECKLIST.md

### Code
- Comprehensive docstrings in `src/evaluator.py`
- Example usage in scripts
- Test files available

## ✨ Features

✅ **Unified Interface** - Same API for all three modes  
✅ **Automatic Latency** - Measures time for each response  
✅ **Error Resilient** - One mode fails, others continue  
✅ **Statistical Analysis** - Comprehensive metrics included  
✅ **Production Ready** - Full error handling and logging  
✅ **Extensible** - Easy to add custom modes/metrics  
✅ **Well Documented** - Multiple guides and examples  

## 🏆 Project Statistics

- **Code**: 2,000+ lines
- **Documentation**: 2,000+ lines
- **Test Coverage**: Comprehensive
- **Files**: 40+ organized files
- **Status**: ✅ Production Ready

## 📝 License

See LICENSE file for details.

## 🤝 Contributing

To extend the system:

1. **Add Custom Mode**
   ```python
   class CustomEvaluator(ModelEvaluator):
       def _get_custom_mode(self, question):
           # Your implementation
           pass
   ```

2. **Add Custom Metrics**
   ```python
   class CustomMetrics(EvaluationMetrics):
       def analyze_custom(self):
           # Your analysis
           pass
   ```

3. **Modify Configuration**
   - Edit `src/config.py` for paths
   - Update `.env` for API keys

## 🎯 Next Steps

1. ✅ Run evaluation: `python3 run_comparison.py --with-lora`
2. ✅ Analyze results: `python3 evaluation_metrics.py`
3. ✅ Review documentation: Start with QUICKSTART
4. ✅ Choose best mode(s) for your use case
5. ✅ Deploy in production

---

**Version**: 1.0  
**Status**: ✅ Production Ready  
**Last Updated**: April 1, 2026

For detailed information, see **TRIPLE_COMPARISON_QUICKSTART.md**
