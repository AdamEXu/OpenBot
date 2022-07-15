# OpenBot
An open source version of [GeekBot](https://geekbot.com/). 

Comes with some basic report commands, run `report ?` or `report help` for syntax

## Step by Step Instructions On How To Setup
1. Download the source code (`app.py`)
2. Get Flask by running `pip3 install Flask` in your terminal
3. Get Waitress by running `pip3 install waitress` in your terminal
4. Go to [api.slack.com] and create an app
5. Go to OAuth and Permissions, scroll down to Scopes, and add `channels:history`, `channels:read`, `chat:write`, `groups:history`, `groups:read`, `im:history`, `im:read`, `im:write`, and `team:read`
6. Go to Event Subscriptions and plug the IP address for your server in and verify it
7. Subscribe to `message.channels`, `message.groups`, and `message.im`
8. Go to `config.txt` and configure your bot.
9. Run `app.py`
10. **(ONLY DO THIS STEP IF YOU ALREADY HAVE AN EXISTING STATUS CHANNEL)** In Slack, open a direct message with the bot and type in `migrate [channel id]`
11. You're good to go!

### Check the wiki for more detailed instructions

## Authors:
[@AdamEXu](https://github.com/AdamEXu) [Adam Xu](https://adamthegreat.rocks)
