"""NPV sanity 회귀 가드 — NPV $30B 버그가 재발하지 않도록 합리적 범위 검증.

기준: default 경제 + OOIP 100 Mbbl, CO2_Miscible.
"""

from economics import evaluate_eor, build_cashflow, pbp
from constants import DEFAULT_ECONOMIC, DEFAULT_RESERVOIR


def _sanity_reservoir():
    return {**DEFAULT_RESERVOIR, "ooip_million_bbl": 100}


def test_default_reservoir_npv_in_sane_range():
    """OOIP 100 NPV는 수십~수백 million $ (수십억 $ 아님)."""
    r = evaluate_eor("CO2_Miscible", _sanity_reservoir(), DEFAULT_ECONOMIC)
    assert 10 < r["npv_million_usd"] < 1000, f"NPV {r['npv_million_usd']}M 비정상"


def test_default_reservoir_irr_in_sane_range():
    """IRR 5-50% (None 아님, 5654% 같은 비정상값 아님)."""
    r = evaluate_eor("CO2_Miscible", _sanity_reservoir(), DEFAULT_ECONOMIC)
    assert r["irr_pct"] is not None
    assert 5 < r["irr_pct"] < 50, f"IRR {r['irr_pct']}% 비정상"


def test_default_reservoir_pbp_in_sane_range():
    """PBP 1-15년 (0년=즉시흑자 버그 아님)."""
    r = evaluate_eor("CO2_Miscible", _sanity_reservoir(), DEFAULT_ECONOMIC)
    assert r["pbp_years"] is not None
    assert 1 <= r["pbp_years"] <= 15


def test_default_reservoir_pir_defined_and_positive():
    """PIR이 정의되고 (None 아님) 양수."""
    r = evaluate_eor("CO2_Miscible", _sanity_reservoir(), DEFAULT_ECONOMIC)
    assert r["pir"] is not None
    assert r["pir"] > 0


def test_capex_distribution_makes_year0_negative():
    """0년차: 생산 0 + CAPEX 60% → 강한 음수 (즉시흑자 회귀 방지)."""
    cf = build_cashflow("CO2_Miscible", _sanity_reservoir(), DEFAULT_ECONOMIC)
    assert cf[0] < 0
    assert abs(cf[0] - (-DEFAULT_ECONOMIC["capex_million_usd"] * 0.60)) < 1e-6


def test_no_instant_payback_regression():
    """NPV $30B 버그 회귀 방지: PBP는 0이 아니어야 함."""
    cf = build_cashflow("CO2_Miscible", _sanity_reservoir(), DEFAULT_ECONOMIC)
    assert pbp(cf) != 0
