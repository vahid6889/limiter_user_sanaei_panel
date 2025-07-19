# X-UI Inbound Connection Limiter

A Python-based background monitoring tool that checks active connections on each inbound in X-UI, compares them with user-defined limits (from remarks), and disables the inbound automatically if the limit is exceeded.

## Features
- 🔹 Monitors active connections every N seconds (customizable)
- 🔹 Reads inbound configuration directly from X-UI SQLite database
- 🔹 Checks connection count based on netstat or ss
- 🔹 Sends Telegram notifications when a user exceeds the limit
- 🔹 Automatically disables the inbound if overused
- 🔹 Simple logging system to track actions
- 🔹 Designed to run in the background with systemd

## Usage

### 1️⃣ Clone this repo:
```bash
git clone https://github.com/vahid6889/limiter_user_sanaei_panel.git
cd limiter_user_sanaei_panel


2️⃣ Configure the Script:

Edit limiter.py and set the following variables at the top:

_db_address = '/etc/x-ui/x-ui.db'  # Path to your X-UI database
_default_max_conn = 1              # Default max connections if not set in remark
_checkCycle = 60                   # Check cycle in seconds
_telegrambot_token = ''            # Your Telegram Bot token (optional)
_telegram_chat_id = ''             # Your Telegram chat ID (optional)
_sv_addr = 'MyServer'              # Name of your server for logs/alerts

3️⃣ Define User Limits:

    In X-UI panel, when creating or editing an inbound, set the user limit in the remark like this:

UserName[2]

    The number inside [] defines the allowed simultaneous IP connections.



4️⃣ Run the Script:
Option 1 — With Screen (for testing):

screen -S limiter
python3 limiter.py

Option 2 — As a systemd Service:

Create a systemd unit file like /etc/systemd/system/x-ui-limiter.service
Example:

[Unit]
Description=X-UI Device Limiter Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /root/x-ui-device-limiter/limiter.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target

Enable and start it:

sudo systemctl daemon-reload
sudo systemctl enable --now x-ui-limiter.service


Logging

    All connection checks are logged into /root/x-ui-device-limiter/limiter-check.log

    Make sure this file is writable and rotated manually if needed

Telegram Notification Example:

UserName[2] has been locked on MyServer due to exceeding connection limits.

Disclaimer

This tool directly modifies your X-UI database and disables inbounds. Use with caution and backup your database before deploying.
License

MIT License
Feel free to use, modify, and distribute under the terms of the MIT license.
