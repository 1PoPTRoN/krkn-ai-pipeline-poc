"""Day 3 tests — runner wiring. No live cluster needed yet."""

from __future__ import annotations

from krkn_ai_poc.pipeline.context import (
    ClusterComponents,
    Recommendation,
    StageContext,
)
from krkn_ai_poc.pipeline.plugins import (
    InventoryPlugin,
    RecommenderPlugin,
)
from krkn_ai_poc.pipeline.registry import PluginRegistry, Stage
from krkn_ai_poc.pipeline.runner import PipelineRunner


class _FakeInventory(InventoryPlugin):
    """Stub that sets known components without touching a cluster."""

    def run(self, ctx: StageContext) -> StageContext:
        ctx.components = ClusterComponents(
            namespaces=["default", "robot-shop"],
            pods=["cart-1", "catalogue-1"],
            pvcs=["data-pvc"],
        )
        return ctx


class _FakeRecommender(RecommenderPlugin):
    def run(self, ctx: StageContext) -> StageContext:
        ctx.recommendations.append(
            Recommendation(
                key="pvc-scenarios.enable",
                value=len(ctx.components.pvcs) > 0,
                reason=f"{len(ctx.components.pvcs)} PVCs in inventory",
            )
        )
        return ctx


def test_runner_threads_context_through_stages():
    reg = PluginRegistry()
    reg.register(Stage.INVENTORY, _FakeInventory())
    reg.register(Stage.RECOMMEND, _FakeRecommender())

    ctx = PipelineRunner(reg).run(kubeconfig_path="/dev/null")

    assert ctx.components.pvcs == ["data-pvc"]
    assert len(ctx.recommendations) == 1
    assert ctx.recommendations[0].key == "pvc-scenarios.enable"
    assert ctx.recommendations[0].value is True
    assert "1 PVCs" in ctx.recommendations[0].reason


def test_runner_skips_empty_stages_cleanly():
    reg = PluginRegistry()
    # No plugins registered for any stage
    ctx = PipelineRunner(reg).run(kubeconfig_path="/dev/null")

    # Empty StageContext flows through unchanged
    assert ctx.components.pods == []
    assert ctx.recommendations == []
