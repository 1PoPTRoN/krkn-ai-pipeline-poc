"""
DefaultInventoryPlugin — Stage 1.

Uses the official kubernetes Python client to enumerate cluster
components. This is the PoC's standalone version of what krkn-ai's
ClusterManager.discover_components() does upstream.

For the PoC, we keep it deliberately thin — namespace, pod, service,
PVC, and node names only. The LFX work will reuse upstream
ClusterManager via dependency injection instead.
"""

from __future__ import annotations

from kubernetes import client, config

from krkn_ai_poc.pipeline.context import ClusterComponents, StageContext
from krkn_ai_poc.pipeline.plugins import InventoryPlugin


class DefaultInventoryPlugin(InventoryPlugin):
    def run(self, ctx: StageContext) -> StageContext:
        config.load_kube_config(config_file=ctx.kubeconfig_path)
        core = client.CoreV1Api()

        namespaces = [ns.metadata.name for ns in core.list_namespace().items]
        pods = [
            p.metadata.name
            for p in core.list_pod_for_all_namespaces().items
        ]
        services = [
            s.metadata.name
            for s in core.list_service_for_all_namespaces().items
        ]
        pvcs = [
            pvc.metadata.name
            for pvc in core.list_persistent_volume_claim_for_all_namespaces().items
        ]
        nodes = [n.metadata.name for n in core.list_node().items]

        ctx.components = ClusterComponents(
            namespaces=namespaces,
            pods=pods,
            services=services,
            pvcs=pvcs,
            nodes=nodes,
        )
        return ctx
