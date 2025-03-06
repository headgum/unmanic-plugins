# Unmanic Plugins by Headgum

## Instructions

### Repo URL:
<!-- Replace the below link with your own repo URL (found in the 'repo' git branch) -->
```
https://raw.githubusercontent.com/Unmanic/unmanic-plugins/repo/repo.json
```

Follow [Unmanic Documentation](http://docs.unmanic.app/docs/plugins/adding_a_custom_plugin_repo/) 
to add this repo to your Unmanic installation.

## Available Plugins

### Slack Notifier
Send Slack notifications when files are moved or tasks are completed in Unmanic.

#### Features:
- Sends notifications for file movements (copy/move operations)
- Sends notifications for task completions (success/failure)
- Sends notifications for file tests (when files are added to the queue)
- Sends notifications for worker processes (when processing starts)

#### Configuration Options:
- **Webhook URL**: Your Slack webhook URL (required)
- **Channel**: The Slack channel to send notifications to (optional)
- **Username**: The username to display for notifications (default: "Unmanic")
- **Icon Emoji**: The emoji to use as the icon (default: ":robot_face:")
- **Notification Types**: Enable/disable specific notification types:
  - File movement notifications
  - Task completion notifications
  - File test notifications
  - Worker process notifications

#### Setup Instructions:
1. Create a Slack webhook URL:
   - Go to https://api.slack.com/apps
   - Create a new app (or use an existing one)
   - Enable "Incoming Webhooks"
   - Create a new webhook URL for your workspace
   - Copy the webhook URL
2. Configure the plugin in Unmanic with your webhook URL

## Links

[Unmanic Documentation](https://docs.unmanic.app/docs/)

[License and Contribution](#license-and-contribution)


---
## License and Contribution

This projected is licensed under th GPL version 3. 

Copyright (C) 2021 Josh Sunnex - All Rights Reserved

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

This project contains libraries imported from external authors.
Please refer to the source of these libraries for more information on their respective licenses.

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) to learn how to contribute to Unmanic.
