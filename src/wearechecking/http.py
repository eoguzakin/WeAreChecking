"""Bounded public API requests with a local cache and conservative throttling."""
import time
from urllib.parse import urlsplit
import requests
import requests_cache

ALLOWED_HOSTS = {"api.openf1.org", "api.jolpi.ca"}


class PublicClient:
    def __init__(self, root):
        self.session = requests_cache.CachedSession(str(root / ".cache/public_http"), expire_after=86400)
        self.last_request = 0.0

    def get(self, url, params=None):
        if urlsplit(url).hostname not in ALLOWED_HOSTS:
            raise ValueError("Unsupported data source.")
        for attempt in range(3):
            # <= 30/minute, including an existing process's cached lookups.
            time.sleep(max(0, 2.1 - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                response = self.session.get(url, params=params, timeout=(10, 45))
                if response.status_code in (429, 502, 503, 504) and attempt < 2:
                    time.sleep(min(10, float(response.headers.get("Retry-After", "3"))))
                    continue
                response.raise_for_status()
                return response.json(), response.url
            except (requests.ConnectionError, requests.Timeout):
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError("The data source did not respond.")
