"""build_cashflow(): 입력 → 연도별 NCF 배열."""

import pytest
from economics import build_cashflow
from constants import DEFAULT_RESERVOIR, DEFAULT_ECONOMIC


def test_build_cashflow_capex_year0():
    """0년차에 CAPEX 60% 차감 (Arps fill-up: 0년차 생산 0). 길이 = years + 1."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 100}
    economic = {**DEFAULT_ECONOMIC, "project_years": 5, "capex_million_usd": 500}
    cf = build_cashflow("CO2_Miscible", reservoir, economic)
    assert cf[0] < 0  # CAPEX 적용
    assert abs(cf[0] - (-500 * 0.60)) < 1e-6  # 0년차 = -CAPEX×60% (생산 0)
    assert len(cf) == 6  # year 0 ~ year 5


def test_build_cashflow_revenue_proportional_to_recovery():
    """회수율 22% (CO2_Miscible) → OOIP × 22% × $70/bbl revenue 발생."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 100}
    economic = {**DEFAULT_ECONOMIC, "project_years": 10}
    cf = build_cashflow("CO2_Miscible", reservoir, economic)
    # CAPEX 환원 후, 0년 외 cashflow 양수 누적이어야 함
    assert sum(cf[1:]) > 0


def test_build_cashflow_zero_recovery():
    """OOIP 0 → 생산 0, cashflow는 분산 CAPEX(60/30/10)만."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 0}
    economic = {**DEFAULT_ECONOMIC, "project_years": 5}
    capex = economic["capex_million_usd"]
    cf = build_cashflow("CO2_Miscible", reservoir, economic)
    assert abs(cf[0] - (-capex * 0.60)) < 1e-6
    assert abs(cf[1] - (-capex * 0.30)) < 1e-6
    assert abs(cf[2] - (-capex * 0.10)) < 1e-6
    assert all(c == 0 for c in cf[3:])


def test_build_cashflow_unknown_technique():
    """존재하지 않는 기법 → ValueError."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}
    with pytest.raises(ValueError):
        build_cashflow("Unknown_Technique", reservoir, economic)
