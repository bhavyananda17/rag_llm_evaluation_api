#!/usr/bin/env python3
"""
RAG Example: Using Vector Store for Document Retrieval

Demonstrates how to use the VectorStore class to retrieve relevant
documents for RAG-based question answering.
"""

import json
import sys
import os
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.vector_db import VectorStore


class RAGExample:
    """Example RAG system using vector store for retrieval."""
    
    def __init__(self):
        """Initialize RAG system with pre-built vector store."""
        self.vector_store = VectorStore(model_name='all-MiniLM-L6-v2')
        
        # Load pre-built index
        index_path = os.path.join(Config.PROCESSED_DATA, "vector_index.faiss")
        if os.path.exists(index_path):
            print(f"Loading pre-built index from {index_path}...")
            self.vector_store.load_index(index_path)
            print("✓ Index loaded successfully")
        else:
            print(f"Index not found at {index_path}")
            print("Building new index...")
            input_dir = os.path.join(Config.BASE_DIR, "data/raw")
            self.vector_store.add_documents(input_dir)
            self.vector_store.save_index(index_path)
        
        # Load QA dataset
        qa_path = os.path.join(Config.PROCESSED_DATA, "synthetic_qa.json")
        with open(qa_path, 'r', encoding='utf-8') as f:
            self.qa_dataset = json.load(f)
    
    def answer_question(self, question: str, k: int = 3) -> Dict:
        """
        Answer a question using RAG retrieval.
        
        Args:
            question: Input question
            k: Number of documents to retrieve
            
        Returns:
            Dictionary with question, retrieved docs, and answer
        """
        print(f"\n{'='*70}")
        print(f"Question: {question}")
        print(f"{'='*70}\n")
        
        # Retrieve relevant documents
        results = self.vector_store.retrieve(question, k=k)
        
        print(f"Retrieved {len(results)} relevant document chunks:\n")
        
        retrieved_context = []
        for result in results:
            print(f"[{result['rank']}] Source: {result['source_file']}")
            print(f"    Similarity: {result['similarity_score']:.4f}")
            print(f"    Content: {result['chunk_text'][:100]}...\n")
            retrieved_context.append(result['chunk_text'])
        
        # Combine context
        context = "\n\n".join(retrieved_context)
        
        return {
            'question': question,
            'retrieved_documents': results,
            'context': context,
            'num_chunks': len(results)
        }
    
    def evaluate_qa_dataset(self) -> Dict:
        """
        Evaluate the QA dataset by retrieving relevant documents.
        
        Args:
            k: Number of documents to retrieve per question
            
        Returns:
            Evaluation statistics
        """
        print(f"\n{'='*70}")
        print("EVALUATING QA DATASET WITH RETRIEVAL")
        print(f"{'='*70}\n")
        
        qa_pairs = self.qa_dataset.get('qa_pairs', [])
        stats = {
            'total_questions': len(qa_pairs),
            'retrieved': 0,
            'source_match': 0,
            'details': []
        }
        
        for i, qa_pair in enumerate(qa_pairs[:5], 1):  # Show first 5
            question = qa_pair.get('question', '')
            source_file = qa_pair.get('source_file', '')
            
            results = self.vector_store.retrieve(question, k=3)
            
            # Check if original source was retrieved
            retrieved_sources = [r['source_file'] for r in results]
            source_match = source_file in retrieved_sources
            
            if source_match:
                stats['source_match'] += 1
            
            stats['retrieved'] += 1
            stats['details'].append({
                'question': question[:80] + '...',
                'original_source': source_file,
                'retrieved_sources': retrieved_sources,
                'source_match': source_match,
                'top_score': results[0]['similarity_score'] if results else 0
            })
            
            print(f"[{i}] {question[:80]}...")
            print(f"    Original source: {source_file}")
            print(f"    Retrieved: {retrieved_sources}")
            print(f"    Match: {'✓' if source_match else '✗'}")
            print()
        
        # Calculate match percentage
        if stats['retrieved'] > 0:
            stats['source_match_percentage'] = (stats['source_match'] / stats['retrieved']) * 100
        
        return stats


def main():
    """Main execution function."""
    
    print("\n" + "="*70)
    print("RAG EXAMPLE: VECTOR STORE FOR DOCUMENT RETRIEVAL")
    print("="*70)
    
    # Initialize RAG system
    try:
        rag = RAGExample()
    except Exception as e:
        print(f"✗ Error initializing RAG: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Example 1: Answer specific questions
    print("\n" + "="*70)
    print("EXAMPLE 1: ANSWERING QUESTIONS WITH RETRIEVAL")
    print("="*70)
    
    test_questions = [
        "What is the difference between self-attention and cross-attention?",
        "How does LoRA reduce memory requirements during fine-tuning?",
        "What are intrinsic and extrinsic hallucinations?",
        "How does RAG improve language model accuracy?",
        "What is the role of positional encodings in transformers?"
    ]
    
    for question in test_questions:
        result = rag.answer_question(question, k=2)
    
    # Example 2: Evaluate QA dataset
    print("\n" + "="*70)
    print("EXAMPLE 2: EVALUATING QA DATASET RETRIEVAL")
    print("="*70)
    
    eval_stats = rag.evaluate_qa_dataset()
    
    print(f"\n{'='*70}")
    print("EVALUATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total questions evaluated: {eval_stats['total_questions']}")
    print(f"Source match rate: {eval_stats['source_match_percentage']:.1f}%")
    print(f"({'='*70}\n")
    
    # Example 3: Vector store statistics
    print("Vector Store Statistics:")
    stats = rag.vector_store.get_index_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n{'='*70}")
    print("✓ RAG Example Complete")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
