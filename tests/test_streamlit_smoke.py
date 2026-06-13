"""Streamlit UI smoke test — golden path 자동 검증.

streamlit.testing.v1.AppTest로 앱 렌더 + 계산 버튼 동작을 헤드리스로 확인.
"""

from pathlib import Path
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parents[1] / "streamlit_app.py")


def test_app_renders_without_exception():
    """초기 로드 시 예외 없이 렌더."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception


def test_app_calc_button_produces_results():
    """[⚙️ 계산] 클릭 → screening + economics 표가 표시되고 예외 없음."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    calc_buttons = [b for b in at.button if "계산" in b.label]
    assert calc_buttons, "계산 버튼을 찾지 못함"
    calc_buttons[0].click().run()
    assert not at.exception
    # screening + economics + recovery 표 (>=2개 dataframe)
    assert len(at.dataframe) >= 2


def test_app_textbook_b_preset_loads():
    """교재 사업 B 검증 프리셋 버튼 클릭 시 예외 없음."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    preset_buttons = [b for b in at.button if "사업 B" in b.label]
    assert preset_buttons, "사업 B 프리셋 버튼을 찾지 못함"
    preset_buttons[0].click().run()
    assert not at.exception
