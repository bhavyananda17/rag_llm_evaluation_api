# 🚀 Token Optimization Guide

## Overview

This guide explains how to efficiently use the RAG vs LoRA evaluation system while minimizing API token costs.

---

## 📊 Token Usage Breakdown

### Cost Estimates (for 13 questions)

| Benchmark | Avg Prompt | Avg Response | Tokens/Q | Total | Cost |
|-----------|-----------|-------------|----------|-------|------|
| **Base Model** | 100 words | 150 words | ~188 | ~2,444 | $0.0002 |
| **RAG Model** | 800 words | 200 words | ~600 | ~7,800 | $0.0006 |
| **Combined** | - | - | ~788 | ~10,244 | $0.0008 |

**Free Tier Daily Limit**: 1,000,000 tokens = ~1,300 full benchmarks

---

## 🎯 Optimization Strategies

### 1. **Response Caching** ✅ (Most Effective)

Identical questions use cached responses instead of API calls.

```python
from src.model_client import GeminiClient

# Initialize with caching enabled (default)
client = GeminiClient(use_cache=True)

# First call - hits API
response1 = client.generate("What is RAG?")  # API call

# Second call - uses cache
response2 = client.generate("What is RAG?")  # Instant, 0 tokens!

# Check cache effectiveness
stats = client.get_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']:.1f}%")
```

**Savings**: 50-80% on repeated evaluations

---

### 2. **Smart Sampling** ✅ (Balanced Approach)

Evaluate representative subset instead of all questions.

```python
from src.optimized_benchmark import OptimizedBenchmark

# Smart sampling: evaluates ~50% of questions
benchmark = OptimizedBenchmark(use_cache=True)
benchmark.run_base_benchmark()

# Or specify exact sample size
benchmark = OptimizedBenchmark(use_cache=True, sample_size=10)
benchmark.run_rag_benchmark()
```

**Savings**: 50% on question count = 50% tokens saved

---

### 3. **Prompt Optimization** ✅ (Always Active)

System automatically optimizes prompts:

```python
# Before optimization
prompt = "Answer the following question in detail with examples..."
# ~150 tokens

# After optimization
prompt = "Answer: What is RAG?"
# ~25 tokens
```

**Savings**: 30-40% per prompt

---

### 4. **Budget Tracking** ✅ (Real-Time Monitoring)

Monitor token usage before and during execution.

```python
from src.token_manager import TokenManager, estimate_benchmark_cost

# Check estimated cost
estimate_benchmark_cost(num_questions=13)

# During execution
manager = TokenManager()
budget = manager.check_budget(required_tokens=1000)
print(f"Remaining tokens: {budget['remaining']:,}")
print(f"Budget status: {budget['percentage_used']:.1f}% used")
```

---

## 📋 Quick Start Commands

### Option 1: Dry Run (No Tokens Used)
```bash
python src/optimized_benchmark.py
# Follow prompts, choose "n" when asked to proceed
```

### Option 2: Estimate Cost Only
```python
from src.token_manager import estimate_benchmark_cost
estimate_benchmark_cost(num_questions=13)
```

### Option 3: Run with Caching Enabled
```python
from src.optimized_benchmark import OptimizedBenchmark

benchmark = OptimizedBenchmark(use_cache=True, sample_size=10)
benchmark.run_base_benchmark(dry_run=False)
benchmark.run_rag_benchmark(dry_run=False)
benchmark.save_results()
benchmark.print_summary()
```

### Option 4: Check Token Usage
```python
from src.token_manager import TokenManager

manager = TokenManager()
print(manager.check_budget())
manager.print_session_report()
```

---

## 🔍 Detailed Components

### Token Manager (`src/token_manager.py`)

**Features**:
- Token estimation before API calls
- Daily budget tracking
- Cost calculation
- Usage logging
- Session reports

**Key Methods**:
```python
manager = TokenManager(daily_budget=1_000_000)

# Estimate single request
estimate = manager.estimate_request("Your prompt", expected_response_length=150)

# Estimate entire benchmark
benchmark_est = manager.estimate_benchmark(
    num_questions=13,
    avg_prompt_length=800,
    avg_response_length=200
)

# Check remaining budget
budget = manager.check_budget(required_tokens=5000)

# Log actual usage
manager.log_request(input_tokens=100, output_tokens=75)

# Save and report
manager.save_usage_log()
manager.print_session_report()
```

---

### Cached Gemini Client (`src/model_client.py`)

**Features**:
- Response caching to disk
- Token estimation before API calls
- Budget enforcement
- Backward compatible with original API

**Key Methods**:
```python
from src.model_client import GeminiClient

client = GeminiClient(use_cache=True, cache_dir="data/cache")

# Generate response (uses cache if available)
response = client.generate(prompt)

# Override cache for specific call
response = client.generate(prompt, use_cache=False)

# Get statistics
stats = client.get_stats()
client.print_stats()
```

---

### Optimized Benchmark (`src/optimized_benchmark.py`)

**Features**:
- Cost estimation before execution
- Smart sampling
- Batch processing
- Real-time token monitoring
- Comprehensive error handling

**Key Methods**:
```python
from src.optimized_benchmark import OptimizedBenchmark

benchmark = OptimizedBenchmark(use_cache=True, sample_size=10)

# Run benchmarks (dry run estimates cost, actual run executes)
benchmark.run_base_benchmark(dry_run=True)   # Estimates only
benchmark.run_base_benchmark(dry_run=False)  # Executes

# Save results
files = benchmark.save_results()

# Print summary
benchmark.print_summary()
```

---

## 💰 Cost Comparison

### Daily Usage Scenarios

| Scenario | Questions | Method | Tokens | Cost | Status |
|----------|-----------|--------|--------|------|--------|
| Small test | 5 | Full | ~3,940 | $0.0003 | ✓ Cheap |
| Medium test | 10 | Cached | ~1,970 | $0.0001 | ✓ Very cheap |
| Full benchmark | 13 | Full | ~10,244 | $0.0008 | ✓ Free tier ok |
| Full benchmark | 13 | Cached | ~5,122 | $0.0004 | ✓ Optimal |

---

## 📈 Optimization Checklist

- [x] Enable response caching by default
- [x] Implement smart sampling for large datasets
- [x] Optimize prompt templates to reduce verbosity
- [x] Track budget before execution
- [x] Log all token usage
- [x] Provide cost estimates
- [x] Implement rate limiting (0.5-2s between calls)
- [x] Handle quota errors gracefully
- [x] Cache successful responses
- [x] Monitor cache hit rates

---

## 🚨 Quota Management

### When You Hit 429 Quota Error:

1. **Check remaining budget**:
```python
from src.token_manager import TokenManager
manager = TokenManager()
print(manager.check_budget())
```

2. **Switch to cached/sampled mode**:
```python
benchmark = OptimizedBenchmark(use_cache=True, sample_size=5)
```

3. **Wait for daily reset** (UTC midnight):
- Free tier quota resets every 24 hours
- Check at: https://console.cloud.google.com

4. **Use a different API key**:
- Get new Google account
- Generate new API key
- Update `.env` file

---

## 📊 Monitoring Dashboard

### Real-Time Metrics

```python
from src.token_manager import TokenManager

manager = TokenManager()

# Daily stats
daily_stats = manager.check_budget()
print(f"""
DAILY TOKEN USAGE
================
Budget: {daily_stats['daily_budget']:,} tokens
Used: {daily_stats['used_today']:,} ({daily_stats['percentage_used']:.1f}%)
Remaining: {daily_stats['remaining']:,} tokens
Can proceed: {'Yes' if daily_stats['can_proceed'] else 'No'}
""")

# Session stats
session = manager.get_session_summary()
print(f"""
SESSION STATS
=============
Duration: {session['duration_seconds']:.1f}s
Requests: {session['requests']}
Tokens: {session['total_tokens']:,}
Avg/Request: {session['tokens_per_request']:.0f}
Rate: {session['requests_per_minute']:.2f} req/min
""")
```

---

## 🎓 Best Practices

### 1. **Always Estimate First**
```python
benchmark = OptimizedBenchmark(use_cache=True, sample_size=10)
benchmark.run_base_benchmark(dry_run=True)  # See cost first
```

### 2. **Use Small Batches During Development**
```python
benchmark = OptimizedBenchmark(use_cache=True, sample_size=5)
# Test with 5 questions first, then scale up
```

### 3. **Enable Caching for Reproducibility**
```python
client = GeminiClient(use_cache=True)
# Run same benchmarks again = instant results, 0 tokens
```

### 4. **Monitor Cache Hit Rate**
```python
stats = client.get_stats()
if stats['cache_hit_rate'] < 20:
    print("Low cache hit rate - consider more similar questions")
```

### 5. **Schedule Benchmarks During Off-Peak**
- Run full benchmarks when you don't have quota urgency
- Use dry runs to plan ahead

---

## 🔗 Related Resources

- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Free Tier Information](https://ai.google.dev/tutorials/setup)

---

## 📞 Troubleshooting

### Q: "Quota exceeded" error after first question?
**A**: Your API key's daily quota is exhausted. Use a different account or wait for reset.

### Q: Low cache hit rate?
**A**: Cache only works for identical prompts. Use optimization tips to make prompts more similar.

### Q: Benchmarks running slowly?
**A**: Rate limiting is active (0.5s between calls). This is intentional to respect quotas.

### Q: How to use different models?
**A**: Edit `src/model_client.py` - change `self.model_name` to 'gemini-pro' or other available models.

---

## 📝 Summary

With these optimizations, you can:
- ✅ Run full benchmarks for **$0.0008** (free tier)
- ✅ Cache responses for **zero token cost** on repeats
- ✅ Sample intelligently to **save 50% tokens**
- ✅ Track budget in **real-time**
- ✅ Estimate costs **before execution**

**Total potential savings: 70-80% reduction in token usage compared to unoptimized approach.**
