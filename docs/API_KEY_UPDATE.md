# 🚨 URGENT: Gemini API Key Update Required

## Issue

Your Gemini API key has been compromised and blocked by Google with the following error:

```
Error: 403 Your API key was reported as leaked. Please use another API key.
```

This prevents the AI summary generation from completing. While articles are still being scraped successfully, the banking intelligence report cannot be created.

## Impact

- ✅ **Article scraping**: Still working (187 articles scraped successfully)
- ✅ **Database storage**: Still working (articles saved to database)
- ❌ **AI summaries**: BLOCKED (cannot generate banking intelligence reports)
- ❌ **Telegram reports**: Missing the AI-generated daily digest section

## Fix Instructions

### Step 1: Generate New Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Get API key"** or **"Create API key"**
4. Select your Google Cloud project (or create a new one)
5. Copy the new API key (format: `AIzaSy...`)

### Step 2: Update GitHub Secret

1. Go to your repository: https://github.com/scraper-bots/news_summarizer
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Find `GEMINI_API_KEY` in the repository secrets list
4. Click the **pencil icon** (Update) next to it
5. Paste your new API key
6. Click **Update secret**

### Step 3: Revoke Old/Leaked Key

**IMPORTANT:** Delete the compromised key to prevent security issues

1. Return to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Find the leaked/old API key in your list
3. Click **Delete** or **Revoke** to permanently disable it

### Step 4: Test the Fix

Verify the new key works by running the scraper manually:

1. Go to the **Actions** tab in your repository
2. Select **Daily News Scraper** workflow
3. Click **Run workflow** → **Run workflow**
4. Monitor the execution logs
5. Verify the summary generation completes successfully

Expected output:
```
[SUCCESS] Gemini API initialized (gemini-flash-latest)
[SUCCESS] Created banking intelligence report from XX relevant articles
```

## Security Best Practices

To prevent future key leaks:

1. **Never commit API keys** to version control
2. **Use GitHub Secrets** for all sensitive credentials
3. **Rotate keys regularly** (every 3-6 months)
4. **Monitor API usage** in Google AI Studio
5. **Set up usage alerts** to detect unusual activity

## Support

If you encounter issues:

1. Check that the new API key is valid in Google AI Studio
2. Verify the GitHub Secret is updated (no typos)
3. Review workflow logs in GitHub Actions for detailed error messages
4. Test locally first with `.env.local` before updating GitHub Secrets

## Timeline

- **Priority**: HIGH - Update within 24 hours
- **Impact**: Medium - Scraping works but no AI summaries
- **Effort**: 5 minutes to update the secret

---

**Last Updated**: 2025-11-22
