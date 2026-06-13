"""검증용 프리셋 + 교재 표 7.4 정답값.

제출본 frame: 도구는 "사용자가 임의 저류층 물성을 입력"하는 워크플로우.
프리셋은 도구의 정확성을 입증하는 검증 케이스(교재 사업 B)만 둔다.
영일만/Weyburn/한국 맥락 시나리오는 제출본 scope 밖이므로 제거됨
(2026-06-13, 핸드오프 §2.2 scope creep 제거).
"""


# 교재 그림 7.9 사업 B → NPV $101.8M 정확 재현 (도구 검증용)
PRESET_TEXTBOOK_B = {
    "scenario_name": "교재 사업 B 검증",
    "description": "교재 그림 7.9 사업 B → NPV $101.8M 정확 재현 (도구 신뢰성 입증)",
    "reservoir": None,  # 사업 B는 reservoir-agnostic, cashflow 직접 입력
    "economic": {
        "discount_rate_pct": 10,  # 교재 표 7.4 (할인율 10% 기준)
        "oil_price_usd_per_bbl": None,
        "project_years": 6,
    },
    "cashflow": [-500, 250, 200, 150, 100, 100, -60],  # 교재 그림 7.9(b) 사업 B 직접 확인 (2026-05-20)
    "expected_npv_million_usd": 101.8,
    "expected_irr_pct": 20.28,
    "expected_pir": 1.20,
    "expected_pbp_years": 3,
    "source": "교재 표 7.4, 그림 7.9 사업 B",
}

# 교재 표 7.4 — 4개 사업의 경제성 분석결과 정답값 (할인율 10%).
# 도구의 npv/irr/pir/pbp 함수가 이 값을 ±0.1 이내로 재현하는지 검증한다.
# (사업 A/C/D는 그림 7.9의 cashflow 배열이 교재에 그래프로만 제시되어
#  현재 사업 B만 cashflow를 직접 확인함. A/C/D는 정답 지표값을 기록만 해 둠.)
# 출처: 교재 표 7.4, _소스캐시_7장.md line 392-398.
TEXTBOOK_PROJECTS_ANSWERS = {
    "A": {"npv": -10.9, "pir": 0.98, "irr_pct": 9.44, "pbp": 5, "year6_cumulative": 240},
    "B": {"npv": 101.8, "pir": 1.20, "irr_pct": 20.28, "pbp": 3, "year6_cumulative": 240},
    "C": {"npv": 55.1, "pir": 1.11, "irr_pct": 14.04, "pbp": 4, "year6_cumulative": 240},
    "D": {"npv": -3.2, "pir": 0.99, "irr_pct": 9.83, "pbp": 5, "year6_cumulative": 240},
}
