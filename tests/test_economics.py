"""economics.py 단위 테스트.

검증 케이스: 교재 그림 7.9 사업 B → NPV $101.8M (할인율 10%).
⚠️ cashflow 배열은 교재 그림 7.9(b)를 직접 보고 정확히 입력 필요.
"""

import pytest
from economics import npv, irr, pir, pbp, evaluate_eor
from constants import DEFAULT_RESERVOIR, DEFAULT_ECONOMIC
import numpy as np


def test_npv_zero_rate():
    """할인율 0% → 단순 합."""
    assert npv([100, 100, 100], 0.0) == 300.0


def test_npv_textbook_case_B():
    """교재 그림 7.9 사업 B → NPV $101.8M (할인율 10%).

    cashflow 배열은 그림 7.9(b)에서 사용자가 직접 확인 (2026-05-20).
    """
    cf = [-500, 250, 200, 150, 100, 100, -60]
    result = npv(cf, 0.10)
    assert abs(result - 101.8) < 1.0, (
        f"NPV {result}이 교재 표 7.4 사업 B의 101.8과 다름."
    )


def test_npv_negative_result():
    """현금 유출 > 유입 → 음수."""
    cf = [-1000, 100, 100]
    result = npv(cf, 0.10)
    assert result < 0


# tests/test_economics.py에 추가


def test_irr_textbook_case_B():
    """교재 표 7.4 사업 B → IRR 20.28%.

    cashflow 배열은 그림 7.9(b)에서 사용자가 직접 확인 (2026-05-20).
    """
    cf = [-500, 250, 200, 150, 100, 100, -60]
    result = irr(cf)
    assert result is not None, "IRR 계산 실패"
    assert 0.10 < result < 0.25, (
        f"IRR {result*100:.2f}%이 합리적 범위 (10-25%) 밖. 교재 기대값 20.28%"
    )
    assert abs(result * 100 - 20.28) < 0.5, (
        f"IRR {result*100:.2f}%이 교재 20.28%와 다름"
    )


def test_irr_no_positive_cashflow():
    """양수 cashflow 없음 → None 또는 NaN."""
    cf = [-100, -50, -30]
    result = irr(cf)
    # numpy-financial.irr returns NaN in this case
    assert result is None or (result is not None and np.isnan(result))


def test_irr_multiple_sign_changes():
    """부호 변화 다수 → 허수/복수 IRR 가능. None 또는 단일 실수, 예외 없이."""
    cf = [-100, 200, -150, 100]
    # 실행 자체가 예외 없이 되어야 함
    try:
        result = irr(cf)
    except Exception:
        pytest.fail("IRR computation should not raise; handle multi-IRR gracefully")


def test_irr_simple_positive():
    """초기 -100, 이후 50씩 → IRR 양수."""
    cf = [-100, 50, 50, 50]
    result = irr(cf)
    assert result is not None
    assert result > 0


def test_pir_basic():
    """미래 현금흐름 NPV / 투자 NPV."""
    # 투자 100 (t=0), 수입 50씩 5년, rate=10%
    revenues = [0, 50, 50, 50, 50, 50]
    investments = [100, 0, 0, 0, 0, 0]
    result = pir(revenues, investments, 0.10)
    # NPV(revenues) ≈ 50*(1/1.1 + 1/1.21 + ...) ≈ 189.5
    # NPV(investments) = 100
    # PIR ≈ 1.895
    assert abs(result - 1.895) < 0.05


def test_pir_textbook_case_B():
    """교재 표 7.4 사업 B → PIR 1.20.

    cashflow 배열은 그림 7.9(b)에서 사용자가 직접 확인 (2026-05-20).
    투자: Year 0 (-500), Year 6 (-60); 수입: Year 1~5 (250, 200, 150, 100, 100).
    """
    investments = [500, 0, 0, 0, 0, 0, 60]
    revenues = [0, 250, 200, 150, 100, 100, 0]
    result = pir(revenues, investments, 0.10)
    assert abs(result - 1.20) < 0.1, f"PIR {result:.3f} vs 교재 1.20"


def test_pir_zero_investment_raises():
    """투자 NPV=0이면 ZeroDivisionError."""
    revenues = [100, 100]
    investments = [0, 0]
    with pytest.raises(ZeroDivisionError):
        pir(revenues, investments, 0.10)


def test_pbp_never_recovers():
    """음수만 있는 cashflow → None."""
    cf = [-100, -50, -30]
    assert pbp(cf) is None


def test_pbp_recovers_at_t0():
    """첫 시점에 이미 양수 cashflow → 0."""
    cf = [100, 50]
    assert pbp(cf) == 0


def test_pbp_recovers_mid_project():
    """-100, 30, 30, 30, 30 → t=4 누적=20 → 회수기간 4."""
    cf = [-100, 30, 30, 30, 30]
    # 누적: -100, -70, -40, -10, 20
    assert pbp(cf) == 4


def test_pbp_textbook_case_B():
    """교재 표 7.4 사업 B → PBP 3년.

    cashflow 배열은 그림 7.9(b)에서 사용자가 직접 확인 (2026-05-20).
    누적: -500, -250, -50, 100, 200, 300, 240 → PBP = 3
    """
    cf = [-500, 250, 200, 150, 100, 100, -60]
    result = pbp(cf)
    assert result == 3, f"PBP {result} vs 교재 3년"


def test_evaluate_eor_returns_all_metrics():
    """한 기법에 대해 NPV/IRR/PIR/PBP + cashflow + 메타 반환."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 1000}
    economic = {**DEFAULT_ECONOMIC}
    result = evaluate_eor("CO2_Miscible", reservoir, economic)

    assert result["technique"] == "CO2_Miscible"
    assert result["incremental_recovery_pct"] == 22  # Taber Table 8
    assert isinstance(result["npv_million_usd"], float)
    # IRR may be None (실패 시); float 또는 None
    assert isinstance(result["irr_pct"], (float, type(None)))
    # PIR may be None
    assert isinstance(result["pir"], (float, type(None)))
    assert isinstance(result["pbp_years"], (int, type(None)))
    assert isinstance(result["cashflow_yearly_million_usd"], list)


def test_evaluate_eor_includes_source_assumptions():
    """결과에 출처 메타 포함."""
    reservoir = {**DEFAULT_RESERVOIR}
    economic = {**DEFAULT_ECONOMIC}
    result = evaluate_eor("CO2_Miscible", reservoir, economic)
    assert "assumptions" in result
    assert "Taber Table 8" in result["assumptions"]["recovery_rate_source"]
    assert "NETL" in result["assumptions"]["cost_source"]


def test_evaluate_eor_incremental_bbl_consistent():
    """incremental_bbl_million = OOIP × recovery_pct / 100."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 1000}
    economic = {**DEFAULT_ECONOMIC}
    result = evaluate_eor("CO2_Miscible", reservoir, economic)
    # 1000 × 22% = 220
    assert abs(result["incremental_bbl_million"] - 220) < 0.1


def test_evaluate_eor_different_techniques_different_results():
    """다른 기법 → 다른 회수율 → 다른 NPV."""
    reservoir = {**DEFAULT_RESERVOIR, "ooip_million_bbl": 1000}
    economic = {**DEFAULT_ECONOMIC}
    r1 = evaluate_eor("CO2_Miscible", reservoir, economic)  # 22%
    r2 = evaluate_eor("CO2_Immiscible", reservoir, economic)  # 10%
    assert r1["npv_million_usd"] != r2["npv_million_usd"]
    assert r1["incremental_recovery_pct"] > r2["incremental_recovery_pct"]


# 교재 표 7.4 — 4개 사업의 정답값 (그림 7.9의 cashflow는 placeholder)
# 실제 cashflow 배열은 교재 그림 7.9를 직접 보고 확인해야 함
TEXTBOOK_PROJECTS_ANSWERS = {
    "A": {"npv": -10.9, "pir": 0.98, "irr_pct": 9.44, "pbp": 5, "year6_cumulative": 240},
    "B": {"npv": 101.8, "pir": 1.20, "irr_pct": 20.28, "pbp": 3, "year6_cumulative": 240},
    "C": {"npv": 55.1, "pir": 1.11, "irr_pct": 14.04, "pbp": 4, "year6_cumulative": 240},
    "D": {"npv": -3.2, "pir": 0.99, "irr_pct": 9.83, "pbp": 5, "year6_cumulative": 240},
}


def test_npv_math_correctness_simple():
    """검증된 수치로 NPV 함수 정확성 확인 — 텍스트북 없이.

    -1000 + 1000/(1.10) = -1000 + 909.09 = -90.91
    """
    cf = [-1000, 1000]
    result = npv(cf, 0.10)
    expected = -1000 + 1000 / 1.10
    assert abs(result - expected) < 0.01


def test_npv_math_correctness_multi_year():
    """검증된 수치 — 100씩 5년 무할인 + 10% 할인."""
    cf = [-300, 100, 100, 100, 100]
    # NPV @ 0% = 100
    assert abs(npv(cf, 0.0) - 100) < 0.01
    # NPV @ 10% = -300 + 100*(1/1.1 + 1/1.21 + 1/1.331 + 1/1.4641)
    expected = -300 + 100 * (1/1.1 + 1/1.21 + 1/1.331 + 1/1.4641)
    assert abs(npv(cf, 0.10) - expected) < 0.01


def test_irr_math_correctness():
    """검증: -100 + 110 at 10% IRR → NPV=0."""
    cf = [-100, 110]
    result = irr(cf)
    assert result is not None
    assert abs(result - 0.10) < 0.001


def test_textbook_answers_loaded():
    """교재 표 7.4 정답값이 dict로 보존됨 (향후 cashflow 확인 후 사용)."""
    assert TEXTBOOK_PROJECTS_ANSWERS["B"]["npv"] == 101.8
    assert TEXTBOOK_PROJECTS_ANSWERS["B"]["irr_pct"] == 20.28
    assert TEXTBOOK_PROJECTS_ANSWERS["B"]["pbp"] == 3
    assert all(p["year6_cumulative"] == 240 for p in TEXTBOOK_PROJECTS_ANSWERS.values())
