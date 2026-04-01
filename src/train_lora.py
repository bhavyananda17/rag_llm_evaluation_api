#!/usr/bin/env python3
"""
LoRA Fine-Tuning Script

Trains a language model using LoRA (Low-Rank Adaptation) on the synthetic QA dataset.
Optimized for Mac with MPS support and memory-efficient training.

Features:
- Load training data from JSONL
- 4-bit quantization for memory efficiency
- LoRA configuration (r=8, lora_alpha=32)
- SFT training with gradient checkpointing
- Mac-optimized training (MPS/CPU)
- Adapter saving to disk
"""

import os
import sys
import json
import torch
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings
warnings.filterwarnings('ignore')

from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    TextDataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

from src.config import Config


class LoRATrainer:
    """Train a language model using LoRA adaptation."""
    
    def __init__(self, 
                 model_name: str = "google/gemma-2-2b-it",
                 data_path: str = None,
                 output_dir: str = None,
                 use_quantization: bool = True):
        """
        Initialize LoRA trainer.
        
        Args:
            model_name: HuggingFace model ID
            data_path: Path to JSONL training data
            output_dir: Directory to save trained adapters
            use_quantization: Use 4-bit quantization
        """
        self.model_name = model_name
        self.data_path = data_path or os.path.join(Config.PROCESSED_DATA, "lora_train_data.jsonl")
        self.output_dir = output_dir or os.path.join(Config.BASE_DIR, "models/lora_adapters")
        self.use_quantization = use_quantization
        
        # Detect device
        self.device = self._detect_device()
        print(f"✓ Detected device: {self.device}")
        
        # Model and tokenizer
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        # Training metadata
        self.training_stats = {
            'model': model_name,
            'device': self.device,
            'start_time': None,
            'end_time': None,
            'total_samples': 0,
            'training_loss': None
        }
    
    def _detect_device(self) -> str:
        """Detect available device (MPS, CUDA, CPU)."""
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"
    
    def _load_dataset(self):
        """Load training dataset from JSONL file."""
        print(f"\n{'='*70}")
        print("LOADING TRAINING DATASET")
        print(f"{'='*70}")
        
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Training data not found at {self.data_path}")
        
        print(f"Loading from: {self.data_path}")
        
        # Load JSONL file
        dataset = load_dataset('json', data_files=self.data_path)
        train_dataset = dataset['train']
        
        print(f"✓ Loaded {len(train_dataset)} training examples")
        self.training_stats['total_samples'] = len(train_dataset)
        
        # Show sample
        if len(train_dataset) > 0:
            sample = train_dataset[0]
            print(f"\nSample training example:")
            print(f"  Instruction: {sample.get('instruction', '')[:50]}...")
            print(f"  Input: {sample.get('input', '')[:50]}...")
            print(f"  Output: {sample.get('output', '')[:50]}...")
        
        return train_dataset
    
    def _setup_model_and_tokenizer(self):
        """Initialize model and tokenizer with quantization."""
        print(f"\n{'='*70}")
        print("SETTING UP MODEL AND TOKENIZER")
        print(f"{'='*70}")
        
        print(f"Model: {self.model_name}")
        
        # Load tokenizer
        print("\nLoading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            use_auth_token=False
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("✓ Tokenizer loaded")
        
        # Setup quantization config if not on Mac
        if self.use_quantization and self.device == "cpu":
            print("\n⚠ 4-bit quantization disabled on CPU (using standard precision)")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                device_map='auto',
                trust_remote_code=True
            )
        else:
            # Mac doesn't support 4-bit quantization well
            print("\nLoading model with optimized dtype for Mac...")
            
            # Use bfloat16 on Mac M-series, float16 otherwise
            if self.device == "mps":
                torch_dtype = torch.bfloat16 if torch.backends.mps.is_available() else torch.float16
            else:
                torch_dtype = torch.float16
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch_dtype,
                device_map='auto',
                trust_remote_code=True
            )
        
        print(f"✓ Model loaded: {self.model.config.model_type}")
        print(f"  Parameters: {self.model.num_parameters():,}")
    
    def _setup_lora(self):
        """Configure and apply LoRA to the model."""
        print(f"\n{'='*70}")
        print("CONFIGURING LORA")
        print(f"{'='*70}")
        
        # LoRA configuration
        lora_config = LoraConfig(
            r=8,                              # LoRA rank
            lora_alpha=32,                    # LoRA scaling factor
            target_modules=['q_proj', 'v_proj'],  # Target attention projections
            lora_dropout=0.05,
            bias='none',
            task_type='CAUSAL_LM'
        )
        
        print(f"LoRA Configuration:")
        print(f"  Rank (r): {lora_config.r}")
        print(f"  Alpha: {lora_config.lora_alpha}")
        print(f"  Target modules: {lora_config.target_modules}")
        print(f"  Dropout: {lora_config.lora_dropout}")
        
        # Prepare model for kbit training if using quantization
        if self.use_quantization and self.device != "cpu":
            print("\nPreparing model for kbit training...")
            self.model = prepare_model_for_kbit_training(self.model)
        
        # Apply LoRA
        print("Applying LoRA to model...")
        self.model = get_peft_model(self.model, lora_config)
        
        # Print trainable parameters
        self.model.print_trainable_parameters()
        print("✓ LoRA applied successfully")
    
    def _setup_training_arguments(self):
        """Configure training arguments."""
        print(f"\n{'='*70}")
        print("CONFIGURING TRAINING ARGUMENTS")
        print(f"{'='*70}")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            
            # Learning rate and optimization
            learning_rate=2e-4,
            lr_scheduler_type='cosine',
            warmup_steps=10,
            
            # Training schedule
            num_train_epochs=3,
            per_device_train_batch_size=1,  # Small batch for Mac
            gradient_accumulation_steps=4,   # Simulate larger batch
            
            # Memory optimization
            gradient_checkpointing=True,
            fp16=False,  # Disable fp16 on Mac
            bf16=(self.device == "mps"),  # Use bf16 on Mac M-series
            
            # Logging and saving
            logging_steps=1,
            logging_dir=os.path.join(self.output_dir, 'logs'),
            save_strategy='epoch',
            save_steps=10,
            eval_strategy='no',  # No evaluation for small dataset
            
            # Device
            device_map=self.device,
            dataloader_pin_memory=False,  # Disable on Mac
            
            # Misc
            seed=42,
            report_to=['tensorboard'],
            optim='paged_adamw_32bit' if self.device != "mps" else 'adamw_torch'
        )
        
        print(f"Training Arguments:")
        print(f"  Learning rate: {training_args.learning_rate}")
        print(f"  Epochs: {training_args.num_train_epochs}")
        print(f"  Batch size: {training_args.per_device_train_batch_size}")
        print(f"  Gradient accumulation: {training_args.gradient_accumulation_steps}")
        print(f"  Gradient checkpointing: {training_args.gradient_checkpointing}")
        print(f"  Output dir: {training_args.output_dir}")
        
        return training_args
    
    def train(self, train_dataset):
        """Train the model using SFTTrainer."""
        print(f"\n{'='*70}")
        print("INITIALIZING TRAINER")
        print(f"{'='*70}")
        
        training_args = self._setup_training_arguments()
        
        # Initialize SFT trainer
        self.trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=train_dataset,
            args=training_args,
            
            # SFT specific
            formatting_func=self._format_training_example,
            max_seq_length=1024,
            packing=False,  # Disable packing on Mac
            
            # Callbacks
            callbacks=[]
        )
        
        print("✓ SFTTrainer initialized")
        
        # Start training
        print(f"\n{'='*70}")
        print("TRAINING STARTED")
        print(f"{'='*70}\n")
        
        self.training_stats['start_time'] = datetime.now().isoformat()
        
        try:
            train_result = self.trainer.train()
            self.training_stats['training_loss'] = train_result.training_loss
            print(f"\n✓ Training completed")
            print(f"  Final loss: {train_result.training_loss:.4f}")
        except Exception as e:
            print(f"\n✗ Training failed: {str(e)}")
            raise
        
        self.training_stats['end_time'] = datetime.now().isoformat()
        
        return train_result
    
    def _format_training_example(self, examples):
        """Format training examples for SFT."""
        # Combine instruction, input, and output
        formatted = []
        for instruction, input_text, output_text in zip(
            examples['instruction'],
            examples['input'],
            examples['output']
        ):
            prompt = f"{instruction}\n{input_text}\n{output_text}"
            formatted.append(prompt)
        
        return {'text': formatted}
    
    def save_model(self):
        """Save trained adapters."""
        print(f"\n{'='*70}")
        print("SAVING TRAINED ADAPTERS")
        print(f"{'='*70}")
        
        if self.model is None:
            print("✗ No model to save")
            return None
        
        try:
            # Save model adapters
            self.model.save_pretrained(self.output_dir)
            
            # Save tokenizer
            self.tokenizer.save_pretrained(self.output_dir)
            
            print(f"✓ Adapters saved to: {self.output_dir}")
            
            # List saved files
            saved_files = os.listdir(self.output_dir)
            print(f"\nSaved files:")
            for file in saved_files:
                file_path = os.path.join(self.output_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    print(f"  - {file} ({size:.2f} MB)")
            
            return self.output_dir
        
        except Exception as e:
            print(f"✗ Failed to save model: {str(e)}")
            raise
    
    def save_training_metadata(self):
        """Save training metadata and statistics."""
        metadata_path = os.path.join(Config.PROCESSED_DATA, "lora_training_metadata.json")
        
        metadata = {
            'training_date': datetime.now().isoformat(),
            'model_name': self.model_name,
            'device': self.device,
            'start_time': self.training_stats['start_time'],
            'end_time': self.training_stats['end_time'],
            'total_samples': self.training_stats['total_samples'],
            'training_loss': self.training_stats['training_loss'],
            'adapter_path': self.output_dir,
            'lora_config': {
                'r': 8,
                'lora_alpha': 32,
                'target_modules': ['q_proj', 'v_proj'],
                'lora_dropout': 0.05
            },
            'training_arguments': {
                'learning_rate': 2e-4,
                'num_epochs': 3,
                'batch_size': 1,
                'gradient_accumulation_steps': 4
            }
        }
        
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"✓ Metadata saved to: {metadata_path}")
        except Exception as e:
            print(f"✗ Failed to save metadata: {str(e)}")
    
    def print_summary(self):
        """Print training summary."""
        print(f"\n{'='*70}")
        print("LORA TRAINING SUMMARY")
        print(f"{'='*70}")
        
        print(f"\nModel Configuration:")
        print(f"  Base model: {self.model_name}")
        print(f"  Device: {self.device}")
        print(f"  Training samples: {self.training_stats['total_samples']}")
        
        if self.training_stats['training_loss']:
            print(f"\nTraining Results:")
            print(f"  Final loss: {self.training_stats['training_loss']:.4f}")
            print(f"  Start time: {self.training_stats['start_time']}")
            print(f"  End time: {self.training_stats['end_time']}")
        
        print(f"\nOutput:")
        print(f"  Adapters saved to: {self.output_dir}")
        
        print(f"\n{'='*70}\n")


def main():
    """Main training execution."""
    print("\n" + "="*70)
    print("LORA FINE-TUNING PIPELINE")
    print("="*70)
    
    try:
        # Check if training data exists
        data_path = os.path.join(Config.PROCESSED_DATA, "lora_train_data.jsonl")
        if not os.path.exists(data_path):
            print(f"\n✗ Training data not found at {data_path}")
            print("Please run src/prep_lora_data.py first to prepare training data.")
            sys.exit(1)
        
        # Initialize trainer
        trainer = LoRATrainer(
            model_name="google/gemma-2-2b-it",
            use_quantization=True
        )
        
        # Load dataset
        train_dataset = trainer._load_dataset()
        
        # Setup model
        trainer._setup_model_and_tokenizer()
        
        # Setup LoRA
        trainer._setup_lora()
        
        # Train
        trainer.train(train_dataset)
        
        # Save
        trainer.save_model()
        trainer.save_training_metadata()
        
        # Summary
        trainer.print_summary()
        
        print("✓ LoRA Training Complete!")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Training interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ LoRA Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
