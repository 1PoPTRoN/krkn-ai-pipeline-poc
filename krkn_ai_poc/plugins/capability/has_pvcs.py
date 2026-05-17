"""
HasPVCsPlugin — Stage 2 (Capability).

Reads the inventory and flips ctx.capabilities.has_pvcs based on
whether the cluster has any PVCs. Trivially small on purpose —
this is the simplest possible CapabilityPlugin and demonstrates
the contract.
"""

from __future__ import annotations

from krkn_ai_poc.pipeline.context import StageContext
from krkn_ai_poc.pipeline.plugins import CapabilityPlugin


class HasPVCsPlugin(CapabilityPlugin):
    def run(self, ctx: StageContext) -> StageContext:
        ctx.capabilities.has_pvcs = len(ctx.components.pvcs) > 0
        return ctx
