"""
Database-backed CORS middleware.

Starlette's stock CORSMiddleware (which FastAPI's `add_middleware(CORSMiddleware, ...)`
just is) takes a fixed `allow_origins` list at process startup and never
reconsiders it. That's exactly what we don't want here: the whole point of
this app's CORS design is that allowed origins live in the `allowed_origins`
database table and can be changed by whoever administers that database,
without redeploying or restarting the backend.

This subclasses Starlette's implementation and overrides only
`is_allowed_origin` — every other part of CORS handling (preflight
responses, credentialed requests, Vary headers, etc.) is inherited
unchanged, so behavior matches the standard middleware exactly except for
where the allow-list comes from.
"""
from __future__ import annotations

from typing import Callable, List

from starlette.middleware.cors import CORSMiddleware as _StarletteCORSMiddleware


class DatabaseBackedCORSMiddleware(_StarletteCORSMiddleware):
    def __init__(self, app, get_allowed_origins: Callable[[], List[str]], **kwargs) -> None:
        # Always constructed with an empty static allow_origins — the real
        # list is resolved per-request via `get_allowed_origins`.
        super().__init__(app, allow_origins=(), **kwargs)
        self._get_allowed_origins = get_allowed_origins

    def is_allowed_origin(self, origin: str) -> bool:
        if self.allow_origin_regex is not None and self.allow_origin_regex.fullmatch(origin):
            return True
        try:
            allowed = self._get_allowed_origins()
        except Exception:
            # If the origin cache/DB lookup itself blows up, fail closed
            # (reject) rather than silently allowing every origin.
            return False
        return origin in allowed
