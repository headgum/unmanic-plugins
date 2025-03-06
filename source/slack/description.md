# Slack Notifier Plugin for Unmanic

This plugin sends notifications to a Slack channel when:
1. Files are moved or copied by Unmanic
2. Tasks are completed (successfully or with errors)

## Configuration

To use this plugin, you need to:

1. Create a Slack webhook URL:
   - Go to https://api.slack.com/apps
   - Create a new app (or use an existing one)
   - Enable "Incoming Webhooks"
   - Create a new webhook URL for your workspace
   - Copy the webhook URL

2. Configure the plugin in Unmanic:
   - Paste the webhook URL in the "Webhook URL" field
   - (Optional) Set a specific channel to send messages to
   - (Optional) Customize the username and emoji icon
   - Enable/disable notifications for file movements and task completions

## Notification Types

### File Movement Notifications
Sent when files are moved or copied by Unmanic. The notification includes:
- The original file path
- The new file path

### Task Completion Notifications
Sent when tasks are completed. The notification includes:
- Success/failure status
- The source file path
- List of destination files (if any)

## Requirements
- Requires the Python 'requests' library (automatically installed) 