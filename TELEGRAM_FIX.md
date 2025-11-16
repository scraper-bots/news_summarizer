# Telegram 400 Bad Request Fix

## Problem
Error: `400 Client Error: Bad Request for url: https://api.telegram.org/bot***/sendMessage`

## Root Cause
The AI-generated session summary from Gemini was **6,544 characters**, which when combined with the rest of the Telegram report exceeded Telegram's **4,096 character message limit**.

## Solution Implemented

### 1. Summary Truncation (scraper/telegram.py:140-152)
```python
# Truncate session summary to 2000 characters max
if len(summary) > 2000:
    summary = summary[:2000] + "...\n\n[Summary truncated - too long for Telegram]"
```

### 2. Full Message Safety Check (scraper/telegram.py:175-179)
```python
# Final check - ensure entire message doesn't exceed 4096 chars
MAX_TELEGRAM_LENGTH = 4096
if len(message) > MAX_TELEGRAM_LENGTH:
    message = message[:MAX_TELEGRAM_LENGTH - 100] + "\n\n⚠️ [Message truncated - exceeded Telegram length limit]"
```

## Test Results

### Before Fix:
- Summary: 6,544 characters
- Full message: ~7,000+ characters
- Result: ❌ 400 Bad Request

### After Fix:
- Summary: 2,048 characters (truncated from 7,000)
- Full message: 2,403 characters
- Result: ✅ Within Telegram limits (< 4,096)

## Impact
- ✅ Telegram messages will now send successfully
- ✅ Users still get comprehensive stats and a summary preview
- ✅ Full summary is always saved in the database (no truncation there)
- ✅ Two-layer protection: summary truncation + full message truncation

## Alternative Solutions (Future Enhancement)

If you want to send the full summary:

**Option 1: Split into Multiple Messages**
```python
def send_long_message(message):
    chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
    for chunk in chunks:
        send_message(chunk)
        time.sleep(1)  # Avoid rate limiting
```

**Option 2: Send Summary as File**
```python
# Send summary as a text file attachment
requests.post(
    f"https://api.telegram.org/bot{token}/sendDocument",
    files={'document': ('summary.txt', summary_text)}
)
```

**Option 3: Link to Web View**
- Upload full summary to a simple web page
- Send link in Telegram message

## Current Behavior

Telegram message now includes:
- ✅ Scraping statistics (duration, sources, counts)
- ✅ Per-source breakdown
- ✅ First 2,000 characters of AI summary (enough for overview)
- ✅ Error reports (if any)
- ✅ Timestamp

Full summary is always available in:
- Database: `news.scraping_summaries.summary`
- Query: `SELECT summary FROM news.scraping_summaries WHERE id = X`
