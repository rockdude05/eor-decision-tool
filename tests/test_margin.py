"""배럴당 마진 + CO2 비용 비율 테스트 — 제출본 § 3-(3).

§ 3-(3): CO2 $15 / OPEX $10-15 / CAPEX $5-10 per bbl,
"CO2 비용이 전체 배럴당 비용의 25-50%를 차지", "예상 마진: 데이터에 따른 자동 계산".
"""

from economics import margin_per_bbl
from constants import DEFAULT_ECONOMIC


def test_margin_components_sum():
    """총비용 = CO2 + OPEX + CAPEX/bbl."""
    m = margin_per_bbl(DEFAULT_ECONOMIC, capex_per_bbl=7.5)
    assert abs(m["total_cost_per_bbl"] - (15 + 12 + 7.5)) < 1e-6


def test_margin_positive_at_105():
    """기준 유가 $105.66에서 마진 양수."""
    m = margin_per_bbl(DEFAULT_ECONOMIC, capex_per_bbl=7.5)
    assert m["margin_per_bbl"] > 0
    # margin = 105.66 - 34.5 = 71.16
    assert abs(m["margin_per_bbl"] - 71.16) < 0.01


def test_co2_cost_ratio_in_submission_range():
    """CO2 비용 비율이 제출본 § 3-(3) 25-50% 범위 안."""
    m = margin_per_bbl(DEFAULT_ECONOMIC, capex_per_bbl=7.5)
    assert 25 <= m["co2_cost_ratio_pct"] <= 50
    # 15 / 34.5 = 43.48%
    assert abs(m["co2_cost_ratio_pct"] - 43.48) < 0.1


def test_margin_pct_relative_to_oil_price():
    """마진율 = margin / oil_price × 100."""
    m = margin_per_bbl(DEFAULT_ECONOMIC, capex_per_bbl=7.5)
    expected = m["margin_per_bbl"] / m["oil_price"] * 100
    assert abs(m["margin_pct"] - expected) < 1e-6


def test_margin_negative_when_oil_below_cost():
    """유가 < 총비용이면 마진 음수."""
    eco = {**DEFAULT_ECONOMIC, "oil_price_usd_per_bbl": 20}
    m = margin_per_bbl(eco, capex_per_bbl=7.5)
    assert m["margin_per_bbl"] < 0
