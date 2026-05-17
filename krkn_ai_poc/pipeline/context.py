"""
Pydantic models that flow through the pipeline.

StageContext is the carrier object. Every plugin reads from it,
mutates it, and returns it. Stages run in fixed order:
Inventory -> Capability -> Probe -> Recommend -> Render.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ClusterComponents(BaseModel):
    """Mirror of krkn-ai's existing ClusterComponents shape.

    Kept minimal for the PoC — full parity lives in upstream
    krkn-ai/utils/cluster_manager.py.
    """

    namespaces: list[str] = Field(default_factory=list)
    pods: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    pvcs: list[str] = Field(default_factory=list)
    nodes: list[str] = Field(default_factory=list)


class Capabilities(BaseModel):
    """Boolean flags about what the cluster can do.

    Each Capability plugin sets exactly one field.
    """

    is_openshift: bool = False
    has_pvcs: bool = False
    has_vmis: bool = False
    prometheus_reachable: bool = False


class ProbeResult(BaseModel):
    """One outbound check — either a health endpoint or a metric query."""

    name: str
    kind: Literal["health", "metric"]
    url: str | None = None
    success: bool


class Recommendation(BaseModel):
    """One config key the pipeline wants to set, with a human-readable reason.

    `reason` is required and must be non-empty — the whole point of the
    pipeline is that every decision is auditable.
    """

    key: str
    value: Any
    reason: str = Field(min_length=1)


class StageContext(BaseModel):
    """The object that flows through all 5 stages."""

    kubeconfig_path: str
    components: ClusterComponents = Field(default_factory=ClusterComponents)
    capabilities: Capabilities = Field(default_factory=Capabilities)
    probes: list[ProbeResult] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
