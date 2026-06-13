"""export.py — spec § 2.4 JSON schema 직렬화."""

import json
import pytest
from datetime import datetime
from export import build_export_dict
from constants import DEFAULT_RESERVOIR, DEFAULT_ECONOMIC


def test_export_includes_schema_version():
    """schema_version='1.1' 명시 (v1.1: korean_context 제거)."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}
    result = build_export_dict(reservoir, economic, scenario_name="test")
    assert result["schema_version"] == "1.1"


def test_export_includes_cost_methodology():
    """제출본 § 3-(3) 유가/비용 출처 방법론 자동 포함."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}
    result = build_export_dict(reservoir, economic, scenario_name="test")
    assert "cost_methodology" in result
    assert "NETL Primer 2010" in result["cost_methodology"]
    assert "105.66" in result["cost_methodology"]


def test_export_includes_screening_economics_recommendation():
    """전체 4개 섹션 포함."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}
    result = build_export_dict(reservoir, economic, scenario_name="test")
    assert "inputs" in result
    assert "screening" in result
    assert "economics" in result
    assert "recommendation" in result


def test_export_serializable_to_json():
    """결과는 json.dumps 가능해야 함."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}
    result = build_export_dict(reservoir, economic, scenario_name="test")
    # 예외 없이 직렬화 가능해야 함
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    assert len(json_str) > 100


def test_export_no_korean_context_field():
    """제출본 scope: korean_context 필드는 export에서 제거됨 (v1.1)."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}
    result = build_export_dict(reservoir, economic, scenario_name="test")
    assert "korean_context" not in result
    assert result["schema_version"] == "1.1"


def test_export_metadata_has_timestamp():
    """metadata.generated_at은 ISO 형식 timestamp."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}
    result = build_export_dict(reservoir, economic, scenario_name="test")
    assert "generated_at" in result["metadata"]
    # ISO 형식 파싱 가능해야 함
    datetime.fromisoformat(result["metadata"]["generated_at"])
