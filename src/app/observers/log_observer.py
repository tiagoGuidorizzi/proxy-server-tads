import logging
from app.patterns.observer import Observer

logger = logging.getLogger("proxy_service")


class LogObserver(Observer):

    def update(self, event: dict) -> None:
        event_type = event.get("event")
        if event_type == "enqueue":
            logger.info(f"[QUEUE] Enqueued request {event.get('request_id')}")
        elif event_type == "dequeue":
            logger.info(f"[QUEUE] Dequeued request {event.get('request_id')}")
        elif event_type == "state_change":
            logger.warning(f"[CIRCUIT] State changed to {event.get('state')}")
        else:
            logger.debug(f"[EVENT] {event}")
