"""recommendation.py — 순위 + 민감도."""

import pytest
from recommendation import rank_techniques, sensitivity_analysis, build_recommendation
from constants import DEFAULT_RESERVOIR, DEFAULT_ECONOMIC


def test_rank_by_npv_descending():
    """NPV 큰 순서로 정렬."""
    economics_list = [
        {"technique": "Steamflood", "npv_million_usd": 50, "passed": True},
        {"technique": "CO2_Miscible", "npv_million_usd": 200, "passed": True},
        {"technique": "Polymer", "npv_million_usd": 100, "passed": True},
    ]
    ranking = rank_techniques(economics_list)
    assert ranking[0] == "CO2_Miscible"
    assert ranking[1] == "Polymer"
    assert ranking[2] == "Steamflood"


def test_rank_excludes_failed():
    """passed=False는 ranking에서 제외."""
    economics_list = [
        {"technique": "CO2_Miscible", "npv_million_usd": 200, "passed": True},
        {"technique": "Steamflood", "npv_million_usd": 999, "passed": False},
    ]
    ranking = rank_techniques(economics_list)
    assert "Steamflood" not in ranking
    assert ranking[0] == "CO2_Miscible"


def test_rank_handles_negative_npv():
    """NPV 음수인 기법도 포함 (나열은 함, 최상위는 아님)."""
    economics_list = [
        {"technique": "Polymer", "npv_million_usd": -10, "passed": True},
        {"technique": "CO2_Miscible", "npv_million_usd": 200, "passed": True},
    ]
    ranking = rank_techniques(economics_list)
    assert ranking[0] == "CO2_Miscible"
    assert "Polymer" in ranking


def test_rank_empty_list():
    """빈 list → 빈 ranking."""
    assert rank_techniques([]) == []


def test_rank_handles_none_npv():
    """NPV가 None인 경우 가장 낮은 우선순위."""
    economics_list = [
        {"technique": "Failed", "npv_million_usd": None, "passed": True},
        {"technique": "CO2_Miscible", "npv_million_usd": 100, "passed": True},
    ]
    ranking = rank_techniques(economics_list)
    assert ranking[0] == "CO2_Miscible"


def test_sensitivity_returns_6_scenarios():
    """6개 유가 시나리오 (60, 70 baseline, 80, 100, 105, 120)."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 1000}
    economic = {**DEFAULT_ECONOMIC}
    passed_techniques = ["CO2_Miscible", "Polymer"]

    sensitivity = sensitivity_analysis(reservoir, economic, passed_techniques)

    expected_keys = {
        "oil_price_60_pessimistic",
        "oil_price_70_low",
        "oil_price_80_eia_4q26",
        "oil_price_100_high",
        "oil_price_105_current_market",
        "oil_price_120_supply_shock",
    }
    assert set(sensitivity.keys()) == expected_keys


def test_sensitivity_higher_oil_higher_npv():
    """유가 ↑ → NPV ↑ (단조 증가)."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 1000}
    economic = {**DEFAULT_ECONOMIC}
    passed_techniques = ["CO2_Miscible"]

    sensitivity = sensitivity_analysis(reservoir, economic, passed_techniques)

    npv_60 = sensitivity["oil_price_60_pessimistic"]["npv_million_usd"]
    npv_120 = sensitivity["oil_price_120_supply_shock"]["npv_million_usd"]
    assert npv_120 > npv_60


def test_sensitivity_each_has_top_technique():
    """각 시나리오에서 top_technique 명시."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}
    passed = ["CO2_Miscible", "Polymer"]

    sensitivity = sensitivity_analysis(reservoir, economic, passed)
    for key, value in sensitivity.items():
        assert "top_technique" in value
        assert "npv_million_usd" in value


def test_sensitivity_empty_passed_list():
    """통과 기법 없으면 각 시나리오의 top_technique = None."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}

    sensitivity = sensitivity_analysis(reservoir, economic, [])
    for key, value in sensitivity.items():
        assert value["top_technique"] is None


def test_build_recommendation_primary_is_top_ranked():
    """primary = ranking[0]."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 1000}
    economic = {**DEFAULT_ECONOMIC}
    screening_results = [
        {"technique": "CO2_Miscible", "passed": True},
        {"technique": "Polymer", "passed": True},
        {"technique": "Steamflood", "passed": False},
    ]
    economics_list = [
        {"technique": "CO2_Miscible", "npv_million_usd": 200, "passed": True},
        {"technique": "Polymer", "npv_million_usd": 100, "passed": True},
    ]
    rec = build_recommendation(reservoir, economic, screening_results, economics_list)
    assert rec["primary"] == "CO2_Miscible"


def test_build_recommendation_no_passed_techniques():
    """screening에서 모두 탈락 시 primary = None."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}
    screening_results = [{"technique": "X", "passed": False}]
    economics_list = []
    rec = build_recommendation(reservoir, economic, screening_results, economics_list)
    assert rec["primary"] is None
    assert "통과 기법 없음" in rec["rationale_short"]


def test_build_recommendation_includes_sensitivity():
    """결과에 sensitivity 6개 시나리오 포함."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 1000}
    economic = {**DEFAULT_ECONOMIC}
    screening_results = [{"technique": "CO2_Miscible", "passed": True}]
    economics_list = [{"technique": "CO2_Miscible", "npv_million_usd": 200, "passed": True}]
    rec = build_recommendation(reservoir, economic, screening_results, economics_list)
    assert "sensitivity" in rec
    # 6 시나리오 + "_note" = 7 keys
    assert len(rec["sensitivity"]) == 7
    assert "_note" in rec["sensitivity"]


def test_build_recommendation_ranking_structure():
    """ranking은 list[str]."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 1000}
    economic = {**DEFAULT_ECONOMIC}
    screening_results = [
        {"technique": "CO2_Miscible", "passed": True},
        {"technique": "Polymer", "passed": True},
    ]
    economics_list = [
        {"technique": "CO2_Miscible", "npv_million_usd": 200, "passed": True},
        {"technique": "Polymer", "npv_million_usd": 100, "passed": True},
    ]
    rec = build_recommendation(reservoir, economic, screening_results, economics_list)
    assert isinstance(rec["ranking"], list)
    assert all(isinstance(t, str) for t in rec["ranking"])
    assert rec["ranking"] == ["CO2_Miscible", "Polymer"]
