"""
demo.py — runs the PoC end-to-end against your local kubeconfig.

Usage:
    PROMETHEUS_URL=http://localhost:9090 uv run python demo.py /path/to/kubeconfig

By end of Day 5: 4 of 5 stages wired (Inventory, Capability, Probe, Recommend).
Day 6 adds the Render stage and produces the before/after YAML diff.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from krkn_ai_poc.pipeline.registry import PluginRegistry, Stage
from krkn_ai_poc.pipeline.runner import PipelineRunner
from krkn_ai_poc.plugins.capability.has_pvcs import HasPVCsPlugin
from krkn_ai_poc.plugins.inventory.default import DefaultInventoryPlugin
from krkn_ai_poc.plugins.probe.prometheus_reachability import (
    PrometheusReachabilityPlugin,
)
from krkn_ai_poc.plugins.recommend.scenario_pvc import (
    PVCScenarioRecommenderPlugin,
)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: uv run python demo.py /path/to/kubeconfig")
        sys.exit(1)

    kubeconfig = Path(sys.argv[1]).expanduser().resolve()
    if not kubeconfig.exists():
        print(f"kubeconfig not found: {kubeconfig}")
        sys.exit(1)

    prom_url = os.environ.get("PROMETHEUS_URL", "http://localhost:9090")

    registry = PluginRegistry()
    registry.register(Stage.INVENTORY, DefaultInventoryPlugin())
    registry.register(Stage.CAPABILITY, HasPVCsPlugin())
    registry.register(Stage.PROBE, PrometheusReachabilityPlugin(prometheus_url=prom_url))
    registry.register(Stage.RECOMMEND, PVCScenarioRecommenderPlugin())

    runner = PipelineRunner(registry)
    ctx = runner.run(kubeconfig_path=str(kubeconfig))

    print("=== inventory ===")
    print(f"namespaces: {len(ctx.components.namespaces)}")
    print(f"pods:       {len(ctx.components.pods)}")
    print(f"services:   {len(ctx.components.services)}")
    print(f"pvcs:       {len(ctx.components.pvcs)}")
    print(f"nodes:      {len(ctx.components.nodes)}")
    print()
    print("=== capabilities ===")
    print(f"has_pvcs:              {ctx.capabilities.has_pvcs}")
    print(f"prometheus_reachable:  {ctx.capabilities.prometheus_reachable}")
    print()
    print("=== probes ===")
    for p in ctx.probes:
        marker = "✓" if p.success else "✗"
        print(f"  {marker} {p.name} ({p.kind}) → {p.url}")
    print()
    print("=== recommendations ===")
    for r in ctx.recommendations:
        print(f"  {r.key} = {r.value}")
        print(f"      reason: {r.reason}")


if __name__ == "__main__":
    main()
