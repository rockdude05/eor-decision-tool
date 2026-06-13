"""screening.py 단위 테스트 — Taber Tables 1-7."""

import pytest
from screening import SCREENING_TABLE, co2_miscible_depth_threshold, evaluate_technique, screen_eor


def test_co2_depth_high_api():
    """API > 40 → 최소 2,500 ft."""
    assert co2_miscible_depth_threshold(45) == 2500


def test_co2_depth_med_api():
    """API 32-39.9 → 2,800 ft."""
    assert co2_miscible_depth_threshold(35) == 2800


def test_co2_depth_28_31_9():
    """API 28-31.9 → 3,300 ft."""
    assert co2_miscible_depth_threshold(30) == 3300


def test_co2_depth_low_api():
    """API 22-27.9 → 4,000 ft."""
    assert co2_miscible_depth_threshold(25) == 4000


def test_co2_depth_below_22():
    """API < 22 → 미시블 불가."""
    assert co2_miscible_depth_threshold(20) is None


def test_co2_depth_boundary_22():
    """API 22 boundary — Taber Table 3에 따르면 미시블 가능 (≥22)."""
    assert co2_miscible_depth_threshold(22) == 4000


def test_co2_depth_boundary_40():
    """API 40 boundary — 32-39.9 범위 (≤39.9)에서 2,800 ft.
    Note: API=40은 ">40"에 해당하므로 2,500ft가 맞음.
    """
    # Taber Table 3에서 ">40" 의미는 strictly > 40
    # 정확히 40일 때는 2,800 ft (32-39.9 범위)
    # 함수 구현은 'if api > 40' 이므로 40.0은 False → 다음 분기로
    assert co2_miscible_depth_threshold(40.0) == 2800
    assert co2_miscible_depth_threshold(40.1) == 2500


def test_screening_table_has_eight_techniques():
    """Taber Tables 1-7 → 8개 기법 (CO2는 미시블/비미시블 2개로 분리)."""
    assert len(SCREENING_TABLE) == 8


def test_screening_table_each_has_source():
    """모든 기법에 Taber Table 출처 명시."""
    for tech, rules in SCREENING_TABLE.items():
        assert "source" in rules
        assert "Taber Table" in rules["source"]


def test_screening_table_co2_miscible_uses_depth_fn():
    """CO2_Miscible은 depth_fn (callable) 사용."""
    rules = SCREENING_TABLE["CO2_Miscible"]
    assert "depth_fn" in rules
    assert callable(rules["depth_fn"])
    # 함수 동작 확인 (Task 10에서 검증됨)
    assert rules["depth_fn"](35) == 2800


def test_evaluate_technique_pass_co2_miscible():
    """API 35, 점도 5, 깊이 8000 → CO2-Miscible 통과."""
    reservoir = {
        "api_gravity_deg": 35,
        "viscosity_cp": 5,
        "depth_ft": 8000,
        "oil_saturation_pct": 60,
    }
    rules = SCREENING_TABLE["CO2_Miscible"]
    passed, checks, fails = evaluate_technique(reservoir, rules)
    assert passed is True
    assert len(fails) == 0


def test_evaluate_technique_fail_steamflood_too_deep():
    """깊이 8000 > 5000 → Steamflood 탈락."""
    reservoir = {
        "api_gravity_deg": 20,
        "viscosity_cp": 1000,
        "depth_ft": 8000,
        "oil_saturation_pct": 60,
        "permeability_md": 300,
    }
    rules = SCREENING_TABLE["Steamflood"]
    passed, checks, fails = evaluate_technique(reservoir, rules)
    assert passed is False
    assert any("깊이" in f or "depth" in f.lower() for f in fails)


def test_evaluate_technique_fail_polymer_too_viscous():
    """점도 200 > 150 → Polymer 탈락."""
    reservoir = {
        "api_gravity_deg": 25,
        "viscosity_cp": 200,
        "depth_ft": 5000,
        "oil_saturation_pct": 60,
        "temperature_f": 150,
        "permeability_md": 50,
    }
    rules = SCREENING_TABLE["Polymer"]
    passed, checks, fails = evaluate_technique(reservoir, rules)
    assert passed is False


def test_screen_eor_returns_all_8():
    """8개 기법에 대해 결과 반환."""
    reservoir = {
        "api_gravity_deg": 30,
        "viscosity_cp": 5,
        "depth_ft": 5000,
        "oil_saturation_pct": 60,
        "temperature_f": 150,
        "permeability_md": 50,
    }
    results = screen_eor(reservoir)
    assert len(results) == 8


def test_screen_eor_deep_light_oil_scenario():
    """깊은 경질유 저류층 (API 35, 깊이 8200) → CO2-Miscible/Polymer 통과."""
    reservoir = {
        "api_gravity_deg": 35,
        "viscosity_cp": 5,
        "depth_ft": 8200,
        "oil_saturation_pct": 60,
        "temperature_f": 150,
        "permeability_md": 50,
    }
    results = screen_eor(reservoir)
    passed = [r["technique"] for r in results if r["passed"]]
    assert "CO2_Miscible" in passed
    # Polymer는 API 35>15, oil_sat 60>50, perm 50>=10, T 150<200 → 통과
    assert "Polymer" in passed
    # Steamflood는 깊이 8200 > 5000 → 탈락
    assert "Steamflood" not in passed


def test_screen_eor_result_structure():
    """결과 dict 구조 검증."""
    reservoir = {
        "api_gravity_deg": 30,
        "viscosity_cp": 5,
        "depth_ft": 5000,
        "oil_saturation_pct": 60,
        "temperature_f": 150,
        "permeability_md": 50,
    }
    results = screen_eor(reservoir)
    for r in results:
        assert "technique" in r
        assert "passed" in r
        assert "criteria_checks" in r
        assert "fail_reasons" in r
        assert "source" in r
        assert "Taber Table" in r["source"]
