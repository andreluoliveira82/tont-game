"""System clock: concrete Clock backed by the operating system time."""

from datetime import UTC, datetime


class SystemClock:
    """A ``Clock`` returning the current OS time as a UTC-aware datetime."""

    def now(self) -> datetime:
        return datetime.now(UTC)
