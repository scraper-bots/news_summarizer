# Azerbaijan News Scraper

Async news scraper for 8 major Azerbaijani news sources with AI summarization and Telegram reporting.

## 🚀 Features

- **8 News Sources**: Banker.az, Marja.az, Report.az, Fed.az, Sonxeber.az, Iqtisadiyyat.az, Trend.az, APA.az
- **Async Architecture**: 3-4x faster than synchronous scraping
- **AI Summarization**: Google Gemini powered article summaries
- **Telegram Reports**: Automatic notifications with summaries
- **PostgreSQL Storage**: Full article database with relationships
- **Concurrent Processing**: Batch scraping with rate limiting

## 📊 Performance

- **Speed**: ~0.30 seconds per article
- **Throughput**: ~200 articles in ~1 minute
- **Concurrent Requests**: 5-10 simultaneous
- **Batch Size**: 10 articles per batch

## 🛠️ Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate

# Install requirements
pip install -r scraper/requirements.txt
```

### 2. Configure Environment

Create `.env.local`:
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 3. Initialize Database

```bash
python scraper/scripts/init_db.py
```

## 🚀 Usage

### Run Scraper

```bash
python scraper/main.py
```

### Test Individual Source

```python
import asyncio
from sources.apa_az import ApaAzScraper

async def test():
    async with ApaAzScraper() as scraper:
        articles = await scraper.scrape_all(num_pages=1, batch_size=10)
        print(f"Scraped {len(articles)} articles")

asyncio.run(test())
```

## 📁 Project Structure

```
scraper/
├── main.py                    # Main async scraper
├── base_scraper.py            # Async base class
├── db.py                      # Database operations
├── summarizer.py              # AI summarization
├── telegram.py                # Telegram reporting
├── sources/                   # News source scrapers
│   ├── banker_az.py
│   ├── marja_az.py
│   ├── report_az.py
│   ├── fed_az.py
│   ├── sonxeber_az.py
│   ├── iqtisadiyyat_az.py
│   ├── trend_az.py
│   └── apa_az.py
└── scripts/                   # Utility scripts
    ├── init_db.py
    ├── verify_db.py
    └── test_*.py
```

## 🔧 Configuration

### Scraper Settings (main.py)

- **Banker.az**: 2 pages
- **Marja.az**: 2 pages
- **Report.az**: 1 page
- **Fed.az**: 2 pages (multi-category)
- **Sonxeber.az**: 2 pages
- **Iqtisadiyyat.az**: 2 pages (multi-category)
- **Trend.az**: 1 page
- **APA.az**: 2 pages

### Rate Limiting

- Max concurrent requests: 5
- Batch size: 10 articles
- Delay between batches: 1 second

## 📦 Dependencies

- **aiohttp**: Async HTTP client
- **beautifulsoup4**: HTML parsing
- **psycopg2-binary**: PostgreSQL adapter
- **google-generativeai**: AI summarization
- **python-dotenv**: Environment variables

## 🎯 Output

Each scraping session generates:
- **Database records**: Articles with metadata
- **AI summary**: Overall news summary
- **Telegram report**: Statistics and summary
- **Console logs**: Detailed progress

## 📈 Statistics Tracked

- Total articles found
- Articles scraped successfully
- New articles saved
- Duplicate articles skipped
- Scraping duration
- Per-source breakdowns

## 🔄 Backup

Synchronous version backed up as: `scraper/main_sync_backup.py`

## 📝 License

Private project for news aggregation.
