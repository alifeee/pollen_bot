# Pollen bot

This is a Telegram bot, to send you a message every time the pollen threshold reaches above a certain level.

## Requirements

| Requirement | Version |
| ----------- | ------- |
| Python      | 3.11.1  |

## Commands

### Set up environment

```bash
python3 -m venv env
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run

```bash
python ./bot.py
```

## Telegram credentials

To obtain an access token for telegram, see [help page](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API), but in essence, talk to the [BotFather](https://t.me/botfather).

The access token is used via an environment variable, or a `.env` file, which is not tracked by git.

Also in the environment should be an "admin ID", where errors are sent via the error handler.

```bash
touch .env
```

```.env
TELEGRAM_BOT_ACCESS_TOKEN=...
ADMIN_USER_ID=...
```

## Persistent data

To store each user's location, reminder preference, and reminder threshold, a persistent pickle file is used. This is not tracked by git. This uses the [Persistence API](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Making-your-bot-persistent) from [python-telegram-bot][ptb].

[ptb]: https://github.com/python-telegram-bot/python-telegram-bot/

```python
persistent_data = PicklePersistence(filepath="bot_data.pickle")
application = Application.builder().token(API_KEY).persistence(persistent_data).build()
```

## Deploy on remote server

### Set up environment on server

```bash
ssh root@...
cd ~/python
git clone https://github.com/alifeee/pollen_bot.git
cd pollen_bot
sudo apt-get update
sudo apt install python3.10-venv
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### Move over secrets

```bash
scp google_credentials.json root@...:~/python/pollen_bot/
scp .env root@...:~/python/pollen_bot/
```

### Run bot

```bash
ssh root@...
tmux attach <session id>
cd ~/python/pollen_bot
source env/bin/activate
python ./bot.py
# Ctrl+B, D to detach from tmux
```

### List tmux sessions

```bash
tmux ls
```

### Attach to tmux session

```bash
tmux attach -t 0
```

### Kill tmux session

```bash
tmux kill-session -t 0
```

### Update

```bash
ssh root@...
cd ~/python/pollen_bot
git pull
```

Then repeat steps in [Run](#run-bot)
