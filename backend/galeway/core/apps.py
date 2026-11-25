from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "galeway.core"

    def ready(self) -> None:
        from galeway.core.logging import configure_structlog  # noqa: PLC0415

        configure_structlog()
