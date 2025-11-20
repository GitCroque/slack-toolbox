#!/usr/bin/env python3
"""
Slack Client - Centralized client for all Slack API operations
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time

# Import validators for config validation
sys.path.insert(0, str(Path(__file__).parent))
from validators import validate_webhook_url, ValidationError

class SlackManager:
    """Centralized Slack API client with error handling and rate limiting"""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize Slack client with configuration

        Args:
            config_path: Path to config.json file. If None, uses default location.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.json"

        self.config = self._load_config(config_path)
        self._validate_config()

        self.token = self.config.get('slack_token')
        placeholder = self.config.get('placeholder_token', 'xoxb-your-bot-token-here')

        if not self.token or self.token == placeholder:
            raise ValueError(
                "Slack token not configured. Please update config/config.json with your Slack token.\n"
                "Visit https://api.slack.com/apps to create an app and get your token."
            )

        self.client = WebClient(token=self.token)
        self.max_retries = self.config.get('max_retries', 3)
        self.rate_limit_delay = self.config.get('rate_limit_delay', 1)

    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Please copy config/config.example.json to config/config.json and add your Slack token."
            )

        with open(config_path, 'r') as f:
            return json.load(f)

    def _validate_config(self) -> None:
        """
        Validate configuration parameters at startup

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate webhook URL if present
        webhook_url = self.config.get('webhook_url')
        if webhook_url and webhook_url != "https://hooks.slack.com/services/YOUR/WEBHOOK/URL":
            try:
                validate_webhook_url(webhook_url)
            except ValidationError as e:
                raise ValueError(f"Invalid webhook URL in configuration: {e}")

        # Validate max_retries
        max_retries = self.config.get('max_retries', 3)
        if not isinstance(max_retries, int) or max_retries < 0:
            raise ValueError(f"max_retries must be a positive integer, got: {max_retries}")

        # Validate rate_limit_delay
        rate_limit = self.config.get('rate_limit_delay', 1)
        if not isinstance(rate_limit, (int, float)) or rate_limit < 0:
            raise ValueError(f"rate_limit_delay must be a positive number, got: {rate_limit}")

    def _api_call_with_retry(self, method: str, **kwargs) -> Dict:
        """
        Make API call with retry logic and rate limiting

        Args:
            method: Slack API method name (e.g., 'users.list')
            **kwargs: Arguments to pass to the API method

        Returns:
            API response as dictionary
        """
        for attempt in range(self.max_retries):
            try:
                # Add rate limiting delay
                if attempt > 0:
                    time.sleep(self.rate_limit_delay * (2 ** attempt))

                response = getattr(self.client, method.replace('.', '_'))(**kwargs)

                if not response['ok']:
                    raise SlackApiError(f"API call failed: {response.get('error', 'Unknown error')}", response)

                return response

            except SlackApiError as e:
                if e.response['error'] == 'ratelimited':
                    retry_after = int(e.response.headers.get('Retry-After', 60))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                elif attempt < self.max_retries - 1:
                    print(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                    continue
                else:
                    raise

        raise Exception(f"Failed to complete API call after {self.max_retries} attempts")

    # ========== User Management Methods ==========

    def list_users(self, include_deleted: bool = False) -> List[Dict]:
        """
        Get list of all users in the workspace

        Args:
            include_deleted: Include deactivated users

        Returns:
            List of user dictionaries
        """
        users = []
        cursor = None

        while True:
            response = self._api_call_with_retry(
                'users.list',
                cursor=cursor,
                limit=200
            )

            users.extend(response['members'])

            cursor = response.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break

        if not include_deleted:
            users = [u for u in users if not u.get('deleted', False)]

        return users

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user information by email address"""
        try:
            response = self._api_call_with_retry('users.lookupByEmail', email=email)
            return response.get('user')
        except SlackApiError as e:
            if e.response['error'] == 'users_not_found':
                return None
            raise

    def invite_user(self, email: str, channels: Optional[List[str]] = None,
                   first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict:
        """
        Invite a user to the workspace (requires admin.users:write scope)

        Args:
            email: User's email address
            channels: List of channel IDs to add user to
            first_name: User's first name
            last_name: User's last name

        Returns:
            API response
        """
        params = {'email': email}

        if channels:
            params['channel_ids'] = ','.join(channels)
        if first_name:
            params['real_name'] = f"{first_name} {last_name}" if last_name else first_name

        return self._api_call_with_retry('admin.users.invite', **params)

    def deactivate_user(self, user_id: str) -> Dict:
        """Deactivate a user (requires admin.users:write scope)"""
        return self._api_call_with_retry('admin.users.remove', user_id=user_id)

    def set_user_admin(self, user_id: str, is_admin: bool = True) -> Dict:
        """Set user as workspace admin (requires admin.users:write scope)"""
        method = 'admin.users.setAdmin' if is_admin else 'admin.users.setRegular'
        return self._api_call_with_retry(method, user_id=user_id)

    # ========== Channel Management Methods ==========

    def list_channels(self, include_private: bool = False,
                     include_archived: bool = False) -> List[Dict]:
        """
        Get list of all channels

        Args:
            include_private: Include private channels
            include_archived: Include archived channels

        Returns:
            List of channel dictionaries
        """
        channels = []
        cursor = None

        types = 'public_channel'
        if include_private:
            types += ',private_channel'

        while True:
            response = self._api_call_with_retry(
                'conversations.list',
                types=types,
                exclude_archived=not include_archived,
                cursor=cursor,
                limit=200
            )

            channels.extend(response['channels'])

            cursor = response.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break

        return channels

    def create_channel(self, name: str, is_private: bool = False,
                      description: Optional[str] = None) -> Dict:
        """
        Create a new channel

        Args:
            name: Channel name (lowercase, no spaces)
            is_private: Create as private channel
            description: Channel description

        Returns:
            Created channel information
        """
        response = self._api_call_with_retry(
            'conversations.create',
            name=name,
            is_private=is_private
        )

        channel = response['channel']

        # Set description if provided
        if description:
            self.set_channel_topic(channel['id'], description)

        return channel

    def archive_channel(self, channel_id: str) -> Dict:
        """Archive a channel"""
        return self._api_call_with_retry('conversations.archive', channel=channel_id)

    def unarchive_channel(self, channel_id: str) -> Dict:
        """Unarchive a channel"""
        return self._api_call_with_retry('conversations.unarchive', channel=channel_id)

    def set_channel_topic(self, channel_id: str, topic: str) -> Dict:
        """Set channel topic/description"""
        return self._api_call_with_retry('conversations.setTopic',
                                        channel=channel_id, topic=topic)

    def get_channel_members(self, channel_id: str) -> List[str]:
        """Get list of user IDs in a channel"""
        members = []
        cursor = None

        while True:
            response = self._api_call_with_retry(
                'conversations.members',
                channel=channel_id,
                cursor=cursor,
                limit=200
            )

            members.extend(response['members'])

            cursor = response.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break

        return members

    def invite_to_channel(self, channel_id: str, user_ids: List[str]) -> Dict:
        """Add users to a channel"""
        return self._api_call_with_retry(
            'conversations.invite',
            channel=channel_id,
            users=','.join(user_ids)
        )

    def remove_from_channel(self, channel_id: str, user_id: str) -> Dict:
        """Remove a user from a channel"""
        return self._api_call_with_retry(
            'conversations.kick',
            channel=channel_id,
            user=user_id
        )

    # ========== Message & History Methods ==========

    def get_channel_history(self, channel_id: str, limit: int = 1000,
                           oldest: Optional[str] = None, latest: Optional[str] = None) -> List[Dict]:
        """
        Get message history from a channel

        Args:
            channel_id: Channel ID
            limit: Maximum number of messages to retrieve
            oldest: Only messages after this timestamp
            latest: Only messages before this timestamp

        Returns:
            List of message dictionaries
        """
        messages = []
        cursor = None

        while len(messages) < limit:
            params = {
                'channel': channel_id,
                'limit': min(200, limit - len(messages))
            }

            if oldest:
                params['oldest'] = oldest
            if latest:
                params['latest'] = latest
            if cursor:
                params['cursor'] = cursor

            response = self._api_call_with_retry('conversations.history', **params)
            messages.extend(response['messages'])

            cursor = response.get('response_metadata', {}).get('next_cursor')
            if not cursor or not response['has_more']:
                break

        return messages[:limit]

    # ========== File Methods ==========

    def list_files(self, user_id: Optional[str] = None,
                  channel_id: Optional[str] = None,
                  count: int = 100) -> List[Dict]:
        """
        List files in workspace

        Args:
            user_id: Filter by user
            channel_id: Filter by channel
            count: Number of files to return

        Returns:
            List of file dictionaries
        """
        params = {'count': min(count, 1000)}

        if user_id:
            params['user'] = user_id
        if channel_id:
            params['channel'] = channel_id

        response = self._api_call_with_retry('files.list', **params)
        return response.get('files', [])

    # ========== Workspace Info Methods ==========

    def get_workspace_info(self) -> Dict:
        """Get workspace/team information"""
        return self._api_call_with_retry('team.info')

    def get_user_stats(self) -> Dict:
        """Get statistics about users in the workspace"""
        users = self.list_users(include_deleted=True)

        stats = {
            'total': len(users),
            'active': len([u for u in users if not u.get('deleted') and not u.get('is_bot')]),
            'deleted': len([u for u in users if u.get('deleted')]),
            'bots': len([u for u in users if u.get('is_bot')]),
            'admins': len([u for u in users if u.get('is_admin')]),
            'owners': len([u for u in users if u.get('is_owner')]),
            'guests': len([u for u in users if u.get('is_restricted') or u.get('is_ultra_restricted')])
        }

        return stats

    def test_connection(self) -> bool:
        """Test if the Slack connection is working"""
        try:
            response = self._api_call_with_retry('auth.test')
            print(f"✅ Connected to Slack workspace: {response['team']}")
            print(f"   Bot user: {response['user']}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Slack: {e}")
            return False
