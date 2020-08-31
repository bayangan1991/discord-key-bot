# discord-key-bot

Simple multi guild bot for giving away product keys to guild members. Any keys added sent to the bot will only be made available on guilds/servers you send the `!share` command.

## Usage

```
KeyStore:
  add     Add a key (Do this in a private message)
  browse  Browse through available games
  claim   Claims a game from available keys
  search  Searches available games
  share   Add this guild the guilds you share keys with
  unshare Remove this guild from the guilds you share keys with
​No Category:
  help    Shows this message

Type !help command for more info on a command.
You can also type !help category for more info on a category.
```

### `!add <key> [game_name...]`

Adds a game key to your collection. (Do this in a private message)

The bot currently supports key parsing for:
- gog
- steam
- playstation
- origin
- uplay
- url (Such as humble gift links)

### `!browse [page=1]`

Browse through available games. 20 per page, sorted alphabetically.

### `!claim [platform] [game_name...]`

Claims a game from available keys.

Platform must be one of the above name.

The game name must evaluate to a single game. 

If you are claiming a key that you provided then the `WAIT_TIME` will not be applied. Otherwise you must wait until collecting your next game.

`WAIT_TIME` is applied across all guilds that the bot is connected too.

### `!search [game_name...]`

Searches available games. Can be used to test claims, so you don't accidentally claim the wrong game.

### `![un]share`

Adds or removes this guild the guilds you share keys with. Must be run inside a guild.

Any keys you have sent to the bot will not be available until you run the `!share` command.

Likewise, they will become unavailable if you `!unshare`

## Setup

### Creating a discord bot

Follow this guide to create a discord bot:

https://discordpy.readthedocs.io/en/latest/discord.html

Minimum permissions required are:
- Send Messages
- Manage Messages

## Usage

### Python

Two environment variables are required.

```shell
TOKEN=<discord bot token> # Required
SQLALCHEMY_URI=<uri for database> # Will default to "sqlite:///:memory:" meaning all data will be lost on restart

#Optional defaults
BANG=! # Bot command
WAIT_TIME=84600 # Time between claims in seconds
```

I use pipenv for virtualenv management. I have also provided the requirements.txt for compatibility. I do recommend using some sort of virtual environment though.

To start the bot:

```shell
pipenv run python run.py
# or
venv/activate
python run.py
```

### Docker

Run this bot in a docker container with the following command

```shell
docker run -e TOKEN=<YOUR DISCORD TOKEN> -e SQLALCHEMY_URI=<DB URI> bayangan/discord-key-bot
```

Or using docker compose. Application runs out of the `/app` folder

#### Sqlite Example

```yaml
version: "3.0"
services:
  keybot:
    restart: unless-stopped
    image: bayangan/discord-key-bot
    volumes:
      - "/app/data"
    environment:
      TOKEN: "<YOUR DISCORD TOKEN>"
      WAIT_TIME: 7200 # In seconds
      SQLALCHEMY_URI: "sqlite:///data/keybot.sqlite"
```

## Contributing

All pull requests are welcome. Any python must be black-ified. Pulls request will be declined unless black has formatted it.

## Licence

[Unlicence](LICENCE)