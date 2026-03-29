"""Simple async circuit breaker for external HTTP calls."""

import time
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Per-service circuit breaker with configurable thresholds."""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        reset_timeout: float = 300.0,  # 5 minutes
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0.0

    @property
    def state(self) -> CircuitState:
        if (
            self._state == CircuitState.OPEN
            and time.monotonic() - self._last_failure_time >= self.reset_timeout
        ):
            self._state = CircuitState.HALF_OPEN
            logger.info("circuit_breaker.half_open", name=self.name)
        return self._state

    def record_success(self) -> None:
        if self._state in (CircuitState.HALF_OPEN, CircuitState.CLOSED):
            self._failure_count = 0
            self._state = CircuitState.CLOSED

    def record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                "circuit_breaker.opened",
                name=self.name,
                failures=self._failure_count,
            )

    def allow_request(self) -> bool:
        current = self.state
        if current == CircuitState.CLOSED:
            return True
        return current == CircuitState.HALF_OPEN


# Global registry of circuit breakers per service key
_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get or create a circuit breaker by name."""
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(name=name, **kwargs)
    return _breakers[name]
