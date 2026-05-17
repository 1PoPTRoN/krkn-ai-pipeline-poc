"""
PVCScenarioRecommenderPlugin — Stage 4 (Recommend).

Reads ctx.capabilities.has_pvcs and emits a single Recommendation
for the pvc-scenarios.enable key. The reason string includes the
PVC count for audit-trail purposes — the whole point of the
pipeline is auditable decisions.

In the full LFX deliverable there will be 12 of these, one per
scenario type. This is the prototype.
"""

from __future__ import annotations

from krkn_ai_poc.pipeline.context import Recommendation, StageContext
from krkn_ai_poc.pipeline.plugins import RecommenderPlugin


class PVCScenarioRecommenderPlugin(RecommenderPlugin):
    def run(self, ctx: StageContext) -> StageContext:
        pvc_count = len(ctx.components.pvcs)
        enable = ctx.capabilities.has_pvcs

        if enable:
            reason = f"{pvc_count} PVC(s) detected; enabling pvc-scenarios"
        else:
            reason = "0 PVCs detected; pvc-scenarios kept disabled"

        ctx.recommendations.append(
            Recommendation(
                key="pvc-scenarios.enable",
                value=enable,
                reason=reason,
            )
        )
        return ctx
