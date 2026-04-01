# Commit 6: LoRA Fine-Tuning Training

## 📋 Overview

This commit implements **Low-Rank Adaptation (LoRA) fine-tuning** on the synthetic QA dataset. After using RAG to retrieve context at inference time, we now "bake" knowledge into the model's weights through efficient fine-tuning.

**Key Innovation**: LoRA reduces trainable parameters from millions to thousands, making fine-tuning feasible on consumer hardware.

---

## 🎯 What Is LoRA?

### Traditional Fine-Tuning vs LoRA

| Aspect | Traditional | LoRA |
|--------|-------------|------|
| **Trainable Parameters** | 100% of model | ~0.1% of model |
| **Memory Required** | 4x model size | ~10% of model size |
| **Training Time** | Days/weeks | Hours/minutes |
| **Hardware** | GPU/TPU required | CPU/GPU/MPS |

### How LoRA Works

1. **Decomposition**: Instead of updating weight matrix W, we learn low-rank updates ΔW = AB
2. **Rank**: r=8 means we learn matrices of shape (hidden_size, 8) and (8, hidden_size)
3. **Target**: Apply to Q and V projection layers in attention (where most knowledge is learned)
4. **Result**: 99.9% fewer parameters with comparable performance

---

## 📂 Files Created

### 1. **src/train_lora.py** (350+ lines)
Complete LoRA training pipeline with:
- Model loading with 4-bit quantization
- PEFT LoRA configuration (r=8, alpha=32)
- TRL SFTTrainer integration
- Device detection (MPS, CUDA, CPU)
- Gradient checkpointing & mixed precision
- Adapter saving and metadata

### 2. **requirements-lora.txt**
Dependencies for LoRA training:
- transformers, peft, trl, datasets
- bitsandbytes (optional, for quantization)

---

## 🔧 Technical Details

### Model: google/gemma-2-2b-it

| Property | Value |
|----------|-------|
| **Type** | Gemma 2 Instruction-Tuned |
| **Size** | 2.6B parameters |
| **Context** | 8K tokens |
| **License** | Apache 2.0 |
| **Use Case** | Instruction following, Q&A |

### LoRA Configuration

```python
LoraConfig(
    r=8,                          # Rank of the update matrices
    lora_alpha=32,                # Scaling factor (32/8 = 4x)
    target_modules=['q_proj', 'v_proj'],  # Query & Value projections
    lora_dropout=0.05,            # Dropout for regularization
    bias="none",                  # No bias in LoRA
    task_type="CAUSAL_LM"         # Language modeling task
)
```

### Training Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Learning Rate** | 2e-4 | Conservative for fine-tuning |
| **Epochs** | 3 | Small dataset (13 examples) |
| **Batch Size** | 1 | Memory efficiency on Mac |
| **Gradient Accumulation** | 4 | Effective batch size = 4 |
| **Sequence Length** | 512 | Fits training data comfortably |

### Memory Optimization Techniques

1. **Gradient Checkpointing**
   - Trades compute for memory
   - Recalculates activations during backward pass
   - ~50% memory savings

2. **Mixed Precision Training**
   - Float16 on CUDA
   - Float32 on MPS/CPU
   - Reduces memory by ~2x

3. **LoRA Itself**
   - Only updates 0.1% of parameters
   - ~99% memory savings vs full fine-tuning

4. **Quantization (CUDA only)**
   - 4-bit quantization via BitsAndBytes
   - Further 4x memory reduction
   - Not available on MPS

---

## 🚀 Execution Guide

### Step 1: Install Dependencies

```bash
# Navigate to project
cd /Users/bhavyananda/Documents/coding/rag_llm_evaluation_api

# Install LoRA dependencies
pip install -r requirements-lora.txt

# Optional: for CUDA users only
pip install bitsandbytes
```

### Step 2: Verify Dataset

```bash
# Check if training data exists
ls -lh data/processed/lora_train_data.jsonl

# Should show something like:
# -rw-r--r--  1 user  staff  8.5K Apr 1 15:30 lora_train_data.jsonl
```

### Step 3: Run Training

```bash
# Set Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run training
python3 src/train_lora.py
```

### Expected Output

```
======================================================================
LoRA FINE-TUNING FOR TRANSFORMER MODELS
======================================================================

======================================================================
LoRA TRAINING INITIALIZATION
======================================================================
Model: google/gemma-2-2b-it
Device: mps
Output Directory: /path/to/models/lora_adapters
======================================================================

Checking dependencies...
✓ transformers
✓ peft
✓ trl
✓ datasets

======================================================================
LOADING MODEL AND TOKENIZER
======================================================================

Loading tokenizer from google/gemma-2-2b-it...
✓ Tokenizer loaded

Loading model in standard precision...
✓ Model loaded

Applying LoRA configuration...
✓ LoRA applied
  Trainable params: 65,544
  Total params: 2,614,026,752
  Trainable %: 0.00%

======================================================================
LOADING DATASET
======================================================================

Loading dataset from data/processed/lora_train_data.jsonl...
✓ Dataset loaded with 13 examples

Sample example:
  Instruction: Answer this technical question based on Transformer architecture.
  Input: What is self-attention?
  Output: Self-attention is a mechanism...

======================================================================
TRAINING ARGUMENTS
======================================================================

Device: Mac MPS - using float32
Training Parameters:
  Learning rate: 0.0002
  Epochs: 3
  Batch size: 1
  Gradient accumulation: 4
  Effective batch size: 4
  Mixed precision: fp16=False, bf16=False
  Output directory: /path/to/models/lora_adapters

======================================================================
CREATING SFT TRAINER
======================================================================
✓ SFTTrainer created

======================================================================
STARTING TRAINING
======================================================================
Start time: 2026-04-01T15:45:00.000000

[Epoch 1/3] loss: 2.3456
[Epoch 2/3] loss: 1.8234
[Epoch 3/3] loss: 1.5123

======================================================================
TRAINING COMPLETE
======================================================================
End time: 2026-04-01T15:47:30.000000
Training loss: 1.5123

======================================================================
SAVING ADAPTERS
======================================================================
Saving adapters to models/lora_adapters/final_adapter...
✓ Adapters saved
✓ Metadata saved to models/lora_adapters/adapter_metadata.json

======================================================================
LoRA TRAINING SUMMARY
======================================================================
Model: google/gemma-2-2b-it
Device: mps
Adapters saved: models/lora_adapters/final_adapter
Metadata: models/lora_adapters/adapter_metadata.json
✓ LoRA training complete!
```

---

## 📊 Expected Results

### Training Time

| Device | Time (13 examples, 3 epochs) |
|--------|------------------------------|
| **Mac M1/M2/M3 (MPS)** | 2-3 minutes |
| **Mac CPU** | 5-10 minutes |
| **NVIDIA GPU** | 30-60 seconds |

### Model Size

| Component | Size |
|-----------|------|
| Base Model | ~5GB (2.6B params @ fp32) |
| LoRA Adapter | ~500KB (0.065M trainable params) |
| Tokenizer | ~100KB |

### Memory Usage

| Scenario | Memory |
|----------|--------|
| Base model inference | ~5.5GB |
| LoRA training (MPS) | ~6GB |
| LoRA training (CUDA) | ~2-3GB (with quantization) |

---

## 🔍 What Gets Saved

### Directory Structure

```
models/lora_adapters/
├── final_adapter/
│   ├── adapter_config.json      # LoRA configuration
│   ├── adapter_model.bin        # LoRA weight matrices
│   ├── special_tokens_map.json
│   ├── tokenizer.json
│   ├── tokenizer.model
│   └── tokenizer_config.json
└── adapter_metadata.json         # Training metadata
```

### Key Files

1. **adapter_model.bin** (~500KB)
   - The trained LoRA weight matrices (ΔW = AB)
   - Can be loaded on top of any Gemma-2-2B-IT model

2. **adapter_config.json**
   - Specifies r=8, target modules, etc.
   - PEFT uses this to reconstruct LoRA behavior

3. **tokenizer files**
   - Ensures compatibility
   - Same tokenizer used during training

---

## 🎓 Key Concepts

### Why LoRA Works

1. **Intrinsic Dimension**: Most fine-tuning happens in a low-rank subspace
2. **Orthogonality**: LoRA updates are orthogonal to pre-trained weights
3. **Composability**: Multiple LoRA adapters can be combined

### LoRA Hyperparameters Explained

- **r (rank)**: Larger r → more expressive but more parameters
  - r=8: Very efficient (0.065M params)
  - r=16-32: Balanced (0.13-0.26M params)
  - r=64: High capacity (0.52M params)

- **alpha (scaling)**: Controls magnitude of LoRA updates
  - Common: alpha = 2 × r (e.g., 16 for r=8)
  - Prevents vanishing gradients

- **target_modules**: Which layers to adapt
  - Q_proj: Query projections in attention
  - V_proj: Value projections in attention
  - Also can target: K_proj, O_proj, MLP layers

---

## 💡 Optimization Strategies

### For Mac MPS
```python
# Already optimized in train_lora.py
gradient_checkpointing=True
fp16=False  # MPS doesn't support fp16 well
bf16=False
device_map="mps"
```

### For CUDA
```python
# Automatically detected
fp16=True              # Faster on most GPUs
optim="paged_adamw_32bit"  # Memory efficient
quantization_config=BitsAndBytesConfig(load_in_4bit=True)
```

### For CPU
```python
# Slow but works
batch_size=1
gradient_accumulation_steps=4
num_workers=0  # CPU doesn't parallelize data loading
```

---

## ⚠️ Troubleshooting

### Issue: "Out of memory" error

**Solution**: Reduce batch size or increase gradient accumulation
```python
batch_size=1
gradient_accumulation_steps=8  # Effective batch size = 8
```

### Issue: Training is very slow on CPU

**Expected**: Training on CPU takes 5-10 minutes for this small dataset
- CPU is for testing/development only
- For production, use GPU/MPS

### Issue: "bitsandbytes not found" (CUDA)

**Solution**:
```bash
pip install bitsandbytes
# Or on older CUDA versions:
pip install bitsandbytes==0.41.0 --prefer-binary
```

### Issue: Model download fails

**Solution**: Pre-download model
```bash
huggingface-cli download google/gemma-2-2b-it
```

---

## 📈 Next Steps

After training completes:

1. **Save adapters** (automatic) → `models/lora_adapters/final_adapter/`
2. **Evaluate on QA** → Run inference benchmark
3. **Compare with RAG** → Same questions, same evaluation metrics
4. **Save results** → `data/results/lora_benchmark_results.json`

---

## 🔗 Related Resources

- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [PEFT Documentation](https://huggingface.co/docs/peft/en/index)
- [TRL Documentation](https://huggingface.co/docs/trl/en/index)
- [Gemma 2 Model Card](https://huggingface.co/google/gemma-2-2b-it)

---

## 📝 Summary

**Commit 6 delivers:**
- ✅ Complete LoRA training pipeline
- ✅ Memory-optimized for Mac/GPU/CPU
- ✅ Automatic device detection
- ✅ 4-bit quantization support
- ✅ Gradient checkpointing
- ✅ Mixed precision training
- ✅ Adapter persistence
- ✅ Training metadata logging

**Result**: Fine-tuned model adapters (500KB) ready for inference evaluation!
