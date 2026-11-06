"""Tiny JSON-over-HTTP helper on the standard library (honours HTTPS_PROXY)."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "jobfinder/0.1 (personal job search; +https://github.com/Raghav-isnt-available/Rocking-Raghav-)"


class HTTPError(Exception):
    def __init__(self, status: int, url: str, body: str = ""):
        super().__init__(f"HTTP {status} for {url}")
        self.status = status
        self.url = url
        self.body = body


def get_json(url: str, params: dict | None = None, timeout: float = 30, retries: int = 2):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:500]
            # 4xx is a real answer (bad slug, bad key); only retry server errors.
            if e.code < 500 or attempt == retries:
                raise HTTPError(e.code, url, body) from None
            last = e
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            if attempt == retries:
                raise
        time.sleep(1.5 * (attempt + 1))
    raise last  # pragma: no cover
