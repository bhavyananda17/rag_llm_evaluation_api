#!/usr/bin/env python3
"""
Comprehensive Test Suite for RAG vs LoRA QA Dataset Generator
Tests all components and validates the entire workflow
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.generate_data import QAGenerator


class ComprehensiveTestSuite:
    """Run all tests on the QA generation system."""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
    
    def print_header(self, title):
        """Print test section header."""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    
    def test_result(self, test_name, passed, details=""):
        """Record test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"      └─ {details}")
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "details": details
        })
    
    def run_all_tests(self):
        """Run all test suites."""
        self.print_header("TEST SUITE: Configuration & Setup")
        self.test_configuration()
        
        self.print_header("TEST SUITE: Module Import & Initialization")
        self.test_module_imports()
        
        self.print_header("TEST SUITE: Core Functionality")
        self.test_core_functionality()
        
        self.print_header("TEST SUITE: Output Files")
        self.test_output_files()
        
        self.print_header("TEST SUITE: Data Quality")
        self.test_data_quality()
        
        self.print_header("TEST SUITE: Analysis Module")
        self.test_analysis_module()
        
        self.print_summary()
    
    def test_configuration(self):
        """Test configuration setup."""
        # Check base directory
        base_dir_exists = os.path.isdir(Config.BASE_DIR)
        self.test_result(
            "Configuration: Base directory exists",
            base_dir_exists,
            f"Path: {Config.BASE_DIR}"
        )
        
        # Check raw data directory
        raw_data_exists = os.path.isdir(Config.RAW_DATA)
        self.test_result(
            "Configuration: Raw data directory exists",
            raw_data_exists,
            f"Path: {Config.RAW_DATA}"
        )
        
        # Check processed data directory
        processed_data_exists = os.path.isdir(Config.PROCESSED_DATA)
        self.test_result(
            "Configuration: Processed data directory exists",
            processed_data_exists,
            f"Path: {Config.PROCESSED_DATA}"
        )
        
        # Check for input files
        txt_files = list(Path(Config.RAW_DATA).glob("*.txt"))
        files_exist = len(txt_files) > 0
        self.test_result(
            "Configuration: Input text files found",
            files_exist,
            f"Found {len(txt_files)} .txt files"
        )
    
    def test_module_imports(self):
        """Test module imports and initialization."""
        try:
            from src.generate_data import QAGenerator
            self.test_result(
                "Import: QAGenerator class",
                True,
                "Successfully imported"
            )
        except Exception as e:
            self.test_result(
                "Import: QAGenerator class",
                False,
                str(e)
            )
        
        try:
            from src.config import Config
            self.test_result(
                "Import: Config class",
                True,
                "Successfully imported"
            )
        except Exception as e:
            self.test_result(
                "Import: Config class",
                False,
                str(e)
            )
        
        try:
            generator = QAGenerator()
            self.test_result(
                "Initialize: QAGenerator instance",
                True,
                "Instance created successfully"
            )
        except Exception as e:
            self.test_result(
                "Initialize: QAGenerator instance",
                False,
                str(e)
            )
    
    def test_core_functionality(self):
        """Test core generation functionality."""
        generator = QAGenerator()
        
        # Test chunk extraction
        sample_text = "This is a test. " * 200  # ~3200 characters
        chunks = generator.extract_chunks(sample_text, 2000)
        chunks_valid = len(chunks) > 0
        self.test_result(
            "Functionality: Text chunk extraction",
            chunks_valid,
            f"Extracted {len(chunks)} chunks from {len(sample_text)} chars"
        )
        
        # Test concept extraction
        test_chunk = """
        Self-attention mechanisms in Transformers enable models to capture
        contextual relationships. Cross-attention allows one sequence to attend
        to another. Hallucinations in language models refer to fabricated content.
        LoRA provides parameter-efficient fine-tuning. Retrieval-augmented
        generation combines retrieval with generation.
        """
        concepts = generator._extract_concepts(test_chunk)
        concepts_found = len(concepts) > 0
        self.test_result(
            "Functionality: Concept extraction",
            concepts_found,
            f"Found {len(concepts)} concepts: {', '.join(concepts[:3])}"
        )
        
        # Test question generation
        qa_pairs = generator._generate_qa_pairs_local(test_chunk, "test.txt")
        qa_generated = len(qa_pairs) > 0
        self.test_result(
            "Functionality: QA pair generation",
            qa_generated,
            f"Generated {len(qa_pairs)} QA pairs"
        )
        
        # Test validation
        if qa_pairs:
            first_pair = qa_pairs[0]
            is_valid = generator._validate_qa_pair(first_pair, test_chunk)
            self.test_result(
                "Functionality: QA pair validation",
                is_valid,
                "QA pair passed validation"
            )
    
    def test_output_files(self):
        """Test generated output files."""
        dataset_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
        
        # Check if main output exists
        file_exists = os.path.isfile(dataset_path)
        self.test_result(
            "Output: Main dataset file exists",
            file_exists,
            f"Path: {dataset_path}"
        )
        
        # Validate JSON
        if file_exists:
            try:
                with open(dataset_path, 'r') as f:
                    dataset = json.load(f)
                self.test_result(
                    "Output: JSON validity",
                    True,
                    "JSON parsed successfully"
                )
            except json.JSONDecodeError as e:
                self.test_result(
                    "Output: JSON validity",
                    False,
                    str(e)
                )
                return
            
            # Check metadata
            has_metadata = "metadata" in dataset
            self.test_result(
                "Output: Dataset metadata",
                has_metadata,
                "Metadata structure present"
            )
            
            # Check QA pairs
            qa_pairs = dataset.get("qa_pairs", [])
            has_qa_pairs = len(qa_pairs) > 0
            self.test_result(
                "Output: QA pairs present",
                has_qa_pairs,
                f"Found {len(qa_pairs)} QA pairs"
            )
            
            # Check file size
            file_size = os.path.getsize(dataset_path)
            size_valid = file_size > 1000  # At least 1KB
            self.test_result(
                "Output: File size",
                size_valid,
                f"File size: {file_size} bytes"
            )
    
    def test_data_quality(self):
        """Test quality of generated data."""
        dataset_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
        
        if not os.path.isfile(dataset_path):
            self.test_result("Data Quality: Load dataset", False, "Dataset not found")
            return
        
        with open(dataset_path, 'r') as f:
            dataset = json.load(f)
        
        qa_pairs = dataset.get("qa_pairs", [])
        
        # Check all pairs have required fields
        all_have_fields = all(
            all(field in pair for field in ["question", "answer", "reasoning_path", "difficulty"])
            for pair in qa_pairs
        )
        self.test_result(
            "Data Quality: Required fields present",
            all_have_fields,
            f"All {len(qa_pairs)} pairs have required fields"
        )
        
        # Check no empty content
        no_empty_content = all(
            pair.get("question", "").strip() and 
            pair.get("answer", "").strip()
            for pair in qa_pairs
        )
        self.test_result(
            "Data Quality: No empty content",
            no_empty_content,
            f"All {len(qa_pairs)} pairs have non-empty content"
        )
        
        # Check difficulty levels
        valid_difficulties = all(
            pair.get("difficulty") in ["Easy", "Medium", "Hard"]
            for pair in qa_pairs
        )
        self.test_result(
            "Data Quality: Valid difficulty levels",
            valid_difficulties,
            "All pairs have valid difficulty levels"
        )
        
        # Check answer grounding
        sourced_correctly = all(
            "source_file" in pair
            for pair in qa_pairs
        )
        self.test_result(
            "Data Quality: Source attribution",
            sourced_correctly,
            f"All {len(qa_pairs)} pairs attributed to source files"
        )
    
    def test_analysis_module(self):
        """Test analysis module functionality."""
        try:
            from analyze_dataset import QADatasetAnalyzer
            dataset_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
            
            if os.path.isfile(dataset_path):
                analyzer = QADatasetAnalyzer(dataset_path)
                self.test_result(
                    "Analysis: Module initialization",
                    True,
                    "Analyzer initialized successfully"
                )
                
                # Check exports directory
                exports_dir = os.path.join(Config.BASE_DIR, "data/exports")
                exports_exist = os.path.isdir(exports_dir)
                self.test_result(
                    "Analysis: Export directory",
                    exports_exist,
                    f"Exports directory present"
                )
                
                # Check export files
                csv_file = os.path.join(exports_dir, "qa_pairs.csv")
                csv_exists = os.path.isfile(csv_file)
                self.test_result(
                    "Analysis: CSV export",
                    csv_exists,
                    f"CSV file generated ({os.path.getsize(csv_file)} bytes)"
                )
                
                eval_file = os.path.join(exports_dir, "evaluation_format.json")
                eval_exists = os.path.isfile(eval_file)
                self.test_result(
                    "Analysis: Evaluation format export",
                    eval_exists,
                    f"Evaluation JSON generated ({os.path.getsize(eval_file)} bytes)"
                )
                
                rag_file = os.path.join(exports_dir, "rag_benchmark.json")
                rag_exists = os.path.isfile(rag_file)
                self.test_result(
                    "Analysis: RAG benchmark export",
                    rag_exists,
                    f"RAG benchmark generated ({os.path.getsize(rag_file)} bytes)"
                )
        except Exception as e:
            self.test_result(
                "Analysis: Module functionality",
                False,
                str(e)
            )
    
    def print_summary(self):
        """Print test summary."""
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"  TEST SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"Total Tests Run:      {total_tests}")
        print(f"Tests Passed:         {self.passed_tests} ✅")
        print(f"Tests Failed:         {self.failed_tests} {'❌' if self.failed_tests > 0 else ''}")
        print(f"Pass Rate:            {pass_rate:.1f}%")
        
        print(f"\n{'='*80}")
        if self.failed_tests == 0:
            print("  🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION 🎉")
        else:
            print(f"  ⚠️  {self.failed_tests} TEST(S) FAILED - REVIEW NEEDED")
        print(f"{'='*80}\n")
        
        return self.failed_tests == 0


def main():
    """Run comprehensive test suite."""
    print("\n" + "="*80)
    print("  RAG vs LoRA QA GENERATOR - COMPREHENSIVE TEST SUITE")
    print("="*80 + "\n")
    
    suite = ComprehensiveTestSuite()
    all_passed = suite.run_all_tests()
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
