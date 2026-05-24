# krkn-ai-pipeline-poc
[![tests](https://github.com/1PoPTRoN/krkn-ai-pipeline-poc/actions/workflows/test.yml/badge.svg)](https://github.com/1PoPTRoN/krkn-ai-pipeline-poc/actions/workflows/test.yml)

Vertical-slice PoC - a 5-stage pluggable discovery pipeline.

Built as the proof-of-concept artifact for the [LFX Mentorship 2026 Term 2](https://mentorship.lfx.linuxfoundation.org/project/b89f3736-7588-4e64-9040-1235ed77155a) application by [@1PoPTRoN](https://github.com/1PoPTRoN). **Not for merge** - this is the architecture proof for the full 12-week deliverable.

## What this proves

`krkn-ai discover` today outputs a YAML inventory that needs hand-editing before it's runnable: hardcoded fitness query, commented-out health checks, scenarios statically enabled regardless of what's in the cluster. The proposed pipeline turns those decisions into auditable, plugin-driven recommendations.

This PoC implements the smallest end-to-end slice that proves the architecture: the framework (5 ABCs + registry + runner) plus **one plugin per stage**. Run it against a real cluster, it ingests components, derives capabilities, probes Prometheus, emits a recommendation, and renders a YAML where `pvc-scenarios.enable` flips based on whether PVCs actually exist — with a `# reason:` comment so the decision is auditable.

```yaml
# examples/before.yaml — what discover produces today
scenario:
  pvc-scenarios:
    enable: false        # static, regardless of cluster state

# examples/after.yaml — what the pipeline produces
scenario:
  pvc-scenarios:
    enable: true
    # reason: 1 PVC(s) detected; enabling pvc-scenarios
```

## Status

| Stage | Plugin in this PoC | Status |
|---|---|---|
| 1. Inventory | `DefaultInventoryPlugin` (wraps the k8s python client) | ✅ |
| 2. Capability | `HasPVCsPlugin` | ✅ |
| 3. Probe | `PrometheusReachabilityPlugin` | ✅ |
| 4. Recommend | `PVCScenarioRecommenderPlugin` | ✅ |
| 5. Render | `Jinja2RendererPlugin` | ✅ |

**14 tests passing**, including end-to-end pipeline tests with mocked cluster + Prometheus, plus a YAML-validity regression test.

**Validated against:** minikube v1.35 on Ubuntu 24.04 (UTM on Apple Silicon), with `kube-prometheus-stack` (Helm) and a single-PVC Postgres workload.

## Try it

```bash
# 1. Clone and install
git clone https://github.com/1PoPTRoN/krkn-ai-pipeline-poc.git
cd krkn-ai-pipeline-poc
uv sync

# 2. Run the test suite (no cluster needed)
uv run pytest -v
# → 14 passed

# 3. Run end-to-end against a real cluster
#    (assumes a running cluster + Prometheus on localhost:9090)
PROMETHEUS_URL=http://localhost:9090 uv run python demo.py ~/.kube/config

# 4. See the diff
diff examples/before.yaml examples/after.yaml
```

## Architecture

```text
kubeconfig
│
▼
┌──────────────────────────────────────────────────────────────┐
│ Stage 1  Inventory      DefaultInventoryPlugin               │
│          │ enumerate namespaces, pods, services, PVCs, nodes │
│          ▼                                                   │
│ Stage 2  Capability     HasPVCsPlugin                        │
│          │ derive booleans from inventory                    │
│          ▼                                                   │
│ Stage 3  Probe          PrometheusReachabilityPlugin         │
│          │ outbound HTTP checks                              │
│          ▼                                                   │
│ Stage 4  Recommend      PVCScenarioRecommenderPlugin         │
│          │ emit Recommendation(key, value, reason)           │
│          ▼                                                   │
│ Stage 5  Render         Jinja2RendererPlugin                 │
│          │ template → krkn-ai.yaml                           │
└──────────┼───────────────────────────────────────────────────┘
|
▼
after.yaml
```

Each stage exposes an ABC (`InventoryPlugin`, `CapabilityPlugin`, `ProbePlugin`, `RecommenderPlugin`, `RendererPlugin`). Adding a new scenario in the full LFX deliverable is one new file implementing one ABC, not an edit to `ClusterManager`.

## What this PoC is NOT

- ❌ A fork of krkn-ai. It's a standalone proof of the pipeline architecture; integration with upstream happens in the LFX work.
- ❌ The full deliverable. The LFX 12-week scope ships 22 plugins total, plus `--explain` and `--merge-with`. This PoC ships 5 (one per stage).
- ❌ Production code. No retry logic, no concurrency, no plugin discovery from entry points. All deferred to the LFX scope where they belong.

## What's deferred to the LFX 12 weeks

- 5 more `CapabilityPlugin`s (OpenShift detection, VMI presence, network exposure type, namespace count tier, node count tier)
- 1 more `ProbePlugin` (Route/Ingress/LB endpoint discovery + reachability)
- 11 more `RecommenderPlugin`s (one per remaining scenario type) + 1 `FitnessRecommenderPlugin`
- `--explain` flag (per-stage trace output to stderr)
- `--merge-with existing.yaml` flag (preserves user customizations across re-runs)
- Plugin discovery via `pyproject.toml` entry points
- Upstream integration as a non-breaking addition to `krkn_ai/cli/cmd.py`

## Related

- Upstream repo: [krkn-chaos/krkn-ai](https://github.com/krkn-chaos/krkn-ai)

## License

[Apache-2.0](./LICENSE) — same as upstream krkn-ai.
