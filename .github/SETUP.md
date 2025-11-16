# GitHub Actions Setup

This document explains how to configure GitHub Actions for automated daily news scraping.

## Workflow Schedule

The scraper runs automatically:
- **Daily at 09:00 UTC** (13:00 Azerbaijan time)
- Can also be triggered manually for testing

## Required GitHub Secrets

You need to configure the following secrets in your GitHub repository:

### DATABASE_URL

Your PostgreSQL connection string from Neon.

**Steps to add:**

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `DATABASE_URL`
5. Value: Your PostgreSQL connection string from `.env.local`
   ```
   postgresql://user:password@host/database?sslmode=require
   ```
6. Click **Add secret**

### TELEGRAM_BOT_TOKEN

Your Telegram bot token for sending scraping reports.

**Steps to add:**

1. Follow the same steps as above
2. Name: `TELEGRAM_BOT_TOKEN`
3. Value: Your bot token from BotFather (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Click **Add secret**

### TELEGRAM_CHAT_ID

Your Telegram chat ID(s) where reports will be sent.

**Steps to add:**

1. Follow the same steps as above
2. Name: `TELEGRAM_CHAT_ID`
3. Value: Your chat ID (e.g., `123456789` or `-123456789` for groups)
   - For multiple chats, separate with commas: `123456789,-987654321`
4. Click **Add secret**

### GEMINI_API_KEY

Your Google Gemini API key for article summarization.

**Steps to add:**

1. Follow the same steps as above
2. Name: `GEMINI_API_KEY`
3. Value: Your Gemini API key (e.g., `AIzaSy...`)
4. Click **Add secret**

**How to get Gemini API key:**
- Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
- Click "Get API key"
- Create new key or use existing
- Copy the API key

**How to get Telegram credentials:**

1. **Get Bot Token:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow instructions
   - Copy the token provided

2. **Get Chat ID:**
   - Start a chat with your bot
   - Send any message to the bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

## Manual Trigger

To test the workflow manually:

1. Go to **Actions** tab in your repository
2. Select **Daily News Scraper** workflow
3. Click **Run workflow** → **Run workflow**
4. Monitor the execution in real-time

## Workflow File

Location: `.github/workflows/scrape-news.yml`

The workflow:
1. Checks out the repository code
2. Sets up Python 3.11
3. Installs dependencies from `scraper/requirements.txt`
4. Runs the scraper with secrets (DATABASE_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GEMINI_API_KEY)
5. Scrapes articles and generates AI summaries using Gemini
6. Sends Telegram report with scraping results and daily digest
7. Logs completion status

## Telegram Reporting

The scraper automatically sends comprehensive reports to your Telegram chat:

**📰 Report includes:**
- ⏱️ Scraping duration
- 📊 Number of sources scraped
- 📝 Total articles found
- 💾 New articles saved to database
- ⏭ Duplicate articles skipped
- 📚 Per-source breakdown with emojis
- 📋 Daily digest (AI-powered summary of all new articles)
- ❌ Error alerts (if any occur)

**Notifications:**
- 🚀 Start notification when scraping begins
- 📰 Detailed report when scraping completes
- 🚨 Error alerts for critical failures

## Monitoring

You can monitor scraping in two ways:

**1. Telegram (Recommended):**
- Receive instant reports in your Telegram chat
- Easy-to-read format with emojis
- No need to check GitHub

**2. GitHub Actions:**
- Go to **Actions** tab
- Click on the latest workflow run
- View detailed logs for each step
- Check for errors or successful completion

## Testing Locally

Before committing, test the scraper locally:

```bash
# Make sure .env.local has all required variables:
# - DATABASE_URL (required)
# - GEMINI_API_KEY (required for summarization)
# - TELEGRAM_BOT_TOKEN (optional for testing)
# - TELEGRAM_CHAT_ID (optional for testing)

python scraper/main.py
```

**Notes:**
- The scraper will work without Telegram credentials, but reports won't be sent
- Summarization will be skipped if GEMINI_API_KEY is missing
- Each scraping run respects Gemini API free tier limits (15 requests/minute)

## Notes

- The workflow uses Ubuntu latest runner
- Python dependencies are cached for faster execution
- The workflow will fail if DATABASE_URL is not configured
- Telegram credentials are optional but recommended for monitoring
- GEMINI_API_KEY is required for article summarization
- Each run will skip duplicate articles automatically
- Reports are sent in HTML format with emoji indicators for easy reading
- Summarization uses Gemini 1.5 Flash model (fast, efficient, free tier friendly)
- Rate limiting is automatically handled (15 requests/minute maximum)
