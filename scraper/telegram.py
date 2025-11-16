"""
Telegram bot for scraping notifications and reporting
"""

import sys
import os
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Fix encoding for Azerbaijani characters on Windows
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    import io
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class TelegramReporter:
    """Send scraping reports to Telegram"""

    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id_str = os.getenv('TELEGRAM_CHAT_ID', '')

        # Parse comma-separated chat IDs
        self.chat_ids = [
            chat_id.strip()
            for chat_id in chat_id_str.split(',')
            if chat_id.strip()
        ]

        self.enabled = bool(self.bot_token and self.chat_ids)

        if not self.enabled:
            print("[INFO] Telegram reporting disabled (missing credentials)")
        else:
            print(f"[INFO] Telegram reporting enabled for {len(self.chat_ids)} chat(s)")

    def send_message(self, message: str) -> bool:
        """
        Send a message to all configured Telegram chats
        If message exceeds Telegram limit, splits into multiple messages

        Args:
            message: Message text (supports HTML formatting)

        Returns:
            True if sent successfully to at least one chat, False otherwise
        """
        if not self.enabled:
            return False

        # Split message if too long
        MAX_TELEGRAM_LENGTH = 4096
        messages = self._split_message(message, MAX_TELEGRAM_LENGTH)

        success_count = 0
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        for chat_id in self.chat_ids:
            try:
                # Send all message parts
                for i, msg_part in enumerate(messages, 1):
                    # Add part indicator if multiple parts
                    if len(messages) > 1:
                        part_indicator = f"\n\n<i>[Part {i}/{len(messages)}]</i>"
                        msg_to_send = msg_part + part_indicator
                    else:
                        msg_to_send = msg_part

                    payload = {
                        'chat_id': chat_id,
                        'text': msg_to_send,
                        'parse_mode': 'HTML',
                        'disable_web_page_preview': True
                    }

                    response = requests.post(url, json=payload, timeout=10)
                    response.raise_for_status()

                    # Small delay between parts to avoid rate limiting
                    if i < len(messages):
                        import time
                        time.sleep(0.5)

                success_count += 1

            except Exception as e:
                print(f"[ERROR] Failed to send Telegram message to chat {chat_id}: {e}")

        return success_count > 0

    def _split_message(self, message: str, max_length: int) -> List[str]:
        """
        Split a long message into multiple parts

        Args:
            message: The message to split
            max_length: Maximum length per part

        Returns:
            List of message parts
        """
        if len(message) <= max_length:
            return [message]

        parts = []
        current_part = ""

        # Split by lines to avoid breaking in middle of content
        lines = message.split('\n')

        for line in lines:
            # If adding this line would exceed limit, save current part and start new one
            if len(current_part) + len(line) + 1 > max_length - 100:  # Leave room for part indicator
                if current_part:
                    parts.append(current_part)
                current_part = line
            else:
                if current_part:
                    current_part += '\n' + line
                else:
                    current_part = line

        # Add remaining content
        if current_part:
            parts.append(current_part)

        return parts

    def format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def send_scraping_report(self, stats: Dict) -> bool:
        """
        Send professional banking intelligence report for public channel

        Args:
            stats: Dictionary containing statistics
                - start_time: datetime
                - end_time: datetime
                - sources: List of source stats
                - total_saved: int (saved to database)
                - session_summary: str (banking intelligence)
                - errors: List of errors (optional)

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False

        try:
            # Professional public channel format
            timestamp = stats['end_time'].strftime("%d.%m.%Y")

            # Check if we have banking intelligence
            if not stats.get('session_summary'):
                # No intelligence to report
                return False

            message_parts = [
                f"📊 <b>Azərbaycan Bank Sektoru</b>",
                f"📅 {timestamp}",
                "",
                stats['session_summary']
            ]

            # Only show errors if they exist (very rare, keep internal)
            # Skip showing errors in public channel

            message = "\n".join(message_parts)

            # send_message will automatically split if needed
            return self.send_message(message)

        except Exception as e:
            print(f"[ERROR] Failed to build banking intelligence report: {e}")
            return False

    def send_error_alert(self, error_message: str) -> bool:
        """
        Send error alert to Telegram

        Args:
            error_message: Error description

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        message = (
            "🚨 <b>Scraping Error Alert</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"❌ {error_message}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🕒 {timestamp}"
        )

        return self.send_message(message)

    def send_start_notification(self, num_sources: int) -> bool:
        """
        Send scraping start notification

        Args:
            num_sources: Number of sources to scrape

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        message = (
            "🚀 <b>Scraping Started</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📚 Sources: {num_sources}\n"
            f"🕒 {timestamp}\n\n"
            "⏳ Processing..."
        )

        return self.send_message(message)
