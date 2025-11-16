"""
Test Telegram message length handling
"""

# Test the length truncation logic
def test_truncation():
    # Simulate a very long summary (like the 6544 char one we had)
    long_summary = "A" * 7000

    max_summary_length = 2000

    if len(long_summary) > max_summary_length:
        summary = long_summary[:max_summary_length] + "...\n\n[Summary truncated - too long for Telegram]"
    else:
        summary = long_summary

    print("Original summary length:", len(long_summary))
    print("Truncated summary length:", len(summary))
    print()

    # Build a sample message
    message_parts = [
        "📰 <b>News Scraping Report</b>",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        "✅ <b>Summary</b>",
        "🕐 Duration: 106.1s",
        "📊 Sources scraped: 2",
        "📝 Total articles found: 82",
        "💾 New articles saved: 56",
        "⏭ Duplicates skipped: 26",
        "",
        "📚 <b>By Source</b>",
        "🟢 <b>Banker.az</b>: 26 new / 52 total",
        "🟢 <b>Marja.az</b>: 30 new / 30 total",
        "",
        "📋 <b>Session Summary</b>",
        summary,
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "🕒 2025-11-16 14:13:52 UTC"
    ]

    message = "\n".join(message_parts)

    print("Full message length:", len(message))

    # Apply Telegram limit
    MAX_TELEGRAM_LENGTH = 4096
    if len(message) > MAX_TELEGRAM_LENGTH:
        message = message[:MAX_TELEGRAM_LENGTH - 100] + "\n\n⚠️ [Message truncated - exceeded Telegram length limit]"
        print("Final message length after Telegram truncation:", len(message))
    else:
        print("✓ Message is within Telegram limits!")

    print()
    print("Status:", "✅ PASS" if len(message) <= MAX_TELEGRAM_LENGTH else "❌ FAIL")

if __name__ == "__main__":
    test_truncation()
