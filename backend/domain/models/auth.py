from dataclasses import dataclass


@dataclass(frozen=True)
class AdminSessionData:
    role: str
    exp: int
    iat: int
