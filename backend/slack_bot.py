"""
Slack Bot integration for URL Shortener
"""
import os
import hmac
import hashlib
import time
import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import parse_qs

from fastapi import HTTPException, Request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from database import SessionLocal, URLMapping, User
from sqlalchemy.orm import Session
from sqlalchemy import desc

logger = logging.getLogger(__name__)

class SlackBot:
    def __init__(self):
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        self.signing_secret = os.getenv("SLACK_SIGNING_SECRET")
        
    def verify_slack_request(self, request_body: bytes, headers: Dict[str, str]) -> bool:
        """Verify that the request came from Slack"""
        if not self.signing_secret:
            logger.error("SLACK_SIGNING_SECRET not set - cannot verify Slack requests")
            return False
            
        timestamp = headers.get('x-slack-request-timestamp', '')
        signature = headers.get('x-slack-signature', '')
        
        if not timestamp or not signature:
            return False
            
        # Check if timestamp is too old (replay attack protection)
        if abs(time.time() - int(timestamp)) > 60 * 5:  # 5 minutes
            return False
            
        # Create expected signature
        sig_basestring = f'v0:{timestamp}:{request_body.decode()}'
        expected_signature = 'v0=' + hmac.new(
            self.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    async def handle_slash_command(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack slash commands"""
        command = form_data.get('command', '')
        text = form_data.get('text', '').strip()
        user_id = form_data.get('user_id', '')
        user_name = form_data.get('user_name', '')
        
        logger.info(f"Slack command received: {command} from {user_name} ({user_id})")
        
        try:
            if command == '/transmute':
                return await self._handle_shorten_command(text, user_id, user_name)
            elif command == '/urlstats':
                return await self._handle_stats_command(text, user_id, user_name)
            elif command == '/urlremove':
                return await self._handle_remove_command(text, user_id, user_name)
            else:
                return {
                    "response_type": "ephemeral",
                    "text": f"Unknown command: {command}. Available commands: /transmute, /urlstats, /urlremove"
                }
        except Exception as e:
            logger.error(f"Error handling command {command}: {str(e)}")
            return {
                "response_type": "ephemeral",
                "text": f"❌ Error: {str(e)}"
            }
    
    async def _handle_shorten_command(self, text: str, user_id: str, user_name: str) -> Dict[str, Any]:
        """Handle /transmute command"""
        if not text:
            return {
                "response_type": "ephemeral",
                "text": "❌ Please provide a URL to transmute. Usage: `/transmute <url> [custom_code]`"
            }
        
        parts = text.split()
        url = parts[0]
        custom_code = parts[1] if len(parts) > 1 else None
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        try:
            db = SessionLocal()
            
            # Get or create slackbot user
            bot_username = f"slackbot-{user_name}"
            bot_user = db.query(User).filter(User.username == bot_username).first()
            if not bot_user:
                # Create a bot user
                bot_user = User(
                    username=bot_username,
                    email=f"{bot_username}@slack.bot",
                    hashed_password="slack-bot-no-password",
                    is_active=True
                )
                db.add(bot_user)
                db.commit()
                db.refresh(bot_user)
            
            # Generate short code if not provided
            if not custom_code:
                import string
                import random
                custom_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Create URL entry
            url_mapping = URLMapping(
                original_url=url,
                short_code=custom_code,
                user_id=bot_user.id
            )
            db.add(url_mapping)
            db.commit()
            db.refresh(url_mapping)
            
            result = url_mapping
            
            base_url = os.getenv('BASE_URL', 'http://localhost:8000')
            short_url = f"{base_url}/{result.short_code}"
            
            response = {
                "response_type": "in_channel",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"🔗 *URL Transmuted by {user_name}*"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Original:*\n{url}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Transmuted:*\n<{short_url}|{short_url}>"
                            }
                        ]
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Code: `{result.short_code}` | Created: {result.created_at.strftime('%Y-%m-%d %H:%M')}"
                            }
                        ]
                    }
                ]
            }
            db.close()
            return response
            
        except Exception as e:
            db.rollback()
            db.close()
            logger.error(f"Error creating short URL: {str(e)}")
            return {
                "response_type": "ephemeral",
                "text": f"❌ Failed to transmute URL: {str(e)}"
            }
    
    async def _handle_stats_command(self, text: str, user_id: str, user_name: str) -> Dict[str, Any]:
        """Handle /urlstats command"""
        text = text.strip()
        
        try:
            db = SessionLocal()
            
            # If no text or "all" flag, show all URLs for this user
            if not text or text.lower() == 'all':
                return await self._handle_all_stats(db, user_id, user_name)
            
            # Otherwise, show stats for specific short code
            short_code = text
            stats = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
            
            if not stats:
                db.close()
                return {
                    "response_type": "ephemeral",
                    "text": f"❌ No URL found with code: `{short_code}`\n💡 Use `/urlstats all` to see all your URLs"
                }
            
            base_url = os.getenv('BASE_URL', 'http://localhost:8000')
            short_url = f"{base_url}/{short_code}"
            
            response = {
                "response_type": "ephemeral",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"📊 *Stats for* `{short_code}`"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Short URL:*\n<{short_url}|{short_url}>"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Original URL:*\n{stats.original_url}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Click Count:*\n{stats.click_count}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Created:*\n{stats.created_at.strftime('%Y-%m-%d %H:%M')}"
                            }
                        ]
                    }
                ]
            }
            db.close()
            return response
            
        except Exception as e:
            db.close()
            logger.error(f"Error getting stats: {str(e)}")
            return {
                "response_type": "ephemeral",
                "text": f"❌ Failed to get stats: {str(e)}"
            }
    
    async def _handle_all_stats(self, db: Session, user_id: str, user_name: str) -> Dict[str, Any]:
        """Handle showing all URLs for a user"""
        try:
            # Get bot username for this Slack user
            bot_username = f"slackbot-{user_name}"
            bot_user = db.query(User).filter(User.username == bot_username).first()
            
            if not bot_user:
                db.close()
                return {
                    "response_type": "ephemeral",
                    "text": f"📭 No URLs found for {user_name}.\n💡 Use `/transmute <url>` to create your first shortened URL!"
                }
            
            # Get all URLs for this user, ordered by most recent
            urls = db.query(URLMapping).filter(URLMapping.user_id == bot_user.id).order_by(desc(URLMapping.created_at)).limit(10).all()
            
            if not urls:
                db.close()
                return {
                    "response_type": "ephemeral",
                    "text": f"📭 No URLs found for {user_name}.\n💡 Use `/transmute <url>` to create your first shortened URL!"
                }
            
            base_url = os.getenv('BASE_URL', 'http://localhost:8000')
            
            # Build the response blocks
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"📊 *All URLs for {user_name}* (showing last {len(urls)})"
                    }
                },
                {
                    "type": "divider"
                }
            ]
            
            total_clicks = sum(url.click_count for url in urls)
            
            for url in urls:
                short_url = f"{base_url}/{url.short_code}"
                # Truncate long URLs for display
                display_url = url.original_url if len(url.original_url) <= 60 else url.original_url[:57] + "..."
                
                blocks.append({
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Code:* `{url.short_code}`\n*Clicks:* {url.click_count}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Short:* <{short_url}|{url.short_code}>\n*Created:* {url.created_at.strftime('%m/%d')}"
                        }
                    ]
                })
                
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Original: {display_url}"
                        }
                    ]
                })
            
            # Add summary
            blocks.append({
                "type": "divider"
            })
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📈 Total: {len(urls)} URLs, {total_clicks} clicks"
                    }
                ]
            })
            
            db.close()
            return {
                "response_type": "ephemeral",
                "blocks": blocks
            }
            
        except Exception as e:
            db.close()
            logger.error(f"Error getting all stats for {user_name}: {str(e)}")
            return {
                "response_type": "ephemeral",
                "text": f"❌ Failed to get all stats: {str(e)}"
            }

    async def _handle_remove_command(self, text: str, user_id: str, user_name: str) -> Dict[str, Any]:
        """Handle /urlremove command"""
        if not text:
            return {
                "response_type": "ephemeral",
                "text": "❌ Please provide a short code to remove. Usage: `/urlremove <short_code>`"
            }

        short_code = text.strip()
        
        try:
            db = SessionLocal()
            
            # Get bot username for this Slack user
            bot_username = f"slackbot-{user_name}"
            bot_user = db.query(User).filter(User.username == bot_username).first()
            
            if not bot_user:
                db.close()
                return {
                    "response_type": "ephemeral",
                    "text": f"📭 No URLs found for {user_name}.\n💡 Use `/transmute <url>` to create your first shortened URL!"
                }
            
            # Find the URL mapping that belongs to this user
            url_mapping = db.query(URLMapping).filter(
                URLMapping.short_code == short_code,
                URLMapping.user_id == bot_user.id
            ).first()
            
            if not url_mapping:
                db.close()
                return {
                    "response_type": "ephemeral",
                    "text": f"❌ URL with code `{short_code}` not found in your collection.\n💡 Use `/urlstats all` to see all your URLs"
                }
            
            # Store info before deletion for confirmation message
            original_url = url_mapping.original_url
            click_count = url_mapping.click_count
            
            # Delete the URL mapping
            db.delete(url_mapping)
            db.commit()
            db.close()
            
            # Truncate long URLs for display
            display_url = original_url if len(original_url) <= 60 else original_url[:57] + "..."
            
            response = {
                "response_type": "ephemeral",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"🗑️ *URL Removed Successfully*"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Short Code:*\n`{short_code}`"
                            },
                            {
                                "type": "mrkdwn", 
                                "text": f"*Click Count:*\n{click_count}"
                            }
                        ]
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Original URL: {display_url}"
                            }
                        ]
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "⚠️ This short URL is now permanently inactive."
                            }
                        ]
                    }
                ]
            }
            
            return response
            
        except Exception as e:
            db.close() if 'db' in locals() else None
            logger.error(f"Error removing URL {short_code} for {user_name}: {str(e)}")
            return {
                "response_type": "ephemeral",
                "text": f"❌ Failed to remove URL: {str(e)}"
            }

# Global bot instance
slack_bot = SlackBot()