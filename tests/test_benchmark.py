#!/usr/bin/env python3
"""Quick test of the benchmark script with minimal samples."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.benchmark_base import BasemodelBenchmark

print("Testing Base Model Benchmark Script...\n")

try:
    # Initialize benchmark
    benchmark = BasemodelBenchmark()
    
    # Run on just 2 samples to test
    print("\nRunning benchmark on 2 samples...")
    results = benchmark.run_benchmark(num_samples=2, rate_limit_delay=1.0)
    
    # Print summary
    benchmark.print_summary()
    
    # Print sample results
    benchmark.print_sample_results(num_samples=1)
    
    # Save results
    output_path = benchmark.save_results()
    
    print(f"✓ Test successful!")
    print(f"Results saved to: {output_path}")
    
except Exception as e:
    print(f"✗ Test failed: {str(e)}")
    import traceback
    traceback.print_exc()
