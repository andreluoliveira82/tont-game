"""UUID-based game identifier generator."""

from uuid import UUID, uuid4


class UuidGameIdGenerator:
    """A ``GameIdGenerator`` producing random UUIDv4 identifiers."""

    def new_id(self) -> UUID:
        return uuid4()
