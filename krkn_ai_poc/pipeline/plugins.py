"""
The five ABCs. Every plugin in this PoC subclasses exactly one of these.

Each ABC has a single method: run(ctx) -> ctx.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from krkn_ai_poc.pipeline.context import StageContext


class InventoryPlugin(ABC):
    """Stage 1: enumerate what exists in the cluster."""

    @abstractmethod
    def run(self, ctx: StageContext) -> StageContext: ...


class CapabilityPlugin(ABC):
    """Stage 2: derive boolean facts from the inventory."""

    @abstractmethod
    def run(self, ctx: StageContext) -> StageContext: ...


class ProbePlugin(ABC):
    """Stage 3: outbound checks (HTTP endpoints, Prometheus reachability)."""

    @abstractmethod
    def run(self, ctx: StageContext) -> StageContext: ...


class RecommenderPlugin(ABC):
    """Stage 4: emit Recommendations based on components + capabilities + probes."""

    @abstractmethod
    def run(self, ctx: StageContext) -> StageContext: ...


class RendererPlugin(ABC):
    """Stage 5: take the final context and emit the YAML."""

    @abstractmethod
    def run(self, ctx: StageContext) -> StageContext: ...
