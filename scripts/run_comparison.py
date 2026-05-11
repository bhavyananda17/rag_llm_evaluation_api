#!/usr/bin/env python3
"""
Triple Comparison Evaluation Runner

Executes the full evaluation pipeline comparing:
1. Base: Direct Gemini API calls
2. RAG: Gemini API with vector store context
3. LoRA: Local inference with LoRA-adapted model

Usage:
    python3 run_comparison.py [options]

Options:
    --with-lora        Include LoRA mode (requires trained adapters)
    --output FILE      Custom output file path
    --qa-file FILE     Custom QA file path
    --skip-rag         Skip RAG mode (no vector store required)
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.evaluator import ModelEvaluator


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run triple comparison evaluation (Base vs RAG vs LoRA)"
    )
    
    parser.add_argument(
        '--with-lora',
        action='store_true',
        help='Include LoRA mode (requires trained adapters)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Custom output file path'
    )
    
    parser.add_argument(
        '--qa-file',
        type=str,
        default=None,
        help='Custom QA file path'
    )
    
    parser.add_argument(
        '--skip-rag',
        action='store_true',
        help='Skip RAG mode'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    return parser.parse_args()


def print_header(title):
    """Print formatted header."""
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70 + "\n")


def verify_prerequisites(args):
    """Verify all prerequisites are in place."""
    print_header("PREREQUISITE VERIFICATION")
    
    checks_passed = True
    
    # Check QA file
    qa_file = args.qa_file or os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
    if os.path.exists(qa_file):
        with open(qa_file) as f:
            qa_data = json.load(f)
            qa_count = len(qa_data.get('qa_pairs', []))
        print(f"✓ QA file found: {qa_count} pairs")
    else:
        print(f"✗ QA file not found: {qa_file}")
        checks_passed = False
    
    # Check vector store if not skipping RAG
    if not args.skip_rag:
        vector_index = os.path.join(Config.PROCESSED_DATA, "vector_index.faiss")
        if os.path.exists(vector_index):
            print(f"✓ Vector store index found")
        else:
            print(f"✗ Vector store index not found (RAG mode will be skipped)")
    
    # Check LoRA adapter if including LoRA mode
    if args.with_lora:
        lora_path = os.path.join(Config.BASE_DIR, "models/lora_adapters")
        if os.path.exists(os.path.join(lora_path, "adapter_config.json")):
            print(f"✓ LoRA adapters found")
        else:
            print(f"✗ LoRA adapters not found (LoRA mode will be skipped)")
    
    # Check Gemini API key
    if Config.API_KEY:
        print(f"✓ Gemini API key configured")
    else:
        print(f"✗ Gemini API key not found")
        checks_passed = False
    
    print()
    return checks_passed


def main():
    """Main execution."""
    args = parse_arguments()
    
    print_header("TRIPLE COMPARISON EVALUATION")
    
    # Verify prerequisites
    if not verify_prerequisites(args):
        print("✗ Prerequisites check failed. Please resolve issues above.")
        return False
    
    # Determine paths
    qa_file = args.qa_file or os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
    output_file = args.output or os.path.join(Config.BASE_DIR, "data/results/final_comparison.json")
    
    lora_path = os.path.join(Config.BASE_DIR, "models/lora_adapters") if args.with_lora else None
    vector_store_path = os.path.join(Config.PROCESSED_DATA, "vector_index.faiss") if not args.skip_rag else None
    
    # Create evaluator
    print("Initializing evaluator...")
    evaluator = ModelEvaluator(
        use_cache=True,
        lora_adapter_path=lora_path,
        vector_store_index=vector_store_path
    )
    
    # Run evaluation
    try:
        results = evaluator.run_full_comparison(
            qa_file=qa_file,
            output_file=output_file
        )
        
        print("\n" + "="*70)
        print("EVALUATION SUMMARY")
        print("="*70 + "\n")
        
        # Print file location
        print(f"Results saved to:")
        print(f"  {output_file}\n")
        
        # Print quick statistics
        stats = results.get('statistics', {})
        print("Mode Comparison:")
        print(f"  Base:  {stats['base']['successful']}/{results['metadata']['total_questions']} successful - "
              f"{stats['base']['avg_latency']:.3f}s avg latency")
        print(f"  RAG:   {stats['rag']['successful']}/{results['metadata']['total_questions']} successful - "
              f"{stats['rag']['avg_latency']:.3f}s avg latency")
        print(f"  LoRA:  {stats['lora']['successful']}/{results['metadata']['total_questions']} successful - "
              f"{stats['lora']['avg_latency']:.3f}s avg latency")
        
        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)
        print("\n1. Analyze responses in final_comparison.json")
        print("2. Compare quality and latency across modes")
        print("3. Run evaluation_metrics.py for detailed metrics")
        print("4. Generate comparison report\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
