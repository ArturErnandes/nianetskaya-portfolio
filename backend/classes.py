from dataclasses import dataclass


@dataclass(frozen=True)
class DbConfig:
    admin: str
    password: str
    host: str
    port: int
    db_name: str


@dataclass(frozen=True)
class WorkSchema:
    id: int
    title: str
    text: str
    img_name: str