# Exact Code Changes Required for run_lora_pipeline.py

## Summary
5 specific code changes needed. Below is the exact before/after for each.

---

## Change 1: Fix `run_data_preparation()` function

### Current Code (BROKEN - Lines 63-98)
```python
def run_data_preparation():
    """Run data preparation script."""
    print_header("PHASE 1: DATA PREPARATION")
    
    print("Preparing training data from synthetic QA pairs...")
    print("This will create: data/processed/lora_train_data.jsonl\n")
    
    result = subprocess.run(
        [sys.executable, "src/prep_lora_data.py"],
        cwd=Config.BASE_DIR,
        capture_output=True,
        text=True
    )
```

### Fixed Code
```python
def run_data_preparation():
    """Run data preparation script with proper environment setup."""
    print_header("PHASE 1: DATA PREPARATION")
    
    print("Preparing training data from synthetic QA pairs...")
    print("This will create: data/processed/lora_train_data.jsonl\n")
    
    # FIX #1: Setup environment with PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = Config.BASE_DIR
    
    try:
        # FIX #2: Add timeout for data preparation
        result = subprocess.run(
            [sys.executable, "src/prep_lora_data.py"],
            cwd=Config.BASE_DIR,
            env=env,  # Include PYTHONPATH for imports
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
    except subprocess.TimeoutExpired:
        # FIX #3: Handle timeout exception
        print("✗ Data preparation timed out (> 5 minutes)")
        return False
    except Exception as e:
        print(f"✗ Subprocess error: {str(e)}")
        return False
```

**Changes Summary**:
- Add lines: `env = os.environ.copy()` and `env['PYTHONPATH'] = Config.BASE_DIR`
- Add parameter: `env=env,`
- Add parameter: `timeout=300,`
- Wrap subprocess call in `try-except` block

---

## Change 2: Fix `run_training()` function

### Current Code (BROKEN - Lines 101-121)
```python
def run_training():
    """Run LoRA training script."""
    print_header("PHASE 2: LORA TRAINING")
    
    print("Starting LoRA fine-tuning...")
    print("This may take 10-15 minutes on Mac M1/M2/M3\n")
    
    result = subprocess.run(
        [sys.executable, "src/train_lora.py"],
        cwd=Config.BASE_DIR,
        capture_output=True,
        text=True,
        timeout=3600  # 1 hour timeout
    )
```

### Fixed Code
```python
def run_training():
    """Run LoRA training script with proper environment setup."""
    print_header("PHASE 2: LORA TRAINING")
    
    print("Starting LoRA fine-tuning...")
    print("This may take 10-15 minutes on Mac M1/M2/M3\n")
    
    # FIX #1: Setup environment with PYTHONPATH
    env = os.environ.copy()
    env['PYTHONPATH'] = Config.BASE_DIR
    
    try:
        # FIX #2: Add proper timeout handling
        result = subprocess.run(
            [sys.executable, "src/train_lora.py"],
            cwd=Config.BASE_DIR,
            env=env,  # Include PYTHONPATH for imports
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
    except subprocess.TimeoutExpired:
        # FIX #3: Handle timeout exception gracefully
        print("✗ Training timed out (> 1 hour)")
        print("The training may still be running in the background")
        return False
    except Exception as e:
        print(f"✗ Subprocess error: {str(e)}")
        return False
```

**Changes Summary**:
- Add lines: `env = os.environ.copy()` and `env['PYTHONPATH'] = Config.BASE_DIR`
- Add parameter: `env=env,`
- Wrap subprocess call in `try-except` block to catch `TimeoutExpired`

---

## Change 3: Update `print_summary()` function

### Current Code (INCOMPLETE - Lines 172-188)
```python
    else:
        print("✗ PIPELINE FAILED\n")
        print("Please check the error messages above.")
        print("Common issues:")
        print("  - Missing dependencies: pip install -r requirements-lora.txt")
        print("  - Out of memory: Reduce batch size in train_lora.py")
        print("  - Missing data: Run src/prep_lora_data.py first")
    
    print("\n" + "="*70)
```

### Fixed Code
```python
    else:
        print("✗ PIPELINE FAILED\n")
        print("Please check the error messages above.")
        print("Common issues:")
        print("  - Missing dependencies: pip install -r requirements-lora.txt")
        print("  - Out of memory: Reduce batch size in train_lora.py")
        print("  - Missing data: Run src/prep_lora_data.py first")
        print("  - PYTHONPATH not set: export PYTHONPATH=$PYTHONPATH:$(pwd)")
    
    print("\n" + "="*70)
```

**Changes Summary**:
- Add one line for PYTHONPATH troubleshooting tip

---

## Change 4: Update docstring

### Current Code
```python
"""
Complete LoRA Pipeline Execution

Runs the entire LoRA fine-tuning pipeline:
1. Data preparation (prep_lora_data.py)
2. Model training (train_lora.py)
3. Results verification
"""
```

### Fixed Code
```python
"""
Complete LoRA Pipeline Execution - FIXED VERSION

Runs the entire LoRA fine-tuning pipeline:
1. Data preparation (prep_lora_data.py)
2. Model training (train_lora.py)
3. Results verification

FIXES APPLIED:
- Added PYTHONPATH to subprocess env for proper imports
- Added timeout handling for data preparation
- Added exception handling for subprocess.TimeoutExpired
- Improved error messages and logging
"""
```

**Changes Summary**:
- Update title and add fixes note

---

## Change 5: Already exists - No change needed for main()

The `main()` function already has try-except in the `if __name__ == "__main__"` block, so no changes needed there.

---

## Summary of All Changes

| Function | Change | Lines | Type |
|----------|--------|-------|------|
| run_data_preparation() | Add env setup | 63-98 | Add 8 lines |
| run_training() | Add env setup + exception handling | 101-121 | Add 8 lines |
| print_summary() | Add PYTHONPATH tip | 180 | Add 1 line |
| Module docstring | Update docstring | 2-9 | Update 8 lines |
| **TOTAL** | **4 functions** | - | **+17 lines** |

---

## Minimal Patch Format

If you want to apply fixes as a patch, here are the minimal changes:

```diff
--- a/run_lora_pipeline.py
+++ b/run_lora_pipeline.py
@@ -1,9 +1,17 @@
 #!/usr/bin/env python3
 """
-Complete LoRA Pipeline Execution
+Complete LoRA Pipeline Execution - FIXED VERSION
 
 Runs the entire LoRA fine-tuning pipeline:
 1. Data preparation (prep_lora_data.py)
 2. Model training (train_lora.py)
 3. Results verification
+
+FIXES APPLIED:
+- Added PYTHONPATH to subprocess env for proper imports
+- Added timeout handling for data preparation
+- Added exception handling for subprocess.TimeoutExpired
+- Improved error messages and logging
 """

@@ -63,6 +71,11 @@ def verify_prerequisites():
 def run_data_preparation():
     """Run data preparation script."""
     print_header("PHASE 1: DATA PREPARATION")
+    
+    # FIX #1: Setup environment with PYTHONPATH
+    env = os.environ.copy()
+    env['PYTHONPATH'] = Config.BASE_DIR
+    
+    try:
         print("Preparing training data from synthetic QA pairs...")
         print("This will create: data/processed/lora_train_data.jsonl\n")
@@ -70,10 +83,22 @@ def run_data_preparation():
         result = subprocess.run(
             [sys.executable, "src/prep_lora_data.py"],
             cwd=Config.BASE_DIR,
+            env=env,
             capture_output=True,
             text=True
+            timeout=300
+        )
+    except subprocess.TimeoutExpired:
+        print("✗ Data preparation timed out (> 5 minutes)")
+        return False
+    except Exception as e:
+        print(f"✗ Subprocess error: {str(e)}")
+        return False

@@ -101,6 +126,10 @@ def run_training():
     print("Starting LoRA fine-tuning...")
     print("This may take 10-15 minutes on Mac M1/M2/M3\n")
     
+    # FIX #1: Setup environment with PYTHONPATH
+    env = os.environ.copy()
+    env['PYTHONPATH'] = Config.BASE_DIR
+    
+    try:
         result = subprocess.run(
             [sys.executable, "src/train_lora.py"],
             cwd=Config.BASE_DIR,
+            env=env,
             capture_output=True,
             text=True,
@@ -108,6 +137,12 @@ def run_training():
         )
         
+    except subprocess.TimeoutExpired:
+        print("✗ Training timed out (> 1 hour)")
+        print("The training may still be running in the background")
+        return False
+    except Exception as e:
+        print(f"✗ Subprocess error: {str(e)}")
+        return False
     print(result.stdout)

@@ -175,6 +210,7 @@ def print_summary(success):
         print("  - Missing dependencies: pip install -r requirements-lora.txt")
         print("  - Out of memory: Reduce batch size in train_lora.py")
         print("  - Missing data: Run src/prep_lora_data.py first")
+        print("  - PYTHONPATH not set: export PYTHONPATH=$PYTHONPATH:$(pwd)")
```

---

## Verification

After applying changes, verify:

1. **Syntax check**:
   ```bash
   python3 -m py_compile run_lora_pipeline.py
   ```
   Should output nothing if no syntax errors.

2. **Quick test**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   python3 run_lora_pipeline.py
   ```
   Should show proper error handling and PYTHONPATH setup.

---

## Priority of Fixes

1. **MUST FIX**: Change 1 (PYTHONPATH in data prep) - Without this, pipeline fails 100%
2. **MUST FIX**: Change 2 (PYTHONPATH in training) - Without this, pipeline fails 100%
3. **SHOULD FIX**: Change 1 timeout + exceptions - Prevents indefinite hangs
4. **SHOULD FIX**: Change 2 exceptions - Prevents unhandled crashes
5. **NICE TO HAVE**: Change 3 - Improves user experience

---

**Total Effort**: 5-10 minutes to apply all changes
**Difficulty**: EASY (straightforward additions)
**Impact**: CRITICAL (fixes 100% failure rate)

