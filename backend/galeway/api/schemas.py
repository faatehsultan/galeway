"""Request and response models: the public API contract (docs/03-architecture/API.md)."""

from ninja import Schema


class HealthOut(Schema):
    status: str
    version: str
