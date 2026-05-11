#!/usr/bin/env python3
"""
Evaluation Metrics Analysis

Analyzes the final_comparison.json results and generates:
1. Quality metrics (response length, diversity)
2. Latency comparison
3. Success rate analysis
4. Statistical summaries
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import statistics

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config


class EvaluationMetrics:
    """Analyze comparison results and generate metrics."""
    
    def __init__(self, results_file: str = None):
        """
        Initialize with results file.
        
        Args:
            results_file: Path to final_comparison.json
        """
        if results_file is None:
            results_file = os.path.join(Config.BASE_DIR, "data/results/final_comparison.json")
        
        self.results_file = results_file
        self.results = None
        self.metrics = {}
        
        self._load_results()
    
    def _load_results(self):
        """Load results from file."""
        if not os.path.exists(self.results_file):
            raise FileNotFoundError(f"Results file not found: {self.results_file}")
        
        with open(self.results_file, 'r') as f:
            self.results = json.load(f)
        
        print(f"✓ Loaded {len(self.results['comparisons'])} comparisons")
    
    def analyze_latency(self) -> Dict:
        """Analyze latency metrics."""
        latency_metrics = {
            'base': [],
            'rag': [],
            'lora': []
        }
        
        for comparison in self.results['comparisons']:
            if comparison['base']['success']:
                latency_metrics['base'].append(comparison['base']['latency'])
            
            if comparison['rag']['success']:
                latency_metrics['rag'].append(comparison['rag']['latency'])
            
            if comparison['lora']['success']:
                latency_metrics['lora'].append(comparison['lora']['latency'])
        
        # Calculate statistics
        stats = {}
        for mode, latencies in latency_metrics.items():
            if latencies:
                stats[mode] = {
                    'count': len(latencies),
                    'min': min(latencies),
                    'max': max(latencies),
                    'mean': statistics.mean(latencies),
                    'median': statistics.median(latencies),
                    'stdev': statistics.stdev(latencies) if len(latencies) > 1 else 0,
                }
            else:
                stats[mode] = {
                    'count': 0,
                    'min': 0,
                    'max': 0,
                    'mean': 0,
                    'median': 0,
                    'stdev': 0,
                }
        
        return stats
    
    def analyze_response_quality(self) -> Dict:
        """Analyze response quality metrics."""
        quality_metrics = {
            'base': [],
            'rag': [],
            'lora': []
        }
        
        for comparison in self.results['comparisons']:
            for mode in ['base', 'rag', 'lora']:
                response = comparison[mode].get('response', '')
                if response:
                    quality_metrics[mode].append({
                        'length': len(response),
                        'word_count': len(response.split()),
                        'has_answer': len(response) > 10,
                    })
        
        # Calculate statistics
        stats = {}
        for mode, responses in quality_metrics.items():
            if responses:
                lengths = [r['length'] for r in responses]
                words = [r['word_count'] for r in responses]
                
                stats[mode] = {
                    'valid_responses': len(responses),
                    'avg_length': statistics.mean(lengths),
                    'avg_words': statistics.mean(words),
                    'min_length': min(lengths),
                    'max_length': max(lengths),
                }
            else:
                stats[mode] = {
                    'valid_responses': 0,
                    'avg_length': 0,
                    'avg_words': 0,
                    'min_length': 0,
                    'max_length': 0,
                }
        
        return stats
    
    def analyze_success_rates(self) -> Dict:
        """Analyze success rates by mode."""
        total = len(self.results['comparisons'])
        
        stats = {
            'total_questions': total,
        }
        
        for mode in ['base', 'rag', 'lora']:
            successful = sum(1 for c in self.results['comparisons'] if c[mode]['success'])
            stats[mode] = {
                'successful': successful,
                'failed': total - successful,
                'success_rate': successful / total if total > 0 else 0,
            }
        
        return stats
    
    def analyze_by_difficulty(self) -> Dict:
        """Analyze performance by question difficulty."""
        difficulties = {}
        
        for comparison in self.results['comparisons']:
            difficulty = comparison.get('difficulty', 'unknown')
            
            if difficulty not in difficulties:
                difficulties[difficulty] = {
                    'count': 0,
                    'base_success': 0,
                    'rag_success': 0,
                    'lora_success': 0,
                }
            
            difficulties[difficulty]['count'] += 1
            
            if comparison['base']['success']:
                difficulties[difficulty]['base_success'] += 1
            if comparison['rag']['success']:
                difficulties[difficulty]['rag_success'] += 1
            if comparison['lora']['success']:
                difficulties[difficulty]['lora_success'] += 1
        
        # Calculate percentages
        for difficulty in difficulties:
            count = difficulties[difficulty]['count']
            difficulties[difficulty]['base_rate'] = difficulties[difficulty]['base_success'] / count if count > 0 else 0
            difficulties[difficulty]['rag_rate'] = difficulties[difficulty]['rag_success'] / count if count > 0 else 0
            difficulties[difficulty]['lora_rate'] = difficulties[difficulty]['lora_success'] / count if count > 0 else 0
        
        return difficulties
    
    def generate_report(self) -> Dict:
        """Generate comprehensive metrics report."""
        print("\nAnalyzing results...\n")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'source_file': self.results_file,
            'latency_analysis': self.analyze_latency(),
            'quality_analysis': self.analyze_response_quality(),
            'success_analysis': self.analyze_success_rates(),
            'difficulty_analysis': self.analyze_by_difficulty(),
        }
        
        self.metrics = report
        return report
    
    def save_report(self, output_file: str = None):
        """Save metrics report to file."""
        if output_file is None:
            output_file = os.path.join(
                Config.BASE_DIR,
                "data/results/evaluation_metrics.json"
            )
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"✓ Metrics saved to {output_file}")
        return output_file
    
    def print_summary(self):
        """Print formatted summary of metrics."""
        print("\n" + "="*70)
        print("EVALUATION METRICS SUMMARY")
        print("="*70 + "\n")
        
        # Latency Summary
        print("LATENCY ANALYSIS (seconds):")
        print("-" * 70)
        latency = self.metrics['latency_analysis']
        
        for mode in ['base', 'rag', 'lora']:
            stats = latency[mode]
            if stats['count'] > 0:
                print(f"\n{mode.upper()}:")
                print(f"  Samples:    {stats['count']}")
                print(f"  Min:        {stats['min']:.4f}s")
                print(f"  Max:        {stats['max']:.4f}s")
                print(f"  Mean:       {stats['mean']:.4f}s")
                print(f"  Median:     {stats['median']:.4f}s")
                print(f"  Std Dev:    {stats['stdev']:.4f}s")
        
        # Success Rate Summary
        print("\n\nSUCCESS RATE ANALYSIS:")
        print("-" * 70)
        success = self.metrics['success_analysis']
        
        for mode in ['base', 'rag', 'lora']:
            stats = success[mode]
            rate = stats['success_rate'] * 100
            print(f"\n{mode.upper()}:")
            print(f"  Success:    {stats['successful']}/{success['total_questions']}")
            print(f"  Rate:       {rate:.1f}%")
            print(f"  Failed:     {stats['failed']}")
        
        # Quality Summary
        print("\n\nRESPONSE QUALITY ANALYSIS:")
        print("-" * 70)
        quality = self.metrics['quality_analysis']
        
        for mode in ['base', 'rag', 'lora']:
            stats = quality[mode]
            if stats['valid_responses'] > 0:
                print(f"\n{mode.upper()}:")
                print(f"  Valid Responses: {stats['valid_responses']}")
                print(f"  Avg Length:      {stats['avg_length']:.0f} chars")
                print(f"  Avg Words:       {stats['avg_words']:.0f}")
                print(f"  Length Range:    {stats['min_length']}-{stats['max_length']} chars")
        
        # Difficulty Analysis
        print("\n\nPERFORMANCE BY DIFFICULTY:")
        print("-" * 70)
        difficulty = self.metrics['difficulty_analysis']
        
        for diff, stats in sorted(difficulty.items()):
            print(f"\n{diff.upper()} ({stats['count']} questions):")
            print(f"  Base:  {stats['base_success']}/{stats['count']} ({stats['base_rate']*100:.1f}%)")
            print(f"  RAG:   {stats['rag_success']}/{stats['count']} ({stats['rag_rate']*100:.1f}%)")
            print(f"  LoRA:  {stats['lora_success']}/{stats['count']} ({stats['lora_rate']*100:.1f}%)")
        
        print("\n" + "="*70 + "\n")


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze evaluation metrics")
    parser.add_argument(
        '--results',
        type=str,
        default=None,
        help='Path to final_comparison.json'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to save metrics report'
    )
    
    args = parser.parse_args()
    
    try:
        # Create analyzer
        analyzer = EvaluationMetrics(results_file=args.results)
        
        # Generate report
        analyzer.generate_report()
        
        # Save report
        analyzer.save_report(output_file=args.output)
        
        # Print summary
        analyzer.print_summary()
        
        print("✓ Analysis complete!")
        return True
        
    except Exception as e:
        print(f"✗ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
