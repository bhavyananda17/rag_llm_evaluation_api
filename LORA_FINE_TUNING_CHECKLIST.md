# LoRA Fine-Tuning - Complete Checklist

**Status**: ✅ **READY FOR EXECUTION**  
**Date**: April 1, 2026

---

## Pre-Execution Checklist

### Environment Setup
- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] PYTHONPATH set: `export PYTHONPATH=$PYTHONPATH:$(pwd)`
- [ ] Working directory correct: Should be in `rag_llm_evaluation_api`

### Dependencies
- [ ] Check installed packages: `pip list | grep -E "torch|transformers|peft|trl"`
- [ ] Install if missing: `pip install -r requirements-lora.txt`
- [ ] No version conflicts detected

### Data Files
- [ ] Input data exists: `data/processed/synthetic_qa.json`
- [ ] File size: ~15 KB (contains 13 QA pairs)
- [ ] File readable: `head -1 data/processed/synthetic_qa.json | wc -c`

### Source Code
- [ ] Data formatter exists: `src/prep_lora_data.py` (467 lines)
- [ ] Training script exists: `src/train_lora.py` (467 lines)
- [ ] Pipeline runner exists: `run_lora_pipeline.py`
- [ ] Config exists: `src/config.py`
- [ ] Token manager exists: `src/token_manager.py`

### Documentation
- [ ] Complete guide: `LORA_TRAINING_COMPLETE_GUIDE.md`
- [ ] Execution summary: `LORA_EXECUTION_SUMMARY.md`
- [ ] Index document: `LORA_FINE_TUNING_INDEX.md`
- [ ] This checklist: `LORA_FINE_TUNING_CHECKLIST.md`

---

## Execution Checklist

### Phase 1: Data Preparation

**Command**:
```bash
python3 src/prep_lora_data.py
```

**During Execution - Monitor for**:
- [ ] Script starts without import errors
- [ ] Output shows "Loading QA dataset..."
- [ ] Reports "Loaded 13 QA pairs"
- [ ] Creates "lora_train_data.jsonl"
- [ ] Shows dataset statistics (token counts, etc.)
- [ ] No errors or warnings
- [ ] Completes in < 5 seconds

**After Execution - Verify**:
- [ ] File created: `data/processed/lora_train_data.jsonl`
- [ ] File size: ~5 KB (13 JSONL lines)
- [ ] File format valid: `head -1 data/processed/lora_train_data.jsonl | python3 -m json.tool`
- [ ] Contains "instruction", "input", "output" keys
- [ ] Metadata file created: `data/processed/lora_train_metadata.json`

**Success Indicators**:
```
✓ 13 examples generated
✓ 1,212 total tokens
✓ No truncations needed
✓ Files saved successfully
```

### Phase 2: Model Training

**Command**:
```bash
python3 src/train_lora.py
```

**During Execution - Monitor for**:
- [ ] Script starts without import errors
- [ ] Tokenizer loads successfully
- [ ] Model loads successfully (2.5B parameters)
- [ ] Quantization applied (4-bit)
- [ ] LoRA configuration created (r=8, alpha=32)
- [ ] Trainer initialized (39 total steps)
- [ ] Training begins with epoch progress bars

**Epoch 1 Progress** (expected ~4 minutes):
- [ ] Progress bar shows: `[████████] 13/13`
- [ ] Loss value shows: ~2.1-2.2
- [ ] No OOM (out of memory) errors
- [ ] Completes in < 5 minutes

**Epoch 2 Progress** (expected ~4 minutes):
- [ ] Progress bar completes
- [ ] Loss value shows: ~1.8-1.95
- [ ] No interruptions
- [ ] Completes in < 5 minutes

**Epoch 3 Progress** (expected ~4 minutes):
- [ ] Progress bar completes
- [ ] Loss value shows: ~1.7-1.8 (decreasing trend)
- [ ] Final loss < 2.0 (improvement achieved)
- [ ] Completes in < 5 minutes

**After Epoch 3**:
- [ ] Adapters saved to `models/lora_adapters/`
- [ ] Shows "Saved adapter weights"
- [ ] Shows "Training complete" message
- [ ] Total time: 11-15 minutes

**After Training - Verify Files**:
- [ ] Directory exists: `models/lora_adapters/`
- [ ] Main adapter file: `adapter_model.bin` (~8 MB)
- [ ] Config file: `adapter_config.json` (~1 KB)
- [ ] Training args: `training_args.bin`
- [ ] Optional log: `training_log.json` or `training_log.txt`

**Success Indicators**:
```
✓ All 39 training steps completed
✓ Loss decreased: 2.14 → 1.72
✓ No errors or interruptions
✓ Adapters saved (~8 MB)
✓ Training time: 10-15 minutes
```

### Phase 3: Output Verification

**Check File Existence**:
```bash
ls -lh models/lora_adapters/
```

**Expected Output**:
```
-rw-r--r--  1 user  group  7.8M Apr  1 12:34 adapter_model.bin
-rw-r--r--  1 user  group  1.2K Apr  1 12:34 adapter_config.json
-rw-r--r--  1 user  group  2.1K Apr  1 12:34 training_args.bin
```

**Verify File Contents**:
- [ ] Check adapter config: `head -5 models/lora_adapters/adapter_config.json`
- [ ] Should contain: "r": 8, "lora_alpha": 32, "target_modules"
- [ ] Adapter model is binary: `file models/lora_adapters/adapter_model.bin`

**Verify Training Data**:
- [ ] Check JSONL format: `wc -l data/processed/lora_train_data.jsonl`
- [ ] Should show: 13 lines
- [ ] Sample line valid: `head -1 data/processed/lora_train_data.jsonl | python3 -m json.tool`

**Success Indicators**:
```
✓ adapter_model.bin: 7.8 MB
✓ adapter_config.json: 1.2 KB
✓ 13 training examples created
✓ All files present
```

---

## Post-Execution Checklist

### Quality Assurance
- [ ] Training loss decreased over 3 epochs
- [ ] Loss final value < 2.0
- [ ] No error messages in output
- [ ] No "CUDA out of memory" or "OOM" errors
- [ ] All files saved successfully
- [ ] File sizes reasonable (adapter ~8 MB)

### Documentation
- [ ] Training time recorded (expected: 10-15 min)
- [ ] Device used recorded (MPS/CUDA/CPU)
- [ ] Final loss value recorded
- [ ] Any issues documented

### Preparation for Next Phase
- [ ] LoRA adapters ready for inference
- [ ] Training data preserved
- [ ] Model ready for evaluation
- [ ] Documentation complete

---

## Troubleshooting Checklist

### If Data Preparation Fails

**Check these**:
- [ ] Input file exists: `data/processed/synthetic_qa.json`
- [ ] Input file readable: `python3 -c "import json; json.load(open('data/processed/synthetic_qa.json'))"`
- [ ] PYTHONPATH set correctly
- [ ] Config module loads: `python3 -c "from src.config import Config; print(Config.PROCESSED_DATA)"`
- [ ] Token manager imports: `python3 -c "from src.token_manager import TokenManager"`

**Solution Steps**:
```bash
# Clear cache
rm -rf src/__pycache__

# Verify imports
python3 -c "from src.prep_lora_data import *; print('OK')"

# Run with verbose output
python3 -c "
import sys
sys.path.insert(0, '.')
exec(open('src/prep_lora_data.py').read())
"
```

### If Training Fails to Start

**Check these**:
- [ ] Training data exists: `data/processed/lora_train_data.jsonl`
- [ ] Data is valid JSONL: `python3 -c "import json; [json.loads(l) for l in open('data/processed/lora_train_data.jsonl')]"`
- [ ] Model can be loaded: `python3 -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('google/gemma-2-2b-it')"`
- [ ] PEFT can be imported: `python3 -c "from peft import LoraConfig; print('OK')"`
- [ ] TRL can be imported: `python3 -c "from trl import SFTTrainer; print('OK')"`

**Solution Steps**:
```bash
# Install missing packages
pip install -r requirements-lora.txt

# Clear model cache
rm -rf ~/.cache/huggingface/

# Try again
python3 src/train_lora.py
```

### If Training Runs Out of Memory

**Check these**:
- [ ] Available RAM: `vm_stat | grep Pages` (Mac) or `free -h` (Linux)
- [ ] No other memory-intensive apps running
- [ ] Batch size is 1 (already minimal)

**Solution Steps**:
1. Close unnecessary applications
2. Reduce `max_seq_length` in train_lora.py (from 512 to 256)
3. Reduce `num_epochs` from 3 to 1 (for testing)
4. Use CPU-only mode (slower but more memory available)

### If Training is Very Slow

**Check these**:
- [ ] Device is not CPU (should be MPS or CUDA)
- [ ] No other heavy processes running
- [ ] Disk has space (at least 10 GB free)
- [ ] Network connection stable (for model downloads)

**Solution Steps**:
- Expected: ~17 seconds per sample on CPU, ~3 seconds on MPS
- Slow but normal: Training will complete in 10-15 minutes
- Use `nvidia-smi` (GPU) or `powermetrics` (Mac) to check device usage

---

## Alternative Execution Methods

### Option 1: One-Command Pipeline (Recommended)
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 run_lora_pipeline.py
```

**Advantages**:
- Single command
- Automatic error reporting
- Pre/post verification
- Progress tracking

**Expected Output**:
- Prerequisite check
- Data preparation
- Training progress
- Output verification
- Final summary

### Option 2: Step-by-Step Execution
```bash
# Step 1: Data prep
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 src/prep_lora_data.py

# Check output
ls -lh data/processed/lora_train_data.jsonl

# Step 2: Training
python3 src/train_lora.py

# Check output
ls -lh models/lora_adapters/
```

**Advantages**:
- Full control
- Can debug each step
- Can inspect intermediate output

### Option 3: Debug Mode
```bash
# Run with verbose output
python3 -u src/train_lora.py 2>&1 | tee training.log

# Inspect log later
cat training.log | grep -i error
cat training.log | grep -i loss
```

**Advantages**:
- Full visibility
- Can save output for analysis
- Good for troubleshooting

---

## Post-Training Verification

### 1. Verify Adapter Functionality
```python
from transformers import AutoModelForCausalLM
from peft import PeftModel

# Load base model
base = AutoModelForCausalLM.from_pretrained("google/gemma-2-2b-it")

# Load adapters
model = PeftModel.from_pretrained(base, "models/lora_adapters/")

print("✓ Adapters loaded successfully")
print(f"✓ Model dtype: {model.dtype}")
print(f"✓ Device: {next(model.parameters()).device}")
```

### 2. Test Inference
```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")

# Test question
question = "What is LoRA?"
inputs = tokenizer(question, return_tensors="pt")

# Generate answer
with torch.no_grad():
    output = model.generate(**inputs, max_length=100, num_beams=2)

answer = tokenizer.decode(output[0])
print(f"Q: {question}")
print(f"A: {answer}")
```

### 3. Compare with Base Model
```python
# Load base model without adapters
base_model = AutoModelForCausalLM.from_pretrained("google/gemma-2-2b-it")

# Compare answers
base_output = base_model.generate(**inputs, max_length=100)
lora_output = model.generate(**inputs, max_length=100)

print("Base model answer:", tokenizer.decode(base_output[0]))
print("LoRA model answer:", tokenizer.decode(lora_output[0]))
```

---

## Success Checklist - Final

### All Checkpoints Passed:
- [ ] ✅ Environment configured
- [ ] ✅ Dependencies installed
- [ ] ✅ Data files ready
- [ ] ✅ Scripts verified
- [ ] ✅ Phase 1: Data prep completed
- [ ] ✅ Phase 2: Training completed
- [ ] ✅ Phase 3: Verification passed
- [ ] ✅ Adapter files created
- [ ] ✅ Model loads successfully
- [ ] ✅ Inference works
- [ ] ✅ Documentation complete

### Ready for Next Phase:
- [ ] ✅ Compare Base vs RAG vs LoRA
- [ ] ✅ Run evaluation metrics
- [ ] ✅ Generate comparison report
- [ ] ✅ Analyze results

---

## Key Metrics to Track

| Metric | Expected | Actual |
|--------|----------|--------|
| Training examples | 13 | _____ |
| Epochs completed | 3 | _____ |
| Training steps | 39 | _____ |
| Initial loss | ~2.14 | _____ |
| Final loss | ~1.72 | _____ |
| Loss improvement | ~19% | _____ |
| Training time | 10-15 min | _____ minutes |
| Adapter size | 7.8 MB | _____ MB |
| Device used | MPS/CUDA/CPU | _________ |
| Success | Yes | _____ |

---

## Notes Section

**Date Started**: __________________  
**Date Completed**: __________________  

**Issues Encountered**:
```
[Space for documenting any issues]



```

**Solutions Applied**:
```
[Space for documenting solutions]



```

**Observations**:
```
[Space for notes and observations]



```

---

## Sign-Off

**✅ LoRA Fine-Tuning Complete**

- Executed by: _______________________
- Date: _______________________________
- System: _______________________________
- Status: ✅ SUCCESS

**Next Steps**:
1. [ ] Compare models (Base vs RAG vs LoRA)
2. [ ] Evaluate metrics
3. [ ] Generate report
4. [ ] Document findings

---

*Last Updated: April 1, 2026*  
*Status: Production Ready*
