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

            # Use Gemini Flash Latest (fast, stable, good for summaries)
            self.model = genai.GenerativeModel('gemini-flash-latest')

            print("[SUCCESS] Gemini API initialized (gemini-flash-latest)")

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

    def create_session_summary(self, articles: List[Dict], sources_stats: List[Dict]) -> Optional[str]:
        """
        Create comprehensive summary of entire scraping session

        Args:
            articles: List of ALL articles (new ones) from this session
            sources_stats: List of stats per source

        Returns:
            Comprehensive summary in Azerbaijani covering all articles
        """
        if not self.enabled or not articles:
            return None

        try:
            # Wait if needed to respect rate limits
            self._wait_for_rate_limit()

            # Prepare article summaries (title + first part of content)
            article_summaries = []
            for i, article in enumerate(articles, 1):
                # Limit content to avoid token overflow
                content_snippet = article.get('content', '')[:300]
                article_summaries.append(
                    f"{i}. [{article['source']}] {article['title']}\n"
                    f"   {content_snippet}..."
                )

            # Combine all articles (limit total to stay within token limits)
            # Gemini Flash: ~32K input tokens ≈ 24K words ≈ 120K chars
            articles_text = "\n\n".join(article_summaries[:50])  # Max 50 articles per summary

            # Create sources overview
            sources_overview = "\n".join([
                f"- {s['name']}: {s['saved']} xəbər"
                for s in sources_stats
            ])

            # Create comprehensive prompt
            prompt = f"""Aşağıdakı xəbər toplama sessiyasından ətraflı icmal hazırla.

MƏNBƏLƏR:
{sources_overview}

TOPLAM: {len(articles)} yeni xəbər

XƏBƏRLƏR:
{articles_text}

ÖNEMLİ GÖSTƏRIŞLƏR:
1. İcmal Azərbaycan dilində olmalıdır
2. Bütün mühüm xəbərləri əhatə etməlidir
3. Xəbərləri mövzulara görə qruplaşdır (məsələn: İqtisadiyyat, Siyasət, Maliyyə və s.)
4. Hər mövzu üzrə 3-5 bullet point ver
5. Ümumi qısa giriş və yekunlaşdırma əlavə et

ƏTRAFL İCMAL:"""

            # Generate comprehensive summary
            response = self.model.generate_content(prompt)
            summary = response.text.strip()

            print(f"[SUCCESS] Created session summary for {len(articles)} articles from {len(sources_stats)} sources")
            return summary

        except Exception as e:
            try:
                print(f"[ERROR] Failed to create session summary: {e}")
            except (UnicodeEncodeError, UnicodeDecodeError):
                print(f"[ERROR] Failed to create session summary (encoding error)")
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
