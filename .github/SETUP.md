# GitHub Actions Setup

This document explains how to configure GitHub Actions for automated daily news scraping.

## Workflow Schedule

The scraper runs automatically:
- **Daily at 09:00 UTC** (13:00 Azerbaijan time)
- Can also be triggered manually for testing

## Required GitHub Secrets

You need to configure the following secret in your GitHub repository:

### DATABASE_URL

Your PostgreSQL connection string from Neon.

**Steps to add the secret:**

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `DATABASE_URL`
5. Value: Your PostgreSQL connection string from `.env.local`
   ```
   postgresql://user:password@host/database?sslmode=require
   ```
6. Click **Add secret**

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
4. Runs the scraper with `DATABASE_URL` from secrets
5. Logs completion status

## Monitoring

To check scraping results:

1. Go to **Actions** tab
2. Click on the latest workflow run
3. View logs for each step
4. Check for errors or successful completion

## Testing Locally

Before committing, test the scraper locally:

```bash
# Make sure .env.local has DATABASE_URL
python scraper/main.py
```

## Notes

- The workflow uses Ubuntu latest runner
- Python dependencies are cached for faster execution
- The workflow will fail if DATABASE_URL is not configured
- Each run will skip duplicate articles automatically
