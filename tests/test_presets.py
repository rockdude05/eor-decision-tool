"""presets.py 단위 테스트 (검증용 사업 B + 표 7.4 정답값)."""

from presets import PRESET_TEXTBOOK_B, TEXTBOOK_PROJECTS_ANSWERS


def test_textbook_b_has_known_npv():
    """사업 B 프리셋 reservoir + economic은 NPV $101.8M을 만들어야 함."""
    assert PRESET_TEXTBOOK_B["scenario_name"] == "교재 사업 B 검증"
    assert PRESET_TEXTBOOK_B["economic"]["discount_rate_pct"] == 10
    # cashflow가 직접 정의되어 있음 — economics 모듈 우회
    assert "cashflow" in PRESET_TEXTBOOK_B
    assert PRESET_TEXTBOOK_B["expected_npv_million_usd"] == 101.8


def test_textbook_b_expected_metrics():
    """교재 표 7.4 사업 B 정답값."""
    assert PRESET_TEXTBOOK_B["expected_irr_pct"] == 20.28
    assert PRESET_TEXTBOOK_B["expected_pir"] == 1.20
    assert PRESET_TEXTBOOK_B["expected_pbp_years"] == 3


def test_textbook_b_has_source():
    """출처 명시."""
    assert "교재" in PRESET_TEXTBOOK_B["source"]
    assert "7.9" in PRESET_TEXTBOOK_B["source"] or "7.4" in PRESET_TEXTBOOK_B["source"]


def test_textbook_answers_table_7_4():
    """교재 표 7.4 사업 A/B/C/D 정답값이 보존됨 (검증 기준)."""
    assert TEXTBOOK_PROJECTS_ANSWERS["A"]["npv"] == -10.9
    assert TEXTBOOK_PROJECTS_ANSWERS["B"]["npv"] == 101.8
    assert TEXTBOOK_PROJECTS_ANSWERS["B"]["irr_pct"] == 20.28
    assert TEXTBOOK_PROJECTS_ANSWERS["C"]["npv"] == 55.1
    assert TEXTBOOK_PROJECTS_ANSWERS["D"]["npv"] == -3.2
    # 4개 사업 모두 명목상 6년차 누적 $240M로 동일
    assert all(p["year6_cumulative"] == 240 for p in TEXTBOOK_PROJECTS_ANSWERS.values())
