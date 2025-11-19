import time
import logging
import os
logger = logging.getLogger(__name__)

RATE_LIMIT = int(os.getenv('RATE_LIMIT_PER_MINUTE', '20'))

class TokenBucket:
    def __init__(self, capacity=RATE_LIMIT, refill_interval=60):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_interval = refill_interval
        self.last = time.time()

    def consume(self, n=1):
        now = time.time()
        elapsed = now - self.last
        # refill proportionally (simple approach)
        if elapsed >= self.refill_interval:
            self.tokens = self.capacity
            self.last = now
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False

# Simple in-memory cache (process-local)
class SimpleCache:
    def __init__(self):
        self.store = {}
    def get(self, key):
        entry = self.store.get(key)
        if not entry: return None
        value, expires = entry
        if expires and time.time() > expires:
            del self.store[key]
            return None
        return value
    def set(self, key, value, ttl=None):
        expires = time.time() + ttl if ttl else None
        self.store[key] = (value, expires)
cache = SimpleCache()
