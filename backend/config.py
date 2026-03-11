import json
from pathlib import Path

from .classes import AppConfig, DbConfig

CONFIG_FILE = Path(__file__).parent.parent / "data.json"


def load_config(filename: str | Path):
    with open(filename, "r") as f:
        return json.load(f)


config = load_config(CONFIG_FILE)

AppConfig = AppConfig(
    host=config["app"]["host"],
    port=int(config["app"]["port"]),
)


DbConfig = DbConfig(
    admin=config["database"]["admin"],
    password=config["database"]["password"],
    host=config["database"]["host"],
    port=int(config["database"]["port"]),
    db_name=config["database"]["db_name"],
)
