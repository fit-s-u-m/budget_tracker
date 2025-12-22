from dataclasses import dataclass

@dataclass
class AppContext:
    """Custom runtime context schema."""

    first_name: str | None = None
    userName: str | None = None
    telegram_id: int | None  = None
    account_id: int | None  = None
