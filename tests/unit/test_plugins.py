"""Day 5 tests — one per plugin written today."""

from __future__ import annotations

import responses

from krkn_ai_poc.pipeline.context import ClusterComponents, StageContext
from krkn_ai_poc.plugins.capability.has_pvcs import HasPVCsPlugin
from krkn_ai_poc.plugins.probe.prometheus_reachability import (
    PrometheusReachabilityPlugin,
)
from krkn_ai_poc.plugins.recommend.scenario_pvc import (
    PVCScenarioRecommenderPlugin,
)


def _ctx_with_pvcs(pvcs: list[str]) -> StageContext:
    ctx = StageContext(kubeconfig_path="/dev/null")
    ctx.components = ClusterComponents(pvcs=pvcs)
    return ctx


# ---------- HasPVCsPlugin ----------

def test_has_pvcs_plugin_sets_true_when_pvcs_exist():
    ctx = _ctx_with_pvcs(["data-pvc", "logs-pvc"])
    out = HasPVCsPlugin().run(ctx)
    assert out.capabilities.has_pvcs is True


def test_has_pvcs_plugin_sets_false_when_no_pvcs():
    ctx = _ctx_with_pvcs([])
    out = HasPVCsPlugin().run(ctx)
    assert out.capabilities.has_pvcs is False


# ---------- PrometheusReachabilityPlugin ----------

@responses.activate
def test_prometheus_probe_records_success_on_200():
    responses.add(
        responses.GET,
        "http://prom.fake/api/v1/query",
        json={"status": "success", "data": {"resultType": "vector", "result": []}},
        status=200,
    )

    ctx = StageContext(kubeconfig_path="/dev/null")
    out = PrometheusReachabilityPlugin(prometheus_url="http://prom.fake").run(ctx)

    assert out.capabilities.prometheus_reachable is True
    assert len(out.probes) == 1
    assert out.probes[0].success is True
    assert out.probes[0].name == "prometheus"


@responses.activate
def test_prometheus_probe_records_failure_on_connection_error():
    # responses raises ConnectionError if no mock matches
    ctx = StageContext(kubeconfig_path="/dev/null")
    out = PrometheusReachabilityPlugin(prometheus_url="http://prom.fake").run(ctx)

    assert out.capabilities.prometheus_reachable is False
    assert out.probes[0].success is False


# ---------- PVCScenarioRecommenderPlugin ----------

def test_pvc_recommender_enables_when_pvcs_present():
    ctx = _ctx_with_pvcs(["postgres-data"])
    ctx.capabilities.has_pvcs = True

    out = PVCScenarioRecommenderPlugin().run(ctx)

    assert len(out.recommendations) == 1
    rec = out.recommendations[0]
    assert rec.key == "pvc-scenarios.enable"
    assert rec.value is True
    assert "1 PVC" in rec.reason


def test_pvc_recommender_disables_when_no_pvcs():
    ctx = _ctx_with_pvcs([])
    ctx.capabilities.has_pvcs = False

    out = PVCScenarioRecommenderPlugin().run(ctx)

    rec = out.recommendations[0]
    assert rec.value is False
    assert "0 PVCs" in rec.reason
