"""
demo.py — runs the PoC end-to-end against your local kubeconfig.

Usage:
    uv run python demo.py /path/to/kubeconfig

Day 3: only DefaultInventoryPlugin is wired in. Other stages are no-ops.
By Day 6 this same script will produce a complete krkn-ai.yaml.
"""

from __future__ import annotations

import sys
from pathlib import Path

from krkn_ai_poc.pipeline.registry import PluginRegistry, Stage
from krkn_ai_poc.pipeline.runner import PipelineRunner
from krkn_ai_poc.plugins.inventory.default import DefaultInventoryPlugin


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: uv run python demo.py /path/to/kubeconfig")
        sys.exit(1)

    kubeconfig = Path(sys.argv[1]).expanduser().resolve()
    if not kubeconfig.exists():
        print(f"kubeconfig not found: {kubeconfig}")
        sys.exit(1)

    registry = PluginRegistry()
    registry.register(Stage.INVENTORY, DefaultInventoryPlugin())

    runner = PipelineRunner(registry)
    ctx = runner.run(kubeconfig_path=str(kubeconfig))

    print("=== inventory ===")
    print(f"namespaces: {len(ctx.components.namespaces)}")
    print(f"pods:       {len(ctx.components.pods)}")
    print(f"services:   {len(ctx.components.services)}")
    print(f"pvcs:       {len(ctx.components.pvcs)}")
    print(f"nodes:      {len(ctx.components.nodes)}")
    print()
    print(f"namespaces detail: {ctx.components.namespaces[:5]}...")


if __name__ == "__main__":
    main()
