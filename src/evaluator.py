#!/usr/bin/env python3
"""
Unified Model Evaluator for Triple Comparison (Base vs RAG vs LoRA)

This module provides a unified evaluator class that can generate responses
from three different model modes:
1. Base: Direct Gemini API call (baseline)
2. RAG: Gemini API with vector store context retrieval
3. LoRA: Local inference with LoRA-adapted model

Includes latency tracking and comprehensive result logging.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.model_client import CachedGeminiClient
from src.vector_db import VectorStore


class ModelEvaluator:
    """
    Unified evaluator for comparing Base, RAG, and LoRA model responses.
    
    Features:
    - Consistent interface across all three modes
    - Automatic latency measurement
    - Error handling and graceful degradation
    - Comprehensive logging and result tracking
    """
    
    def __init__(self, 
                 use_cache: bool = True,
                 lora_adapter_path: Optional[str] = None,
                 vector_store_index: Optional[str] = None):
        """
        Initialize the evaluator with all three models.
        
        Args:
            use_cache: Enable caching for Gemini API calls
            lora_adapter_path: Path to LoRA adapter directory
            vector_store_index: Path to FAISS vector store index
        """
        self.logger = self._setup_logger()
        
        # Initialize Gemini client for base and RAG modes
        self.logger.info("Initializing Gemini client...")
        self.gemini_client = CachedGeminiClient(use_cache=use_cache)
        self.logger.info("✓ Gemini client initialized")
        
        # Initialize vector store for RAG mode
        self.logger.info("Initializing vector store...")
        self.vector_store = VectorStore()
        
        # Try to load existing vector store index
        if vector_store_index and os.path.exists(vector_store_index):
            self.vector_store.load_index(vector_store_index)
            self.logger.info(f"✓ Vector store loaded from {vector_store_index}")
        else:
            self.logger.warning("Vector store index not found. RAG mode may not work.")
            self.vector_store = None
        
        # Initialize LoRA model
        self.lora_model = None
        self.lora_adapter_path = lora_adapter_path
        if lora_adapter_path:
            self.logger.info("Initializing LoRA model...")
            self._initialize_lora_model(lora_adapter_path)
        else:
            self.logger.warning("LoRA adapter path not provided. LoRA mode unavailable.")
        
        # Statistics tracking
        self.stats = {
            'total_questions': 0,
            'successful_base': 0,
            'successful_rag': 0,
            'successful_lora': 0,
            'failed_base': 0,
            'failed_rag': 0,
            'failed_lora': 0,
            'total_latency_base': 0.0,
            'total_latency_rag': 0.0,
            'total_latency_lora': 0.0,
        }
    
    def _setup_logger(self):
        """Setup simple logger for tracking."""
        class SimpleLogger:
            def info(self, msg):
                print(f"[INFO] {msg}")
            
            def warning(self, msg):
                print(f"[WARN] {msg}")
            
            def error(self, msg):
                print(f"[ERROR] {msg}")
        
        return SimpleLogger()
    
    def _initialize_lora_model(self, adapter_path: str):
        """
        Initialize LoRA-adapted model using PEFT.
        
        Args:
            adapter_path: Path to LoRA adapter directory
        """
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import PeftModel
            
            base_model_name = "google/gemma-2-2b-it"
            
            self.logger.info(f"Loading base model: {base_model_name}")
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                device_map="auto",
                torch_dtype="auto"
            )
            
            self.logger.info(f"Loading LoRA adapter from: {adapter_path}")
            self.lora_model = PeftModel.from_pretrained(base_model, adapter_path)
            
            # Load tokenizer
            self.lora_tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            
            self.logger.info("✓ LoRA model initialized")
        
        except ImportError as e:
            self.logger.error(f"Missing required libraries for LoRA: {e}")
            self.logger.error("Install with: pip install peft transformers torch")
            self.lora_model = None
        except Exception as e:
            self.logger.error(f"Failed to initialize LoRA model: {e}")
            self.lora_model = None
    
    def get_answer(self, 
                   question: str, 
                   mode: str = 'base') -> Dict[str, any]:
        """
        Get an answer for a question using the specified mode.
        
        Args:
            question: The question to answer
            mode: 'base', 'rag', or 'lora'
        
        Returns:
            Dictionary with keys:
            - response: The generated response text
            - latency: Time taken in seconds
            - success: Whether the query succeeded
            - error: Error message if failed (None otherwise)
            - mode: The mode used
        """
        if mode == 'base':
            return self._get_base_answer(question)
        elif mode == 'rag':
            return self._get_rag_answer(question)
        elif mode == 'lora':
            return self._get_lora_answer(question)
        else:
            return {
                'response': '',
                'latency': 0.0,
                'success': False,
                'error': f'Unknown mode: {mode}',
                'mode': mode
            }
    
    def _get_base_answer(self, question: str) -> Dict[str, any]:
        """Get answer using base Gemini API."""
        start_time = time.time()
        
        try:
            response = self.gemini_client.generate(question)
            latency = time.time() - start_time
            
            self.stats['successful_base'] += 1
            self.stats['total_latency_base'] += latency
            
            return {
                'response': response,
                'latency': latency,
                'success': True,
                'error': None,
                'mode': 'base'
            }
        except Exception as e:
            latency = time.time() - start_time
            self.stats['failed_base'] += 1
            self.logger.error(f"Base mode failed: {str(e)}")
            
            return {
                'response': '',
                'latency': latency,
                'success': False,
                'error': str(e),
                'mode': 'base'
            }
    
    def _get_rag_answer(self, question: str) -> Dict[str, any]:
        """Get answer using RAG (retrieval-augmented generation)."""
        start_time = time.time()
        
        if self.vector_store is None:
            return {
                'response': '',
                'latency': 0.0,
                'success': False,
                'error': 'Vector store not initialized',
                'mode': 'rag'
            }
        
        try:
            # Retrieve relevant context
            retrieval_start = time.time()
            results = self.vector_store.search(question, top_k=3)
            retrieval_time = time.time() - retrieval_start
            
            # Build context from retrieved documents
            context = "\n\n".join([
                f"Document {i+1}:\n{result['text']}"
                for i, result in enumerate(results)
            ])
            
            # Create augmented prompt
            augmented_prompt = f"""Use the following context to answer the question.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""
            
            # Generate response with context
            response = self.gemini_client.generate(augmented_prompt)
            latency = time.time() - start_time
            
            self.stats['successful_rag'] += 1
            self.stats['total_latency_rag'] += latency
            
            return {
                'response': response,
                'latency': latency,
                'retrieval_time': retrieval_time,
                'success': True,
                'error': None,
                'context_count': len(results),
                'mode': 'rag'
            }
        except Exception as e:
            latency = time.time() - start_time
            self.stats['failed_rag'] += 1
            self.logger.error(f"RAG mode failed: {str(e)}")
            
            return {
                'response': '',
                'latency': latency,
                'success': False,
                'error': str(e),
                'mode': 'rag'
            }
    
    def _get_lora_answer(self, question: str) -> Dict[str, any]:
        """Get answer using locally loaded LoRA-adapted model."""
        start_time = time.time()
        
        if self.lora_model is None:
            return {
                'response': '',
                'latency': 0.0,
                'success': False,
                'error': 'LoRA model not initialized',
                'mode': 'lora'
            }
        
        try:
            # Prepare input
            inputs = self.lora_tokenizer(
                question,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # Generate response
            generation_start = time.time()
            with torch.no_grad():
                outputs = self.lora_model.generate(
                    **inputs,
                    max_length=256,
                    num_beams=1,
                    do_sample=False,
                    temperature=0.7,
                    top_p=0.9
                )
            
            # Decode response
            response_text = self.lora_tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            latency = time.time() - start_time
            
            self.stats['successful_lora'] += 1
            self.stats['total_latency_lora'] += latency
            
            return {
                'response': response_text,
                'latency': latency,
                'success': True,
                'error': None,
                'mode': 'lora'
            }
        except Exception as e:
            latency = time.time() - start_time
            self.stats['failed_lora'] += 1
            self.logger.error(f"LoRA mode failed: {str(e)}")
            
            return {
                'response': '',
                'latency': latency,
                'success': False,
                'error': str(e),
                'mode': 'lora'
            }
    
    def run_full_comparison(self, 
                           qa_file: str = None,
                           output_file: str = None) -> Dict:
        """
        Run full comparison across all three modes for all QA pairs.
        
        Args:
            qa_file: Path to QA pairs JSON file
            output_file: Path to save results
        
        Returns:
            Results dictionary with all comparisons
        """
        # Set default paths
        if qa_file is None:
            qa_file = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
        
        if output_file is None:
            output_file = os.path.join(Config.BASE_DIR, "data/results/final_comparison.json")
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info("STARTING TRIPLE COMPARISON EVALUATION")
        self.logger.info(f"{'='*70}\n")
        
        # Load QA pairs
        self.logger.info(f"Loading QA pairs from {qa_file}")
        with open(qa_file, 'r') as f:
            qa_data = json.load(f)
        
        qa_pairs = qa_data.get('qa_pairs', [])
        self.logger.info(f"✓ Loaded {len(qa_pairs)} QA pairs\n")
        
        # Run evaluation
        results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_questions': len(qa_pairs),
                'qa_source': qa_file,
                'output_file': output_file
            },
            'comparisons': []
        }
        
        self.stats['total_questions'] = len(qa_pairs)
        
        for idx, qa_pair in enumerate(qa_pairs, 1):
            question = qa_pair.get('question', '')
            ground_truth = qa_pair.get('answer', '')
            
            self.logger.info(f"[{idx}/{len(qa_pairs)}] Processing: {question[:60]}...")
            
            # Get answers from all three modes
            base_result = self.get_answer(question, mode='base')
            rag_result = self.get_answer(question, mode='rag')
            lora_result = self.get_answer(question, mode='lora')
            
            # Compile comparison
            comparison = {
                'question_id': idx,
                'question': question,
                'ground_truth': ground_truth,
                'source_file': qa_pair.get('source_file', 'unknown'),
                'difficulty': qa_pair.get('difficulty', 'unknown'),
                'base': {
                    'response': base_result.get('response', ''),
                    'latency': base_result.get('latency', 0.0),
                    'success': base_result.get('success', False),
                    'error': base_result.get('error', None)
                },
                'rag': {
                    'response': rag_result.get('response', ''),
                    'latency': rag_result.get('latency', 0.0),
                    'success': rag_result.get('success', False),
                    'error': rag_result.get('error', None),
                    'retrieval_time': rag_result.get('retrieval_time', None),
                    'context_count': rag_result.get('context_count', 0)
                },
                'lora': {
                    'response': lora_result.get('response', ''),
                    'latency': lora_result.get('latency', 0.0),
                    'success': lora_result.get('success', False),
                    'error': lora_result.get('error', None)
                }
            }
            
            results['comparisons'].append(comparison)
            
            # Print summary for this question
            self.logger.info(f"  Base: {base_result.get('latency', 0):.3f}s - "
                           f"{'✓' if base_result.get('success') else '✗'}")
            self.logger.info(f"  RAG:  {rag_result.get('latency', 0):.3f}s - "
                           f"{'✓' if rag_result.get('success') else '✗'}")
            self.logger.info(f"  LoRA: {lora_result.get('latency', 0):.3f}s - "
                           f"{'✓' if lora_result.get('success') else '✗'}")
            self.logger.info("")
        
        # Add statistics
        results['statistics'] = {
            'base': {
                'successful': self.stats['successful_base'],
                'failed': self.stats['failed_base'],
                'success_rate': (self.stats['successful_base'] / self.stats['total_questions'] 
                               if self.stats['total_questions'] > 0 else 0),
                'avg_latency': (self.stats['total_latency_base'] / self.stats['successful_base']
                              if self.stats['successful_base'] > 0 else 0)
            },
            'rag': {
                'successful': self.stats['successful_rag'],
                'failed': self.stats['failed_rag'],
                'success_rate': (self.stats['successful_rag'] / self.stats['total_questions']
                               if self.stats['total_questions'] > 0 else 0),
                'avg_latency': (self.stats['total_latency_rag'] / self.stats['successful_rag']
                              if self.stats['successful_rag'] > 0 else 0)
            },
            'lora': {
                'successful': self.stats['successful_lora'],
                'failed': self.stats['failed_lora'],
                'success_rate': (self.stats['successful_lora'] / self.stats['total_questions']
                               if self.stats['total_questions'] > 0 else 0),
                'avg_latency': (self.stats['total_latency_lora'] / self.stats['successful_lora']
                              if self.stats['successful_lora'] > 0 else 0)
            }
        }
        
        # Save results
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info("EVALUATION COMPLETE")
        self.logger.info(f"{'='*70}")
        self.logger.info(f"Results saved to: {output_file}\n")
        
        # Print statistics summary
        self._print_statistics_summary(results)
        
        return results
    
    def _print_statistics_summary(self, results: Dict):
        """Print a formatted summary of statistics."""
        stats = results.get('statistics', {})
        
        self.logger.info(f"\n{'='*70}")
        self.logger.info("PERFORMANCE STATISTICS")
        self.logger.info(f"{'='*70}\n")
        
        for mode in ['base', 'rag', 'lora']:
            mode_stats = stats.get(mode, {})
            self.logger.info(f"{mode.upper():>6} Mode:")
            self.logger.info(f"  Success Rate: {mode_stats.get('success_rate', 0)*100:.1f}% "
                           f"({mode_stats.get('successful', 0)}/{results['metadata']['total_questions']})")
            self.logger.info(f"  Avg Latency: {mode_stats.get('avg_latency', 0):.3f}s")
            self.logger.info("")


# Optional: For LoRA inference with torch
try:
    import torch
except ImportError:
    torch = None


if __name__ == "__main__":
    # Example usage
    evaluator = ModelEvaluator(
        use_cache=True,
        lora_adapter_path=os.path.join(Config.BASE_DIR, "models/lora_adapters")
    )
    
    # Run full evaluation
    results = evaluator.run_full_comparison()
    
    print("\nEvaluation complete! Results saved to data/results/final_comparison.json")
