"""
PipelineRunner — walks the 5 stages in fixed order.

For each stage, it asks the registry for the plugins registered against
that stage and runs them sequentially, threading the StageContext through.

The order is load-bearing: Capability needs Inventory's output, Probe
needs Capability, Recommend needs all three, Render needs everything.
"""

from __future__ import annotations

from krkn_ai_poc.pipeline.context import StageContext
from krkn_ai_poc.pipeline.registry import PluginRegistry, Stage


# Fixed stage order. Do not reorder without updating the design doc.
_STAGE_ORDER: list[Stage] = [
    Stage.INVENTORY,
    Stage.CAPABILITY,
    Stage.PROBE,
    Stage.RECOMMEND,
    Stage.RENDER,
]


class PipelineRunner:
    def __init__(self, registry: PluginRegistry) -> None:
        self._registry = registry

    def run(self, kubeconfig_path: str) -> StageContext:
        ctx = StageContext(kubeconfig_path=kubeconfig_path)
        for stage in _STAGE_ORDER:
            for plugin in self._registry.get(stage):
                ctx = plugin.run(ctx)
        return ctx
