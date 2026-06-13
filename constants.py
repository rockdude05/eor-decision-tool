"""Default values + recovery factors + 출처 메타.

모든 magic number는 이 파일에만 정의. 다른 모듈은 import.
근거 (제출본 § 3-(3)): 유가는 2026 현재 시장가(WTI 2026-05-15 $105.66),
비용 항목(CO2/OPEX/CAPEX)은 NETL Primer 2010 p.13.
"""

# 저류층 default — 보고서·슬라이드 대표 케이스(깊은 경질유)와 동일하게 맞춤.
# OOIP 100 (이전 1000은 CAPEX $500M 대비 과대 → IRR 비현실적으로 큼).
DEFAULT_RESERVOIR = {
    "api_gravity_deg": 35,
    "viscosity_cp": 5.0,
    "depth_ft": 8200,
    "permeability_md": 50.0,
    "temperature_f": 150,
    "oil_saturation_pct": 60,
    "ooip_million_bbl": 100,
}

# 경제 default — 제출본 § 3-(3) 명시값
DEFAULT_ECONOMIC = {
    "oil_price_usd_per_bbl": 105.66,   # WTI 2026-05-15 (tradingeconomics)
    "oil_price_source": "WTI 2026-05-15 (tradingeconomics)",
    "discount_rate_pct": 15,           # 교재 표 7.2 탐사단계 (위험 프리미엄 9.5% 포함)
    "project_years": 20,
    "capex_million_usd": 500,
    "opex_usd_per_bbl": 12,            # NETL Primer 2010 p.13 ($10-15 중앙값)
    "co2_cost_usd_per_bbl": 15,        # NETL Primer 2010 p.13 ($2/Mcf 구입 + 재활용)
}

# 회수율 증분 % OOIP
RECOVERY_FACTOR = {
    "CO2_Miscible": 22,        # Taber Table 8
    "CO2_Immiscible": 10,      # Taber Table 8
    "Polymer": 11,             # Taber Table 5 median
    "Steamflood": 15,
    "HC_Miscible": 18,
    "ASP_Micellar": 12,
    "In_Situ_Combustion": 8,
    "N2_Flue_Gas": 15,
}

# 제출본 § 3-(2): 회수율 범위 + 출처.
# default_pct = 위 RECOVERY_FACTOR 점추정값(경제성 기본 계산에 사용, 모두 Taber 검증값).
# slider_range_pct = UI 민감도 조절 범위 (점추정 ± 보수적 폭; 경험적 분포 주장 아님).
# CO2 미시블만 NETL field 범위(4-15%)와 Taber Table 8(22%)을 함께 명시.
RECOVERY_FACTOR_STATS = {
    "CO2_Miscible": {
        "default_pct": 22,
        "netl_field_range_pct": (4, 15),   # NETL Primer 2010 (보수적 field 범위)
        "taber_table8_pct": 22,            # Taber Table 8 미시블 (절반의 프로젝트 달성)
        "slider_range_pct": (4, 22),
        "source": "Taber Table 8 미시블 22%(절반 프로젝트) + NETL Primer 2010 field 4-15%",
    },
    "CO2_Immiscible": {
        "default_pct": 10, "slider_range_pct": (2, 12),
        "source": "Taber Table 8 비미시블 10%",
    },
    "Polymer": {
        "default_pct": 11, "slider_range_pct": (5, 15),
        "source": "Taber Table 5 median",
    },
    "Steamflood": {
        "default_pct": 15, "slider_range_pct": (8, 25),
        "source": "Taber Table 7 (열공법/증기공법)",
    },
    "HC_Miscible": {
        "default_pct": 18, "slider_range_pct": (8, 22),
        "source": "Taber Table 2 (HC 미시블)",
    },
    "ASP_Micellar": {
        "default_pct": 12, "slider_range_pct": (5, 18),
        "source": "Taber Table 4 (Micellar/ASP)",
    },
    "In_Situ_Combustion": {
        "default_pct": 8, "slider_range_pct": (3, 12),
        "source": "Taber Table 6 (연소법)",
    },
    "N2_Flue_Gas": {
        "default_pct": 15, "slider_range_pct": (5, 18),
        "source": "Taber Table 1 (N2/연도가스)",
    },
}

# 제출본 § 3-(2): 글로벌 실증 통계의 경험적 근거 (메타 사실만 인용).
ALADASSANI_BAI_NOTE = (
    "전세계 652개 실제 EOR 적용 사례(Aladassani & Bai 2010, SPE 130726)가 "
    "EOR 회수율의 경험적 분포를 뒷받침한다. 본 도구는 기법별 점추정에 "
    "Taber 1997(SPE 35385)·NETL Primer 2010 검증값을 사용하며, 사용자가 "
    "슬라이더로 범위 내에서 회수율을 조정해 민감도를 볼 수 있다. "
    "(개별 기법별 회수율 중앙값은 Aladassani-Bai 원문 표 미입수로 직접 인용하지 않음.)"
)

# 제출본 § 3-(3): 유가/비용 출처 방법론 (JSON에 자동 포함)
COST_METHODOLOGY = (
    "유가: WTI 2026-05-15 (tradingeconomics) $105.66/bbl. "
    "비용 항목(CO2 $15 / OPEX $12 / CAPEX): NETL Primer 2010 p.13. "
    "할인율 15%: 교재 표 7.2 탐사단계 (위험 프리미엄 9.5% 포함). "
    "제출본 § 3-(3)·(4) 명시."
)

# sensitivity 유가 시나리오 (라벨 + 값). 기준 $105.66을 중심으로 bracket.
OIL_PRICE_SCENARIOS = {
    "oil_price_60_pessimistic": 60,
    "oil_price_70_low": 70,
    "oil_price_80_eia_4q26": 80,
    "oil_price_100_high": 100,
    "oil_price_105_current_market": 105,
    "oil_price_120_supply_shock": 120,
}
