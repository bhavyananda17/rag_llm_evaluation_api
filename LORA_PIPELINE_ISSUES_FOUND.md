# Problems Found in run_lora_pipeline.py

## Critical Issues

### 1. **Missing PYTHONPATH in subprocess calls**
**Location**: Lines 72-76 and 108-113

**Problem**: 
The subprocess runs `src/prep_lora_data.py` and `src/train_lora.py` WITHOUT setting PYTHONPATH environment variable. These scripts need PYTHONPATH to import modules from `src/`.

**Current Code**:
```python
result = subprocess.run(
    [sys.executable, "src/prep_lora_data.py"],
    cwd=Config.BASE_DIR,
    capture_output=True,
    text=True
)
```

**Effect**: The child process cannot import `from src.config import Config` or other src modules, causing ImportError.

**Fix**: Add `env` parameter with PYTHONPATH:
```python
import os as os_module
env = os.environ.copy()
env['PYTHONPATH'] = Config.BASE_DIR

result = subprocess.run(
    [sys.executable, "src/prep_lora_data.py"],
    cwd=Config.BASE_DIR,
    env=env,  # <-- ADD THIS
    capture_output=True,
    text=True
)
```

---

### 2. **Missing timeout parameter for data preparation**
**Location**: Line 72-76

**Problem**: The data preparation subprocess has no timeout. If it hangs, the pipeline hangs indefinitely.

**Current Code**:
```python
result = subprocess.run(
    [sys.executable, "src/prep_lora_data.py"],
    cwd=Config.BASE_DIR,
    capture_output=True,
    text=True
    # No timeout!
)
```

**Fix**: Add timeout parameter:
```python
result = subprocess.run(
    [sys.executable, "src/prep_lora_data.py"],
    cwd=Config.BASE_DIR,
    env=env,
    capture_output=True,
    text=True,
    timeout=300  # 5 minutes max for data prep
)
```

---

### 3. **No exception handling for subprocess.TimeoutExpired**
**Location**: Lines 100-120

**Problem**: If training exceeds the 3600 second timeout, `subprocess.TimeoutExpired` is raised but NOT caught, causing the pipeline to crash ungracefully.

**Current Code**:
```python
result = subprocess.run(
    [sys.executable, "src/train_lora.py"],
    cwd=Config.BASE_DIR,
    capture_output=True,
    text=True,
    timeout=3600  # Can raise TimeoutExpired
)
```

**Fix**: Wrap in try-except:
```python
try:
    result = subprocess.run(
        [sys.executable, "src/train_lora.py"],
        cwd=Config.BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=3600
    )
except subprocess.TimeoutExpired:
    print("✗ Training exceeded 1 hour timeout")
    return False
```

---

### 4. **Incorrect output path construction**
**Location**: Lines 156-162

**Problem**: Uses `Config.PROCESSED_DATA` which may be undefined if Config import fails, or the path logic is fragile.

**Current Code**:
```python
adapter_dir = os.path.join(Config.BASE_DIR, "models/lora_adapters")
```

**Better Approach**: Use Path object:
```python
from pathlib import Path
adapter_dir = Path(Config.BASE_DIR) / "models" / "lora_adapters"
```

---

### 5. **Missing error handling in main()**
**Location**: Lines 224-244

**Problem**: The main function doesn't handle the case where prerequisites fail, or Config initialization fails.

**Current Code**:
```python
def main():
    """Main execution."""
    print_header("LORA FINE-TUNING PIPELINE")
    
    # Verify prerequisites
    if not verify_prerequisites():
        print("\n✗ Prerequisites check failed")
        return False
    # No error handling if verify_prerequisites() crashes
```

**Better Approach**: Add try-except wrapper.

---

## Summary of Fixes Needed

| Issue | Severity | Fix |
|-------|----------|-----|
| Missing PYTHONPATH in subprocess | **CRITICAL** | Add `env` param with PYTHONPATH |
| No timeout on data prep | High | Add `timeout=300` |
| No exception handling for TimeoutExpired | High | Wrap in try-except |
| Fragile path handling | Medium | Use pathlib.Path |
| No error handling in main | Medium | Add try-except |

---

## Corrected Code Template

```python
def run_data_preparation():
    """Run data preparation script."""
    print_header("PHASE 1: DATA PREPARATION")
    
    print("Preparing training data from synthetic QA pairs...")
    print("This will create: data/processed/lora_train_data.jsonl\n")
    
    # Setup environment
    env = os.environ.copy()
    env['PYTHONPATH'] = Config.BASE_DIR
    
    try:
        result = subprocess.run(
            [sys.executable, "src/prep_lora_data.py"],
            cwd=Config.BASE_DIR,
            env=env,  # <-- FIX 1
            capture_output=True,
            text=True,
            timeout=300  # <-- FIX 2: 5 minutes max
        )
    except subprocess.TimeoutExpired:
        print("✗ Data preparation timed out (> 5 minutes)")
        return False
    except Exception as e:
        print(f"✗ Subprocess error: {str(e)}")
        return False
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"✗ Data preparation failed with code {result.returncode}")
        return False
    
    print("✓ Data preparation completed")
    
    # Verify output
    lora_data_path = os.path.join(Config.PROCESSED_DATA, "lora_train_data.jsonl")
    if os.path.exists(lora_data_path):
        with open(lora_data_path) as f:
            lines = f.readlines()
        print(f"✓ Generated {len(lines)} training examples")
        print(f"✓ File size: {os.path.getsize(lora_data_path) / 1024:.1f} KB")
        return True
    else:
        print("✗ Training data file not found")
        return False


def run_training():
    """Run LoRA training script."""
    print_header("PHASE 2: LORA TRAINING")
    
    print("Starting LoRA fine-tuning...")
    print("This may take 10-15 minutes on Mac M1/M2/M3\n")
    
    # Setup environment
    env = os.environ.copy()
    env['PYTHONPATH'] = Config.BASE_DIR
    
    try:
        result = subprocess.run(
            [sys.executable, "src/train_lora.py"],
            cwd=Config.BASE_DIR,
            env=env,  # <-- FIX 1
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
    except subprocess.TimeoutExpired:
        print("✗ Training timed out (> 1 hour)")
        print("The training may still be running in the background")
        return False
    except Exception as e:
        print(f"✗ Subprocess error: {str(e)}")
        return False
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"✗ Training failed with code {result.returncode}")
        return False
    
    print("✓ Training completed")
    return True
```

---

## How to Apply Fixes

Choose one of the following:

### Option A: Use the corrected script (Recommended)
I will provide a corrected version of `run_lora_pipeline.py`

### Option B: Manual fixes
Apply the fixes shown above to your existing `run_lora_pipeline.py`

### Option C: Run scripts individually
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 src/prep_lora_data.py
python3 src/train_lora.py
```

---

## Verification Checklist

After fixing, verify:
- [ ] PYTHONPATH is set in subprocess `env` parameter
- [ ] Timeouts are set (300s for data prep, 3600s for training)
- [ ] TimeoutExpired exception is caught
- [ ] Path handling uses consistent methods
- [ ] Error messages are clear and actionable

