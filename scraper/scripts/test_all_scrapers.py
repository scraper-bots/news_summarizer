"""
Test all news scrapers to verify they are working correctly
"""

import sys
import os
from datetime import datetime

# Fix encoding for Azerbaijani characters on Windows
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    import io
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory (scraper) to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.banker_az import BankerAzScraper
from sources.marja_az import MarjaAzScraper
from sources.report_az import ReportAzScraper
from sources.fed_az import FedAzScraper


def test_scraper(scraper, name, test_category=None):
    """
    Test a single scraper

    Args:
        scraper: Scraper instance
        name: Scraper name for display
        test_category: Optional category for scrapers with multiple categories

    Returns:
        dict: Test results
    """
    print(f"\n{'=' * 70}")
    print(f"TESTING: {name}")
    print(f"{'=' * 70}")

    results = {
        'name': name,
        'list_fetch': False,
        'article_count': 0,
        'article_scrape': False,
        'article_data': None,
        'errors': []
    }

    try:
        # Test 1: Fetch article list
        print(f"\n[1/2] Fetching article list from page 1...")
        if test_category:
            article_urls = scraper.scrape_article_list(page=1, category=test_category)
        else:
            article_urls = scraper.scrape_article_list(page=1)

        if article_urls:
            results['list_fetch'] = True
            results['article_count'] = len(article_urls)
            print(f"✓ SUCCESS: Found {len(article_urls)} articles")
            print(f"  Sample URLs:")
            for i, url in enumerate(article_urls[:3], 1):
                print(f"    {i}. {url}")
        else:
            results['errors'].append("No articles found in list")
            print(f"✗ FAILED: No articles found")
            return results

        # Test 2: Scrape first article
        print(f"\n[2/2] Scraping first article...")
        test_url = article_urls[0]
        print(f"  URL: {test_url}")

        article = scraper.scrape_article(test_url)

        if article:
            results['article_scrape'] = True
            results['article_data'] = article
            print(f"✓ SUCCESS: Article scraped")
            print(f"\n  Article Details:")
            print(f"    Title: {article.get('title', 'N/A')[:80]}...")
            print(f"    Source: {article.get('source', 'N/A')}")
            print(f"    URL: {article.get('url', 'N/A')[:60]}...")
            print(f"    Published: {article.get('published_date', 'N/A')}")
            print(f"    Language: {article.get('language', 'N/A')}")
            print(f"    Content length: {len(article.get('content', ''))} chars")
            if article.get('content'):
                print(f"    Content preview: {article['content'][:150]}...")
        else:
            results['errors'].append("Failed to scrape article")
            print(f"✗ FAILED: Could not scrape article")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        results['errors'].append(error_msg)
        print(f"✗ ERROR: {error_msg}")
        import traceback
        traceback.print_exc()

    return results


def main():
    """Run tests for all scrapers"""
    print("\n" + "=" * 70)
    print("SCRAPER FUNCTIONALITY TEST")
    print("=" * 70)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version}")
    print(f"Encoding: {sys.stdout.encoding}")

    all_results = []

    # Test 1: Banker.az
    print("\n\n" + "█" * 70)
    print("TEST 1/4: BANKER.AZ")
    print("█" * 70)
    banker_scraper = BankerAzScraper()
    banker_results = test_scraper(banker_scraper, "Banker.az")
    all_results.append(banker_results)

    # Test 2: Marja.az
    print("\n\n" + "█" * 70)
    print("TEST 2/4: MARJA.AZ")
    print("█" * 70)
    marja_scraper = MarjaAzScraper()
    marja_results = test_scraper(marja_scraper, "Marja.az")
    all_results.append(marja_results)

    # Test 3: Report.az
    print("\n\n" + "█" * 70)
    print("TEST 3/4: REPORT.AZ")
    print("█" * 70)
    report_scraper = ReportAzScraper()
    report_results = test_scraper(report_scraper, "Report.az")
    all_results.append(report_results)

    # Test 4: Fed.az (test first category)
    print("\n\n" + "█" * 70)
    print("TEST 4/4: FED.AZ")
    print("█" * 70)
    fed_scraper = FedAzScraper()
    fed_results = test_scraper(fed_scraper, "Fed.az", test_category="az/maliyye")
    all_results.append(fed_results)

    # Summary
    print("\n\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    total_scrapers = len(all_results)
    successful_list_fetch = sum(1 for r in all_results if r['list_fetch'])
    successful_article_scrape = sum(1 for r in all_results if r['article_scrape'])
    total_articles_found = sum(r['article_count'] for r in all_results)

    print(f"\nTotal scrapers tested: {total_scrapers}")
    print(f"Successful list fetches: {successful_list_fetch}/{total_scrapers}")
    print(f"Successful article scrapes: {successful_article_scrape}/{total_scrapers}")
    print(f"Total articles found: {total_articles_found}")

    print("\n" + "-" * 70)
    print("Individual Results:")
    print("-" * 70)

    for result in all_results:
        status = "✓ PASS" if (result['list_fetch'] and result['article_scrape']) else "✗ FAIL"
        print(f"\n{result['name']:<15} {status}")
        print(f"  List fetch:       {'✓ Yes' if result['list_fetch'] else '✗ No'}")
        print(f"  Articles found:   {result['article_count']}")
        print(f"  Article scrape:   {'✓ Yes' if result['article_scrape'] else '✗ No'}")
        if result['errors']:
            print(f"  Errors:")
            for error in result['errors']:
                print(f"    - {error}")

    # Final verdict
    print("\n" + "=" * 70)
    if successful_list_fetch == total_scrapers and successful_article_scrape == total_scrapers:
        print("FINAL RESULT: ✓ ALL SCRAPERS WORKING")
    else:
        print("FINAL RESULT: ✗ SOME SCRAPERS FAILED")
        failed = [r['name'] for r in all_results if not (r['list_fetch'] and r['article_scrape'])]
        print(f"Failed scrapers: {', '.join(failed)}")
    print("=" * 70)

    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
