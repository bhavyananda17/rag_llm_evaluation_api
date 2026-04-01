#!/usr/bin/env python3
"""
LoRA Training Setup Verification

Checks that all components are ready for training:
1. Dependencies installed
2. Training data exists
3. Model can be loaded
4. LoRA config is valid
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config


def check_dependencies():
    """Check if all required packages are installed."""
    print("\n" + "="*70)
    print("1. CHECKING DEPENDENCIES")
    print("="*70)
    
    deps = {
        'torch': 'PyTorch',
        'transformers': 'Transformers',
        'peft': 'PEFT (LoRA)',
        'trl': 'TRL (SFT)',
        'datasets': 'Datasets',
    }
    
    missing = []
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - NOT INSTALLED")
            missing.append(module)
    
    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install -r requirements-lora.txt")
        return False
    
    return True


def check_training_data():
    """Check if training data file exists."""
    print("\n" + "="*70)
    print("2. CHECKING TRAINING DATA")
    print("="*70)
    
    data_path = os.path.join(Config.PROCESSED_DATA, "lora_train_data.jsonl")
    
    if not os.path.exists(data_path):
        print(f"✗ Training data not found at {data_path}")
        print(f"  Run: python src/prep_lora_data.py")
        return False
    
    print(f"✓ Data file exists: {data_path}")
    
    # Check file size
    size = os.path.getsize(data_path)
    print(f"  Size: {size:,} bytes ({size/1024:.1f} KB)")
    
    # Count examples
    try:
        with open(data_path, 'r') as f:
            count = sum(1 for _ in f)
        print(f"  Examples: {count}")
        
        # Show sample
        with open(data_path, 'r') as f:
            first_line = f.readline()
            example = json.loads(first_line)
            print(f"\n  Sample:")
            print(f"    Instruction: {example.get('instruction', '')[:50]}...")
            print(f"    Input: {example.get('input', '')[:50]}...")
            print(f"    Output: {example.get('output', '')[:50]}...")
        
        return True
    
    except Exception as e:
        print(f"✗ Error reading data: {str(e)}")
        return False


def check_model_availability():
    """Check if model can be downloaded/cached."""
    print("\n" + "="*70)
    print("3. CHECKING MODEL AVAILABILITY")
    print("="*70)
    
    model_name = "google/gemma-2-2b-it"
    print(f"Model: {model_name}")
    
    try:
        from transformers import AutoTokenizer
        
        print(f"\nAttempting to load tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            token=None  # Uses HuggingFace token if available
        )
        print(f"✓ Tokenizer loaded successfully")
        print(f"  Vocab size: {len(tokenizer)}")
        
        return True
    
    except Exception as e:
        print(f"✗ Failed to load tokenizer: {str(e)}")
        print(f"\nNote: First run will download the model (~5GB)")
        print(f"Ensure you have internet and ~6GB free space")
        return False


def check_output_directory():
    """Check/create output directory."""
    print("\n" + "="*70)
    print("4. CHECKING OUTPUT DIRECTORY")
    print("="*70)
    
    output_dir = os.path.join(Config.BASE_DIR, "models/lora_adapters")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"✓ Output directory ready: {output_dir}")
        
        # Check permissions
        test_file = os.path.join(output_dir, ".test")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print(f"✓ Write permissions OK")
        
        return True
    
    except Exception as e:
        print(f"✗ Directory issue: {str(e)}")
        return False


def check_device():
    """Check available device."""
    print("\n" + "="*70)
    print("5. CHECKING DEVICE")
    print("="*70)
    
    try:
        import torch
        
        if torch.backends.mps.is_available():
            device = "mps"
            print(f"✓ Device: Mac MPS (Metal Performance Shaders)")
        elif torch.cuda.is_available():
            device = "cuda"
            print(f"✓ Device: NVIDIA CUDA")
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
            print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            device = "cpu"
            print(f"⚠ Device: CPU only (training will be slow)")
        
        return True
    
    except Exception as e:
        print(f"✗ Device check failed: {str(e)}")
        return False


def print_summary(results):
    """Print verification summary."""
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    checks = [
        ("Dependencies", results[0]),
        ("Training Data", results[1]),
        ("Model Available", results[2]),
        ("Output Directory", results[3]),
        ("Device", results[4]),
    ]
    
    for name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results)
    
    print(f"\n{'='*70}")
    if all_passed:
        print("✓ ALL CHECKS PASSED - Ready for training!")
        print(f"\nRun: python3 src/train_lora.py")
    else:
        print("✗ Some checks failed - See above for details")
        print(f"\nFix issues before running training")
    
    print(f"{'='*70}\n")
    
    return all_passed


def main():
    """Main verification."""
    print("\n" + "="*70)
    print("LoRA TRAINING SETUP VERIFICATION")
    print("="*70)
    
    results = [
        check_dependencies(),
        check_training_data(),
        check_model_availability(),
        check_output_directory(),
        check_device(),
    ]
    
    all_passed = print_summary(results)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
