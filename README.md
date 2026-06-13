# EOR 의사결정 도구

저류층 물성을 입력하면 **EOR 기법 스크리닝(공학적 적합성) + 경제성 평가(NPV/IRR/PIR/PBP)**를
한 번에 산출하는 Streamlit 도구. 석유가스공학 팀 프로젝트 "EOR 기법 선정과 경제성 평가의 통합
의사결정"(교재 6장 EOR 기법 + 7장 경제성)의 산출물.

기준: 유가 WTI 2026-05-15 **$105.66/bbl** (tradingeconomics), 비용 **NETL Primer 2010 p.13**,
할인율 **15%** (교재 표 7.2 탐사단계).

## 실행

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py        # → http://localhost:8501
```

## 사용 흐름

1. 사이드바에 저류층 물성(API·점성도·깊이·투과율·온도·유포화·OOIP) + 경제 변수 입력
   (또는 "교재 사업 B 검증" 프리셋으로 도구 정확성 확인)
2. **[⚙️ 계산]** → 스크리닝 표 · 경제성 표 · 회수율 근거 · 배럴당 마진 · 추천 · 유가 민감도 · JSON Export
3. 회수율 슬라이더(4–22%)로 민감도 확인

## 구성

| 파일 | 역할 |
|---|---|
| `streamlit_app.py` | UI 메인 (입력 → 스크리닝 → 경제성 → 추천) |
| `screening.py` | Taber Tables 1-7 스크리닝 (8 후보 기법) |
| `economics.py` | NPV/IRR/PIR/PBP + 6장 Arps 감퇴(식 6.6/6.9) + 배럴당 마진 |
| `recommendation.py` | NPV 순위 + 유가 민감도 |
| `constants.py` | default 값 + 회수율 범위·출처 |
| `export.py` | JSON Export (Claude Code 보고서 생성용) |
| `tests/` | pytest 113개 |

## 근거 출처 (5)

Taber·Martin·Seright 1997 (SPE 35385) · Aladassani & Bai 2010 (SPE 130726, 652개 실증사례) ·
NETL CO2-EOR Primer 2010 · tradingeconomics WTI 2026-05-15 · 본 강의 교재 6·7장.

## 검증

교재 그림 7.9 사업 B(NPV $101.8M / IRR 20.28% / PIR 1.20 / PBP 3년)를 함수로 ±0.1 이내 재현.

```bash
pytest tests/ -q     # 113 passed
```
