"""
Jinja2RendererPlugin — Stage 5 (Render).

Takes everything previous stages produced and turns it into a YAML
file. Pulls fitness_query from a recommendation if one exists,
otherwise falls back to the same hardcoded value krkn-ai uses today
(so the `before` and `after` comparison is honest).
"""

from __future__ import annotations

from pathlib import Path

import jinja2

from krkn_ai_poc.pipeline.context import StageContext
from krkn_ai_poc.pipeline.plugins import RendererPlugin

# Match krkn-ai's current hardcoded fitness query.
# This is the BEFORE-state value — the proposal's pipeline replaces
# it with a recommender-emitted value when one is available.
_DEFAULT_FITNESS_QUERY = "sum(kube_pod_container_status_restarts_total)"


class Jinja2RendererPlugin(RendererPlugin):
    def __init__(self, template_path: Path, output_path: Path) -> None:
        self._template_path = Path(template_path)
        self._output_path = Path(output_path)

    def run(self, ctx: StageContext) -> StageContext:
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self._template_path.parent),
            autoescape=False,
	    keep_trailing_newline=True,
        )
        template = env.get_template(self._template_path.name)

        # Pull fitness query from recommendations if a recommender emitted one
        fitness_query = _DEFAULT_FITNESS_QUERY
        fitness_reason = None
        scenario_recs = []
        for rec in ctx.recommendations:
            if rec.key == "fitness_function.query":
                fitness_query = rec.value
                fitness_reason = rec.reason
            elif rec.key.endswith(".enable"):
                scenario_recs.append(
                    {
                        "scenario_key": rec.key.removesuffix(".enable"),
                        "enabled": bool(rec.value),
                        "reason": rec.reason,
                    }
                )

        # Health checks come from probe results of kind=health
        health_checks = [
            {"name": p.name, "url": p.url}
            for p in ctx.probes
            if p.kind == "health" and p.success
        ]

        rendered = template.render(
            kubeconfig_path=ctx.kubeconfig_path,
            components=ctx.components,
            fitness_query=fitness_query,
            fitness_reason=fitness_reason,
            health_checks=health_checks,
            scenario_recommendations=scenario_recs,
        )

        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        self._output_path.write_text(rendered)
        return ctx
