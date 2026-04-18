from dataclasses import dataclass


@dataclass(frozen=True)
class AdminLoginRequest:
    password: str


@dataclass(frozen=True)
class AdminAuthResponse:
    ok: bool
