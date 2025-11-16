# Utility Scripts

This folder contains one-time and debugging scripts for the news scraper project.

## Scripts

### Database Scripts

- **init_db.py** - Initialize database schema
  - Creates the `news.articles` table
  - Sets up indexes and triggers
  - Run once during initial setup
  ```bash
  python scraper/scripts/init_db.py
  ```

- **test_db.py** - Test database connection
  - Verifies connection to PostgreSQL
  - Lists table columns and schema
  - Useful for debugging connection issues
  ```bash
  python scraper/scripts/test_db.py
  ```

- **verify_db.py** - Verify database contents
  - Shows article counts by source
  - Displays latest articles
  - Verifies Azerbaijani character encoding
  ```bash
  python scraper/scripts/verify_db.py
  ```

### Scraper Testing Scripts

- **test_banker_az.py** - Test Banker.az scraper
  - Tests article list scraping
  - Tests single article scraping
  - Verifies Azerbaijani character handling
  ```bash
  python scraper/scripts/test_banker_az.py
  ```

- **test_marja_az.py** - Test Marja.az scraper
  - Tests article list scraping
  - Tests single article scraping
  - Verifies Azerbaijani character handling
  ```bash
  python scraper/scripts/test_marja_az.py
  ```

## Usage

All scripts should be run from the project root directory:

```bash
# From project root (news_summarizer/)
python scraper/scripts/<script_name>.py
```

## Notes

- These are utility scripts, not part of the main scraper workflow
- Use for testing, debugging, and one-time setup tasks
- Main scraper entry point is `scraper/main.py`
