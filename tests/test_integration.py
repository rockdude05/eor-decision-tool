"""E2E 통합 테스트.

Streamlit 직접 실행은 어려우므로 함수 chain을 시뮬레이션.
제출본 frame: 사용자가 임의 저류층 물성을 입력하는 워크플로우를 대표하는
일반 저류층(SAMPLE_RESERVOIR)으로 검증한다.
"""

import json
from export import build_export_dict
from constants import DEFAULT_ECONOMIC

# CO2-Miscible이 통과하는 대표 저류층 (깊은 경질유): API 35, 깊이 8200ft
SAMPLE_RESERVOIR = {
    "api_gravity_deg": 35,
    "viscosity_cp": 5.0,
    "depth_ft": 8200,
    "permeability_md": 50.0,
    "temperature_f": 150,
    "oil_saturation_pct": 60,
    "ooip_million_bbl": 1000,
}
SAMPLE_ECONOMIC = {**DEFAULT_ECONOMIC}


def test_e2e_recommends_co2_miscible():
    """대표 저류층(API 35, 깊이 8200) → CO2-Miscible이 ranking에 포함."""
    export = build_export_dict(
        SAMPLE_RESERVOIR, SAMPLE_ECONOMIC, scenario_name="sample",
    )
    assert "CO2_Miscible" in export["recommendation"]["ranking"]


def test_e2e_json_export_serializable():
    """전체 export dict가 JSON으로 직렬화되어야 함."""
    export = build_export_dict(
        SAMPLE_RESERVOIR, SAMPLE_ECONOMIC, scenario_name="sample",
    )
    json_str = json.dumps(export, ensure_ascii=False, indent=2)
    assert len(json_str) > 1000
    parsed = json.loads(json_str)
    assert parsed["schema_version"] == "1.1"


def test_e2e_sensitivity_monotonic():
    """sensitivity 6 시나리오에서 유가↑ → NPV↑ (단조 증가)."""
    export = build_export_dict(
        SAMPLE_RESERVOIR, SAMPLE_ECONOMIC, scenario_name="sample",
    )
    sens = export["recommendation"]["sensitivity"]
    npv_60 = sens["oil_price_60_pessimistic"]["npv_million_usd"]
    npv_70 = sens["oil_price_70_low"]["npv_million_usd"]
    npv_120 = sens["oil_price_120_supply_shock"]["npv_million_usd"]

    assert npv_70 > npv_60
    assert npv_120 > npv_70


def test_e2e_screening_returns_8_techniques():
    """Screening은 항상 8개 기법 결과 반환 (Taber Tables 1-7, CO2 미시블/비미시블 분리)."""
    export = build_export_dict(
        SAMPLE_RESERVOIR, SAMPLE_ECONOMIC, scenario_name="sample",
    )
    assert len(export["screening"]["results"]) == 8


def test_e2e_no_korean_context_field():
    """제출본 scope: korean_context 필드는 더 이상 export에 없어야 함."""
    export = build_export_dict(
        SAMPLE_RESERVOIR, SAMPLE_ECONOMIC, scenario_name="sample",
    )
    assert "korean_context" not in export
