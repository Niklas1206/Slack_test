#!/usr/bin/env python3
"""
Slack Connection Test
"""

import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

SEND_MESSAGE_FLAG = os.getenv('SEND_SLACK_TEST_MESSAGE', '0').lower() in {'1', 'true', 'yes'}

def test_slack_connection():
    """Testet Slack-Verbindung und Berechtigungen."""

    token = os.getenv('SLACK_BOT_TOKEN')
    channel = os.getenv('SLACK_CHANNEL', 'test-projekt-bewerbung')

    print("Testing Slack connection...")
    print(f"Token: {token[:20]}..." if token else "No token")
    print(f"Channel: #{channel}")

    if not token or not token.startswith('xoxb-'):
        print("[ERROR] Invalid Slack token")
        return False

    try:
        client = WebClient(token=token)

        print("\n[TEST 1] Testing authentication...")
        auth_response = client.auth_test()
        print(f"[SUCCESS] Bot connected as: {auth_response['user']}")
        print(f"[SUCCESS] Team: {auth_response['team']}")

        print("\n[TEST 2] Listing channels...")
        channels_response = client.conversations_list(types="public_channel,private_channel")

        target_channel_id = None
        print("Available channels:")
        for channel_info in channels_response['channels']:
            channel_name = channel_info['name']
            channel_id = channel_info['id']
            is_member = channel_info.get('is_member', False)
            print(f"  #{channel_name} (ID: {channel_id}) - Member: {is_member}")

            if channel_name == channel:
                target_channel_id = channel_id
                print(f"  -> TARGET CHANNEL FOUND: {channel_id}")

        if not target_channel_id:
            print(f"[ERROR] Channel #{channel} not found!")
            print(f"[TIP] Create channel #{channel} or use existing channel")
            return False

        if not SEND_MESSAGE_FLAG:
            print("\n[INFO] Skipping test message (set SEND_SLACK_TEST_MESSAGE=1 to enable sending).")
            return True

        print(f"\n[TEST 3] Sending test message to #{channel}...")
        test_message = {
            "channel": target_channel_id,
            "text": "Slack integration test completed.",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Slack Test*\nManually triggered integration check."
                    }
                }
            ]
        }

        response = client.chat_postMessage(**test_message)
        print(f"[SUCCESS] Message sent! Timestamp: {response['ts']}")

        return True

    except SlackApiError as error:
        print(f"[ERROR] Slack API Error: {error.response['error']}")
        if error.response['error'] == 'not_in_channel':
            print(f"[TIP] Bot is not in channel #{channel}")
            print("[TIP] Run in Slack: /invite @ai-interview-agent")
        elif error.response['error'] == 'channel_not_found':
            print(f"[TIP] Channel #{channel} does not exist")
        elif error.response['error'] == 'missing_scope':
            print("[TIP] Bot needs 'chat:write' permission")
        return False

    except Exception as exc:
        print(f"[ERROR] Connection failed: {exc}")
        return False

if __name__ == "__main__":
    print("=== Slack Connection Test ===\n")
    success = test_slack_connection()

    if success:
        print("\n[SUCCESS] Slack integration working!")
    else:
        print("\n[FAILED] Fix issues above and try again")
