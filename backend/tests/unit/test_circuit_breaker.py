"""Unit tests for the circuit breaker module."""

import time

from app.core.circuit_breaker import CircuitBreaker, CircuitState, get_circuit_breaker


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker(name="test")
        assert cb.state == CircuitState.CLOSED

    def test_success_keeps_closed(self):
        cb = CircuitBreaker(name="test")
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(name="test", failure_threshold=3)
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_open_blocks_requests(self):
        cb = CircuitBreaker(name="test", failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert not cb.allow_request()

    def test_half_open_after_timeout(self):
        cb = CircuitBreaker(name="test", failure_threshold=1, reset_timeout=0.1)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN
        assert cb.allow_request()

    def test_success_resets_to_closed(self):
        cb = CircuitBreaker(name="test", failure_threshold=1, reset_timeout=0.1)
        cb.record_failure()
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 0

    def test_get_circuit_breaker_reuses(self):
        cb1 = get_circuit_breaker("shared_test")
        cb2 = get_circuit_breaker("shared_test")
        assert cb1 is cb2
