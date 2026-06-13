다음 JSON 결과(도구 v0.2, schema 1.1)를 분석하여 한국어 의사결정 보고서를 작성해줘.

이 보고서는 팀 프로젝트 "EOR 기법 선정과 경제성 평가의 통합 의사결정"의 산출물이며,
**제출본의 4단계 방법 + 4개 세부 검토 항목**만 다룬다.

[보고서 구조 — 8개 섹션]

1. **경영 요약** (3줄): 추천 기법 + NPV/IRR + 핵심 근거 한 줄.

2. **입력 시나리오**: 저류층 물성(API/점성도/깊이/온도/투과율/유포화/OOIP) + 경제 변수.
   - 기준 유가는 `cost_methodology` 필드 그대로 명시: "WTI 2026-05-15 $105.66/bbl (tradingeconomics),
     비용 항목(CO2/OPEX/CAPEX)은 NETL Primer 2010 p.13, 할인율 15%는 교재 표 7.2 탐사단계(위험 프리미엄 9.5% 포함)".

3. **공학적 스크리닝 (제출본 § 3-(1))**: `screening.results` 기반 통과/탈락 + 이유.
   - 출처: Taber, Martin & Seright (1997, SPE 35385)의 **7개 적용범위표(Tables 1-7)**.
   - 표는 7개이나 CO2가 미시블/비미시블 두 영역으로 나뉘어 **총 8개 후보 기법**을 스크리닝함을 한 문장으로 명시.

4. **회수율 분석 (제출본 § 3-(2))**: `recovery_basis` 기반.
   - 글로벌 통계: 전세계 **652개 실증 사례 (Aladassani & Bai 2010, SPE 130726)**가 경험적 근거.
   - CO2 EOR 효율: NETL 자료 기반 **OOIP 4~15% 추가 회수** + Taber Table 8 미시블 22%(절반의 프로젝트).
   - `recovery_basis.empirical_note`의 한계(기법별 중앙값은 원문 미입수)를 그대로 반영.

5. **비용 구조 및 마진 (제출본 § 3-(3))**: `margin_analysis` 기반.
   - 단위 비용(NETL Primer 2010 p.13): CO2 $15/bbl, OPEX $10-15/bbl, CAPEX $5-10/bbl.
   - 배럴당 마진 = 유가 − 총비용 (도구 자동 계산값).
   - **"CO2 비용이 전체 배럴당 비용의 25~50%를 차지"** — `margin_analysis.co2_cost_ratio_pct`로 확인.

6. **경제성 평가 (제출본 § 3-(4))**: `economics.by_technique`의 NPV/IRR/PIR/PBP 표(통과 기법 전체).
   - 수식 출처: 교재 식 (7.4) NPV, (7.5) IRR, (7.6) PIR, 7.2.6 PBP. 할인율 15%.
   - 생산 프로파일은 6장 Arps 감퇴(식 6.6/6.9) + CO2 fill-up 지연 + CAPEX 0~2년 분산을 반영했음을 명시
     (= 6장 EOR 기법과 7장 경제성의 통합).
   - 도구 신뢰성: 교재 표 7.4 사업 B(NPV 101.8/IRR 20.28%/PIR 1.20/PBP 3)를 ±0.1로 재현함을 1줄 명시.

7. **민감도 분석**: `recommendation.sensitivity` 6개 유가 시나리오($60~$120).
   - 명시: "유가만 변동, 비용 항목(CO2/OPEX/CAPEX)은 NETL Primer 2010 p.13 고정".
   - 회수율 가정(4-15% vs 22%)이 경제성을 가르는 핵심 변수임을 언급(해당 데이터가 있으면).

8. **한계 및 향후 검토**:
   - 회수율 기법별 중앙값 미입수(Aladassani-Bai 원문 표), CAPEX 총액은 사업규모에 따라 별도 산정 필요.
   - 허수/복수 IRR 가능성(교재 식 7.5 한계).
   - 비용 항목은 2010 NETL 기준이라 2026 인플레이션 미반영.

[작성 원칙]
- 모든 수치에 출처 표기. **인용 출처는 정확히 5개만**: Taber 1997(SPE 35385) / Aladassani & Bai 2010(SPE 130726) /
  NETL Primer 2010 / tradingeconomics WTI 2026-05-15 / 본 강의 교재(6·7장).
- 도구가 계산한 값은 "도구 계산값"으로 명시. JSON 안의 수치만 사용, 외삽·가정 금지.
- **금지**: 영일만 / 동해 CCS / Weyburn / 한국 맥락 / 위 5개 외 출처 추가.
- 한국어 학술 톤(반말·과장 금지). 분량 A4 2~3페이지.

[YAML metadata block을 markdown 맨 위에 포함]
---
title: "EOR 기법 선정과 경제성 평가의 통합 의사결정 — 분석 보고서"
author: "도구 v0.2 (자동 생성)"
date: "<generated_at>"
---

출력: Markdown 형식 (이후 pandoc + xelatex로 PDF 변환)
