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
class ClosedEntitySchema:
    id: int
    title: str
    caption: str
    img_name: str


@dataclass(frozen=True)
class OpenedWorkSchema:
    section_name: str
    title: str
    description: str
    img_name: str


@dataclass(frozen=True)
class ProjectImageSchema:
    img_name: str
    description: str | None


@dataclass(frozen=True)
class OpenedProjectSchema:
    section_name: str
    title: str
    description: str
    cover_img_name: str
    images: list[ProjectImageSchema]