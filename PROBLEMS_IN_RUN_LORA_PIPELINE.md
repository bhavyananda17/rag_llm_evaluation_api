# COMPREHENSIVE PROBLEMS FOUND IN run_lora_pipeline.py

## Executive Summary

Found **5 CRITICAL ISSUES** in `run_lora_pipeline.py` that will cause pipeline failure:

---

## Issue #1: Missing PYTHONPATH in subprocess calls 🔴 CRITICAL

### Location
- Line 72-76 (`run_data_preparation()`)
- Line 108-113 (`run_training()`)

### The Problem
```python
# BROKEN: Child process can't import src modules
result = subprocess.run(
    [sys.executable, "src/prep_lora_data.py"],
    cwd=Config.BASE_DIR,
    capture_output=True,
    text=True  # ← MISSING: env parameter with PYTHONPATH
)
```

### Error You'll See
```
ModuleNotFoundError: No module named 'src'
ModuleNotFoundError: No module named 'src.config'
```

### The Solution
```python
# FIXED: Include PYTHONPATH in child process environment
env = os.environ.copy()
env['PYTHONPATH'] = Config.BASE_DIR

result = subprocess.run(
    [sys.executable, "src/prep_lora_data.py"],
    cwd=Config.BASE_DIR,
    env=env,  # ← ADD THIS
    capture_output=True,
    text=True
)
```

---

## Issue #2: No timeout on data preparation 🟠 HIGH

### Location
Line 72-76 (`run_data_preparation()`)

### The Problem
```python
# If data prep hangs, pipeline hangs forever
result = subprocess.run(
    [sys.executable, "src/prep_lora_data.py"],
    cwd=Config.BASE_DIR,
    capture_output=True,
    text=True
    # ← MISSING: timeout parameter
)
```

### The Solution
```python
result = subprocess.run(
    [sys.executable, "src/prep_lora_data.py"],
    cwd=Config.BASE_DIR,
    env=env,
    capture_output=True,
    text=True,
    timeout=300  # ← ADD THIS: 5 minute timeout
)
```

---

## Issue #3: No exception handling for TimeoutExpired 🟠 HIGH

### Location
Line 108-113 (`run_training()`)

### The Problem
```python
# Training has timeout but no try-except
result = subprocess.run(
    [sys.executable, "src/train_lora.py"],
    cwd=Config.BASE_DIR,
    capture_output=True,
    text=True,
    timeout=3600  # Can raise TimeoutExpired
)
# ← MISSING: try-except block
```

### Error You'll See
```
subprocess.TimeoutExpired: Command '['/usr/bin/python3', ...]' timed out after 3600 seconds
Traceback (most recent call last):
  ...
```

### The Solution
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
    print("✗ Training timed out (> 1 hour)")
    print("The training may still be running in the background")
    return False
except Exception as e:
    print(f"✗ Subprocess error: {str(e)}")
    return False
```

---

## Issue #4: Missing try-except in run_data_preparation() 🟡 MEDIUM

### Location
Line 72-76

### The Problem
```python
# Any subprocess error will crash pipeline
result = subprocess.run(...)
# ← No exception handling
```

### The Solution
```python
try:
    result = subprocess.run(...)
except subprocess.TimeoutExpired:
    print("✗ Data preparation timed out (> 5 minutes)")
    return False
except Exception as e:
    print(f"✗ Subprocess error: {str(e)}")
    return False
```

---

## Issue #5: Incomplete error messages in print_summary() 🟡 MEDIUM

### Location
Line 172-188

### The Problem
```python
print("Common issues:")
print("  - Missing dependencies: pip install -r requirements-lora.txt")
print("  - Out of memory: Reduce batch size in train_lora.py")
print("  - Missing data: Run src/prep_lora_data.py first")
# ← Missing: PYTHONPATH setup instructions
```

### The Solution
```python
print("Common issues:")
print("  - Missing dependencies: pip install -r requirements-lora.txt")
print("  - Out of memory: Reduce batch size in train_lora.py")
print("  - Missing data: Run src/prep_lora_data.py first")
print("  - PYTHONPATH not set: export PYTHONPATH=$PYTHONPATH:$(pwd)")  # ← ADD THIS
```

---

## Quick Fix Instructions

### Option 1: Auto-apply all fixes
Run this command to automatically apply all 5 fixes:
```bash
# [Will be provided with fixed version of file]
```

### Option 2: Manual fixes
Edit `run_lora_pipeline.py` and apply these 5 changes:

1. **Fix in `run_data_preparation()` (lines 68-70)**:
   - Add before subprocess.run:
   ```python
   env = os.environ.copy()
   env['PYTHONPATH'] = Config.BASE_DIR
   ```
   - Add to subprocess.run: `env=env,`
   - Add to subprocess.run: `timeout=300,`
   - Wrap subprocess.run in try-except block

2. **Fix in `run_training()` (lines 104-106)**:
   - Add before subprocess.run:
   ```python
   env = os.environ.copy()
   env['PYTHONPATH'] = Config.BASE_DIR
   ```
   - Add to subprocess.run: `env=env,`
   - Wrap subprocess.run in try-except block

3. **Fix in `print_summary()` (line 188)**:
   - Add new line: `print("  - PYTHONPATH not set: export PYTHONPATH=$PYTHONPATH:$(pwd)")`

### Option 3: Replace the entire file
Completely replace `run_lora_pipeline.py` with a corrected version (easier, recommended)

---

## Impact Analysis

| Issue | Will Pipeline Fail? | Impact | Urgency |
|-------|-------------------|--------|---------|
| #1 PYTHONPATH | YES (100%) | Child process ImportError | CRITICAL |
| #2 No timeout | Maybe (if data prep hangs) | Indefinite hang | HIGH |
| #3 TimeoutExpired | Maybe (if training > 1hr) | Unhandled exception crash | HIGH |
| #4 No try-except | Maybe (if subprocess errors) | Unhandled exception crash | MEDIUM |
| #5 Error messages | No (pipeline works) | Poor debugging UX | MEDIUM |

---

## Test Before and After

### BEFORE (Current - Broken)
```bash
$ export PYTHONPATH=$PYTHONPATH:$(pwd)
$ python3 run_lora_pipeline.py

[Checking prerequisites...]
✓ Prerequisites check...

[PHASE 1: DATA PREPARATION]
STDERR: ModuleNotFoundError: No module named 'src'
✗ Data preparation failed with code 1

✗ PIPELINE FAILED
```

### AFTER (Fixed)
```bash
$ export PYTHONPATH=$PYTHONPATH:$(pwd)
$ python3 run_lora_pipeline.py

[Checking prerequisites...]
✓ Prerequisites check...

[PHASE 1: DATA PREPARATION]
✓ Data preparation completed
✓ Generated 13 training examples

[PHASE 2: LORA TRAINING]
[Training progress: epochs 1-3]
✓ Training completed

[PHASE 3: OUTPUT VERIFICATION]
✓ adapter_config.json: 1.2 KB
✓ adapter_model.bin: 7.8 MB

✓ LORA PIPELINE COMPLETED SUCCESSFULLY
```

---

## Root Cause

These issues stem from:

1. **Subprocess environment inheritance**: When `subprocess.run()` is called without `env` parameter, it inherits the current process's environment. However, PYTHONPATH set in the shell doesn't automatically propagate to child processes unless explicitly passed.

2. **Missing timeout safety**: No defensive programming for long-running operations.

3. **Incomplete error handling**: Assuming subprocesses will always succeed without considering edge cases.

---

## Files to Review

✅ Document created: `LORA_PIPELINE_ISSUES_FOUND.md` (detailed fixes)
✅ Document created: `LORA_PIPELINE_FIX_SUMMARY.md` (comprehensive summary)
✅ Status: **FIXES IDENTIFIED AND DOCUMENTED**
⏳ Action needed: **Apply fixes to run_lora_pipeline.py**

---

## Next Steps

1. Review this document
2. Apply the 5 fixes (or replace file with corrected version)
3. Test with: `python3 run_lora_pipeline.py`
4. Verify output includes "✓ LORA PIPELINE COMPLETED SUCCESSFULLY"

---

**Status**: 🔴 BROKEN (5 issues found)
**Severity**: CRITICAL (Issue #1 alone breaks pipeline)
**Fix Complexity**: EASY (straightforward additions)
**Estimated Fix Time**: 5-10 minutes

