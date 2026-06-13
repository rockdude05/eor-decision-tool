"""교재 표 7.4 검증 — 도구 신뢰성 입증.

사업 B는 그림 7.9(b) cashflow를 직접 확인(2026-05-20)했으므로 NPV/IRR/PIR/PBP
4지표를 함수로 ±0.1 이내 재현한다.

사업 A/C/D는 그림 7.9에 그래프로만 제시되어 연도별 cashflow를 디지타이즈하지
못했으므로 (수치 날조 금지) 표 7.4 목표 지표값만 TEXTBOOK_PROJECTS_ANSWERS에
기록해 두고, 함수 재현 검증은 cashflow를 확보한 사업 B에 한정한다.
"""

from economics import npv, irr, pir, pbp
from presets import PRESET_TEXTBOOK_B, TEXTBOOK_PROJECTS_ANSWERS

# 사업 B 그림 7.9(b) cashflow (직접 확인)
CF_B = [-500, 250, 200, 150, 100, 100, -60]
INV_B = [500, 0, 0, 0, 0, 0, 60]
REV_B = [0, 250, 200, 150, 100, 100, 0]
RATE = 0.10  # 표 7.4 할인율


def test_case_b_npv_within_0_1():
    assert abs(npv(CF_B, RATE) - 101.8) < 0.1


def test_case_b_irr_within_0_1():
    assert abs(irr(CF_B) * 100 - 20.28) < 0.1


def test_case_b_pir_within_0_1():
    assert abs(pir(REV_B, INV_B, RATE) - 1.20) < 0.1


def test_case_b_pbp_exact():
    assert pbp(CF_B) == 3


def test_case_b_all_four_metrics_match_preset():
    """PRESET_TEXTBOOK_B의 expected_* 값과 함수 재현이 일치 (4지표)."""
    assert abs(npv(CF_B, RATE) - PRESET_TEXTBOOK_B["expected_npv_million_usd"]) < 0.1
    assert abs(irr(CF_B) * 100 - PRESET_TEXTBOOK_B["expected_irr_pct"]) < 0.1
    assert abs(pir(REV_B, INV_B, RATE) - PRESET_TEXTBOOK_B["expected_pir"]) < 0.1
    assert pbp(CF_B) == PRESET_TEXTBOOK_B["expected_pbp_years"]


def test_acd_target_metrics_documented():
    """사업 A/C/D 표 7.4 목표값이 기록됨 (cashflow 미디지타이즈, 목표값만 보존)."""
    for case in ("A", "C", "D"):
        ans = TEXTBOOK_PROJECTS_ANSWERS[case]
        assert "npv" in ans and "irr_pct" in ans and "pir" in ans and "pbp" in ans
    # 4개 사업 모두 명목 6년차 누적 $240M로 동일 (교재 그림 7.9 전제)
    assert all(p["year6_cumulative"] == 240 for p in TEXTBOOK_PROJECTS_ANSWERS.values())
