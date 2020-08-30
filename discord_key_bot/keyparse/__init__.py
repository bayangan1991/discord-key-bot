import re

keyspace = {
    "gog": [r"^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$"],
    "steam": [
        r"^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$",
        r"^[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}-[a-z,A-Z,0-9]{5}$",
    ],
    "playstation": [r"^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$"],
    "origin": [
        r"^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$"
    ],
    "uplay": [
        r"^[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$",
        r"^[a-z,A-Z,0-9]{3}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}-[a-z,A-Z,0-9]{4}$",
    ],
    "url": [r"^http"],
}

_compiled = {k: [re.compile(r) for r in v] for k, v in keyspace.items()}


def parse_name(pretty_name):
    name = re.sub(r"\W", "_", pretty_name.lower())
    return name


def parse_key(key):
    for k, v in _compiled.items():
        for r in v:
            if r.match(key):
                return k, key

    return False, "Bad key format!"
