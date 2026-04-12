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


@dataclass(frozen=True)
class AdminLoginRequest:
    password: str


@dataclass(frozen=True)
class AdminAuthResponse:
    ok: bool


@dataclass(frozen=True)
class AdminSessionData:
    role: str
    exp: int
    iat: int


@dataclass(frozen=True)
class WorkCreateSchema:
    section_name: str
    title: str
    caption: str
    description: str
    img_name: str | None = None


@dataclass(frozen=True)
class ProjectImageCreateSchema:
    img_name: str | None = None
    description: str | None = None
    order_index: int = 0


@dataclass(frozen=True)
class ProjectCreateSchema:
    section_name: str
    title: str
    caption: str
    description: str
    cover_img_name: str | None = None
    images: list[ProjectImageCreateSchema] | None = None
