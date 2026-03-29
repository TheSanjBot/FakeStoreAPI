"""Small in-memory rate limiter middleware."""

from __future__ import annotations

from collections import defaultdict, deque
from time import time

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SimpleRateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        now = time()
        identifier = request.client.host if request.client else "unknown"
        window = self._requests[identifier]

        while window and window[0] <= now - self.window_seconds:
            window.popleft()

        if len(window) >= self.max_requests:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded."})

        window.append(now)
        return await call_next(request)
