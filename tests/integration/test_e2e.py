"""Day 6 tests — end-to-end pipeline with mocked Inventory.

These tests do NOT touch a real cluster. They register a fake
InventoryPlugin that produces a known ClusterComponents, then run
the full pipeline and assert the rendered YAML contains the right
recommendation.
"""

from __future__ import annotations

from pathlib import Path

import responses

from krkn_ai_poc.pipeline.context import ClusterComponents, StageContext
from krkn_ai_poc.pipeline.plugins import InventoryPlugin
from krkn_ai_poc.pipeline.registry import PluginRegistry, Stage
from krkn_ai_poc.pipeline.runner import PipelineRunner
from krkn_ai_poc.plugins.capability.has_pvcs import HasPVCsPlugin
from krkn_ai_poc.plugins.probe.prometheus_reachability import (
    PrometheusReachabilityPlugin,
)
from krkn_ai_poc.plugins.recommend.scenario_pvc import (
    PVCScenarioRecommenderPlugin,
)
from krkn_ai_poc.plugins.render.jinja2 import Jinja2RendererPlugin

REPO_ROOT = Path(__file__).parent.parent.parent
TEMPLATE = REPO_ROOT / "krkn_ai_poc" / "templates" / "krkn-ai.yaml.j2"


class _FakeInventory(InventoryPlugin):
    def __init__(self, pvcs: list[str]) -> None:
        self._pvcs = pvcs

    def run(self, ctx: StageContext) -> StageContext:
        ctx.components = ClusterComponents(
            namespaces=["default", "stateful-demo"],
            pods=["postgres-1"],
            services=["postgres"],
            pvcs=self._pvcs,
            nodes=["minikube"],
        )
        return ctx


def _build_registry(pvcs: list[str], output: Path) -> PluginRegistry:
    reg = PluginRegistry()
    reg.register(Stage.INVENTORY, _FakeInventory(pvcs=pvcs))
    reg.register(Stage.CAPABILITY, HasPVCsPlugin())
    reg.register(Stage.PROBE, PrometheusReachabilityPlugin(prometheus_url="http://prom.fake"))
    reg.register(Stage.RECOMMEND, PVCScenarioRecommenderPlugin())
    reg.register(Stage.RENDER, Jinja2RendererPlugin(TEMPLATE, output))
    return reg


@responses.activate
def test_pipeline_enables_pvc_scenarios_when_pvcs_exist(tmp_path):
    responses.add(
        responses.GET,
        "http://prom.fake/api/v1/query",
        json={"status": "success", "data": {"resultType": "vector", "result": []}},
        status=200,
    )

    output = tmp_path / "after.yaml"
    reg = _build_registry(pvcs=["data-pvc"], output=output)
    PipelineRunner(reg).run(kubeconfig_path="/dev/null")

    content = output.read_text()
    assert "pvc-scenarios:" in content
    assert "enable: true" in content
    assert "1 PVC(s) detected" in content


@responses.activate
def test_pipeline_disables_pvc_scenarios_when_no_pvcs(tmp_path):
    responses.add(
        responses.GET,
        "http://prom.fake/api/v1/query",
        json={"status": "success", "data": {"resultType": "vector", "result": []}},
        status=200,
    )

    output = tmp_path / "after.yaml"
    reg = _build_registry(pvcs=[], output=output)
    PipelineRunner(reg).run(kubeconfig_path="/dev/null")

    content = output.read_text()
    assert "pvc-scenarios:" in content
    assert "enable: false" in content
    assert "0 PVCs detected" in content

@responses.activate
def test_rendered_yaml_is_valid_yaml(tmp_path):
    responses.add(
        responses.GET,
        "http://prom.fake/api/v1/query",
        json={"status": "success", "data": {"resultType": "vector", "result": []}},
        status=200,
    )
    import yaml

    output = tmp_path / "after.yaml"
    reg = _build_registry(pvcs=["data-pvc"], output=output)
    PipelineRunner(reg).run(kubeconfig_path="/dev/null")

    content = output.read_text()
    parsed = yaml.safe_load(content)
    assert parsed is not None
    assert "scenario" in parsed
    assert parsed["scenario"]["pvc-scenarios"]["enable"] is True
