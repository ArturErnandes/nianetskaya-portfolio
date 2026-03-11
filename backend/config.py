import json

from .classes import AppConfig, DbConfig


AppConfig = AppConfig(
    host="localhost",
    port=8000,
)


DbConfig = DbConfig(
    admin="postgres",
    password="2208",
    host ="localhost",
    port=5555,
    db_name="nia-portfolio"
)