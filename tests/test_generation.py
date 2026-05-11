#!/usr/bin/env python3
"""Simple test script to verify QA generation works."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.generate_data import QAGenerator
from src.config import Config

print("Starting QA Generation Test...")
print(f"Base directory: {Config.BASE_DIR}")
print(f"Raw data directory: {Config.RAW_DATA}")
print(f"Processed data directory: {Config.PROCESSED_DATA}")

# Initialize generator
generator = QAGenerator()

# Test with a small sample first
input_dir = os.path.join(Config.BASE_DIR, "data/raw")
output_file = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")

print(f"\nProcessing directory: {input_dir}")
print(f"Output file: {output_file}")

# Process directory
stats = generator.process_directory(input_dir, output_file)

print("\nGeneration complete!")
