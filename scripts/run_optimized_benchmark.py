#!/usr/bin/env python3
"""
Simple Optimized Benchmark Runner

Demonstrates how to run benchmarks with token optimization.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_manager import estimate_benchmark_cost, TokenManager
from src.optimized_benchmark import OptimizedBenchmark


def print_intro():
    """Print introduction and menu."""
    print("\n" + "="*70)
    print("RAG vs LoRA EVALUATION SYSTEM - Token Optimized")
    print("="*70)
    print("\nThis system is designed to evaluate language models efficiently.")
    print("All API calls are cached and token usage is tracked in real-time.\n")


def menu():
    """Display menu and get user choice."""
    print("="*70)
    print("MAIN MENU")
    print("="*70)
    print("\n1. Estimate benchmark cost (no tokens used)")
    print("2. Run base model benchmark (optimized)")
    print("3. Run RAG model benchmark (optimized)")
    print("4. Check current token budget")
    print("5. Run both benchmarks")
    print("6. Exit")
    
    choice = input("\nSelect option (1-6): ").strip()
    return choice


def option_1():
    """Estimate benchmark cost."""
    print("\n" + "="*70)
    print("COST ESTIMATION")
    print("="*70)
    
    try:
        num_questions = int(input("Number of questions to estimate (default 13): ") or "13")
    except ValueError:
        num_questions = 13
    
    estimate_benchmark_cost(num_questions=num_questions)


def option_2():
    """Run base model benchmark."""
    print("\n" + "="*70)
    print("BASE MODEL BENCHMARK")
    print("="*70)
    
    try:
        sample_size = int(input("Number of questions to evaluate (default 5): ") or "5")
    except ValueError:
        sample_size = 5
    
    benchmark = OptimizedBenchmark(use_cache=True, sample_size=sample_size)
    
    # Estimate
    estimate = benchmark._estimate_total_cost("base")
    print(f"\nEstimated tokens: {estimate['total_tokens']:,}")
    print(f"Estimated cost: ${estimate['estimated_cost_usd']:.4f}")
    
    response = input("\nProceed? (y/n): ").strip().lower()
    if response == 'y':
        benchmark.run_base_benchmark(dry_run=False)
        benchmark.save_results()
        benchmark.print_summary()
    else:
        print("Cancelled.")


def option_3():
    """Run RAG model benchmark."""
    print("\n" + "="*70)
    print("RAG MODEL BENCHMARK")
    print("="*70)
    
    try:
        sample_size = int(input("Number of questions to evaluate (default 5): ") or "5")
    except ValueError:
        sample_size = 5
    
    benchmark = OptimizedBenchmark(use_cache=True, sample_size=sample_size)
    
    # Estimate
    estimate = benchmark._estimate_total_cost("rag")
    print(f"\nEstimated tokens: {estimate['total_tokens']:,}")
    print(f"Estimated cost: ${estimate['estimated_cost_usd']:.4f}")
    
    response = input("\nProceed? (y/n): ").strip().lower()
    if response == 'y':
        benchmark.run_rag_benchmark(dry_run=False)
        benchmark.save_results()
        benchmark.print_summary()
    else:
        print("Cancelled.")


def option_4():
    """Check token budget."""
    print("\n" + "="*70)
    print("TOKEN BUDGET STATUS")
    print("="*70)
    
    manager = TokenManager()
    budget = manager.check_budget()
    
    print(f"\nDaily Budget: {budget['daily_budget']:,} tokens")
    print(f"Used: {budget['used_today']:,} tokens ({budget['percentage_used']:.1f}%)")
    print(f"Remaining: {budget['remaining']:,} tokens")
    print(f"Status: {'✓ Can proceed' if budget['can_proceed'] else '✗ Budget exceeded'}")
    
    # Session stats if available
    session = manager.get_session_summary()
    if session['requests'] > 0:
        print(f"\nSession Stats:")
        print(f"  Requests: {session['requests']}")
        print(f"  Total Tokens: {session['total_tokens']:,}")
        print(f"  Avg per Request: {session['tokens_per_request']:.0f}")


def option_5():
    """Run both benchmarks."""
    print("\n" + "="*70)
    print("RUNNING BASE + RAG BENCHMARKS")
    print("="*70)
    
    try:
        sample_size = int(input("Number of questions for each (default 5): ") or "5")
    except ValueError:
        sample_size = 5
    
    benchmark = OptimizedBenchmark(use_cache=True, sample_size=sample_size)
    
    # Estimate combined cost
    base_est = benchmark._estimate_total_cost("base")
    rag_est = benchmark._estimate_total_cost("rag")
    total_tokens = base_est['total_tokens'] + rag_est['total_tokens']
    total_cost = base_est['estimated_cost_usd'] + rag_est['estimated_cost_usd']
    
    print(f"\nBase Model: {base_est['total_tokens']:,} tokens (${base_est['estimated_cost_usd']:.4f})")
    print(f"RAG Model: {rag_est['total_tokens']:,} tokens (${rag_est['estimated_cost_usd']:.4f})")
    print(f"Total: {total_tokens:,} tokens (${total_cost:.4f})")
    
    response = input("\nProceed? (y/n): ").strip().lower()
    if response == 'y':
        print("\n1. Running Base Model Benchmark...")
        benchmark.run_base_benchmark(dry_run=False)
        
        print("\n2. Running RAG Model Benchmark...")
        benchmark.run_rag_benchmark(dry_run=False)
        
        # Save and print
        benchmark.save_results()
        benchmark.print_summary()
    else:
        print("Cancelled.")


def main():
    """Main loop."""
    print_intro()
    
    while True:
        choice = menu()
        
        if choice == '1':
            option_1()
        elif choice == '2':
            option_2()
        elif choice == '3':
            option_3()
        elif choice == '4':
            option_4()
        elif choice == '5':
            option_5()
        elif choice == '6':
            print("\nExiting. Goodbye!\n")
            break
        else:
            print("\n✗ Invalid choice. Please select 1-6.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!\n")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
