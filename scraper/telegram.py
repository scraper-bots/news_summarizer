"""
Telegram bot for scraping notifications and reporting
"""

import os
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional


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

        Args:
            message: Message text (supports HTML formatting)

        Returns:
            True if sent successfully to at least one chat, False otherwise
        """
        if not self.enabled:
            return False

        success_count = 0
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        for chat_id in self.chat_ids:
            try:
                payload = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                }

                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                success_count += 1

            except Exception as e:
                print(f"[ERROR] Failed to send Telegram message to chat {chat_id}: {e}")

        return success_count > 0

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
        Send comprehensive scraping report

        Args:
            stats: Dictionary containing scraping statistics
                - start_time: datetime
                - end_time: datetime
                - sources: List of source stats
                - total_found: int (total articles found across all sources)
                - total_scraped: int (successfully scraped, excluding duplicates)
                - total_saved: int (saved to database)
                - total_skipped: int (duplicates skipped)
                - errors: List of errors (optional)

        Returns:
            True if sent successfully
        """
        if not self.enabled:
            return False

        try:
            # Calculate duration
            duration = (stats['end_time'] - stats['start_time']).total_seconds()
            duration_str = self.format_duration(duration)

            # Build header
            message_parts = [
                "📰 <b>News Scraping Report</b>",
                "━━━━━━━━━━━━━━━━━━━━",
                ""
            ]

            # Overall stats
            success_emoji = "✅" if stats['total_saved'] > 0 else "⚠️"
            message_parts.extend([
                f"{success_emoji} <b>Summary</b>",
                f"🕐 Duration: {duration_str}",
                f"📊 Sources scraped: {len(stats['sources'])}",
                f"📝 Total articles found: {stats['total_found']}",
                f"💾 New articles saved: {stats['total_saved']}",
                f"⏭ Duplicates skipped: {stats['total_skipped']}",
                ""
            ])

            # Per-source breakdown
            if stats['sources']:
                message_parts.append("📚 <b>By Source</b>")
                for source in stats['sources']:
                    source_emoji = "📌"
                    if source['saved'] == 0:
                        source_emoji = "⚪️"
                    elif source['saved'] > 10:
                        source_emoji = "🟢"
                    elif source['saved'] > 0:
                        source_emoji = "🟡"

                    message_parts.append(
                        f"{source_emoji} <b>{source['name']}</b>: "
                        f"{source['saved']} new / {source['total']} total"
                    )
                message_parts.append("")

            # Session summary (if available) - truncate if too long
            if stats.get('session_summary'):
                summary = stats['session_summary']
                max_summary_length = 2000  # Leave room for the rest of the message

                if len(summary) > max_summary_length:
                    summary = summary[:max_summary_length] + "...\n\n[Summary truncated - too long for Telegram]"

                message_parts.extend([
                    "📋 <b>Session Summary</b>",
                    summary,
                    ""
                ])

            # Errors (if any)
            if stats.get('errors'):
                message_parts.extend([
                    "❌ <b>Errors</b>",
                    f"⚠️ {len(stats['errors'])} error(s) occurred"
                ])
                for error in stats['errors'][:3]:  # Show max 3 errors
                    message_parts.append(f"  • {error}")
                if len(stats['errors']) > 3:
                    message_parts.append(f"  • ... and {len(stats['errors']) - 3} more")
                message_parts.append("")

            # Footer
            timestamp = stats['end_time'].strftime("%Y-%m-%d %H:%M:%S UTC")
            message_parts.extend([
                "━━━━━━━━━━━━━━━━━━━━",
                f"🕒 {timestamp}"
            ])

            message = "\n".join(message_parts)

            # Telegram has a 4096 character limit - ensure we don't exceed it
            MAX_TELEGRAM_LENGTH = 4096
            if len(message) > MAX_TELEGRAM_LENGTH:
                # Truncate and add warning
                message = message[:MAX_TELEGRAM_LENGTH - 100] + "\n\n⚠️ [Message truncated - exceeded Telegram length limit]"

            return self.send_message(message)

        except Exception as e:
            print(f"[ERROR] Failed to build Telegram report: {e}")
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
