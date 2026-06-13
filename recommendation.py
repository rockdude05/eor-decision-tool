"""Recommendation 모듈 — NPV 기반 순위 + 유가 민감도 분석."""

from economics import evaluate_eor
from constants import OIL_PRICE_SCENARIOS


def rank_techniques(economics_list: list[dict]) -> list[str]:
    """NPV 내림차순으로 통과한 기법 정렬.

    Args:
        economics_list: dict에 'technique', 'npv_million_usd', 'passed' 키 포함.

    Returns:
        기법 이름 list (NPV 내림차순, passed=True만).
    """
    filtered = [e for e in economics_list if e.get("passed", True)]
    sorted_list = sorted(
        filtered,
        key=lambda e: e["npv_million_usd"] if e["npv_million_usd"] is not None else -1e18,
        reverse=True,
    )
    return [e["technique"] for e in sorted_list]


def sensitivity_analysis(
    reservoir: dict, economic: dict, passed_techniques: list[str]
) -> dict:
    """6개 유가 시나리오에서 최우수 기법과 NPV 계산.

    제출본 § 3-(3)·(4): 유가만 변동, 비용 항목(CO2, O&M, CAPEX)은 NETL Primer 2010 p.13 고정.

    Args:
        reservoir: 저류층 dict.
        economic: 경제 dict (oil_price는 시나리오로 덮어씌움).
        passed_techniques: screening 통과 기법 이름 list.

    Returns:
        dict with keys from OIL_PRICE_SCENARIOS, values =
        {'top_technique': str, 'npv_million_usd': float}.
    """
    result = {}
    for scenario_key, oil_price in OIL_PRICE_SCENARIOS.items():
        # 유가만 변경
        scenario_economic = {**economic, "oil_price_usd_per_bbl": oil_price}

        if not passed_techniques:
            result[scenario_key] = {
                "top_technique": None,
                "npv_million_usd": None,
            }
            continue

        # 각 통과 기법에 대해 NPV 계산
        best_tech = None
        best_npv = -float("inf")
        for tech in passed_techniques:
            metrics = evaluate_eor(tech, reservoir, scenario_economic)
            if metrics["npv_million_usd"] is not None and metrics["npv_million_usd"] > best_npv:
                best_npv = metrics["npv_million_usd"]
                best_tech = tech

        result[scenario_key] = {
            "top_technique": best_tech,
            "npv_million_usd": round(best_npv, 1) if best_tech else None,
        }
    return result


def build_recommendation(
    reservoir: dict,
    economic: dict,
    screening_results: list[dict],
    economics_list: list[dict],
) -> dict:
    """최종 추천 dict (spec § 2.4 schema의 recommendation 필드).

    Args:
        reservoir: 저류층 입력.
        economic: 경제 입력.
        screening_results: screen_eor() 결과.
        economics_list: 각 통과 기법에 대한 evaluate_eor() 결과.

    Returns:
        dict with primary, ranking, rationale_short, sensitivity (_note 포함).
    """
    # passed 기법만
    passed_tech_names = [s["technique"] for s in screening_results if s["passed"]]

    if not passed_tech_names:
        return {
            "primary": None,
            "ranking": [],
            "rationale_short": "통과 기법 없음. 저류층 조건 재검토 또는 EOR 적용 부적합.",
            "sensitivity": {
                "_note": "통과 기법 없음 — sensitivity 분석 스킵"
            },
        }

    ranking = rank_techniques(economics_list)
    primary = ranking[0] if ranking else None

    sensitivity = sensitivity_analysis(reservoir, economic, passed_tech_names)
    sensitivity["_note"] = (
        "유가만 변동, 비용 항목(CO2/OPEX/CAPEX)은 NETL Primer 2010 p.13 고정 "
        "(제출본 § 3-(3))"
    )

    return {
        "primary": primary,
        "ranking": ranking,
        "rationale_short": (
            f"{primary}이 NPV 1위 + Taber Table screening 통과. "
            "유가 WTI 2026 $105.66 / 비용 NETL Primer 2010 p.13 기준."
        ),
        "sensitivity": sensitivity,
    }
