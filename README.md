# Pollen bot

This is a Telegram bot, to send you a message every time the pollen threshold reaches above a certain level.

It uses the [Met Office's pollen forecast](https://www.metoffice.gov.uk/weather/warnings-and-advice/seasonal-advice/pollen-forecast)

Message <https://t.me/pollen_count_bot> on Telegram to use.

## Requirements

| Requirement | Version |
| ----------- | ------- |
| Python      | 3.11.1  |

## Commands

### Set up environment

```bash
pip install -r requirements.txt
```

### Run

```bash
python bot.py
```

### Run and run scheduled tasks on startup

```bash
python bot.py start
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

### Set up environment on server (Linux)

```bash
ssh alifeee@...
sudo apt-get update
sudo apt install python3.11-venv
sudo mkdir -p /usr/alifeee
sudo chown alifeee:alifeee /usr/alifeee
cd /usr/alifeee
git clone git@github.com:alifeee/pollen_bot.git
sudo adduser --system --no-create-home --group pollen_bot
# sudo cat /etc/group
# sudo cat /etc/passwd
# sudo -u pollen_bot whoami
python3 -m venv env
./env/bin/pip install -r requirements.txt
sudo chown -R alifeee:pollen_bot .
```

### Move over secrets

```bash
scp .env alifeee@...:~/python/pollen_bot/
sudo chown -R alifeee:pollen_bot .env
```

### Set up to run as a process

#### With systemd

```bash
cp pollen_bot.service /etc/systemd/system/pollen_bot.service
sudo systemctl enable pollen_bot.service
sudo systemctl start pollen_bot.service
sudo systemctl status pollen_bot.service
```

#### With runit

[`runit`](https://smarden.org/runit/) is a bit like systemd. See [FAQ](https://smarden.org/runit/faq).

```bash
mkdir /home/alifeee/python/pollen_bot/logs
sudo mkdir /etc/sv/pollen_bot
sudo echo '#!/bin/sh
  #cd /home/alifeee/python/pollen_bot & ./env/bin/python3 bot.py
  # redirect stderr to stdout
  exec 2>&1
  # start program
  exec /home/alifeee/python/pollen_bot/env/bin/python3 /home/alifeee/python/pollen_bot/bot.py
  ' > /etc/sv/pollen_bot/run
sudo mkdir /etc/sv/pollen_bot/log
sudo echo '#!/bin/sh
  exec svlogd -tt /home/alifeee/python/pollen_bot/logs
  ' > /etc/sv/pollen_bot/log/run
sudo ln -s /etc/sv/pollen_bot /etc/service/

sudo sv start pollen_bot
sudo sv stop pollen_bot
sudo sv status pollen_bot
sudo sv restart pollen_bot
```

#### Logs

Log files are stored in the folder specified above, so for this script, they are in `~/python/pollen_bot/logs`.

### Update

```bash
ssh alifeee@...
cd ~/python/pollen_bot
git pull
sudo sv restart pollen_bot
```

