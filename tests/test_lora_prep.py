#!/usr/bin/env python3
"""Quick test of LoRA data formatter without hanging."""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.token_manager import TokenManager

print("="*70)
print("LORA DATA PREPARATION TEST")
print("="*70)

# Step 1: Load QA data
print("\n1. Loading QA dataset...")
qa_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")

try:
    with open(qa_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    qa_pairs = dataset.get('qa_pairs', [])
    print(f"✓ Loaded {len(qa_pairs)} QA pairs")
except Exception as e:
    print(f"✗ Failed to load: {e}")
    sys.exit(1)

# Step 2: Initialize token manager
print("\n2. Initializing token manager...")
try:
    tm = TokenManager()
    print(f"✓ Token manager ready")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Step 3: Format examples
print("\n3. Formatting examples...")

INSTRUCTION_TEMPLATE = "Answer the following technical question about machine learning and transformers based on your knowledge."
MAX_TOKENS = 1024

formatted_examples = []
warnings = []

for idx, qa_pair in enumerate(qa_pairs, 1):
    question = qa_pair.get('question', '').strip()
    answer = qa_pair.get('answer', '').strip()
    source = qa_pair.get('source_file', 'unknown')
    difficulty = qa_pair.get('difficulty', 'medium')
    
    if not question or not answer:
        warnings.append(f"Example {idx}: Missing data")
        continue
    
    # Estimate tokens
    instruction_tokens = tm.estimate_tokens(INSTRUCTION_TEMPLATE)
    input_tokens = tm.estimate_tokens(question)
    output_tokens = tm.estimate_tokens(answer)
    total_tokens = instruction_tokens + input_tokens + output_tokens
    
    # Truncate if needed
    was_truncated = False
    if total_tokens > MAX_TOKENS:
        reserved = instruction_tokens + input_tokens + 50
        available = MAX_TOKENS - reserved
        if available > 50:
            words = answer.split()
            estimated_words = int(available / tm.TOKENS_PER_WORD)
            answer = ' '.join(words[:estimated_words]) + " [truncated]"
            was_truncated = True
            output_tokens = tm.estimate_tokens(answer)
            total_tokens = instruction_tokens + input_tokens + output_tokens
    
    # Create formatted example
    example = {
        "instruction": INSTRUCTION_TEMPLATE,
        "input": question,
        "output": answer,
        "metadata": {
            "example_id": idx,
            "source_file": source,
            "difficulty": difficulty,
            "instruction_tokens": instruction_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "was_truncated": was_truncated
        }
    }
    
    formatted_examples.append(example)
    print(f"  [{idx:2d}] ✓ {question[:50]}... ({total_tokens} tokens)")

print(f"\n✓ Formatted {len(formatted_examples)} examples")

# Step 4: Save JSONL
print("\n4. Saving JSONL...")

output_dir = Config.PROCESSED_DATA
os.makedirs(output_dir, exist_ok=True)

jsonl_path = os.path.join(output_dir, "lora_train_data.jsonl")
with open(jsonl_path, 'w', encoding='utf-8') as f:
    for example in formatted_examples:
        f.write(json.dumps(example, ensure_ascii=False) + '\n')

print(f"✓ Saved to {jsonl_path}")

# Step 5: Save metadata
print("\n5. Saving metadata...")

metadata = {
    'total_examples': len(formatted_examples),
    'token_budget': MAX_TOKENS,
    'statistics': {
        'total_loaded': len(qa_pairs),
        'total_formatted': len(formatted_examples),
        'warnings': len(warnings)
    },
    'examples': [
        {
            'id': ex['metadata']['example_id'],
            'source': ex['metadata']['source_file'],
            'difficulty': ex['metadata']['difficulty'],
            'tokens': ex['metadata']['total_tokens'],
            'truncated': ex['metadata']['was_truncated']
        }
        for ex in formatted_examples
    ]
}

metadata_path = os.path.join(output_dir, "lora_train_metadata.json")
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"✓ Saved to {metadata_path}")

# Step 6: Print summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Total loaded: {len(qa_pairs)}")
print(f"Total formatted: {len(formatted_examples)}")
print(f"Warnings: {len(warnings)}")
print(f"\nOutput files:")
print(f"  - {jsonl_path}")
print(f"  - {metadata_path}")

# Show first example
if formatted_examples:
    print(f"\nFirst example:")
    ex = formatted_examples[0]
    print(f"  Instruction: {ex['instruction'][:60]}...")
    print(f"  Input: {ex['input'][:60]}...")
    print(f"  Output: {ex['output'][:60]}...")
    print(f"  Tokens: {ex['metadata']['total_tokens']}")

print(f"\n{'='*70}")
print("✓ LoRA data preparation complete!")
print(f"{'='*70}\n")
