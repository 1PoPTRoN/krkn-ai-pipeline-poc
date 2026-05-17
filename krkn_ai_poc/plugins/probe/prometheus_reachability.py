"""
PrometheusReachabilityPlugin — Stage 3 (Probe).

Sends one HTTP request to a Prometheus instance's /api/v1/query
endpoint with query=up. Records a ProbeResult either way and flips
ctx.capabilities.prometheus_reachable based on the outcome.

Probe failure is NOT pipeline failure. Downstream plugins decide
what to do with unreachable Prometheus (e.g., FitnessRecommender
falls back to a default query).
"""

from __future__ import annotations

import os

import requests

from krkn_ai_poc.pipeline.context import ProbeResult, StageContext
from krkn_ai_poc.pipeline.plugins import ProbePlugin


class PrometheusReachabilityPlugin(ProbePlugin):
    def __init__(self, prometheus_url: str | None = None, timeout: float = 5.0) -> None:
        # Fall back to env var, then to None (caller responsibility).
        self._url = prometheus_url or os.environ.get("PROMETHEUS_URL")
        self._timeout = timeout

    def run(self, ctx: StageContext) -> StageContext:
        if not self._url:
            ctx.probes.append(
                ProbeResult(
                    name="prometheus",
                    kind="metric",
                    url=None,
                    success=False,
                )
            )
            ctx.capabilities.prometheus_reachable = False
            return ctx

        query_url = f"{self._url.rstrip('/')}/api/v1/query"
        success = False
        try:
            r = requests.get(
                query_url,
                params={"query": "up"},
                timeout=self._timeout,
            )
            success = r.status_code == 200 and r.json().get("status") == "success"
        except (requests.RequestException, ValueError):
            success = False

        ctx.probes.append(
            ProbeResult(
                name="prometheus",
                kind="metric",
                url=query_url,
                success=success,
            )
        )
        ctx.capabilities.prometheus_reachable = success
        return ctx
