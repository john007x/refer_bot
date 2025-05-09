# Telegram Referral Bot

A Telegram bot that manages referrals and rewards users for inviting others.

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the bot:
```bash
python main.py
```

## Features

- User referral system
- Balance tracking
- Withdrawal requests
- Channel membership verification
- 24/7 hosting capability using Flask and UptimeRobot

## Hosting on Replit

1. Create a new Repl and upload these files
2. Install dependencies from requirements.txt
3. Run the bot
4. Set up UptimeRobot monitor with your Repl URL (5 min interval)

## Configuration

Bot settings are configured in `main.py`:
- Minimum withdrawal amount: 8400 TK
- Referral reward: 210 TK per referral
- Required channel membership for participation
