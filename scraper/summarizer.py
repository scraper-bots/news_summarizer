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

    def filter_relevant_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter articles to keep only those relevant to banking/finance sector

        Args:
            articles: List of all articles

        Returns:
            List of relevant articles only
        """
        if not self.enabled or not articles:
            return articles

        try:
            print(f"\n[INFO] Filtering {len(articles)} articles for banking/finance relevance...")
            self._wait_for_rate_limit()

            # Prepare articles for filtering
            articles_list = []
            for i, article in enumerate(articles, 1):
                content_snippet = article.get('content', '')[:200]
                articles_list.append(
                    f"{i}. {article['title']}\n{content_snippet}..."
                )

            articles_text = "\n\n".join(articles_list)

            # Filtering prompt
            filter_prompt = f"""Sən bank sektorunda Business Analyst üçün asistansan. Aşağıdakı xəbərləri analiz et və YALNIZ bank sektoruna aid olanları seç.

RELEVANT (UYĞUN) XƏBƏRLƏR:
- Bank və maliyyə sektoru xəbərləri
- Makroiqtisadi göstəricilər (inflyasiya, iqtisadi artım, və s.)
- Tənzimləmə və qanunvericilik dəyişiklikləri
- Kredit, ipoteka, depozit bazarları
- Bank kapitalı və maliyyə nəticələri
- Fintex və rəqəmsal bank xidmətləri
- Valyuta məzənnəsi və pul siyasəti
- Beynəlxalq maliyyə təşkilatları (IMF, World Bank, və s.)
- Biznes mühiti və investisiya iqlimi

IRRELEVANT (UYĞUN OLMAYAN) XƏBƏRLƏR:
- Beynəlxalq siyasət və münaqişələr (bank sektoruna təsiri yoxdursa)
- İdman xəbərləri
- Mədəniyyət və əyləncə
- Texnologiya (fintex deyilsə)
- Ümumi infrastruktur layihələri (maliyyələşmə aspekti yoxdursa)

XƏBƏRLƏR:
{articles_text}

TAPŞıRıQ: Yuxarıdakı xəbərlərdən YALNIZ bank sektoru üçün relevant olanların nömrələrini ver.
Cavabı bu formatda ver: 1,3,5,7 (vergüllə ayrılmış nömrələr, heç bir izahat yox)

RELEVANT XƏBƏRLƏR:"""

            response = self.model.generate_content(filter_prompt)
            relevant_indices_str = response.text.strip()

            # Parse indices
            try:
                relevant_indices = [int(x.strip()) - 1 for x in relevant_indices_str.split(',') if x.strip().isdigit()]
                relevant_articles = [articles[i] for i in relevant_indices if 0 <= i < len(articles)]

                print(f"[SUCCESS] Filtered: {len(relevant_articles)}/{len(articles)} articles are banking-relevant")
                return relevant_articles

            except Exception as parse_error:
                print(f"[WARNING] Could not parse filter results: {parse_error}")
                print(f"[INFO] Using all articles as fallback")
                return articles

        except Exception as e:
            print(f"[ERROR] Filtering failed: {e}")
            print(f"[INFO] Using all articles as fallback")
            return articles

    def create_session_summary(self, articles: List[Dict], sources_stats: List[Dict]) -> Optional[str]:
        """
        Create banking intelligence summary with actionable insights

        Args:
            articles: List of ALL articles (new ones) from this session
            sources_stats: List of stats per source

        Returns:
            Banking intelligence report in Azerbaijani with strategic insights
        """
        if not self.enabled or not articles:
            return None

        try:
            # STEP 1: Filter for relevant articles
            relevant_articles = self.filter_relevant_articles(articles)

            if not relevant_articles:
                return "Bu sessiyada bank sektoruna aid heç bir xəbər tapılmadı."

            # STEP 2: Create banking intelligence report
            self._wait_for_rate_limit()

            # Prepare article summaries
            article_summaries = []
            for i, article in enumerate(relevant_articles, 1):
                content_snippet = article.get('content', '')[:400]
                article_summaries.append(
                    f"{i}. [{article['source']}] {article['title']}\n"
                    f"   {content_snippet}..."
                )

            articles_text = "\n\n".join(article_summaries[:40])

            # Create sources overview
            sources_overview = "\n".join([
                f"- {s['name']}: {s['saved']} xəbər"
                for s in sources_stats
            ])

            # Banking intelligence prompt
            prompt = f"""Sən Azərbaycan bankında Business Analyst üçün strateji məsləhətçisən.
Aşağıdakı bank sektoruna aid xəbərlərdən ACTIONABLE banking intelligence report hazırla.

MƏNBƏLƏR:
{sources_overview}

BANK SEKTORUNA AİD XƏBƏRLƏR ({len(relevant_articles)}/{len(articles)}):
{articles_text}

REPORT STRUKTURU:

## 📊 İCMAL ÖZƏTİ
[2-3 cümlədə əsas trendləri və kritik məqamları qeyd et]

## 🏦 BANK SEKTORU ANALİZİ

### Makroiqtisadi Mühit
- İnflyasiya, faiz dərəcələri, iqtisadi artım
- Bank sektoruna potensial təsiri

### Tənzimləmə və Qanunvericilik
- Yeni qanunlar, Mərkəzi Bank qərarları
- Compliance tələbləri

### Bazar Dinamikası
- Bank nəticələri, kapital artımı, kredit portfeli
- Rəqabət mühiti, bazar payı dəyişiklikləri

### Rəqəmsal Transformasiya
- Fintech, yeni məhsullar, texnologiya təbənniyyatı

### Beynəlxalq Əməkdaşlıq
- Xarici maliyyələşmə, beynəlxalq təşkilatlarla münasibətlər

## 💡 STRATEJİ RİSKLƏR VƏ İMKANLAR

### Risklər ⚠️
1. [Risk 1]: Təsvir və potensial təsir
2. [Risk 2]: Təsvir və potensial təsir

### İmkanlar ✅
1. [İmkan 1]: Necə istifadə etmək olar
2. [İmkan 2]: Necə istifadə etmək olar

## 🎯 TÖVSİYƏLƏR VƏ ACTIONABLE INSIGHTS

### Qısa Müddətli (1-3 ay)
1. [Konkret təklif və addımlar]
2. [Konkret təklif və addımlar]

### Orta Müddətli (3-6 ay)
1. [Strateji tövsiyə]
2. [Strateji tövsiyə]

### İzləməli Məsələlər 👁️
- [İzləməli trend 1]
- [İzləməli trend 2]

## 📈 ƏSAS GÖSTƏRİCİLƏR
[Xəbərlərdən çıxan əsas rəqəmlər və statistika]

ÖNEMLİ:
- Konkret, actionable olsun
- Business impact-ə fokuslan
- Rəqəmləri və faktları istifadə et
- Azərbaycan dilində professional ton
- Banking terminologiyasını düzgün işlət

BANKING INTELLIGENCE REPORT:"""

            # Generate banking intelligence
            response = self.model.generate_content(prompt)
            summary = response.text.strip()

            print(f"[SUCCESS] Created banking intelligence report from {len(relevant_articles)} relevant articles")
            print(f"[INFO] Filtered out {len(articles) - len(relevant_articles)} non-banking articles")

            return summary

        except Exception as e:
            try:
                print(f"[ERROR] Failed to create banking intelligence: {e}")
            except (UnicodeEncodeError, UnicodeDecodeError):
                print(f"[ERROR] Failed to create banking intelligence (encoding error)")
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
