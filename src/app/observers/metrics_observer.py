from prometheus_client import Counter, Gauge
from patterns.observer import Observer

# Contadores e gauges do Prometheus
REQUESTS_ENQUEUED = Counter("proxy_requests_enqueued_total", "Total de requisições enfileiradas")
REQUESTS_DEQUEUED = Counter("proxy_requests_dequeued_total", "Total de requisições processadas")
CIRCUIT_STATE = Gauge("proxy_circuit_state", "Estado atual do Circuit Breaker (0=CLOSED, 1=OPEN, 2=HALF-OPEN)")


class MetricsObserver(Observer):

    def update(self, event: dict) -> None:
        event_type = event.get("event")

        if event_type == "enqueue":
            REQUESTS_ENQUEUED.inc()

        elif event_type == "dequeue":
            REQUESTS_DEQUEUED.inc()

        elif event_type == "state_change":
            state = event.get("state")
            if state == "CLOSED":
                CIRCUIT_STATE.set(0)
            elif state == "OPEN":
                CIRCUIT_STATE.set(1)
            elif state == "HALF-OPEN":
                CIRCUIT_STATE.set(2)
