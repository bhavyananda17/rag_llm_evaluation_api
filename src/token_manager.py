#!/usr/bin/env python3
"""
Token Manager: Track and limit API token usage across benchmarks.

Implements:
- Token counting before API calls
- Budget management and alerts
- Cost estimation
- Usage logging and reports
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional


class TokenManager:
    """Manage and track token usage across API calls."""
    
    # Average tokens per word (rough estimate)
    TOKENS_PER_WORD = 0.75
    
    # Pricing (per 1M tokens, as of 2024)
    PRICING = {
        'gemini-1.5-flash': {
            'input': 0.075,
            'output': 0.30
        },
        'gemini-2.0-flash': {
            'input': 0.075,
            'output': 0.30
        }
    }
    
    # Daily quota for free tier
    FREE_TIER_DAILY_LIMIT = 1_000_000  # tokens
    FREE_TIER_RPM_LIMIT = 60  # requests per minute
    
    def __init__(self, daily_budget: int = None, log_dir: str = None):
        """
        Initialize token manager.
        
        Args:
            daily_budget: Daily token budget (default: free tier limit)
            log_dir: Directory for logs (default: data/logs/)
        """
        self.daily_budget = daily_budget or self.FREE_TIER_DAILY_LIMIT
        self.log_dir = log_dir or "data/logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, "token_usage.json")
        self.usage_data = self._load_usage_data()
        
        # Current session tracking
        self.session_tokens = {
            'input': 0,
            'output': 0,
            'total': 0
        }
        self.session_requests = 0
        self.session_start = datetime.now()
    
    def _load_usage_data(self) -> Dict:
        """Load previous usage data from log file."""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return {
            'daily_usage': {},
            'total_usage': {
                'input': 0,
                'output': 0,
                'total': 0,
                'requests': 0
            }
        }
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        word_count = len(text.split())
        return max(1, int(word_count * self.TOKENS_PER_WORD))
    
    def estimate_request(self, prompt: str, expected_response_length: int = 150) -> Dict:
        """
        Estimate tokens and cost for a single API request.
        
        Args:
            prompt: The prompt text
            expected_response_length: Expected response word count
            
        Returns:
            Dictionary with token and cost estimates
        """
        input_tokens = self.estimate_tokens(prompt)
        output_tokens = max(1, int(expected_response_length * self.TOKENS_PER_WORD))
        total_tokens = input_tokens + output_tokens
        
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'estimated_cost_usd': self._estimate_cost(input_tokens, output_tokens)
        }
    
    def estimate_benchmark(self, num_questions: int, avg_prompt_length: int = 500,
                          avg_response_length: int = 150) -> Dict:
        """
        Estimate tokens for entire benchmark run.
        
        Args:
            num_questions: Number of QA pairs
            avg_prompt_length: Average prompt word count
            avg_response_length: Average response word count
            
        Returns:
            Benchmark estimate dictionary
        """
        single_request = self.estimate_request(
            "x" * avg_prompt_length,
            avg_response_length
        )
        
        total_input = single_request['input_tokens'] * num_questions
        total_output = single_request['output_tokens'] * num_questions
        total_tokens = total_input + total_output
        
        return {
            'num_questions': num_questions,
            'tokens_per_request': single_request['total_tokens'],
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_tokens,
            'estimated_cost_usd': self._estimate_cost(total_input, total_output),
            'within_daily_budget': total_tokens <= self.daily_budget,
            'budget_remaining': max(0, self.daily_budget - total_tokens)
        }
    
    def _estimate_cost(self, input_tokens: int, output_tokens: int,
                      model: str = 'gemini-1.5-flash') -> float:
        """Estimate USD cost for tokens."""
        pricing = self.PRICING.get(model, self.PRICING['gemini-1.5-flash'])
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        return round(input_cost + output_cost, 6)
    
    def log_request(self, input_tokens: int, output_tokens: int,
                   question_id: str = None, success: bool = True) -> None:
        """
        Log an API request.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            question_id: ID of the question
            success: Whether request was successful
        """
        total_tokens = input_tokens + output_tokens
        
        # Update session
        self.session_tokens['input'] += input_tokens if success else 0
        self.session_tokens['output'] += output_tokens if success else 0
        self.session_tokens['total'] = (
            self.session_tokens['input'] + self.session_tokens['output']
        )
        self.session_requests += 1
        
        # Update usage data
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.usage_data['daily_usage']:
            self.usage_data['daily_usage'][today] = {
                'input': 0,
                'output': 0,
                'total': 0,
                'requests': 0,
                'cost': 0
            }
        
        if success:
            self.usage_data['daily_usage'][today]['input'] += input_tokens
            self.usage_data['daily_usage'][today]['output'] += output_tokens
            self.usage_data['daily_usage'][today]['total'] += total_tokens
            self.usage_data['total_usage']['input'] += input_tokens
            self.usage_data['total_usage']['output'] += output_tokens
            self.usage_data['total_usage']['total'] += total_tokens
            cost = self._estimate_cost(input_tokens, output_tokens)
            self.usage_data['daily_usage'][today]['cost'] += cost
        
        self.usage_data['daily_usage'][today]['requests'] += 1
        self.usage_data['total_usage']['requests'] += 1
    
    def get_session_summary(self) -> Dict:
        """Get current session token usage."""
        duration = (datetime.now() - self.session_start).total_seconds()
        return {
            'duration_seconds': duration,
            'requests': self.session_requests,
            'input_tokens': self.session_tokens['input'],
            'output_tokens': self.session_tokens['output'],
            'total_tokens': self.session_tokens['total'],
            'tokens_per_request': (
                self.session_tokens['total'] / self.session_requests
                if self.session_requests > 0 else 0
            ),
            'requests_per_minute': (
                (self.session_requests / duration) * 60
                if duration > 0 else 0
            )
        }
    
    def get_daily_remaining(self) -> int:
        """Get remaining tokens for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        used = self.usage_data['daily_usage'].get(today, {}).get('total', 0)
        return max(0, self.daily_budget - used)
    
    def check_budget(self, required_tokens: int = 0) -> Dict:
        """
        Check if operation fits within budget.
        
        Args:
            required_tokens: Tokens needed for operation
            
        Returns:
            Dictionary with budget check results
        """
        remaining = self.get_daily_remaining()
        
        return {
            'daily_budget': self.daily_budget,
            'used_today': self.daily_budget - remaining,
            'remaining': remaining,
            'required': required_tokens,
            'can_proceed': remaining >= required_tokens,
            'percentage_used': (
                ((self.daily_budget - remaining) / self.daily_budget) * 100
            )
        }
    
    def save_usage_log(self) -> str:
        """Save usage data to log file."""
        with open(self.log_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
        return self.log_file
    
    def print_session_report(self) -> None:
        """Print session usage report."""
        summary = self.get_session_summary()
        budget = self.check_budget()
        
        print("\n" + "="*70)
        print("TOKEN USAGE REPORT")
        print("="*70)
        print(f"\nSession Statistics:")
        print(f"  Duration: {summary['duration_seconds']:.1f}s")
        print(f"  Requests: {summary['requests']}")
        print(f"  Input Tokens: {summary['input_tokens']:,}")
        print(f"  Output Tokens: {summary['output_tokens']:,}")
        print(f"  Total Tokens: {summary['total_tokens']:,}")
        print(f"  Avg per Request: {summary['tokens_per_request']:.0f}")
        print(f"  Requests/min: {summary['requests_per_minute']:.2f}")
        
        print(f"\nDaily Budget:")
        print(f"  Budget: {budget['daily_budget']:,} tokens")
        print(f"  Used: {budget['used_today']:,} ({budget['percentage_used']:.1f}%)")
        print(f"  Remaining: {budget['remaining']:,}")
        print(f"{'='*70}\n")


def estimate_benchmark_cost(num_questions: int = 13) -> None:
    """Utility to estimate benchmark cost."""
    manager = TokenManager()
    
    print("\n" + "="*70)
    print("BENCHMARK COST ESTIMATION")
    print("="*70)
    
    # Base model estimate
    print("\n1. Base Model Benchmark (question only):")
    base_est = manager.estimate_benchmark(
        num_questions=num_questions,
        avg_prompt_length=100,
        avg_response_length=150
    )
    print(f"   Questions: {base_est['num_questions']}")
    print(f"   Total Tokens: {base_est['total_tokens']:,}")
    print(f"   Estimated Cost: ${base_est['estimated_cost_usd']:.4f}")
    print(f"   Within Budget: {'✓' if base_est['within_daily_budget'] else '✗'}")
    
    # RAG model estimate
    print("\n2. RAG Benchmark (context + question):")
    rag_est = manager.estimate_benchmark(
        num_questions=num_questions,
        avg_prompt_length=800,  # Context + question
        avg_response_length=200
    )
    print(f"   Questions: {rag_est['num_questions']}")
    print(f"   Total Tokens: {rag_est['total_tokens']:,}")
    print(f"   Estimated Cost: ${rag_est['estimated_cost_usd']:.4f}")
    print(f"   Within Budget: {'✓' if rag_est['within_daily_budget'] else '✗'}")
    
    # Combined estimate
    total_est = base_est['total_tokens'] + rag_est['total_tokens']
    combined_cost = base_est['estimated_cost_usd'] + rag_est['estimated_cost_usd']
    
    print("\n3. Combined (Base + RAG):")
    print(f"   Total Tokens: {total_est:,}")
    print(f"   Estimated Cost: ${combined_cost:.4f}")
    print(f"   Within Daily Budget: {'✓' if total_est <= manager.FREE_TIER_DAILY_LIMIT else '✗'}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    estimate_benchmark_cost(num_questions=13)
