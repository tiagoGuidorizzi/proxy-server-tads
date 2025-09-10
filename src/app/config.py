import os

UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://score.hsborges.dev/score")
RATE_LIMIT_INTERVAL = float(os.getenv("RATE_LIMIT_INTERVAL", "1.0"))
QUEUE_MAX_SIZE = int(os.getenv("QUEUE_MAX_SIZE", "200"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5.0"))
RETRY_COUNT = int(os.getenv("RETRY_COUNT", "2"))
CIRCUIT_ERROR_THRESHOLD = int(os.getenv("CIRCUIT_ERROR_THRESHOLD", "5"))
CIRCUIT_OPEN_SECONDS = int(os.getenv("CIRCUIT_OPEN_SECONDS", "30"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))
ADAPTIVE_INC_FACTOR = float(os.getenv("ADAPTIVE_INC_FACTOR", "1.5"))
ADAPTIVE_DECAY_SECONDS = int(os.getenv("ADAPTIVE_DECAY_SECONDS", "60"))
