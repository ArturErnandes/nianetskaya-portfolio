import json
from pathlib import Path

from .settings.models import AdminConfig as AdminConfigModel
from .settings.models import AppConfig as AppConfigModel
from .settings.models import DbConfig as DbConfigModel

CONFIG_FILE = Path(__file__).parent.parent / "data.json"


def load_config(filename: str | Path):
    with open(filename, "r") as f:
        return json.load(f)


config = load_config(CONFIG_FILE)

AppConfig = AppConfigModel(
    host=config["app"]["host"],
    port=int(config["app"]["port"]),
)


DbConfig = DbConfigModel(
    admin=config["database"]["admin"],
    password=config["database"]["password"],
    host=config["database"]["host"],
    port=int(config["database"]["port"]),
    db_name=config["database"]["db_name"],
)


AdminConfig = AdminConfigModel(
    password_hash=config["admin"]["password_hash"],
)
