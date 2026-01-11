# Troubleshooting Guide

This document covers common issues, limitations, and their solutions.

## Known Issues

### OXU.AZ: 403 Forbidden Errors

**Status:** Known limitation, cannot be fixed without browser automation

**Issue:**
```
Error: [ERROR] Client error fetching https://oxu.az/iqtisadiyyat: 403, message='Forbidden'
```

**Cause:**
OXU.AZ uses aggressive bot protection (likely Cloudflare or similar) that blocks automated scraping, even with realistic headers.

**Impact:**
- OXU.AZ articles cannot be scraped
- The scraper gracefully handles this by continuing with other sources
- No articles from OXU.AZ will appear in the database

**Solutions (not currently implemented):**

1. **Browser Automation (Selenium/Playwright)**
   - Pros: Can bypass most bot protection
   - Cons: Slow, resource-intensive, complex setup
   - Not suitable for GitHub Actions environment

2. **Scraping API Services**
   - Pros: Handles bot protection automatically
   - Cons: Costs money, requires API keys
   - Examples: ScraperAPI, Bright Data

3. **Manual Monitoring**
   - Check if OXU.AZ changes their bot protection policy
   - Contact their team for API access or permission

**Current Approach:**
The scraper suppresses 403 errors from OXU.AZ to avoid cluttering logs. Other sources continue working normally.

---

### Banker.az: Special Character URLs

**Status:** Fixed with fallback selectors

**Issue:**
Some Banker.az articles with URL-encoded Azerbaijani characters (e.g., `%c9%99` = ə) had different HTML structure.

**Example:**
```
https://banker.az/prezident-d%c9%99rman-preparatlari-istehsali-mu%c9%99ssis%c9%99sinin-acilisinda-istirak-edib/
```

**Fix:**
Added multiple fallback selectors for both title and content extraction:

- **Title:** `h1.tdb-title-text` → `h1.entry-title` → `h1`
- **Content:** `.tdb_single_content .tdb-block-inner` → `.tdb_single_content` → `article .entry-content` → `.td-post-content`

**Status:** ✅ Resolved

---

### Iqtisadiyyat.az: 404 on Page 2

**Status:** Expected behavior, not an error

**Issue:**
```
Error: [ERROR] Client error fetching https://iqtisadiyyat.az/az/category/bank-35/page/2: 404
```

**Cause:**
The site only has 1 page of articles in this category, but the scraper tries to fetch 2 pages.

**Fix:**
404 errors are now suppressed as they indicate normal pagination boundaries.

**Status:** ✅ Resolved

---

## Gemini API Errors

### 403: API Key Leaked

**Issue:**
```
Error: 403 Your API key was reported as leaked. Please use another API key.
```

**Solution:**
See [API_KEY_UPDATE.md](./API_KEY_UPDATE.md) for step-by-step instructions to:
1. Generate a new Gemini API key
2. Update GitHub Secret
3. Revoke old key

**Impact:**
- Article scraping continues to work
- AI summary generation is blocked until key is updated

---

### Rate Limiting

**Issue:**
```
[INFO] Rate limit: waiting 45.2s...
```

**Cause:**
Gemini API free tier has these limits:
- 15 requests per minute
- 1 million tokens per minute
- 1500 requests per day

**Solution:**
The scraper automatically handles rate limiting by:
1. Tracking request timestamps
2. Waiting when limit is reached
3. Resuming after the wait period

**Status:** ✅ Handled automatically

---

## Database Issues

### Connection Refused

**Issue:**
```
[ERROR] Failed to connect to database
```

**Causes:**
1. Invalid `DATABASE_URL` in GitHub Secrets
2. Database server is down
3. Network connectivity issues
4. SSL/TLS certificate problems

**Solutions:**

1. **Verify DATABASE_URL:**
   ```bash
   # Format should be:
   postgresql://user:password@host/database?sslmode=require
   ```

2. **Check database status** (for Neon):
   - Log in to Neon console
   - Verify project is active (not suspended)
   - Check for maintenance notifications

3. **Test connection locally:**
   ```bash
   # Install psql
   psql "postgresql://user:password@host/database?sslmode=require"
   ```

4. **Update GitHub Secret:**
   - Settings → Secrets → Actions → DATABASE_URL
   - Paste new connection string

---

## Telegram Reporting Issues

### Messages Not Sending

**Issue:**
No Telegram messages received after scraping

**Causes:**
1. Invalid `TELEGRAM_BOT_TOKEN`
2. Invalid `TELEGRAM_CHAT_ID`
3. Bot not added to group/channel
4. Bot blocked by user

**Solutions:**

1. **Verify bot token:**
   ```bash
   # Test with curl
   curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
   ```

2. **Verify chat ID:**
   - Start chat with bot
   - Send a message
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Find "chat":{"id": YOUR_CHAT_ID}

3. **For groups/channels:**
   - Add bot as admin
   - Chat ID should start with `-` (e.g., `-123456789`)

4. **Update GitHub Secrets:**
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID

---

## Performance Issues

### Scraping Takes Too Long

**Expected Duration:** 3-7 minutes for all sources

**If longer than 10 minutes:**

1. **Check timeout errors:**
   - Look for `[ERROR] Timeout fetching` in logs
   - Some sites may be slow or down

2. **Network issues:**
   - GitHub Actions may have network congestion
   - Retry the workflow

3. **Rate limiting:**
   - Gemini API rate limiting adds wait time
   - This is normal and expected

---

## GitHub Actions Issues

### Workflow Fails to Start

**Causes:**
1. GitHub Actions disabled for repository
2. Workflow file has syntax errors
3. Branch protection rules

**Solutions:**
- Check Actions tab for error messages
- Validate YAML syntax: https://www.yamllint.com/
- Review branch protection settings

### Workflow Fails with Permission Errors

**Cause:**
Missing repository secrets

**Solution:**
Ensure all required secrets are configured:
- `DATABASE_URL` (required)
- `GEMINI_API_KEY` (required for summaries)
- `TELEGRAM_BOT_TOKEN` (optional)
- `TELEGRAM_CHAT_ID` (optional)

---

## Getting Help

### Check Logs

**GitHub Actions:**
1. Go to Actions tab
2. Click on failed workflow run
3. Expand failing step
4. Review error messages

**Telegram:**
- Check for error alerts sent by the bot
- Review the scraping report for statistics

### Common Error Patterns

| Error Message | Location | Fix |
|--------------|----------|-----|
| `Could not find title` | Banker.az | Fixed with fallback selectors |
| `403 Forbidden` | OXU.AZ | Known limitation (bot protection) |
| `404 Not Found` | Any source | Normal pagination boundary |
| `Database connection failed` | Database | Check DATABASE_URL secret |
| `API key leaked` | Gemini | Update GEMINI_API_KEY secret |
| `Rate limit` | Gemini | Automatic wait, no action needed |

---

## Best Practices

### Monitoring

1. **Daily checks:**
   - Review Telegram reports
   - Check for drop in article count

2. **Weekly review:**
   - Review GitHub Actions success rate
   - Check for new error patterns

3. **Monthly maintenance:**
   - Update dependencies
   - Rotate API keys (security)
   - Review database size

### Security

1. **Never commit secrets** to version control
2. **Use GitHub Secrets** for all credentials
3. **Rotate API keys** every 3-6 months
4. **Monitor API usage** for anomalies
5. **Keep dependencies updated** for security patches

---

**Last Updated:** 2025-11-22
