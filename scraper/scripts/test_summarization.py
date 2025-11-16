"""
Test summarization with correct model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import Database
from sources.banker_az import BankerAzScraper
from summarizer import GeminiSummarizer

print('Testing Gemini summarization...')
print('=' * 80)

# Initialize
db = Database()
db.connect()
scraper = BankerAzScraper()
summarizer = GeminiSummarizer()

# Get just 2 articles for testing
article_urls = scraper.scrape_article_list(page=1)[:2]
print(f'Testing with {len(article_urls)} articles\n')

success_count = 0
for url in article_urls:
    print(f'Scraping: {url[:70]}...')
    article = scraper.scrape_article(url)

    if article:
        try:
            print(f'Title: {article["title"][:60]}...')
        except:
            print(f'Title: [Azerbaijani - {len(article["title"])} chars]')

        # Test summarization
        summary = summarizer.summarize_article(article)

        if summary:
            try:
                print(f'SUCCESS: Summary: {summary[:80]}...')
            except:
                print(f'SUCCESS: Summary generated ({len(summary)} chars)')
            article['summary'] = summary
            success_count += 1
        else:
            print('FAILED: No summary generated')

        # Save
        db.insert_article(article)
        print()

print('=' * 80)
print(f'Result: {success_count}/{len(article_urls)} articles summarized successfully')

# Verify in database
db.cursor.execute('SELECT COUNT(*) as total, COUNT(summary) as with_summary FROM news.articles')
stats = db.cursor.fetchone()
print(f'Database: {stats["with_summary"]} out of {stats["total"]} articles have summaries')

db.close()
