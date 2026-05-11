# Repository Organization Guide

This document explains the repository structure after cleanup and reorganization.

## 📁 Root Directory

```
project/
├── README.md                      # Main project overview
├── QUICK_START.md                 # Quick start guide for first-time users
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── .git/                          # Git repository
│
├── src/                           # ✅ Core application code (do not modify)
│   ├── __init__.py
│   ├── benchmark_base.py          # Base model benchmark
│   ├── benchmark_rag.py           # RAG benchmark
│   ├── build_index.py             # Vector index builder
│   ├── config.py                  # Configuration
│   ├── evaluator.py               # Triple model evaluator
│   ├── generate_data.py           # QA pair generation
│   ├── generate_mock_results.py   # Mock result generation
│   ├── judge_metrics.py           # Evaluation metrics
│   ├── model_client.py            # API client with caching
│   ├── optimized_benchmark.py     # Token-optimized runner
│   ├── prep_lora_data.py          # LoRA data formatter
│   ├── token_manager.py           # Token tracking system
│   ├── train_lora.py              # LoRA training script
│   ├── vector_db.py               # FAISS vector store
│   └── utils/                     # Utility modules
│
├── tests/                         # ✅ Test suite
│   ├── test_benchmark.py
│   ├── test_generation.py
│   ├── test_lora_prep.py
│   ├── test_optimization.py
│   ├── test_rag_benchmark.py
│   └── test_vector_store.py
│
├── scripts/                       # 🎯 Demo, example, and runner scripts
│   ├── analyze_dataset.py         # Dataset analysis tool
│   ├── comprehensive_test.py      # Full system test
│   ├── demo_status.py             # Status check demo
│   ├── evaluation_metrics.py      # Metrics runner
│   ├── integration_test.py        # Integration test
│   ├── rag_example.py             # RAG example
│   ├── rag_pipeline_demo.py       # RAG pipeline demo
│   ├── run_comparison.py          # Main comparison runner
│   ├── run_lora_pipeline_fixed.py # LoRA pipeline runner
│   ├── run_optimized_benchmark.py # Optimized benchmark runner
│   ├── simple_rag_test.py         # Simple RAG test
│   ├── USAGE_EXAMPLES.py          # Usage examples
│   └── verify_lora_setup.py       # LoRA setup verification
│
├── data/                          # Data directory (generated, not in git)
│   ├── raw/                       # Raw documents for RAG
│   ├── processed/                 # Generated QA pairs, indices
│   ├── cache/                     # API response cache
│   ├── logs/                      # Token usage logs
│   ├── results/                   # Benchmark results
│   └── exports/                   # Data exports
│
├── docs/                          # Documentation
│   ├── REPOSITORY_STRUCTURE.md    # This file
│   ├── guides/                    # Technical guides
│   │   ├── BENCHMARKING_GUIDE.md
│   │   ├── LORA_TRAINING_GUIDE.md
│   │   └── TOKEN_OPTIMIZATION_GUIDE.md
│   └── archive/                   # Historical implementation reports
│       ├── AI_GENERATED_PATTERN_ANALYSIS.md
│       ├── CLEANUP_AUDIT_REPORT.md
│       ├── STRICT_EVIDENCE_AUDIT.md
│       └── [40+ other reports]    # Preserved for reference
│
├── notebooks/                     # Jupyter notebooks (if any)
│
└── venv/                          # Python virtual environment (in .gitignore)
```

## 📚 Documentation Organization

### Core Documentation (Root)
- **README.md** - Project overview, architecture, key results
- **QUICK_START.md** - First-time setup and basic usage

### Technical Guides (docs/guides/)
- **BENCHMARKING_GUIDE.md** - How to run benchmarks
- **LORA_TRAINING_GUIDE.md** - How to train LoRA adapters
- **TOKEN_OPTIMIZATION_GUIDE.md** - Token efficiency best practices

### Historical Records (docs/archive/)
Preserved for reference but organized out of root:
- Implementation checklists and progress reports
- Audit findings and analysis results
- Cleanup documentation
- Code pattern detection reports
- Status updates from development

## 🎯 Script Usage

All demo, example, and runner scripts are in `scripts/`:

### Main Entry Points
```bash
# Full triple comparison
python3 scripts/run_comparison.py

# Token-optimized benchmark
python3 scripts/run_optimized_benchmark.py

# LoRA pipeline
python3 scripts/run_lora_pipeline_fixed.py
```

### Examples & Testing
```bash
# RAG example
python3 scripts/rag_example.py

# Integration test
python3 scripts/integration_test.py

# Full system test
python3 scripts/comprehensive_test.py
```

## ✅ Test Execution

Run all tests:
```bash
pytest tests/
```

Run specific test:
```bash
pytest tests/test_rag_benchmark.py
```

## 🔧 Cleanup Done

### Deleted (Empty/Redundant)
- ✅ `run_lora_pipeline.py` (empty, 0 bytes)
- ✅ `requirements-lora.txt` (empty, 0 bytes)
- ✅ `integration_test_output.txt` (empty)
- ✅ `lora_output.log` (empty)
- ✅ `generation.log` (generated artifact)

### Moved to scripts/
- 13 demo/example/runner scripts (was cluttering root)

### Moved to tests/
- 6 test files (was cluttering root)

### Moved to docs/guides/
- 3 core technical guides (organized for reference)

### Archived to docs/archive/
- 40+ historical implementation reports and audit findings
- Preserved for reference but no longer in root

## 📝 .gitignore Updates

Updated to properly ignore:
- Generated artifacts: `data/cache/`, `data/logs/`, `*.log`
- Python artifacts: `__pycache__/`, `*.pyc`, `.venv/`
- OS files: `.DS_Store`, etc.
- IDE files: `.vscode/`, `.idea/`, etc.

Note: `docs/archive/` is committed to preserve historical records.

## 🎯 Best Practices Going Forward

1. **Core logic** stays in `src/` - no modification to structure
2. **New scripts** go to `scripts/` not root
3. **New tests** go to `tests/` not root
4. **New docs** go to `docs/guides/` for active use or `docs/archive/` for historical
5. **Generated data** goes to appropriate `data/` subdirectory
6. **Old reports/checklists** go to `docs/archive/`

## 📊 Metrics

- **Root files reduced**: 47 files → 3 files (README, QUICK_START, requirements)
- **Documentation organized**: 22,587 lines distributed across guides/ and archive/
- **Scripts organized**: 13 demo/runner scripts moved to scripts/
- **Tests organized**: 6 test files moved to tests/
- **Clutter reduction**: ~90% cleaner root directory

---

**Last Updated**: May 11, 2025  
**Status**: Repository cleanup complete. Structure is now clean and organized.
