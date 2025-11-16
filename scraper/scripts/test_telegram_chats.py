"""
Test Telegram message delivery to all configured chat IDs
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.local
env_path = Path(__file__).parent / '.env.local'
load_dotenv(env_path)

sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.telegram import TelegramReporter
from datetime import datetime, timezone

print("=" * 80)
print("TELEGRAM CHAT IDs TEST")
print("=" * 80)

# Initialize Telegram reporter
telegram = TelegramReporter()

# Check configuration
print(f"\n[INFO] Telegram enabled: {telegram.enabled}")
print(f"[INFO] Number of chat IDs configured: {len(telegram.chat_ids)}")

if telegram.chat_ids:
    print("\n[INFO] Configured chat IDs:")
    for i, chat_id in enumerate(telegram.chat_ids, 1):
        print(f"  {i}. {chat_id}")
else:
    print("\n[ERROR] No chat IDs configured!")
    sys.exit(1)

print("\n" + "=" * 80)
print("SENDING TEST MESSAGE")
print("=" * 80)

# Create test message with new clean format
test_message = f"""✅ <b>Test Message - Banking Intelligence</b>
⏱ Test Mode | 💾 3 chat IDs configured

📚 Chat IDs: {len(telegram.chat_ids)}

🏦 <b>System Check</b>

🔥 ƏSAS TEST
Bu test mesajıdır. Əgər bu mesajı alırsınızsa, Telegram inteqrasiyası işləyir.

💰 KONFIQURASIYA
• Chat ID sayı: {len(telegram.chat_ids)}
• Bot token: Configured ✅
• Multi-message: Enabled ✅

✅ STATUS
Sistem hazırdır və işləyir!

🕒 {datetime.now(timezone.utc).strftime("%H:%M, %d.%m.%Y")}"""

print("\n[INFO] Attempting to send test message...")
success = telegram.send_message(test_message)

print("\n" + "=" * 80)
print("TEST RESULTS")
print("=" * 80)

if success:
    print("\n✅ SUCCESS! Test message sent to at least one chat")
    print("\n[INFO] Check your Telegram to confirm which chats received the message")
    print("[INFO] Expected: All 3 chat IDs should receive the message")
else:
    print("\n❌ FAILED! Could not send test message")
    print("\n[INFO] Check the error messages above for details")
    print("[INFO] Common issues:")
    print("  - Invalid bot token")
    print("  - Invalid chat ID")
    print("  - Bot not started by user (each user must /start the bot first)")
    print("  - Network connectivity")

print("\n" + "=" * 80)
