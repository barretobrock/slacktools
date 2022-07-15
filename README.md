# SlackTools
An easier way to automate things in Slack

## Info
This is really something I built for personal use. There are credential collection methods that rely on prebuilt routines that might prove specific to only my use case. Should anyone discover this and wish to use it, feel free to contact me and I'll work on adapting this to wider use cases.

### Required scopes
#### Bot
 - channels.history
 - channels.read
 - chat.write
 - emoji.read
 - files.write
 - groups.history
 - groups.read
 - im.history
 - im.read
 - im.write
 - mpim.read
 - reactions.read
 - reactions.write
 - users.read
#### User
 - search.read

## Installation
```bash
cd ~/venvs && python3 -m venv slackspace
source ~/venvs/slackspace/bin/activate
cd ~/extras && git clone https://github.com/barretobrock/slacktools.git
cd slacktools && sh ppmgr.sh pull
```

## Upgrade
```bash
poetry update -v
```
