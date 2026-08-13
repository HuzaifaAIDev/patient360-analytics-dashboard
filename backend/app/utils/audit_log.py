"""
Audit logging.

Because this application intentionally has no user accounts, "audit log"
here means IP-based event logging: who (by IP), did what (endpoint/action),
to what (e.g. which patient), and when. This is a separate logger channel
(`patient360.audit`) so it can be routed to its own log file/sink in a real
deployment without mixing with general application logs.

Hard rule: never log passwords, API keys, database credentials, full
patient record payloads, or complete medical documents. Only enough context
to answer "who looked at what, when" — the same category of information
already visible in a web server's access log, expressed with clearer
semantics (e.g. "patient_viewed" rather than just "GET /api/patient/...").
"""
from __future__ import annotations

import logging
from typing import Any

audit_logger = logging.getLogger("patient360.audit")


def audit_log(action: str, **fields: Any) -> None:
    """
    Record a single audit event.

    Usage: audit_log("patient_viewed", patient_name="Ali Saleem", ip="1.2.3.4")

    Deliberately takes only keyword scalars (strings/numbers/bools) — this
    shape makes it structurally awkward to accidentally pass a whole
    record/DataFrame/dict of patient data through here.
    """
    parts = " ".join(f"{key}={value!r}" for key, value in fields.items())
    audit_logger.info("%s %s", action, parts)
