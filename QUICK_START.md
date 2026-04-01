# Quick Start Guide - RAG vs LoRA Evaluation System

## Setup (One-time)

```bash
# Navigate to project
cd /Users/bhavyananda/Documents/coding/rag_llm_evaluation_api

# Activate virtual environment
source venv/bin/activate
```

## Run Each Component

### 1️⃣ Generate QA Dataset (13 benchmark questions)
```bash
python3 src/generate_data.py
```
**Output:** `data/processed/synthetic_qa.json`

### 2️⃣ Build Vector Index (147 document chunks)
```bash
python3 src/build_index.py
```
**Output:** 
- `data/processed/vector_index.faiss`
- `data/processed/vector_index_metadata.json`

### 3️⃣ Benchmark Base Model (without context)
```bash
python3 src/benchmark_base.py
```
**Output:** `data/results/base_model_results.json`

### 4️⃣ Analyze Results
```bash
python3 analyze_dataset.py
```

---

## Testing Individual Components

### Test QA Generation
```bash
python3 test_generation.py
```

### Test Vector Store
```bash
python3 test_vector_store.py
```

### Test Benchmark
```bash
python3 test_benchmark.py
```

---

## Programmatic Usage

### Load QA Dataset
```python
import json

with open('data/processed/synthetic_qa.json') as f:
    dataset = json.load(f)
    
qa_pairs = dataset['qa_pairs']
for pair in qa_pairs[:3]:
    print(f"Q: {pair['question'][:80]}...")
```

### Use Vector Store
```python
from src.vector_db import VectorStore
from src.config import Config

vs = VectorStore()
vs.load_index('data/processed/vector_index.faiss')

results = vs.retrieve("attention mechanisms", k=3)
for result in results:
    print(f"[{result['rank']}] {result['source_file']}: {result['similarity_score']:.4f}")
```

### Run Benchmark
```python
from src.benchmark_base import BaseModelBenchmark

benchmark = BaseModelBenchmark()
results = benchmark.run_benchmark(num_samples=5, rate_limit_delay=2.0)
benchmark.save_results()
```

---

## Key Files & Locations

| File | Purpose | Location |
|------|---------|----------|
| **synthetic_qa.json** | 13 benchmark QA pairs | `data/processed/` |
| **vector_index.faiss** | FAISS vector index (147 chunks) | `data/processed/` |
| **base_model_results.json** | Benchmark results | `data/results/` |
| **qa_pairs.csv** | QA pairs in CSV format | `data/exports/` |
| **evaluation_format.json** | Standard evaluation format | `data/exports/` |
| **rag_benchmark.json** | RAG-specific format | `data/exports/` |

---

## Dataset Statistics

```
QA Pairs: 13 (all difficulty: Hard)
Vector Chunks: 147 (500 tokens each with 100-token overlap)
Source Files: 8 technical documents
Focus Areas: 
  - Self-attention vs Cross-attention
  - Intrinsic vs Extrinsic hallucinations
  - LoRA vs Full fine-tuning
  - RAG retrieval quality
  - Transformer architecture
  - Vector embeddings
```

---

## Benchmarking Tips

### Rate Limiting
```python
# The system uses 2s delay between API calls by default
# Adjust with rate_limit_delay parameter
benchmark.run_benchmark(rate_limit_delay=1.0)  # 1 second delay
```

### Sample Size
```python
# Test with small samples first
benchmark.run_benchmark(num_samples=1)   # 1 question
benchmark.run_benchmark(num_samples=3)   # 3 questions
benchmark.run_benchmark(num_samples=None) # All 13 questions
```

### Error Handling
```python
# Results include success flag and timestamps
for result in benchmark.results:
    if result['success']:
        print(f"✓ {result['id']}")
    else:
        print(f"✗ {result['id']}: {result.get('error', 'Unknown error')}")
```

---

## Troubleshooting

### Issue: "QA dataset not found"
```
Solution: Run src/generate_data.py first
```

### Issue: "Index not found"
```
Solution: Run src/build_index.py first
```

### Issue: "API quota exceeded"
```
Solution: Wait for quota reset or use different API key
```

### Issue: Import errors
```
Solution: source venv/bin/activate && pip install -r requirements.txt
```

---

## Output Files Structure

```
data/
├── raw/                    # Input documents (8 files)
├── processed/
│   ├── synthetic_qa.json                  # Main QA dataset
│   ├── vector_index.faiss                 # FAISS index
│   └── vector_index_metadata.json         # Index metadata
├── results/
│   └── base_model_results.json            # Benchmark results
└── exports/
    ├── qa_pairs.csv                       # CSV format
    ├── evaluation_format.json             # Standard format
    └── rag_benchmark.json                 # RAG-specific format
```

---

## Performance Expectations

| Operation | Time | Memory |
|-----------|------|--------|
| QA Generation | <5s | <100MB |
| Index Building | ~30s | <200MB |
| Vector Query | <100ms | <50MB |
| Benchmark (1 Q) | ~2s | <150MB |
| Full Benchmark (13 Q) | ~26s | <200MB |

---

## Next Commands (When Ready)

```bash
# When RAG evaluation is ready
python3 src/benchmark_rag.py

# When LoRA evaluation is ready
python3 src/benchmark_lora.py

# Generate comparison report
python3 src/compare_models.py
```

---

## Project Structure Map

```
┌─ data/raw/                          (Input documents)
│  └─ 8 .txt files
│
├─ data/processed/                    (Generated data)
│  ├─ synthetic_qa.json              (13 QA pairs)
│  └─ vector_index.*                 (147 chunks)
│
├─ data/results/                      (Benchmark results)
│  └─ base_model_results.json
│
├─ src/
│  ├─ generate_data.py               (QA generation)
│  ├─ vector_db.py                   (Vector store)
│  ├─ build_index.py                 (Index building)
│  ├─ benchmark_base.py              (Base benchmarking)
│  └─ ...
│
└─ Documentation/
   ├─ COMPLETE_SYSTEM_SUMMARY.md
   ├─ QA_GENERATION_GUIDE.md
   ├─ VECTOR_STORE_SUMMARY.md
   └─ README.md
```

---

## Validation Checklist

- [x] QA dataset generated (13 pairs)
- [x] Vector index built (147 chunks)
- [x] Base model benchmark functional
- [x] Results exportable to JSON
- [x] Rate limiting implemented
- [x] Progress tracking working
- [x] All tests passing
- [ ] RAG evaluation ready
- [ ] LoRA evaluation ready
- [ ] Comparative analysis ready

---

**Ready to use! Start with:** `python3 src/generate_data.py`
