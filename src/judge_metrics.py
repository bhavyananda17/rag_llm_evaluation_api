#!/usr/bin/env python3
"""
Judge Metrics System for Triple Comparison Evaluation

This module implements an impartial judge that rates responses from Base, RAG,
and LoRA models on:
1. Accuracy - How correct is the answer?
2. Completeness - Does it cover all key points?
3. Hallucination - Does it invent facts not in context?

The judge uses a calibrated scoring system (1-5) and generates comprehensive
statistical reports suitable for professional visualization.
"""

import os
import sys
import json
import time
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.model_client import CachedGeminiClient


class JudgeMetrics:
    """
    Impartial judge for evaluating model responses.
    
    Uses Gemini with a specific system prompt to rate answers on:
    - Accuracy (1-5)
    - Completeness (1-5)
    - Hallucination penalty (-2 if invents facts)
    
    Generates structured scoring and statistical analysis.
    """
    
    def __init__(self, use_cache: bool = True):
        """
        Initialize the judge with Gemini client.
        
        Args:
            use_cache: Enable caching for judge evaluations
        """
        self.gemini_client = CachedGeminiClient(use_cache=use_cache)
        
        self.judge_prompt_template = """You are an impartial judge evaluating LLM responses.

GROUND TRUTH:
{ground_truth}

RESPONSE TO EVALUATE:
{response}

Rate this response on the following criteria (1-5 scale):

1. ACCURACY (1-5):
   1 = Completely wrong or contradicts ground truth
   2 = Mostly incorrect with some accurate elements
   3 = Partially correct, but misses key details
   4 = Mostly accurate with minor errors
   5 = Completely accurate and factually correct

2. COMPLETENESS (1-5):
   1 = Missing most key points
   2 = Covers less than 50% of important concepts
   3 = Covers about 50% of key points
   4 = Covers most key points with minor omissions
   5 = Comprehensive coverage of all key concepts

3. HALLUCINATION CHECK:
   Does this response invent facts or details NOT in the context?
   - If YES (invents facts): Apply -2 penalty to accuracy score
   - If NO (stays grounded): No penalty
   
   Also note: "Contains hallucination: YES/NO"

IMPORTANT: Respond ONLY with this exact JSON format, no other text:
{{
    "accuracy": <1-5 or accuracy-2 if hallucination>,
    "completeness": <1-5>,
    "hallucination_detected": <true/false>,
    "reasoning": "<brief explanation of scores>",
    "hallucination_examples": "<list any invented facts or null>"
}}"""
        
        self.scores = {
            'base': [],
            'rag': [],
            'lora': []
        }
        
        self.statistics = None
    
    def judge_response(self, 
                      ground_truth: str,
                      response: str,
                      question: str = "") -> Dict:
        """
        Judge a single response against ground truth.
        
        Args:
            ground_truth: The correct answer
            response: The response to evaluate
            question: The question (for context)
        
        Returns:
            Dictionary with scores and reasoning
        """
        # Build the prompt
        prompt = self.judge_prompt_template.format(
            ground_truth=ground_truth,
            response=response
        )
        
        try:
            # Get judge's evaluation
            raw_response = self.gemini_client.generate(prompt)
            
            # Parse JSON response
            import json
            
            # Extract JSON from response (handle cases where model adds extra text)
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = raw_response[json_start:json_end]
                score_dict = json.loads(json_str)
            else:
                # Fallback if JSON extraction fails
                score_dict = {
                    'accuracy': 2,
                    'completeness': 2,
                    'hallucination_detected': True,
                    'reasoning': 'Could not parse judge response',
                    'hallucination_examples': None
                }
            
            return {
                'accuracy': score_dict.get('accuracy', 2),
                'completeness': score_dict.get('completeness', 2),
                'hallucination_detected': score_dict.get('hallucination_detected', False),
                'reasoning': score_dict.get('reasoning', ''),
                'hallucination_examples': score_dict.get('hallucination_examples', None),
                'success': True
            }
        
        except Exception as e:
            print(f"  ⚠️  Judge error: {str(e)}")
            return {
                'accuracy': 2,
                'completeness': 2,
                'hallucination_detected': False,
                'reasoning': f'Judgment error: {str(e)}',
                'hallucination_examples': None,
                'success': False
            }
    
    def judge_comparison(self, comparison: Dict) -> Dict:
        """
        Judge all three responses in a comparison.
        
        Args:
            comparison: Dictionary with base/rag/lora responses
        
        Returns:
            Dictionary with scores for all three modes
        """
        ground_truth = comparison.get('ground_truth', '')
        question = comparison.get('question', '')
        
        results = {
            'question_id': comparison.get('question_id', 0),
            'question': question,
            'ground_truth': ground_truth,
            'source_file': comparison.get('source_file', ''),
            'difficulty': comparison.get('difficulty', ''),
            'scores': {}
        }
        
        # Judge each mode
        for mode in ['base', 'rag', 'lora']:
            if mode not in comparison:
                continue
            
            mode_data = comparison[mode]
            response = mode_data.get('response', '')
            
            # Skip if no response
            if not response or not mode_data.get('success', False):
                results['scores'][mode] = {
                    'accuracy': 0,
                    'completeness': 0,
                    'hallucination_detected': False,
                    'reasoning': 'No response generated',
                    'success': False
                }
                continue
            
            # Get judge scores
            score = self.judge_response(ground_truth, response, question)
            results['scores'][mode] = score
            self.scores[mode].append(score)
        
        return results
    
    def run_full_judgment(self, 
                         comparison_file: str = None,
                         output_file: str = None) -> Dict:
        """
        Run judgment on all comparisons.
        
        Args:
            comparison_file: Path to final_comparison.json
            output_file: Path to save judgment results
        
        Returns:
            Dictionary with all judgments and statistics
        """
        # Set default paths
        if comparison_file is None:
            comparison_file = os.path.join(
                Config.BASE_DIR, 
                "data/results/final_comparison.json"
            )
        
        if output_file is None:
            output_file = os.path.join(
                Config.BASE_DIR,
                "data/results/evaluation_report.json"
            )
        
        print("\n" + "="*70)
        print("JUDGE EVALUATION - RATING RESPONSES")
        print("="*70 + "\n")
        
        # Load comparisons
        print(f"Loading comparisons from {comparison_file}")
        with open(comparison_file, 'r') as f:
            comparison_data = json.load(f)
        
        comparisons = comparison_data.get('comparisons', [])
        print(f"✓ Loaded {len(comparisons)} comparisons\n")
        
        # Judge each comparison
        judgments = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'source_file': comparison_file,
                'total_questions': len(comparisons),
                'judge_model': self.gemini_client.model_name
            },
            'judgments': []
        }
        
        for idx, comparison in enumerate(comparisons, 1):
            print(f"[{idx}/{len(comparisons)}] Judging: {comparison.get('question', '')[:60]}...")
            
            judgment = self.judge_comparison(comparison)
            judgments['judgments'].append(judgment)
            
            # Show scores
            for mode in ['base', 'rag', 'lora']:
                if mode in judgment['scores']:
                    score = judgment['scores'][mode]
                    if score.get('success', False):
                        acc = score.get('accuracy', 0)
                        comp = score.get('completeness', 0)
                        hall = "✗ Hallucination" if score.get('hallucination_detected') else "✓ Grounded"
                        print(f"  {mode:>5}: Accuracy={acc}/5, Completeness={comp}/5, {hall}")
                    else:
                        print(f"  {mode:>5}: No response")
            print()
        
        # Calculate statistics
        print("\nCalculating aggregate statistics...")
        statistics = self._calculate_statistics(judgments)
        judgments['statistics'] = statistics
        
        # Save results
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(judgments, f, indent=2)
        
        print(f"✓ Judgments saved to {output_file}\n")
        
        self._print_statistics_summary(statistics)
        
        return judgments
    
    def _calculate_statistics(self, judgments: Dict) -> Dict:
        """Calculate aggregate statistics from judgments."""
        stats = {
            'by_mode': {},
            'hallucination_summary': {},
            'performance_ranking': []
        }
        
        # Aggregate by mode
        mode_stats = {
            'base': {'accuracy': [], 'completeness': []},
            'rag': {'accuracy': [], 'completeness': []},
            'lora': {'accuracy': [], 'completeness': []}
        }
        
        hallucinations = {
            'base': 0,
            'rag': 0,
            'lora': 0
        }
        
        grounded = {
            'base': 0,
            'rag': 0,
            'lora': 0
        }
        
        # Process each judgment
        for judgment in judgments.get('judgments', []):
            for mode in ['base', 'rag', 'lora']:
                if mode in judgment['scores']:
                    score = judgment['scores'][mode]
                    
                    if score.get('success', False):
                        acc = score.get('accuracy', 0)
                        comp = score.get('completeness', 0)
                        
                        if acc > 0:
                            mode_stats[mode]['accuracy'].append(acc)
                        if comp > 0:
                            mode_stats[mode]['completeness'].append(comp)
                        
                        if score.get('hallucination_detected', False):
                            hallucinations[mode] += 1
                        else:
                            grounded[mode] += 1
        
        # Calculate averages
        for mode in ['base', 'rag', 'lora']:
            accuracy_scores = mode_stats[mode]['accuracy']
            completeness_scores = mode_stats[mode]['completeness']
            
            avg_accuracy = (sum(accuracy_scores) / len(accuracy_scores) 
                          if accuracy_scores else 0)
            avg_completeness = (sum(completeness_scores) / len(completeness_scores)
                              if completeness_scores else 0)
            
            # Overall score (weighted average)
            overall = (avg_accuracy * 0.6 + avg_completeness * 0.4)
            
            stats['by_mode'][mode] = {
                'avg_accuracy': round(avg_accuracy, 2),
                'avg_completeness': round(avg_completeness, 2),
                'overall_score': round(overall, 2),
                'accuracy_count': len(accuracy_scores),
                'completeness_count': len(completeness_scores),
                'grounded_responses': grounded[mode],
                'hallucination_count': hallucinations[mode]
            }
        
        # Hallucination summary
        total_evals = sum(hallucinations.values()) + sum(grounded.values())
        for mode in ['base', 'rag', 'lora']:
            total_mode = hallucinations[mode] + grounded[mode]
            stats['hallucination_summary'][mode] = {
                'total_hallucinations': hallucinations[mode],
                'hallucination_rate': (hallucinations[mode] / total_mode 
                                     if total_mode > 0 else 0),
                'grounded_rate': (grounded[mode] / total_mode
                                if total_mode > 0 else 0)
            }
        
        # Ranking
        ranking = sorted(
            stats['by_mode'].items(),
            key=lambda x: x[1]['overall_score'],
            reverse=True
        )
        
        stats['performance_ranking'] = [
            {
                'rank': idx + 1,
                'mode': mode,
                'score': score['overall_score'],
                'accuracy': score['avg_accuracy'],
                'completeness': score['avg_completeness']
            }
            for idx, (mode, score) in enumerate(ranking)
        ]
        
        return stats
    
    def _print_statistics_summary(self, statistics: Dict):
        """Print formatted statistics summary."""
        print("="*70)
        print("JUDGE EVALUATION SUMMARY")
        print("="*70 + "\n")
        
        # Overall ranking
        print("PERFORMANCE RANKING:")
        print("-"*70)
        for rank_item in statistics['performance_ranking']:
            print(f"\n{rank_item['rank']}. {rank_item['mode'].upper()}")
            print(f"   Overall Score: {rank_item['score']:.2f}/5")
            print(f"   Accuracy:     {rank_item['accuracy']:.2f}/5")
            print(f"   Completeness: {rank_item['completeness']:.2f}/5")
        
        # Detailed stats
        print("\n\nDETAILED STATISTICS:")
        print("-"*70)
        
        for mode in ['base', 'rag', 'lora']:
            mode_stat = statistics['by_mode'][mode]
            hall_stat = statistics['hallucination_summary'][mode]
            
            print(f"\n{mode.upper()}:")
            print(f"  Accuracy:          {mode_stat['avg_accuracy']:.2f}/5 ({mode_stat['accuracy_count']} evals)")
            print(f"  Completeness:      {mode_stat['avg_completeness']:.2f}/5 ({mode_stat['completeness_count']} evals)")
            print(f"  Overall Score:     {mode_stat['overall_score']:.2f}/5")
            print(f"  Hallucinations:    {mode_stat['hallucination_count']}")
            print(f"  Hallucination Rate: {hall_stat['hallucination_rate']*100:.1f}%")
            print(f"  Grounded Rate:      {hall_stat['grounded_rate']*100:.1f}%")
        
        print("\n" + "="*70)
    
    def calculate_benchmarks(self, 
                            judgment_file: str = None,
                            output_file: str = None) -> Dict:
        """
        Calculate benchmark statistics and save report.
        
        Args:
            judgment_file: Path to evaluation_report.json
            output_file: Path to save benchmark summary
        
        Returns:
            Dictionary with benchmark statistics
        """
        # Set default paths
        if judgment_file is None:
            judgment_file = os.path.join(
                Config.BASE_DIR,
                "data/results/evaluation_report.json"
            )
        
        if output_file is None:
            output_file = os.path.join(
                Config.BASE_DIR,
                "data/results/benchmark_summary.csv"
            )
        
        print("\nCalculating benchmarks...")
        
        # Load judgments
        with open(judgment_file, 'r') as f:
            judgment_data = json.load(f)
        
        statistics = judgment_data.get('statistics', {})
        
        # Prepare CSV data
        csv_data = []
        
        # Header row
        csv_data.append([
            'Metric',
            'Base',
            'RAG',
            'LoRA'
        ])
        
        # Extract data from statistics
        by_mode = statistics.get('by_mode', {})
        
        csv_data.append([
            'Accuracy (avg)',
            f"{by_mode.get('base', {}).get('avg_accuracy', 0):.2f}",
            f"{by_mode.get('rag', {}).get('avg_accuracy', 0):.2f}",
            f"{by_mode.get('lora', {}).get('avg_accuracy', 0):.2f}"
        ])
        
        csv_data.append([
            'Completeness (avg)',
            f"{by_mode.get('base', {}).get('avg_completeness', 0):.2f}",
            f"{by_mode.get('rag', {}).get('avg_completeness', 0):.2f}",
            f"{by_mode.get('lora', {}).get('avg_completeness', 0):.2f}"
        ])
        
        csv_data.append([
            'Overall Score',
            f"{by_mode.get('base', {}).get('overall_score', 0):.2f}",
            f"{by_mode.get('rag', {}).get('overall_score', 0):.2f}",
            f"{by_mode.get('lora', {}).get('overall_score', 0):.2f}"
        ])
        
        csv_data.append([
            'Hallucinations',
            f"{by_mode.get('base', {}).get('hallucination_count', 0)}",
            f"{by_mode.get('rag', {}).get('hallucination_count', 0)}",
            f"{by_mode.get('lora', {}).get('hallucination_count', 0)}"
        ])
        
        hall_summary = statistics.get('hallucination_summary', {})
        
        csv_data.append([
            'Hallucination Rate (%)',
            f"{hall_summary.get('base', {}).get('hallucination_rate', 0)*100:.1f}",
            f"{hall_summary.get('rag', {}).get('hallucination_rate', 0)*100:.1f}",
            f"{hall_summary.get('lora', {}).get('hallucination_rate', 0)*100:.1f}"
        ])
        
        csv_data.append([
            'Grounded Rate (%)',
            f"{hall_summary.get('base', {}).get('grounded_rate', 0)*100:.1f}",
            f"{hall_summary.get('rag', {}).get('grounded_rate', 0)*100:.1f}",
            f"{hall_summary.get('lora', {}).get('grounded_rate', 0)*100:.1f}"
        ])
        
        # Save CSV
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
        
        print(f"✓ Benchmark summary saved to {output_file}\n")
        
        return {
            'csv_data': csv_data,
            'output_file': output_file
        }
    
    def export_for_visualization(self) -> Dict:
        """Export data in formats suitable for visualization tools."""
        visualization_data = {
            'timestamp': datetime.now().isoformat(),
            'formats': {}
        }
        
        # CSV format
        csv_file = os.path.join(
            Config.BASE_DIR,
            "data/results/benchmark_summary.csv"
        )
        
        if os.path.exists(csv_file):
            with open(csv_file, 'r') as f:
                visualization_data['formats']['csv'] = {
                    'file': csv_file,
                    'preview': f.read().split('\n')[:5]
                }
        
        # JSON format for web visualization
        report_file = os.path.join(
            Config.BASE_DIR,
            "data/results/evaluation_report.json"
        )
        
        if os.path.exists(report_file):
            with open(report_file, 'r') as f:
                report_data = json.load(f)
                visualization_data['formats']['json'] = {
                    'file': report_file,
                    'statistics': report_data.get('statistics', {})
                }
        
        return visualization_data


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Judge model responses and generate evaluation report"
    )
    
    parser.add_argument(
        '--comparison-file',
        type=str,
        default=None,
        help='Path to final_comparison.json'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to save evaluation_report.json'
    )
    
    parser.add_argument(
        '--skip-judge',
        action='store_true',
        help='Skip judging (only calculate benchmarks)'
    )
    
    args = parser.parse_args()
    
    try:
        judge = JudgeMetrics(use_cache=True)
        
        # Run judgment
        if not args.skip_judge:
            judgments = judge.run_full_judgment(
                comparison_file=args.comparison_file,
                output_file=args.output
            )
        
        # Calculate benchmarks and export
        benchmark_result = judge.calculate_benchmarks()
        visualization = judge.export_for_visualization()
        
        print("\n" + "="*70)
        print("JUDGMENT COMPLETE")
        print("="*70)
        print(f"\n✓ Evaluation Report: data/results/evaluation_report.json")
        print(f"✓ Benchmark Summary: data/results/benchmark_summary.csv")
        print(f"\nFiles ready for visualization in Excel or Python libraries")
        print("="*70 + "\n")
        
        return True
    
    except Exception as e:
        print(f"\n✗ Judgment failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
