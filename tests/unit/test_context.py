"""Day 2 tests — pure type-shape checks. No cluster, no plugins."""

import pytest
from pydantic import ValidationError

from krkn_ai_poc.pipeline.context import (
    Capabilities,
    Recommendation,
    StageContext,
)


def test_stage_context_roundtrips_through_dict():
    ctx = StageContext(kubeconfig_path="/tmp/kc.yaml")
    as_dict = ctx.model_dump()
    rebuilt = StageContext(**as_dict)
    assert rebuilt.kubeconfig_path == "/tmp/kc.yaml"
    assert rebuilt.components.pods == []
    assert rebuilt.capabilities.has_pvcs is False


def test_empty_capabilities_default_all_false():
    caps = Capabilities()
    assert caps.is_openshift is False
    assert caps.has_pvcs is False
    assert caps.has_vmis is False
    assert caps.prometheus_reachable is False


def test_recommendation_rejects_empty_reason():
    with pytest.raises(ValidationError):
        Recommendation(key="pvc-scenarios.enable", value=True, reason="")
