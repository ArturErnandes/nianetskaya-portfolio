from dataclasses import dataclass


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
class AdminWorkSchema:
    section_name: str
    title: str
    caption: str
    description: str
    img_name: str


@dataclass(frozen=True)
class AdminProjectImageSchema:
    image_id: int
    img_name: str
    description: str | None
    order_index: int


@dataclass(frozen=True)
class AdminProjectSchema:
    section_name: str
    title: str
    caption: str
    description: str
    cover_img_name: str
    images: list[AdminProjectImageSchema]


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


@dataclass(frozen=True)
class WorkUpdateSchema:
    section_name: str
    title: str
    caption: str
    description: str
    img_name: str | None = None


@dataclass(frozen=True)
class ProjectUpdateSchema:
    section_name: str
    title: str
    caption: str
    description: str
    cover_img_name: str | None = None


@dataclass(frozen=True)
class ProjectImageUpdateSchema:
    description: str | None
    order_index: int
