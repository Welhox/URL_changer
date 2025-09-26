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
        # Skip verification in development mode
        if os.getenv("ENVIRONMENT", "development") == "development":
            logger.info("Development mode - skipping Slack signature verification")
            return True
            
        if not self.signing_secret:
            logger.warning("SLACK_SIGNING_SECRET not set - skipping verification")
            return True
            
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
            if command == '/shorten':
                return await self._handle_shorten_command(text, user_id, user_name)
            elif command == '/urlstats':
                return await self._handle_stats_command(text, user_id, user_name)
            else:
                return {
                    "response_type": "ephemeral",
                    "text": f"Unknown command: {command}"
                }
        except Exception as e:
            logger.error(f"Error handling command {command}: {str(e)}")
            return {
                "response_type": "ephemeral",
                "text": f"❌ Error: {str(e)}"
            }
    
    async def _handle_shorten_command(self, text: str, user_id: str, user_name: str) -> Dict[str, Any]:
        """Handle /shorten command"""
        if not text:
            return {
                "response_type": "ephemeral",
                "text": "❌ Please provide a URL to shorten. Usage: `/shorten <url> [custom_code]`"
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
                            "text": f"🔗 *URL Shortened by {user_name}*"
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
                                "text": f"*Shortened:*\n<{short_url}|{short_url}>"
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
                "text": f"❌ Failed to shorten URL: {str(e)}"
            }
    
    async def _handle_stats_command(self, text: str, user_id: str, user_name: str) -> Dict[str, Any]:
        """Handle /urlstats command"""
        if not text:
            return {
                "response_type": "ephemeral",
                "text": "❌ Please provide a short code. Usage: `/urlstats <short_code>`"
            }
        
        short_code = text.strip()
        
        try:
            db = SessionLocal()
            stats = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
            
            if not stats:
                return {
                    "response_type": "ephemeral",
                    "text": f"❌ No URL found with code: `{short_code}`"
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
            logger.error(f"Error getting stats for {short_code}: {str(e)}")
            return {
                "response_type": "ephemeral",
                "text": f"❌ Failed to get stats: {str(e)}"
            }

# Global bot instance
slack_bot = SlackBot()