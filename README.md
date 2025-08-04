# OpenBot

OpenBot is an open source alternative to [GeekBot](https://geekbot.com/), designed for automating standup and reporting workflows within Slack. The project provides a basic set of reporting commands and can be easily extended or adapted for custom team workflows.

## Overview

OpenBot enables teams to automate daily standup reporting and other routine check-ins in Slack channels, groups, or direct messages. It leverages Flask and Waitress for serving a lightweight API and integrates with Slack via its Events API and OAuth permissions.

### Features

- Responds to report commands (`report ?` or `report help` for usage)
- Slack event and message handling
- Customizable via `config.txt`
- Simple migration for existing status channels

## Getting Started

### Prerequisites

- Python 3.x
- [Flask](https://flask.palletsprojects.com/)
- [Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/)
- Slack account with permissions to create/manage apps

### Installation

1. **Download the source code:**  
   Download or clone this repository to your local machine.

2. **Install dependencies:**  
   ```
   pip3 install Flask waitress
   ```

3. **Create a Slack App:**
   - Go to [api.slack.com](https://api.slack.com/) and create a new app.
   - In **OAuth & Permissions**, add the following scopes:  
     `channels:history`, `channels:read`, `chat:write`, `groups:history`, `groups:read`, `im:history`, `im:read`, `im:write`, `team:read`
   - In **Event Subscriptions**, enter your server's public IP address and verify.
   - Subscribe to the following events:  
     `message.channels`, `message.groups`, `message.im`

4. **Configure the bot:**  
   Edit `config.txt` with your Slack app credentials and configuration.

5. **Run the bot:**  
   ```
   python3 app.py
   ```

6. **(Optional) Migrate existing status channels:**  
   In Slack, direct message the bot with:  
   ```
   migrate [channel id]
   ```

### Usage

- Type `report ?` or `report help` in Slack to see available commands and syntax.
- OpenBot will listen and respond to configured events in your Slack workspace.

For more detailed setup and troubleshooting, refer to the project's Wiki.

## Project Structure

- `app.py` — Main Flask application serving Slack events and commands
- `config.txt` — Configuration for Slack API keys and custom settings
- Additional documentation in the Wiki

## License

OpenBot is released under the MIT License. See the `LICENSE` file for more details.

## Acknowledgements

- Inspired by the workflow and features of [GeekBot](https://geekbot.com/)
- Built using Flask and Waitress
