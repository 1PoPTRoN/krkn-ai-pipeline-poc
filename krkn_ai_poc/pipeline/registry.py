"""
PluginRegistry — keeps track of which plugins are registered for each stage.

The runner walks stages in fixed order and asks the registry for the
plugins registered against each one.
"""

from __future__ import annotations

from enum import Enum

from krkn_ai_poc.pipeline.plugins import (
    CapabilityPlugin,
    InventoryPlugin,
    ProbePlugin,
    RecommenderPlugin,
    RendererPlugin,
)


class Stage(str, Enum):
    INVENTORY = "inventory"
    CAPABILITY = "capability"
    PROBE = "probe"
    RECOMMEND = "recommend"
    RENDER = "render"


# Type alias for any plugin
AnyPlugin = (
    InventoryPlugin
    | CapabilityPlugin
    | ProbePlugin
    | RecommenderPlugin
    | RendererPlugin
)


class PluginRegistry:
    """Stage -> list[plugin instance]."""

    def __init__(self) -> None:
        self._by_stage: dict[Stage, list[AnyPlugin]] = {s: [] for s in Stage}

    def register(self, stage: Stage, plugin: AnyPlugin) -> None:
        self._by_stage[stage].append(plugin)

    def get(self, stage: Stage) -> list[AnyPlugin]:
        return list(self._by_stage[stage])
