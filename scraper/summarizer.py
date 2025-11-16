"""
News summarization using Google Gemini API
"""

import os
import time
from typing import Dict, List, Optional
from datetime import datetime


class GeminiSummarizer:
    """
    Summarize news articles using Google Gemini API

    Free tier limits (Gemini 1.5 Flash):
    - 15 requests per minute
    - 1 million tokens per minute
    - 1500 requests per day
    """

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.enabled = bool(self.api_key)
        self.model = None

        # Rate limiting
        self.requests_per_minute = 15
        self.request_times = []

        if not self.enabled:
            print("[INFO] Summarization disabled (missing GEMINI_API_KEY)")
        else:
            self._initialize_model()

    def _initialize_model(self):
        """Initialize Gemini model"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)

            # Use Gemini Pro (stable, well-supported)
            # Available models: gemini-pro, gemini-1.5-pro-latest, gemini-1.5-flash-latest
            self.model = genai.GenerativeModel('gemini-pro')

            print("[SUCCESS] Gemini API initialized (gemini-pro)")

        except ImportError:
            print("[ERROR] google-generativeai package not installed")
            print("[INFO] Run: pip install google-generativeai")
            self.enabled = False

        except Exception as e:
            print(f"[ERROR] Failed to initialize Gemini: {e}")
            self.enabled = False

    def _wait_for_rate_limit(self):
        """
        Ensure we don't exceed rate limits (15 requests per minute)
        """
        current_time = time.time()

        # Remove requests older than 60 seconds
        self.request_times = [
            t for t in self.request_times
            if current_time - t < 60
        ]

        # If we've made 15 requests in the last minute, wait
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0])
            if wait_time > 0:
                print(f"[INFO] Rate limit: waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                # Clear old requests after waiting
                self.request_times = []

        # Record this request
        self.request_times.append(time.time())

    def summarize_article(self, article: Dict) -> Optional[str]:
        """
        Summarize a single article

        Args:
            article: Article dictionary with 'title' and 'content'

        Returns:
            Summary text (2-3 sentences in Azerbaijani)
        """
        if not self.enabled:
            return None

        try:
            # Wait if needed to respect rate limits
            self._wait_for_rate_limit()

            # Create prompt
            prompt = f"""Aşağıdakı xəbər məqaləsini 2-3 cümlə ilə Azərbaycan dilində yekunlaşdır.
Yekunlaşdırma qısa, aydın və informativ olmalıdır.

Başlıq: {article['title']}

Mətn:
{article['content'][:3000]}

Yekunlaşdırma:"""

            # Generate summary
            response = self.model.generate_content(prompt)
            summary = response.text.strip()

            print(f"[SUCCESS] Summarized: {article['title'][:50]}...")
            return summary

        except Exception as e:
            print(f"[ERROR] Failed to summarize article: {e}")
            return None

    def create_daily_digest(self, articles: List[Dict]) -> Optional[str]:
        """
        Create a daily digest summary of multiple articles

        Args:
            articles: List of article dictionaries with 'title', 'source', 'summary'

        Returns:
            Digest summary in Azerbaijani
        """
        if not self.enabled or not articles:
            return None

        try:
            # Wait if needed to respect rate limits
            self._wait_for_rate_limit()

            # Build article list for digest
            article_list = []
            for i, article in enumerate(articles[:20], 1):  # Limit to 20 articles
                summary = article.get('summary', article.get('content', '')[:200])
                article_list.append(
                    f"{i}. [{article['source']}] {article['title']}\n"
                    f"   {summary}"
                )

            articles_text = "\n\n".join(article_list)

            # Create digest prompt
            prompt = f"""Aşağıdakı {len(articles)} xəbər məqaləsindən gündəlik xəbər icmalı yarat.

İcmal aşağıdakı formada olmalıdır:
- Ən vacib xəbərləri qeyd et
- Əsas mövzuları qruplaşdır
- 5-7 bullet point ilə yazılmalıdır
- Azərbaycan dilində olmalıdır

Xəbərlər:

{articles_text}

Gündəlik İcmal:"""

            # Generate digest
            response = self.model.generate_content(prompt)
            digest = response.text.strip()

            print(f"[SUCCESS] Created daily digest for {len(articles)} articles")
            return digest

        except Exception as e:
            print(f"[ERROR] Failed to create daily digest: {e}")
            return None

    def get_usage_stats(self) -> Dict:
        """
        Get current usage statistics

        Returns:
            Dictionary with usage stats
        """
        current_time = time.time()

        # Count requests in last minute
        recent_requests = [
            t for t in self.request_times
            if current_time - t < 60
        ]

        return {
            'requests_last_minute': len(recent_requests),
            'requests_limit': self.requests_per_minute,
            'requests_available': max(0, self.requests_per_minute - len(recent_requests)),
            'enabled': self.enabled
        }
