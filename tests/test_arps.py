"""Arps 감퇴 곡선 + Arps 기반 build_cashflow 테스트 (교재 6장 통합).

검증 기준점: 교재 예제 6.1 (지수, 99.44 STB/day), 예제 6.2 (쌍곡선, 200.75 STB/day).
"""

import numpy as np
from economics import (
    arps_exponential,
    arps_hyperbolic,
    production_profile_arps,
    build_cashflow,
)
from constants import DEFAULT_ECONOMIC


# ---------- arps_exponential (식 6.6) ----------

def test_arps_exponential_textbook_example_6_1():
    """교재 예제 6.1: Q_i=230, D=0.1398/년, t=6년 → Q≈99.44 STB/day."""
    q = arps_exponential(Q_i=230, D=0.1398, t=6)
    assert abs(q - 99.44) < 0.5


def test_arps_exponential_t_zero_returns_qi():
    """t=0이면 초기생산량 그대로."""
    assert abs(arps_exponential(Q_i=100, D=0.1, t=0) - 100) < 1e-9


def test_arps_exponential_array_input():
    """t 배열 입력 → 배열 출력 (감소)."""
    t = np.array([0, 1, 2, 3])
    q = arps_exponential(Q_i=100, D=0.2, t=t)
    assert q.shape == (4,)
    assert q[0] > q[1] > q[2] > q[3]


# ---------- arps_hyperbolic (식 6.9) ----------

def test_arps_hyperbolic_textbook_example_6_2():
    """교재 예제 6.2: Q_i=230, D_i=0.1398/년, b=0.4, t=1년 → Q≈200.75 STB/day."""
    q = arps_hyperbolic(Q_i=230, D_i=0.1398, b=0.4, t=1)
    assert abs(q - 200.75) < 0.5


def test_arps_hyperbolic_b_near_zero_approximates_exponential():
    """b→0이면 지수 감퇴(식 6.6)에 수렴 (식 6.9 §6장 명시)."""
    q_hyp = arps_hyperbolic(Q_i=200, D_i=0.15, b=1e-6, t=5)
    q_exp = arps_exponential(Q_i=200, D=0.15, t=5)
    assert abs(q_hyp - q_exp) < 0.1


# ---------- production_profile_arps ----------

def test_production_profile_arps_length():
    """길이 = project_years + 1 (year 0 ~ year N)."""
    prof = production_profile_arps(total_recoverable_bbl=1000, project_years=20)
    assert len(prof) == 21


def test_production_profile_arps_total_preserved():
    """프로파일 총합이 입력 total_recoverable_bbl과 일치 (normalize)."""
    prof = production_profile_arps(total_recoverable_bbl=1000, project_years=20)
    assert abs(prof.sum() - 1000) < 0.5


def test_production_profile_arps_year0_no_production():
    """0년차는 CO2 주입/fill-up 기간 → 증분 생산 0 (NPV $30B 버그의 핵심 수정)."""
    prof = production_profile_arps(total_recoverable_bbl=1000, project_years=20)
    assert prof[0] == 0


def test_production_profile_arps_declines_after_peak():
    """생산 시작(year 1) 이후 Arps 감퇴로 단조 감소."""
    prof = production_profile_arps(
        total_recoverable_bbl=1000, project_years=20, decline_type="exponential"
    )
    assert prof[1] > prof[2] > prof[3]


# ---------- build_cashflow (Arps + CAPEX 분산) ----------

def _reservoir(ooip=100):
    return {
        "api_gravity_deg": 35, "viscosity_cp": 5.0, "depth_ft": 8200,
        "permeability_md": 50.0, "temperature_f": 150,
        "oil_saturation_pct": 60, "ooip_million_bbl": ooip,
    }


def test_build_cashflow_length_includes_year0():
    """cashflow 길이 = project_years + 1."""
    cf = build_cashflow("CO2_Miscible", _reservoir(), DEFAULT_ECONOMIC)
    assert len(cf) == DEFAULT_ECONOMIC["project_years"] + 1


def test_build_cashflow_year0_strongly_negative():
    """0년차: 생산 없음 + CAPEX 60% 차감 → 강한 음수 (즉시흑자 버그 제거)."""
    cf = build_cashflow("CO2_Miscible", _reservoir(), DEFAULT_ECONOMIC)
    capex = DEFAULT_ECONOMIC["capex_million_usd"]
    # 0년차는 생산이 없으므로 cf[0] ≈ -capex*0.60
    assert abs(cf[0] - (-capex * 0.60)) < 1e-6


def test_build_cashflow_year1_capex_still_charged():
    """1년차: CAPEX 30% 추가 차감 (분산 투자)."""
    cf = build_cashflow("CO2_Miscible", _reservoir(), DEFAULT_ECONOMIC)
    capex = DEFAULT_ECONOMIC["capex_million_usd"]
    # 1년차 = 생산수익 - 비용 - capex*0.30. 1년차 생산이 있으므로 정확한 등식은 아니지만
    # capex 분산이 반영되어 production-only 대비 capex*0.30 만큼 낮아야 한다.
    # 직접 검증: capex 0으로 두면 cf1이 capex*0.30 만큼 높아짐.
    eco0 = {**DEFAULT_ECONOMIC, "capex_million_usd": 0}
    cf0 = build_cashflow("CO2_Miscible", _reservoir(), eco0)
    assert abs((cf0[1] - cf[1]) - capex * 0.30) < 1e-6


def test_build_cashflow_total_production_preserved():
    """총 생산량 보존: 총 수익 = 총증분bbl × 유가 (CAPEX·비용 제외 시)."""
    eco = {**DEFAULT_ECONOMIC, "capex_million_usd": 0, "opex_usd_per_bbl": 0,
           "co2_cost_usd_per_bbl": 0}
    cf = build_cashflow("CO2_Miscible", _reservoir(ooip=100), eco)
    # 100 Mbbl × 22% = 22 Mbbl 증분 × $105.66 = $2324.5M
    expected = 100 * 0.22 * eco["oil_price_usd_per_bbl"]
    assert abs(sum(cf) - expected) < 1.0
