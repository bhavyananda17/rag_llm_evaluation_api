"""
Vector Store Implementation for RAG Document Retrieval

This module provides a FAISS-based vector store for efficient semantic search
over document collections. It uses sentence transformers to encode documents
and queries into dense vector embeddings.
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import faiss
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config


class VectorStore:
    """
    FAISS-based vector store for semantic document retrieval.
    
    Handles document chunking, embedding generation, index building,
    and similarity search for RAG applications.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', use_gpu: bool = False):
        """
        Initialize the vector store with a sentence transformer model.
        
        Args:
            model_name: Name of the SentenceTransformer model to use
            use_gpu: Whether to use GPU for embeddings (if available)
        """
        self.model_name = model_name
        self.use_gpu = use_gpu
        
        # Load sentence transformer model
        print(f"Loading SentenceTransformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Load tokenizer for token-based chunking
        self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
        
        # Initialize FAISS index (will be set in add_documents)
        self.index = None
        self.documents = []  # Store original document text
        self.metadata = []   # Store metadata for each chunk
        
        # Embedding dimension
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        print(f"✓ Model loaded: {model_name}")
        print(f"✓ Embedding dimension: {self.embedding_dim}")
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
        """
        Chunk text into token-based segments with overlap.
        
        Args:
            text: Input text to chunk
            chunk_size: Target number of tokens per chunk
            overlap: Number of overlapping tokens between chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Tokenize the text
        tokens = self.tokenizer.tokenize(text)
        
        chunks = []
        step = chunk_size - overlap
        
        for i in range(0, len(tokens), step):
            chunk_tokens = tokens[i : i + chunk_size]
            
            # Skip very small chunks
            if len(chunk_tokens) < chunk_size * 0.5:
                continue
            
            # Convert tokens back to text
            chunk_text = self.tokenizer.convert_tokens_to_string(chunk_tokens)
            
            chunks.append({
                'text': chunk_text,
                'start_token': i,
                'end_token': min(i + chunk_size, len(tokens)),
                'token_count': len(chunk_tokens)
            })
        
        return chunks
    
    def add_documents(self, directory_path: str, chunk_size: int = 500, chunk_overlap: int = 100) -> Dict:
        """
        Read all .txt files from directory, chunk them, and compute embeddings.
        
        Args:
            directory_path: Path to directory containing .txt files
            chunk_size: Target tokens per chunk
            chunk_overlap: Overlapping tokens between chunks
            
        Returns:
            Dictionary with statistics about indexed documents
        """
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory not found: {directory_path}")
        
        print(f"\n{'='*70}")
        print(f"Building Vector Index from: {directory_path}")
        print(f"{'='*70}\n")
        
        all_embeddings = []
        all_chunks = []
        stats = {
            'total_files': 0,
            'total_chunks': 0,
            'files_processed': []
        }
        
        # Get all .txt files
        txt_files = sorted(Path(directory_path).glob("*.txt"))
        
        if not txt_files:
            raise ValueError(f"No .txt files found in {directory_path}")
        
        # Process each file
        for txt_file in txt_files:
            file_name = txt_file.name
            print(f"Processing: {file_name}")
            
            try:
                # Read file
                with open(txt_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Chunk the text
                chunks = self._chunk_text(text, chunk_size=chunk_size, overlap=chunk_overlap)
                print(f"  → Extracted {len(chunks)} chunks")
                
                # Encode chunks
                chunk_texts = [chunk['text'] for chunk in chunks]
                embeddings = self.model.encode(chunk_texts, show_progress_bar=False)
                
                # Store chunks and embeddings
                for chunk, embedding in zip(chunks, embeddings):
                    chunk['source_file'] = file_name
                    all_chunks.append(chunk)
                    all_embeddings.append(embedding)
                
                stats['total_files'] += 1
                stats['files_processed'].append({
                    'file': file_name,
                    'chunks': len(chunks)
                })
                
                print(f"  → Encoded {len(chunks)} embeddings")
            
            except Exception as e:
                print(f"  ✗ Error processing {file_name}: {str(e)}")
                continue
        
        if not all_embeddings:
            raise ValueError("No embeddings were generated from the documents")
        
        # Convert to numpy array
        embeddings_array = np.array(all_embeddings, dtype=np.float32)
        
        # Create FAISS index
        print(f"\nCreating FAISS index...")
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.index.add(embeddings_array)
        
        # Store documents and metadata
        self.documents = all_chunks
        self.metadata = [{
            'source_file': chunk['source_file'],
            'start_token': chunk['start_token'],
            'end_token': chunk['end_token'],
            'token_count': chunk['token_count']
        } for chunk in all_chunks]
        
        stats['total_chunks'] = len(all_chunks)
        
        print(f"\n{'='*70}")
        print(f"✓ Index created successfully")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Embedding dimension: {self.embedding_dim}")
        print(f"  Index size: {embeddings_array.nbytes / 1024 / 1024:.2f} MB")
        print(f"{'='*70}\n")
        
        return stats
    
    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        """
        Retrieve the top k most similar document chunks for a query.
        
        Args:
            query: Input query string
            k: Number of results to return
            
        Returns:
            List of retrieved chunks with metadata and similarity scores
        """
        if self.index is None:
            raise ValueError("Index not built. Call add_documents() first.")
        
        if k > len(self.documents):
            print(f"Warning: k={k} exceeds number of chunks ({len(self.documents)}). Using k={len(self.documents)}")
            k = len(self.documents)
        
        # Encode query
        query_embedding = self.model.encode([query], show_progress_bar=False)[0]
        query_embedding = np.array([query_embedding], dtype=np.float32)
        
        # Search index
        distances, indices = self.index.search(query_embedding, k)
        
        # Prepare results
        results = []
        for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            chunk = self.documents[int(idx)]
            result = {
                'rank': i + 1,
                'chunk_text': chunk['text'],
                'source_file': chunk['source_file'],
                'metadata': self.metadata[int(idx)],
                'similarity_score': float(1.0 / (1.0 + distance)),  # Convert L2 distance to similarity
                'distance': float(distance)
            }
            results.append(result)
        
        return results
    
    def save_index(self, path: str) -> None:
        """
        Save the FAISS index and metadata to disk.
        
        Args:
            path: Path to save the index file
        """
        if self.index is None:
            raise ValueError("No index to save. Call add_documents() first.")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save FAISS index
        index_path = path
        faiss.write_index(self.index, index_path)
        print(f"✓ FAISS index saved to: {index_path}")
        
        # Save metadata as JSON
        metadata_path = path.replace('.faiss', '_metadata.json')
        metadata_dict = {
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim,
            'total_chunks': len(self.documents),
            'documents': [
                {
                    'text': chunk['text'],
                    'source_file': chunk['source_file'],
                    'metadata': self.metadata[i]
                }
                for i, chunk in enumerate(self.documents)
            ]
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
        print(f"✓ Metadata saved to: {metadata_path}")
    
    def load_index(self, path: str) -> None:
        """
        Load a previously saved FAISS index and metadata.
        
        Args:
            path: Path to the saved index file
        """
        # Load FAISS index
        if not os.path.exists(path):
            raise ValueError(f"Index file not found: {path}")
        
        self.index = faiss.read_index(path)
        print(f"✓ FAISS index loaded from: {path}")
        
        # Load metadata
        metadata_path = path.replace('.faiss', '_metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)
            
            self.model_name = metadata_dict.get('model_name', self.model_name)
            self.embedding_dim = metadata_dict.get('embedding_dim', self.embedding_dim)
            
            # Restore documents and metadata
            self.documents = [
                {
                    'text': doc['text'],
                    'source_file': doc['source_file'],
                    'start_token': doc['metadata']['start_token'],
                    'end_token': doc['metadata']['end_token'],
                    'token_count': doc['metadata']['token_count']
                }
                for doc in metadata_dict.get('documents', [])
            ]
            
            self.metadata = [
                doc['metadata']
                for doc in metadata_dict.get('documents', [])
            ]
            
            print(f"✓ Metadata loaded: {len(self.documents)} chunks")
        else:
            print(f"Warning: Metadata file not found at {metadata_path}")
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the current index.
        
        Returns:
            Dictionary with index statistics
        """
        if self.index is None:
            return {'status': 'No index built'}
        
        return {
            'status': 'Index built',
            'total_chunks': len(self.documents),
            'embedding_dimension': self.embedding_dim,
            'model': self.model_name,
            'index_type': type(self.index).__name__,
            'index_size_mb': self.index.ntotal * self.embedding_dim * 4 / 1024 / 1024
        }
    
    def batch_retrieve(self, queries: List[str], k: int = 3) -> List[List[Dict]]:
        """
        Retrieve results for multiple queries in batch.
        
        Args:
            queries: List of query strings
            k: Number of results per query
            
        Returns:
            List of result lists, one per query
        """
        results = []
        for query in queries:
            results.append(self.retrieve(query, k=k))
        return results
