#!/usr/bin/env python3
"""
Quick reference for running all three benchmarks.
"""

print("""
╔════════════════════════════════════════════════════════════════════╗
║      RAG vs LoRA Evaluation: Complete Benchmarking System          ║
╚════════════════════════════════════════════════════════════════════╝

📊 THREE-TIER EVALUATION SYSTEM
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│ 1. BASE MODEL BENCHMARK (src/benchmark_base.py)                 │
├─────────────────────────────────────────────────────────────────┤
│ • Evaluates LLM on QA pairs WITHOUT any additional context      │
│ • Pure model knowledge test                                      │
│ • Output: data/results/base_model_results.json                  │
│                                                                  │
│ Usage:  python3 src/benchmark_base.py                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 2. RAG MODEL BENCHMARK (src/benchmark_rag.py)                   │
├─────────────────────────────────────────────────────────────────┤
│ • Evaluates LLM WITH Retrieval-Augmented Generation             │
│ • Uses FAISS vector store for context retrieval                │
│ • Helper functions:                                             │
│   - format_context(): Labels retrieved chunks by source         │
│   - construct_augmented_prompt(): Combines context + question  │
│ • Error Handling: Detects 429 quota errors, retries after 60s  │
│ • Output: data/results/rag_model_results.json                  │
│                                                                  │
│ Usage:  python3 src/benchmark_rag.py                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 3. LORA MODEL BENCHMARK (Planned)                               │
├─────────────────────────────────────────────────────────────────┤
│ • Evaluates LoRA-fine-tuned model on QA pairs                  │
│ • Tests parameter-efficient fine-tuning effectiveness           │
│ • Output: data/results/lora_model_results.json                 │
│                                                                  │
│ Usage:  python3 src/benchmark_lora.py (Coming soon)            │
└─────────────────────────────────────────────────────────────────┘

📈 COMPARISON ANALYSIS
═════════════════════════════════════════════════════════════════

                  Base Model    RAG Model     LoRA Model
Context           ❌ None       ✅ Retrieved  ✅ Fine-tuned
Grounding         Low           High          Medium
Hallucinations    High          Low           Medium
Speed             Fast          Slower        Fast
Cost              Low           Medium        High
Customization     Global        Per-query     Per-domain

🎯 EVALUATION METRICS
═════════════════════════════════════════════════════════════════

For each benchmark, the following are captured:

✓ Question                    - Input question to model
✓ Ground Truth               - Expected answer from dataset
✓ Model Response             - Model's actual response
✓ Source File                - Document the question came from
✓ Difficulty                 - Question difficulty (Hard)
✓ Retrieved Context (RAG)    - Chunks retrieved from vector store
✓ Similarity Scores (RAG)    - Relevance scores for retrieved chunks
✓ Success/Error Status       - Completion status

📁 DATA FLOW
═════════════════════════════════════════════════════════════════

raw documents (8 files)
          ↓
[src/generate_data.py] → synthetic_qa.json (13 QA pairs)
          ↓
[src/build_index.py] → vector_index.faiss (FAISS embeddings)
          ↓
    ┌────────────────────────────────┐
    ↓                                ↓
[benchmark_base.py]         [benchmark_rag.py]
         ↓                            ↓
base_model_results.json      rag_model_results.json

🚀 QUICK START GUIDE
═════════════════════════════════════════════════════════════════

# Step 1: Generate QA Dataset (if not already done)
python3 src/generate_data.py

# Step 2: Build Vector Index (if not already done)
python3 src/build_index.py

# Step 3: Run Base Model Benchmark
python3 src/benchmark_base.py
→ Saves to: data/results/base_model_results.json

# Step 4: Run RAG Model Benchmark
python3 src/benchmark_rag.py
→ Saves to: data/results/rag_model_results.json

# Step 5: Compare Results
python3 scripts/compare_benchmarks.py (coming soon)

⚙️ CONFIGURATION
═════════════════════════════════════════════════════════════════

# Rate Limiting (between API calls)
BASE_MODEL:   2 seconds
RAG_MODEL:    2 seconds + retrieval time

# Quota Error Handling (429 errors)
RETRY_DELAY:  60 seconds
MAX_RETRIES:  3 attempts

# Vector Retrieval
TOP_K:        3 (retrieve top-3 most similar chunks)
EMBEDDING:    all-MiniLM-L6-v2 (384-dim embeddings)

# Chunk Settings
CHUNK_SIZE:   500 tokens
CHUNK_OVERLAP: 100 tokens

✅ VERIFICATION CHECKLIST
═════════════════════════════════════════════════════════════════

Before running benchmarks, verify:

□ src/benchmark_base.py        - Base model benchmark script
□ src/benchmark_rag.py         - RAG model benchmark script
□ src/vector_db.py             - FAISS vector store implementation
□ src/generate_data.py         - QA dataset generation
□ data/processed/synthetic_qa.json         - QA dataset (13 pairs)
□ data/processed/vector_index.faiss        - Vector index
□ data/processed/vector_index_metadata.json - Index metadata

📊 EXPECTED OUTPUT FILES
═════════════════════════════════════════════════════════════════

After running benchmarks:

data/results/
├── base_model_results.json      - Base model evaluation results
│   ├── metadata (model, total_questions, success_rate)
│   ├── results (13 Q&A pairs with base model responses)
│   └── errors (any failed evaluations)
│
└── rag_model_results.json       - RAG model evaluation results
    ├── metadata (model, dataset, total_questions)
    ├── retrieval_statistics (avg_similarity, success_rate)
    ├── results (13 Q&A pairs with RAG responses + context)
    └── errors (any failed evaluations)

🔍 KEY DIFFERENCES IN OUTPUT
═════════════════════════════════════════════════════════════════

Base Model Results:
{
  "base_model_response": "model's answer without context",
  "source_file": "attention_mechanism.txt"
}

RAG Model Results:
{
  "rag_response": "model's answer with retrieved context",
  "retrieved_context_count": 3,
  "retrieved_sources": ["file1.txt", "file2.txt", "file3.txt"],
  "avg_retrieval_score": 0.92
}

💡 ANALYSIS TIPS
═════════════════════════════════════════════════════════════════

1. Compare response lengths:
   - RAG responses might be longer (using more context)
   - Base model might be shorter (limited knowledge)

2. Check retrieval effectiveness:
   - High similarity scores (>0.8) indicate good matches
   - Retrieved sources matching original source = success

3. Analyze error patterns:
   - 429 errors: API quota exceeded (wait and retry)
   - Other errors: Check network/API key

4. Evaluate answer quality:
   - Factual correctness vs ground truth
   - Relevance to question
   - Grounding in retrieved context (RAG)

📝 NOTES
═════════════════════════════════════════════════════════════════

- All benchmarks use the same 13 QA pairs for fair comparison
- Results include timestamps for tracking execution history
- Error logging preserves detailed error messages for debugging
- Rate limiting prevents API quota exhaustion
- Vector store enables real-time retrieval with precomputed embeddings

🎓 RELATED DOCUMENTATION
═════════════════════════════════════════════════════════════════

- QA_GENERATION_GUIDE.md     - How QA pairs are generated
- VECTOR_STORE_SUMMARY.md    - FAISS vector store details
- BENCHMARKING_GUIDE.md      - Comprehensive benchmarking guide

Last Updated: March 31, 2026
Status: Production Ready ✓
""")
