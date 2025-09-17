import time
from patterns.singleton import SingletonMeta
from patterns.observer import Observable


class CircuitBreaker(Observable, metaclass=SingletonMeta):

    def __init__(self, failure_threshold: int = 5, recovery_time: int = 30):
        super().__init__()
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"

    def _set_state(self, new_state: str) -> None:
        self.state = new_state
        self.notify_observers({"event": "state_change", "state": new_state})

    def allow_request(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_time:
                self._set_state("HALF-OPEN")
                return True
            return False
        return True

    def record_success(self) -> None:
        self.failures = 0
        if self.state != "CLOSED":
            self._set_state("CLOSED")

    def record_failure(self) -> None:
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self._set_state("OPEN")
