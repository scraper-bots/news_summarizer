# Schema Analysis and Improvement Plan

## Current Issues

### 1. **`summary` column in `articles` table**
- Currently: NULL for all articles
- Purpose: Unclear - could be for individual article AI summaries OR redundant
- Problem: Not being used, wasting space

### 2. **No relationship between articles and scraping_summaries**
- `scraping_summaries` contains comprehensive session summaries
- No way to know which specific articles were included in which summary session
- Cannot trace back which articles contributed to a summary

## Proposed Solution

### Option A: Individual Article Summaries + Session Link
```
articles table:
- summary: AI-generated summary of THIS specific article (individual)
- scraping_session_id: FK to scraping_summaries (which session collected it)

scraping_summaries table:
- summary: Comprehensive summary of ALL articles in this session
```

**Use case:**
- `articles.summary` = "Bu xəbər SOCAR-ın BB reytinqi alması haqqındadır..." (individual)
- `scraping_summaries.summary` = "Bugün 56 xəbər toplandı. Bank sektoru..." (comprehensive)

### Option B: Remove Individual Summaries, Add Session Link Only
```
articles table:
- Remove 'summary' column entirely
- scraping_session_id: FK to scraping_summaries

scraping_summaries table:
- summary: Comprehensive summary only
```

## Recommendation: **Option A**

### Why?
1. **Individual summaries** useful for:
   - Quick article preview in UI
   - Search/indexing
   - Social media sharing
   - API responses

2. **Session summaries** useful for:
   - Daily digest emails
   - Telegram reports
   - Historical analysis
   - Trend tracking

3. **Session link** useful for:
   - Tracking which articles in which session
   - Audit trail
   - Re-generating summaries
   - Quality control

## Implementation Plan

### 1. Add foreign key to articles
```sql
ALTER TABLE news.articles
ADD COLUMN scraping_session_id INTEGER
REFERENCES news.scraping_summaries(id);

CREATE INDEX idx_articles_session
ON news.articles(scraping_session_id);
```

### 2. Update article insertion to link to session
- When scraping starts, create scraping_summary record FIRST
- Get the session_id
- Pass session_id when inserting articles
- Articles automatically linked to their session

### 3. Optionally: Generate individual summaries
- For each article, call Gemini API to summarize just that article
- Store in articles.summary column
- This is separate from the comprehensive session summary

## Schema After Changes

```
news.articles
├── id (PK)
├── title
├── content
├── summary                    ← Individual article AI summary
├── source
├── url (UNIQUE)
├── published_date
├── scraped_at
├── language
├── created_at
├── updated_at
└── scraping_session_id (FK)   ← Links to scraping_summaries

news.scraping_summaries
├── id (PK)
├── scraping_date
├── summary                     ← Comprehensive session summary
├── articles_count
├── sources_count
├── new_articles_count
├── scraping_duration_seconds
├── created_at
└── updated_at
```

## Benefits

1. ✅ Clear separation: individual vs session summaries
2. ✅ Traceability: know which articles in which session
3. ✅ Flexibility: can query "show me all articles from yesterday's scraping session"
4. ✅ Audit: can verify summary accuracy by checking linked articles
5. ✅ Re-generation: can re-run summarization on specific sessions
