"""constants 모듈이 제출본 §3-(3) default + 회수율 + 출처를 한 곳에 모은다."""

from constants import (
    DEFAULT_ECONOMIC,
    DEFAULT_RESERVOIR,
    RECOVERY_FACTOR,
    COST_METHODOLOGY,
)


def test_default_economic_submission_frame():
    """제출본 § 3-(3): 유가 WTI 2026 $105.66, 비용 NETL Primer 2010 p.13."""
    assert DEFAULT_ECONOMIC["oil_price_usd_per_bbl"] == 105.66
    assert DEFAULT_ECONOMIC["co2_cost_usd_per_bbl"] == 15
    assert DEFAULT_ECONOMIC["opex_usd_per_bbl"] == 12
    assert DEFAULT_ECONOMIC["discount_rate_pct"] == 15
    assert DEFAULT_ECONOMIC["project_years"] == 20


def test_default_reservoir_ranges():
    """저류층 default = 보고서 대표 케이스(깊은 경질유, OOIP 100)."""
    assert DEFAULT_RESERVOIR["api_gravity_deg"] == 35
    assert DEFAULT_RESERVOIR["depth_ft"] == 8200
    assert DEFAULT_RESERVOIR["ooip_million_bbl"] == 100


def test_recovery_factor_taber_table_8():
    """spec § 2.3: Taber Table 8 미시블 22% / 비미시블 10%."""
    assert RECOVERY_FACTOR["CO2_Miscible"] == 22
    assert RECOVERY_FACTOR["CO2_Immiscible"] == 10


def test_cost_methodology_present():
    """제출본 § 3-(3): 유가/비용 출처 방법론 문자열."""
    assert "105.66" in COST_METHODOLOGY
    assert "NETL Primer 2010" in COST_METHODOLOGY
    assert "제출본 § 3-(3)" in COST_METHODOLOGY
