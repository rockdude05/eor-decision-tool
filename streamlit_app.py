"""Streamlit UI — EOR 의사결정 도구.

실행: streamlit run streamlit_app.py
"""

import streamlit as st
from constants import DEFAULT_RESERVOIR, DEFAULT_ECONOMIC
from presets import PRESET_TEXTBOOK_B

st.set_page_config(
    page_title="EOR 의사결정 도구",
    layout="wide",
)

st.title("EOR 기법 선정과 경제성 평가 통합 의사결정 도구")
st.caption("Taber Tables 1-7 스크리닝 + 교재 7장 식 7.3-7.6 (유가 WTI 2026 $105.66 / 비용 NETL Primer 2010 p.13)")


def _load_preset(preset_data: dict, preset_name: str):
    """프리셋 데이터를 session_state에 로드."""
    st.session_state["preset"] = preset_name

    # reservoir 입력값 적용 (None이면 건너뜀 — 사업 B 케이스)
    if preset_data.get("reservoir"):
        for key, val in preset_data["reservoir"].items():
            st.session_state[f"input_{key}"] = val

    # economic 입력값 적용 (None 값은 건너뜀)
    if preset_data.get("economic"):
        for key, val in preset_data["economic"].items():
            if val is not None:
                st.session_state[f"input_{key}"] = val


# session_state 초기화 (첫 로드 시)
for key, val in DEFAULT_RESERVOIR.items():
    st.session_state.setdefault(f"input_{key}", val)
for key, val in DEFAULT_ECONOMIC.items():
    st.session_state.setdefault(f"input_{key}", val)
st.session_state.setdefault("input_co2_recovery_pct", 22.0)
st.session_state.setdefault("preset", "default")


# 사이드바
with st.sidebar:
    st.header("🎬 검증 프리셋")
    st.caption("교재 사업 B로 도구의 NPV/IRR/PIR/PBP 계산 정확성을 확인")
    if st.button("교재 사업 B 검증", width='stretch', help="교재 그림 7.9 사업 B → NPV $101.8M 재현"):
        _load_preset(PRESET_TEXTBOOK_B, "textbook_b")
        st.rerun()

    # 현재 프리셋 표시
    if st.session_state["preset"] != "default":
        st.caption(f"현재 프리셋: **{st.session_state['preset']}**")

    st.divider()

    st.header("📥 입력")

    st.subheader("저류층 물성")
    st.number_input(
        "API gravity (°)",
        min_value=5.0, max_value=60.0,
        step=1.0,
        key="input_api_gravity_deg",
        help="Taber Table 3: CO2-Miscible은 API ≥22°",
    )
    st.number_input(
        "Viscosity (cp)",
        min_value=0.1, max_value=100000.0,
        key="input_viscosity_cp",
        help="Taber Table 3: CO2-Miscible은 점도 ≤10 cp",
    )
    st.number_input(
        "Depth (ft)",
        min_value=100, max_value=20000,
        step=100,
        key="input_depth_ft",
    )
    st.number_input(
        "Permeability (md)",
        min_value=0.1, max_value=15000.0,
        key="input_permeability_md",
    )
    st.number_input(
        "Temperature (°F)",
        min_value=60, max_value=400,
        key="input_temperature_f",
    )
    st.number_input(
        "Oil saturation (%)",
        min_value=10.0, max_value=100.0,
        key="input_oil_saturation_pct",
    )
    st.number_input(
        "OOIP (million bbl)",
        min_value=1, max_value=50000,
        step=100,
        key="input_ooip_million_bbl",
    )

    st.subheader("경제 변수 (제출본 § 3-(3))")
    st.number_input(
        "Oil price ($/bbl)",
        min_value=10.0, max_value=300.0,
        key="input_oil_price_usd_per_bbl",
        help="기준 유가 WTI 2026-05-15 $105.66 (tradingeconomics). 민감도 분석에서 $60-120 변동.",
    )
    st.number_input(
        "Discount rate (%)",
        min_value=0.0, max_value=50.0,
        key="input_discount_rate_pct",
        help="교재 표 7.2 탐사단계 15%",
    )
    st.number_input(
        "Project years",
        min_value=1, max_value=50,
        key="input_project_years",
    )
    st.number_input(
        "CAPEX (million $)",
        min_value=0, max_value=10000,
        key="input_capex_million_usd",
    )
    st.number_input(
        "CO2 cost ($/bbl)",
        min_value=0.0, max_value=100.0,
        key="input_co2_cost_usd_per_bbl",
        help="NETL: $2/Mcf 구입 + $0.70/Mcf 재활용",
    )
    st.number_input(
        "O&M ($/bbl)",
        min_value=0.0, max_value=100.0,
        key="input_opex_usd_per_bbl",
    )

    st.subheader("회수율 민감도 (제출본 § 3-(2))")
    st.slider(
        "CO2 미시블 회수율 (% OOIP)",
        min_value=4.0, max_value=22.0, step=0.5,
        key="input_co2_recovery_pct",
        help="NETL Primer 2010 field 범위 4-15% ~ Taber Table 8 미시블 22%(절반 프로젝트).",
    )

# 메인 영역에 계산 버튼 + 결과
def get_inputs():
    """session_state에서 입력값 추출."""
    reservoir = {
        "api_gravity_deg": st.session_state["input_api_gravity_deg"],
        "viscosity_cp": st.session_state["input_viscosity_cp"],
        "depth_ft": st.session_state["input_depth_ft"],
        "permeability_md": st.session_state["input_permeability_md"],
        "temperature_f": st.session_state["input_temperature_f"],
        "oil_saturation_pct": st.session_state["input_oil_saturation_pct"],
        "ooip_million_bbl": st.session_state["input_ooip_million_bbl"],
    }
    economic = {
        "oil_price_usd_per_bbl": st.session_state["input_oil_price_usd_per_bbl"],
        "discount_rate_pct": st.session_state["input_discount_rate_pct"],
        "project_years": st.session_state["input_project_years"],
        "capex_million_usd": st.session_state["input_capex_million_usd"],
        "co2_cost_usd_per_bbl": st.session_state["input_co2_cost_usd_per_bbl"],
        "opex_usd_per_bbl": st.session_state["input_opex_usd_per_bbl"],
    }
    return reservoir, economic


if st.button("⚙️ 계산", type="primary", width='stretch'):
    reservoir, economic = get_inputs()

    # Screening
    from screening import screen_eor
    screening_results = screen_eor(reservoir)

    st.subheader("🔍 Screening 결과 (Taber Tables 1-7)")
    import pandas as pd
    df_screen = pd.DataFrame([
        {
            "기법": r["technique"],
            "통과": "✅" if r["passed"] else "❌",
            "탈락 사유": ", ".join(r["fail_reasons"]) if r["fail_reasons"] else "—",
            "출처": r["source"],
        }
        for r in screening_results
    ])
    st.dataframe(df_screen, width='stretch', hide_index=True)

    # Economics for passed
    passed = [r["technique"] for r in screening_results if r["passed"]]
    if not passed:
        st.error("⚠️ 통과한 기법 없음. 입력값을 재검토하세요.")
        st.stop()

    from economics import evaluate_eor
    co2_recovery = st.session_state.get("input_co2_recovery_pct", 22.0)
    economics_list = [
        evaluate_eor(
            t, reservoir, economic,
            recovery_pct=co2_recovery if t == "CO2_Miscible" else None,
        )
        for t in passed
    ]

    st.subheader("💰 경제성 비교 (NPV/IRR/PIR/PBP)")
    df_econ = pd.DataFrame([
        {
            "기법": e["technique"],
            "회수율 (%)": e["incremental_recovery_pct"],
            "증분 (Mbbl)": e["incremental_bbl_million"],
            "NPV ($M)": e["npv_million_usd"],
            "IRR (%)": e["irr_pct"] if e["irr_pct"] is not None else "N/A",
            "PIR": e["pir"] if e["pir"] is not None else "N/A",
            "PBP (년)": e["pbp_years"] if e["pbp_years"] is not None else "N/A",
        }
        for e in economics_list
    ])
    st.dataframe(df_econ, width='stretch', hide_index=True)

    # 회수율 근거 (제출본 § 3-(2))
    from constants import RECOVERY_FACTOR_STATS, ALADASSANI_BAI_NOTE
    with st.expander("📈 회수율 근거 (제출본 § 3-(2): Taber 1997 + NETL + Aladassani-Bai 652 사례)"):
        df_rec = pd.DataFrame([
            {
                "기법": t,
                "적용 회수율 (% OOIP)": next(
                    (e["incremental_recovery_pct"] for e in economics_list if e["technique"] == t), "—"
                ),
                "조절 범위 (%)": f"{RECOVERY_FACTOR_STATS[t]['slider_range_pct'][0]}–{RECOVERY_FACTOR_STATS[t]['slider_range_pct'][1]}",
                "출처": RECOVERY_FACTOR_STATS[t]["source"],
            }
            for t in passed
        ])
        st.dataframe(df_rec, width='stretch', hide_index=True)
        st.caption(ALADASSANI_BAI_NOTE)

    # 추천
    from recommendation import build_recommendation
    for e in economics_list:
        e["passed"] = True
    rec = build_recommendation(reservoir, economic, screening_results, economics_list)

    st.subheader("🏆 추천")
    if rec["primary"]:
        st.success(f"**1순위: {rec['primary']}** — {rec['rationale_short']}")
        st.caption(f"전체 순위: {' → '.join(rec['ranking'])}")
    else:
        st.warning(rec["rationale_short"])

    # 배럴당 마진 분석 (제출본 § 3-(3))
    st.subheader("💵 배럴당 마진 분석 (제출본 § 3-(3))")
    from economics import margin_per_bbl
    m = margin_per_bbl(economic)
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("배럴당 마진", f"${m['margin_per_bbl']:.2f}", f"{m['margin_pct']:.1f}%")
    mc2.metric("총 비용/bbl", f"${m['total_cost_per_bbl']:.2f}",
               help=f"CO2 ${m['co2_cost']} + OPEX ${m['opex']} + CAPEX ${m['capex_per_bbl']}/bbl (NETL Primer 2010 p.13)")
    co2_ok = "✅ 25-50% 범위" if 25 <= m["co2_cost_ratio_pct"] <= 50 else "⚠️ 범위 밖"
    mc3.metric("CO2 비용 비율", f"{m['co2_cost_ratio_pct']:.1f}%", co2_ok)
    st.caption(
        f"유가 ${m['oil_price']}/bbl − 총비용 ${m['total_cost_per_bbl']}/bbl "
        f"= 마진 ${m['margin_per_bbl']:.2f}/bbl. "
        "CAPEX는 배럴당 환산 $7.5 (NETL $5-10 중앙값); 사업 NPV의 CAPEX 총액은 별도 입력."
    )

    # Sensitivity 민감도 차트
    st.subheader("📊 유가 민감도")
    st.caption("⚠️ 유가만 변동, 비용 항목(CO2/OPEX/CAPEX)은 NETL Primer 2010 p.13 고정 (제출본 § 3-(3))")

    sensitivity = rec["sensitivity"]
    # _note 키 제외
    scenarios = {k: v for k, v in sensitivity.items() if k != "_note"}

    import plotly.graph_objects as go

    oil_prices = []
    npvs = []
    techniques = []
    labels = []
    for key, val in scenarios.items():
        # key 예: "oil_price_60_pessimistic" → 60
        try:
            price = int(key.split("_")[2])
        except (IndexError, ValueError):
            continue
        oil_prices.append(price)
        npvs.append(val["npv_million_usd"] if val["npv_million_usd"] is not None else 0)
        techniques.append(val["top_technique"] or "—")
        # 라벨에 시나리오 설명
        # 예: "oil_price_60_pessimistic" → "60 pessimistic"
        label_parts = key.replace("oil_price_", "").split("_", 1)
        labels.append(f"${price}<br>{label_parts[1] if len(label_parts) > 1 else ''}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=oil_prices,
        y=npvs,
        mode="lines+markers+text",
        text=labels,
        textposition="top center",
        marker=dict(size=12, color="#1f77b4"),
        line=dict(width=3),
        hovertemplate="유가: $%{x}/bbl<br>NPV: $%{y:.1f}M<extra></extra>",
    ))
    fig.update_layout(
        xaxis_title="유가 ($/bbl)",
        yaxis_title="NPV ($M)",
        title=f"민감도: {rec['primary']} (최우수 기법)",
        height=450,
        showlegend=False,
    )
    st.plotly_chart(fig, width='stretch')

    st.caption(
        "참고: $105 = 2026-05-15 WTI 기준 유가(제출본 § 3-(3)), $60 = 비관 시나리오, "
        "$120 = 공급충격. 비용 항목은 전 시나리오 NETL Primer 2010 p.13 고정."
    )

    # JSON Export
    st.subheader("📥 JSON Export")

    from export import build_export_dict
    import json
    from datetime import datetime

    scenario_name = st.session_state.get("preset", "custom")

    export_data = build_export_dict(
        reservoir,
        economic,
        scenario_name=scenario_name,
    )

    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)

    filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M')}_{scenario_name}.json"

    col_export, col_preview = st.columns([1, 2])

    with col_export:
        st.download_button(
            label="📥 JSON 다운로드",
            data=json_str,
            file_name=filename,
            mime="application/json",
            width='stretch',
        )

    with col_preview:
        with st.expander("📋 Claude Code 명령어 미리보기"):
            st.markdown("**다운로드한 JSON을 `prototype/results/`에 저장 후:**")
            st.code(
                f"cd ~/Desktop/Claude/Projects/petroleum-eor-team-project/prototype\n"
                f"cat results/{filename} | claude \"$(cat prompts/report_prompt_ko.md)\" > results/report_{datetime.now().strftime('%Y%m%d_%H%M')}.md\n"
                f"./scripts/md_to_pdf.sh results/report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                language="bash",
            )
            st.caption("위 명령어는 Claude Code 터미널에서 실행. PDF는 약 5초 내 자동 생성됨.")

    # JSON 일부 미리보기 (디버깅)
    with st.expander("🔍 JSON 미리보기 (디버깅)"):
        st.json(export_data)

    # state 저장 (sensitivity / export에서 재사용 — Tasks 24, 25)
    st.session_state["last_results"] = {
        "reservoir": reservoir,
        "economic": economic,
        "screening": screening_results,
        "economics": economics_list,
        "recommendation": rec,
    }
else:
    st.info("좌측 사이드바에서 프리셋을 선택하거나 직접 입력 후 [⚙️ 계산] 버튼을 누르세요.")
