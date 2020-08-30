# discord-key-bot

Simple single guild bot for giving away product keys to guild members.

Two environment variables required.

```
TOKEN=<discord bot token> # Required
SQLALCHEMY_URI=<uri for database> # Will default to "sqlite:///:memory:" meaning all data will be lost on restart

#Optional defaults
BANG=! # Bot command
WAIT_TIME=84600 # Time between claims
```

Once connected use !help for more information