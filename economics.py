"""경제성 평가 함수 (교재 7장 식 7.3-7.6).

모든 함수는 cashflow list 또는 reservoir/economic dict를 받음.
결과는 float 또는 dict로 반환.
"""

import numpy as np
import numpy_financial as npf

from constants import RECOVERY_FACTOR


def npv(cashflows: list[float], rate: float) -> float:
    """순현재가치 (Net Present Value) — 교재 식 (7.4).

    Args:
        cashflows: 연도별 순현금흐름 ($, 첫 원소 = t=0)
        rate: 할인율 (decimal, 예: 0.10 = 10%)

    Returns:
        NPV ($).
    """
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))


def irr(cashflows: list[float]) -> float | None:
    """내부수익률 (Internal Rate of Return) — 교재 식 (7.5).

    NPV=0을 만드는 할인율.

    Args:
        cashflows: 연도별 순현금흐름.

    Returns:
        IRR (decimal, 예: 0.20 = 20%). 계산 불가 시 None.

    Note:
        교재 7.2.4 한계: 허수/복수 IRR 가능.
        numpy-financial은 단일 실수만 반환. NaN/예외는 None으로 변환.
    """
    try:
        result = npf.irr(cashflows)
        if result is None or np.isnan(result):
            return None
        return float(result)
    except (ValueError, FloatingPointError):
        return None


def pir(revenues: list[float], investments: list[float], rate: float) -> float:
    """수익성지수 (Profit to Investment Ratio) — 교재 식 (7.6).

    Args:
        revenues: 연도별 수입 (이미 양수).
        investments: 연도별 투자 (이미 양수).
        rate: 할인율 (decimal).

    Returns:
        PIR (>1 이면 채택 가능).

    Raises:
        ZeroDivisionError: 투자 NPV가 0인 경우.
    """
    rev_npv = npv(revenues, rate)
    inv_npv = npv(investments, rate)
    if inv_npv == 0:
        raise ZeroDivisionError("Investment NPV = 0; PIR undefined")
    return rev_npv / inv_npv


def pbp(cashflows: list[float]) -> int | None:
    """회수기간 (Payback Period) — 교재 7.2.6.

    누적 NCF가 0 이상이 되는 첫 시점 (년).

    Args:
        cashflows: 연도별 순현금흐름.

    Returns:
        회수기간 (년, 0-indexed). 회수 불가 시 None.
    """
    cum = np.cumsum(cashflows)
    for t, c in enumerate(cum):
        if c >= 0:
            return int(t)
    return None


def arps_exponential(Q_i: float, D: float, t):
    """지수 감퇴곡선 — 교재 식 (6.6): Q(t) = Q_i · e^(-Dt).

    Args:
        Q_i: 초기 생산량.
        D: 연간 감퇴율 (decimal, 예: 0.10 = 10%/year).
        t: 시간 (년, scalar 또는 np.ndarray).

    Returns:
        Q(t) (scalar t → float, array t → np.ndarray). 단위·감퇴율 시간단위는
        일관되게 사용 (6장 식 6.6 주의).
    """
    return Q_i * np.exp(-D * t)


def arps_hyperbolic(Q_i: float, D_i: float, b: float, t):
    """쌍곡선 감퇴곡선 — 교재 식 (6.9): Q(t) = Q_i · (1 + b·D_i·t)^(-1/b).

    b → 0 이면 식 (6.6) 지수 감퇴에 수렴, b = 1 이면 식 (6.11) 조화 감퇴.

    Args:
        Q_i: 초기 생산량.
        D_i: 초기 감퇴율 (decimal).
        b: 쌍곡선 지수 (전통적 유전 0~1).
        t: 시간 (년).

    Returns:
        Q(t).
    """
    return Q_i * (1.0 + b * D_i * t) ** (-1.0 / b)


def production_profile_arps(
    total_recoverable_bbl: float,
    project_years: int,
    decline_type: str = "exponential",
    D: float = 0.10,
    b: float = 0.5,
    ramp_years: int = 1,
) -> np.ndarray:
    """6장 Arps 감퇴 + CO2 fill-up 지연을 반영한 연간 생산 프로파일.

    - Year 0 ~ ramp_years-1: CO2 주입/fill-up 기간 → 증분 생산 0
      (NETL Primer 2010: CO2 주입 후 oil response까지 지연).
    - Year ramp_years ~ project_years: Arps 감퇴 (감퇴 시계 = year - ramp_years).
    - 총량을 total_recoverable_bbl로 normalize (질량 보존).

    Args:
        total_recoverable_bbl: 총 증분 회수량 (million bbl).
        project_years: 사업 기간 (년).
        decline_type: "exponential"(식 6.6) 또는 "hyperbolic"(식 6.9).
        D: (초기)감퇴율.
        b: 쌍곡선 지수 (hyperbolic일 때).
        ramp_years: fill-up 지연 (생산 0인 초기 연수).

    Returns:
        길이 (project_years + 1)의 배열 (year 0 ~ year N). 총합 ≈ total_recoverable_bbl.
    """
    profile = np.zeros(project_years + 1)
    for year in range(ramp_years, project_years + 1):
        decline_t = year - ramp_years
        if decline_type == "hyperbolic":
            profile[year] = arps_hyperbolic(1.0, D, b, decline_t)
        else:
            profile[year] = arps_exponential(1.0, D, decline_t)

    total = profile.sum()
    if total > 0:
        profile = profile / total * total_recoverable_bbl
    return profile


def build_cashflow(
    technique: str, reservoir: dict, economic: dict, recovery_pct: float | None = None
) -> list[float]:
    """입력 → 연도별 NCF 배열 ($ million), 6장 Arps + CAPEX 분산 반영.

    - 생산: production_profile_arps (Arps 감퇴, 0년차 fill-up 생산 0).
    - CAPEX: 0~2년 분산 (60/30/10, NETL Primer 2010 p.13 패턴).

    economic의 선택 키:
        decline_type ("exponential"/"hyperbolic"), decline_rate (D),
        hyperbolic_b (b), ramp_years.

    Args:
        technique: EOR 기법 이름 (RECOVERY_FACTOR key 중 하나).
        reservoir: ooip_million_bbl 등.
        economic: oil_price, capex, opex, co2_cost, project_years, ...
        recovery_pct: 회수율(% OOIP) override. None이면 RECOVERY_FACTOR 점추정 사용
            (제출본 § 3-(2) 민감도용, UI 슬라이더 연결).

    Returns:
        cashflow list (length = project_years + 1, year 0 ~ year N).
    """
    if technique not in RECOVERY_FACTOR:
        raise ValueError(f"Unknown technique: {technique}")

    years = economic["project_years"]
    rf = recovery_pct if recovery_pct is not None else RECOVERY_FACTOR[technique]
    total_inc_bbl = reservoir["ooip_million_bbl"] * rf / 100
    annual_prod = production_profile_arps(
        total_inc_bbl,
        years,
        decline_type=economic.get("decline_type", "exponential"),
        D=economic.get("decline_rate", 0.10),
        b=economic.get("hyperbolic_b", 0.5),
        ramp_years=economic.get("ramp_years", 1),
    )

    cf = np.zeros(years + 1)

    # CAPEX 0~2년 분산 (NETL Primer 2010 p.13 일반 패턴: 시추·인프라 → 설비 → 마무리)
    capex = economic["capex_million_usd"]
    capex_schedule = [0.60, 0.30, 0.10]
    for t, frac in enumerate(capex_schedule):
        if t <= years:
            cf[t] -= capex * frac

    # 수익 - 운영비 (배럴당 마진 × 생산량). CAPEX는 위에서 별도 분산 차감.
    unit_margin = economic["oil_price_usd_per_bbl"] - (
        economic["opex_usd_per_bbl"] + economic["co2_cost_usd_per_bbl"]
    )
    cf += annual_prod * unit_margin

    return cf.tolist()


def margin_per_bbl(economic: dict, capex_per_bbl: float = 7.5) -> dict:
    """배럴당 마진 + CO2 비용 비율 — 제출본 § 3-(3).

    § 3-(3) 단위 비용 (NETL Primer 2010 p.13): CO2 $15, OPEX $10-15, CAPEX $5-10/bbl.
    "CO2 비용이 전체 배럴당 비용의 25-50%를 차지" 검토 착안점 자동 계산.

    Args:
        economic: oil_price_usd_per_bbl, co2_cost_usd_per_bbl, opex_usd_per_bbl.
        capex_per_bbl: 배럴당 자본비 ($5-10 중앙값 7.5, NETL Primer 2010 p.13).

    Returns:
        oil_price / co2_cost / opex / capex_per_bbl / total_cost_per_bbl /
        margin_per_bbl / margin_pct / co2_cost_ratio_pct.
    """
    oil_price = economic["oil_price_usd_per_bbl"]
    co2 = economic["co2_cost_usd_per_bbl"]
    opex = economic["opex_usd_per_bbl"]
    total_cost = co2 + opex + capex_per_bbl
    margin = oil_price - total_cost
    return {
        "oil_price": oil_price,
        "co2_cost": co2,
        "opex": opex,
        "capex_per_bbl": capex_per_bbl,
        "total_cost_per_bbl": total_cost,
        "margin_per_bbl": margin,
        "margin_pct": margin / oil_price * 100 if oil_price else 0.0,
        "co2_cost_ratio_pct": co2 / total_cost * 100 if total_cost else 0.0,
    }


def evaluate_eor(
    technique: str, reservoir: dict, economic: dict, recovery_pct: float | None = None
) -> dict:
    """한 기법에 대해 모든 경제성 지표 + 메타 반환.

    Args:
        recovery_pct: 회수율(% OOIP) override. None이면 RECOVERY_FACTOR 점추정.

    Returns dict 구조 (spec § 2.4 schema의 economics.by_technique[] 한 요소):
        - technique, incremental_recovery_pct, incremental_bbl_million
        - npv_million_usd, irr_pct, pir, pbp_years
        - cashflow_yearly_million_usd
        - assumptions: {recovery_rate_source, cost_source}
    """
    cf = build_cashflow(technique, reservoir, economic, recovery_pct=recovery_pct)
    rate = economic["discount_rate_pct"] / 100  # UI percent → decimal

    # PIR용: revenue / investment 분리
    investments = [-c if c < 0 else 0 for c in cf]
    revenues = [c if c > 0 else 0 for c in cf]

    rf = recovery_pct if recovery_pct is not None else RECOVERY_FACTOR[technique]
    inc_bbl = reservoir["ooip_million_bbl"] * rf / 100

    irr_value = irr(cf)

    return {
        "technique": technique,
        "incremental_recovery_pct": rf,
        "incremental_bbl_million": round(inc_bbl, 1),
        "npv_million_usd": round(npv(cf, rate), 1),
        "irr_pct": round(irr_value * 100, 2) if irr_value is not None else None,
        "pir": (
            round(pir(revenues, investments, rate), 2)
            if sum(investments) > 0
            else None
        ),
        "pbp_years": pbp(cf),
        "cashflow_yearly_million_usd": [round(c, 1) for c in cf],
        "assumptions": {
            "recovery_rate_source": (
                "Taber Table 8 미시블 22% / 비미시블 10% / "
                "기타 Taber Table 5 median 등"
            ),
            "cost_source": "NETL Primer 2010 p.13",
        },
    }
