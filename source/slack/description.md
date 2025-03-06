# Slack Notifier Plugin for Unmanic

This plugin sends notifications to a Slack channel when:
1. Files are moved or copied by Unmanic
2. Tasks are completed (successfully or with errors)
3. Files are tested for processing eligibility
4. Worker processes start processing files

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
   - Enable/disable specific notification types

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

### File Test Notifications
Sent when files are tested for processing eligibility. The notification includes:
- The file path
- File type (Video, Audio, or Other)
- Any issues detected
- Whether the file will be added to the processing queue

### Worker Process Notifications
Sent when worker processes start processing files. The notification includes:
- The original file path
- The processing file path (if different)
- The output file path (if different)
- The command being executed (if available)

## Configuration Options
- **Webhook URL**: Your Slack webhook URL (required)
- **Channel**: The Slack channel to send notifications to (optional)
- **Username**: The username to display for notifications (default: "Unmanic")
- **Icon Emoji**: The emoji to use as the icon (default: ":robot_face:")
- **Notification Types**: Enable/disable specific notification types:
  - File movement notifications
  - Task completion notifications
  - File test notifications
  - Worker process notifications

## Requirements
- Requires the Python 'requests' library (automatically installed) 