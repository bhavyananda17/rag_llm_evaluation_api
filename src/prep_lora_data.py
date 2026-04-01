#!/usr/bin/env python3
"""
LORA Dataset Preparation Script

Converts synthetic QA pairs into Alpaca-style instruction-tuning format
optimized for PEFT/TRL fine-tuning with token budgeting.

Features:
- Loads 13 golden QA pairs from synthetic_qa.json
- Converts to Alpaca format (instruction, input, output)
- Integrates token optimization (max 1024 tokens per example)
- Validates and truncates if needed
- Generates JSONL training manifest
- Detailed logging and statistics
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.token_manager import TokenManager


class LoRADataFormatter:
    """Format QA pairs into supervised fine-tuning (SFT) format for LoRA."""
    
    # Max tokens per training example for efficient processing
    MAX_TOKENS_PER_EXAMPLE = 1024
    
    # Alpaca format template
    INSTRUCTION_TEMPLATE = "Answer the following technical question about machine learning and transformers based on your knowledge."
    
    def __init__(self, token_budget: int = MAX_TOKENS_PER_EXAMPLE):
        """
        Initialize LoRA data formatter.
        
        Args:
            token_budget: Maximum tokens per training example
        """
        self.token_budget = token_budget
        self.token_manager = TokenManager()
        
        # Statistics tracking
        self.stats = {
            'total_loaded': 0,
            'total_formatted': 0,
            'within_budget': 0,
            'truncated': 0,
            'failed': 0,
            'avg_input_tokens': 0,
            'avg_output_tokens': 0,
            'avg_total_tokens': 0,
            'warnings': []
        }
        
        print("\n" + "="*70)
        print("LORA DATA FORMATTER INITIALIZATION")
        print("="*70)
        print(f"Token budget per example: {self.token_budget} tokens")
    
    def load_qa_dataset(self, qa_path: str = None) -> List[Dict]:
        """
        Load synthetic QA pairs.
        
        Args:
            qa_path: Path to synthetic_qa.json (default: Config.PROCESSED_DATA)
            
        Returns:
            List of QA pair dictionaries
        """
        if qa_path is None:
            qa_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
        
        print(f"\nLoading QA dataset from {qa_path}...")
        
        if not os.path.exists(qa_path):
            raise FileNotFoundError(f"QA dataset not found: {qa_path}")
        
        with open(qa_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        qa_pairs = dataset.get('qa_pairs', [])
        self.stats['total_loaded'] = len(qa_pairs)
        
        print(f"✓ Loaded {len(qa_pairs)} QA pairs")
        return qa_pairs
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using TokenManager."""
        return self.token_manager.estimate_tokens(text)
    
    def format_example(self, qa_pair: Dict, example_id: int) -> Tuple[Dict | None, bool]:
        """
        Format a single QA pair into Alpaca format.
        
        Args:
            qa_pair: Dictionary with 'question' and 'answer' keys
            example_id: Example index
            
        Returns:
            Tuple of (formatted_example, was_truncated)
        """
        try:
            question = qa_pair.get('question', '').strip()
            answer = qa_pair.get('answer', '').strip()
            source = qa_pair.get('source_file', 'unknown')
            difficulty = qa_pair.get('difficulty', 'medium')
            
            if not question or not answer:
                warning = f"Example {example_id}: Missing question or answer"
                self.stats['warnings'].append(warning)
                self.stats['failed'] += 1
                return None, False
            
            # Create instruction (system message)
            instruction = self.INSTRUCTION_TEMPLATE
            
            # Estimate tokens
            instruction_tokens = self.estimate_tokens(instruction)
            input_tokens = self.estimate_tokens(question)
            output_tokens = self.estimate_tokens(answer)
            total_tokens = instruction_tokens + input_tokens + output_tokens
            
            # Check if within budget
            was_truncated = False
            if total_tokens > self.token_budget:
                # Truncate output to fit within budget
                # Reserve tokens for instruction and input
                reserved = instruction_tokens + input_tokens + 50  # 50 token buffer
                available = self.token_budget - reserved
                
                if available > 50:
                    # Truncate answer to fit
                    words = answer.split()
                    estimated_words = int(available / self.token_manager.TOKENS_PER_WORD)
                    truncated_answer = ' '.join(words[:estimated_words])
                    
                    if truncated_answer != answer:
                        answer = truncated_answer + " [truncated]"
                        was_truncated = True
                        output_tokens = self.estimate_tokens(answer)
                        total_tokens = instruction_tokens + input_tokens + output_tokens
                        
                        warning = (
                            f"Example {example_id}: Truncated from {total_tokens} to "
                            f"{total_tokens} tokens"
                        )
                        self.stats['warnings'].append(warning)
                else:
                    warning = f"Example {example_id}: Cannot fit within budget (skipping)"
                    self.stats['warnings'].append(warning)
                    self.stats['failed'] += 1
                    return None, False
            
            # Create Alpaca-format example
            example = {
                "instruction": instruction,
                "input": question,
                "output": answer,
                "metadata": {
                    "example_id": example_id,
                    "source_file": source,
                    "difficulty": difficulty,
                    "instruction_tokens": instruction_tokens,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "was_truncated": was_truncated
                }
            }
            
            # Update statistics
            self.stats['total_formatted'] += 1
            if not was_truncated:
                self.stats['within_budget'] += 1
            else:
                self.stats['truncated'] += 1
            
            # Accumulate for averages
            self.stats['avg_input_tokens'] += input_tokens
            self.stats['avg_output_tokens'] += output_tokens
            self.stats['avg_total_tokens'] += total_tokens
            
            return example, was_truncated
        
        except Exception as e:
            warning = f"Example {example_id}: Error formatting - {str(e)}"
            self.stats['warnings'].append(warning)
            self.stats['failed'] += 1
            return None, False
    
    def format_dataset(self, qa_pairs: List[Dict]) -> List[Dict]:
        """
        Format all QA pairs into Alpaca format.
        
        Args:
            qa_pairs: List of QA pair dictionaries
            
        Returns:
            List of formatted examples
        """
        print(f"\nFormatting {len(qa_pairs)} QA pairs...")
        
        formatted_examples = []
        
        for idx, qa_pair in enumerate(qa_pairs, 1):
            example, was_truncated = self.format_example(qa_pair, idx)
            
            if example:
                formatted_examples.append(example)
                status = "✓ (truncated)" if was_truncated else "✓"
                print(f"  [{idx:2d}] {status} - {example['input'][:60]}...")
        
        print(f"\n✓ Formatted {len(formatted_examples)} examples successfully")
        
        return formatted_examples
    
    def save_jsonl(self, examples: List[Dict], output_path: str = None) -> str:
        """
        Save formatted examples to JSONL file.
        
        Args:
            examples: List of formatted examples
            output_path: Output file path (default: data/processed/lora_train_data.jsonl)
            
        Returns:
            Path to saved file
        """
        if output_path is None:
            output_path = os.path.join(Config.PROCESSED_DATA, "lora_train_data.jsonl")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"\nSaving JSONL to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for example in examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        print(f"✓ Saved {len(examples)} training examples to {output_path}")
        
        return output_path
    
    def save_metadata(self, examples: List[Dict], output_dir: str = None) -> str:
        """
        Save metadata and statistics.
        
        Args:
            examples: List of formatted examples
            output_dir: Output directory (default: Config.PROCESSED_DATA)
            
        Returns:
            Path to metadata file
        """
        if output_dir is None:
            output_dir = Config.PROCESSED_DATA
        
        # Calculate final statistics
        if self.stats['total_formatted'] > 0:
            self.stats['avg_input_tokens'] /= self.stats['total_formatted']
            self.stats['avg_output_tokens'] /= self.stats['total_formatted']
            self.stats['avg_total_tokens'] /= self.stats['total_formatted']
        
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'source': 'synthetic_qa.json',
            'format': 'Alpaca (instruction, input, output)',
            'total_examples': len(examples),
            'token_budget_per_example': self.token_budget,
            'statistics': self.stats,
            'examples': [
                {
                    'id': ex['metadata']['example_id'],
                    'source_file': ex['metadata']['source_file'],
                    'difficulty': ex['metadata']['difficulty'],
                    'tokens': ex['metadata']['total_tokens'],
                    'truncated': ex['metadata']['was_truncated']
                }
                for ex in examples
            ]
        }
        
        metadata_path = os.path.join(output_dir, "lora_train_metadata.json")
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved metadata to {metadata_path}")
        
        return metadata_path
    
    def print_statistics(self) -> None:
        """Print detailed statistics."""
        print("\n" + "="*70)
        print("LORA DATA PREPARATION SUMMARY")
        print("="*70)
        
        print(f"\nDataset Statistics:")
        print(f"  Total loaded: {self.stats['total_loaded']}")
        print(f"  Successfully formatted: {self.stats['total_formatted']}")
        print(f"  Within token budget: {self.stats['within_budget']}")
        print(f"  Truncated: {self.stats['truncated']}")
        print(f"  Failed: {self.stats['failed']}")
        
        print(f"\nToken Statistics (per example):")
        print(f"  Max budget: {self.token_budget} tokens")
        print(f"  Avg input: {self.stats['avg_input_tokens']:.0f} tokens")
        print(f"  Avg output: {self.stats['avg_output_tokens']:.0f} tokens")
        print(f"  Avg total: {self.stats['avg_total_tokens']:.0f} tokens")
        
        if self.stats['warnings']:
            print(f"\nWarnings ({len(self.stats['warnings'])}):")
            for warning in self.stats['warnings'][:5]:  # Show first 5
                print(f"  ⚠ {warning}")
            if len(self.stats['warnings']) > 5:
                print(f"  ... and {len(self.stats['warnings']) - 5} more")
        
        print(f"\n{'='*70}\n")
    
    def print_sample_examples(self, examples: List[Dict], num_samples: int = 2) -> None:
        """
        Print sample formatted examples.
        
        Args:
            examples: List of formatted examples
            num_samples: Number of samples to print
        """
        print("\n" + "="*70)
        print(f"SAMPLE TRAINING EXAMPLES (First {min(num_samples, len(examples))})")
        print("="*70)
        
        for example in examples[:num_samples]:
            meta = example['metadata']
            print(f"\nExample {meta['example_id']} (Source: {meta['source_file']}, {meta['difficulty']})")
            print(f"Tokens: {meta['total_tokens']} (instruction: {meta['instruction_tokens']}, "
                  f"input: {meta['input_tokens']}, output: {meta['output_tokens']})")
            print(f"Truncated: {'Yes' if meta['was_truncated'] else 'No'}\n")
            
            print(f"Instruction:\n{example['instruction']}\n")
            print(f"Input (Question):\n{example['input']}\n")
            print(f"Output (Answer):\n{example['output'][:200]}...\n")
            print("-" * 70)


def main():
    """Main execution function."""
    
    try:
        # Initialize formatter
        formatter = LoRADataFormatter(token_budget=1024)
        
        # Load dataset
        qa_pairs = formatter.load_qa_dataset()
        
        # Format dataset
        formatted_examples = formatter.format_dataset(qa_pairs)
        
        # Save JSONL
        jsonl_path = formatter.save_jsonl(formatted_examples)
        
        # Save metadata
        metadata_path = formatter.save_metadata(formatted_examples)
        
        # Print statistics
        formatter.print_statistics()
        
        # Print sample examples
        formatter.print_sample_examples(formatted_examples, num_samples=2)
        
        print("\n✓ LoRA data preparation complete!")
        print(f"\nOutput files:")
        print(f"  - Training data: {jsonl_path}")
        print(f"  - Metadata: {metadata_path}")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ LoRA data preparation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
