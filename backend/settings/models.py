from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    host: str
    port: int


@dataclass(frozen=True)
class DbConfig:
    admin: str
    password: str
    host: str
    port: int
    db_name: str


@dataclass(frozen=True)
class AdminConfig:
    password_hash: str
