import google.generativeai as genai
import sys
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.token_manager import TokenManager


class CachedGeminiClient:
    """Gemini API client with caching and token management."""
    
    def __init__(self, use_cache: bool = True, cache_dir: str = None):
        """
        Initialize Gemini client with optional caching.
        
        Args:
            use_cache: Enable response caching
            cache_dir: Directory for cache files (default: data/cache/)
        """
        genai.configure(api_key=Config.API_KEY)
        
        # Model selection
        self.model_name = self._select_model()
        self.model = genai.GenerativeModel(self.model_name)
        
        # Caching
        self.use_cache = use_cache
        self.cache_dir = cache_dir or os.path.join(Config.BASE_DIR, "data/cache")
        if self.use_cache:
            os.makedirs(self.cache_dir, exist_ok=True)
        
        # Token manager
        self.token_manager = TokenManager()
        
        # Statistics
        self.cache_hits = 0
        self.cache_misses = 0
        self.api_calls = 0
    
    def _select_model(self) -> str:
        """Select available model with fallback."""
        models_to_try = [
            'gemini-2.0-flash',
            'gemini-1.5-flash',
            'gemini-pro'
        ]
        
        for model in models_to_try:
            try:
                genai.GenerativeModel(model)
                print(f"✓ Using model: {model}")
                return model
            except:
                continue
        
        raise RuntimeError("No available Gemini models")
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key from prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _get_cached_response(self, prompt: str) -> dict | None:
        """Retrieve cached response if exists."""
        if not self.use_cache:
            return None
        
        cache_key = self._get_cache_key(prompt)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        
        return None
    
    def _cache_response(self, prompt: str, response: str) -> None:
        """Cache API response."""
        if not self.use_cache:
            return
        
        cache_key = self._get_cache_key(prompt)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        cache_data = {
            'prompt_hash': cache_key,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'model': self.model_name
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False)
        except:
            pass  # Fail silently if cache write fails
    
    def generate(self, prompt: str, use_cache: bool = None) -> str:
        """
        Generate response with optional caching.
        
        Args:
            prompt: Input prompt
            use_cache: Override default cache setting
            
        Returns:
            Generated response text
        """
        should_cache = use_cache if use_cache is not None else self.use_cache
        
        # Check cache first
        if should_cache:
            cached = self._get_cached_response(prompt)
            if cached:
                self.cache_hits += 1
                return cached['response']
            self.cache_misses += 1
        
        # Estimate tokens
        estimate = self.token_manager.estimate_request(
            prompt,
            expected_response_length=150
        )
        
        # Check budget
        budget = self.token_manager.check_budget(estimate['total_tokens'])
        if not budget['can_proceed']:
            return f"Error: Insufficient token budget. Required: {estimate['total_tokens']}, Remaining: {budget['remaining']}"
        
        # Call API
        try:
            self.api_calls += 1
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Log tokens
            self.token_manager.log_request(
                estimate['input_tokens'],
                estimate['output_tokens'],
                success=True
            )
            
            # Cache response
            if should_cache:
                self._cache_response(prompt, response_text)
            
            return response_text
        
        except Exception as e:
            error_msg = str(e)
            self.token_manager.log_request(0, 0, success=False)
            return f"Error: {error_msg}"
    
    def get_stats(self) -> dict:
        """Get client statistics."""
        return {
            'model': self.model_name,
            'api_calls': self.api_calls,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': (
                (self.cache_hits / (self.cache_hits + self.cache_misses) * 100)
                if (self.cache_hits + self.cache_misses) > 0 else 0
            ),
            'token_session': self.token_manager.get_session_summary()
        }
    
    def print_stats(self) -> None:
        """Print statistics."""
        stats = self.get_stats()
        print("\n" + "="*70)
        print("GEMINI CLIENT STATISTICS")
        print("="*70)
        print(f"Model: {stats['model']}")
        print(f"API Calls: {stats['api_calls']}")
        print(f"Cache Hits: {stats['cache_hits']}")
        print(f"Cache Misses: {stats['cache_misses']}")
        print(f"Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
        print(f"{'='*70}\n")
        self.token_manager.print_session_report()


# Backward compatibility
class GeminiClient(CachedGeminiClient):
    """Alias for backward compatibility."""
    pass