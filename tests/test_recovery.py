"""회수율 분포(RECOVERY_FACTOR_STATS) + 회수율 override 테스트.

제출본 § 3-(2): CO2 EOR OOIP 4-15% (NETL) + 652개 사례 (Aladassani & Bai 2010).
검증 데이터: Taber Table 8 미시블 22% / 비미시블 10% (04-taber-screening-tables.md).
"""

from constants import RECOVERY_FACTOR, RECOVERY_FACTOR_STATS, ALADASSANI_BAI_NOTE
from economics import build_cashflow, evaluate_eor


def test_recovery_stats_covers_all_techniques():
    """STATS는 RECOVERY_FACTOR의 모든 기법을 포함."""
    assert set(RECOVERY_FACTOR_STATS) == set(RECOVERY_FACTOR)


def test_recovery_stats_default_matches_point_factor():
    """각 기법 default_pct는 점추정 RECOVERY_FACTOR와 일치 (경제성 회귀 방지)."""
    for tech, point in RECOVERY_FACTOR.items():
        assert RECOVERY_FACTOR_STATS[tech]["default_pct"] == point


def test_recovery_stats_co2_netl_range_and_taber():
    """CO2 미시블: NETL field 4-15% + Taber Table 8 22% 둘 다 명시 (제출본 § 3-(2))."""
    co2 = RECOVERY_FACTOR_STATS["CO2_Miscible"]
    assert co2["netl_field_range_pct"] == (4, 15)
    assert co2["taber_table8_pct"] == 22
    assert "NETL" in co2["source"] and "Taber" in co2["source"]


def test_aladassani_bai_note_cites_652():
    """Aladassani-Bai 메타: 652개 사례 + SPE 130726 인용 (per-기법 수치 날조 금지)."""
    assert "652" in ALADASSANI_BAI_NOTE
    assert "Aladassani" in ALADASSANI_BAI_NOTE or "Aladassani & Bai" in ALADASSANI_BAI_NOTE
    assert "130726" in ALADASSANI_BAI_NOTE


def _reservoir(ooip=100):
    return {
        "api_gravity_deg": 35, "viscosity_cp": 5.0, "depth_ft": 8200,
        "permeability_md": 50.0, "temperature_f": 150,
        "oil_saturation_pct": 60, "ooip_million_bbl": ooip,
    }


def test_evaluate_eor_recovery_override():
    """recovery_pct 지정 시 회수율·증분bbl이 그 값을 사용."""
    from constants import DEFAULT_ECONOMIC
    r = evaluate_eor("CO2_Miscible", _reservoir(100), DEFAULT_ECONOMIC, recovery_pct=10)
    assert r["incremental_recovery_pct"] == 10
    assert abs(r["incremental_bbl_million"] - 10.0) < 0.1  # 100 × 10%


def test_build_cashflow_recovery_override_scales_production():
    """recovery_pct=10이 default(22)보다 생산·수익 작음."""
    from constants import DEFAULT_ECONOMIC
    eco = {**DEFAULT_ECONOMIC, "capex_million_usd": 0, "opex_usd_per_bbl": 0,
           "co2_cost_usd_per_bbl": 0}
    cf_default = build_cashflow("CO2_Miscible", _reservoir(100), eco)
    cf_low = build_cashflow("CO2_Miscible", _reservoir(100), eco, recovery_pct=10)
    # 총 수익 비율 = 10/22
    assert abs(sum(cf_low) / sum(cf_default) - 10 / 22) < 0.01
