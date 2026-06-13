"""JSON Export — spec § 2.4 schema 직렬화 (v1.1: korean_context 제거)."""

from datetime import datetime
from screening import screen_eor
from economics import evaluate_eor, margin_per_bbl
from recommendation import build_recommendation
from constants import COST_METHODOLOGY, RECOVERY_FACTOR_STATS, ALADASSANI_BAI_NOTE


def build_export_dict(
    reservoir: dict,
    economic: dict,
    scenario_name: str = "default",
    validation: dict | None = None,
) -> dict:
    """spec § 2.4 schema에 맞춘 export dict 생성.

    Args:
        reservoir: 입력 저류층.
        economic: 입력 경제.
        scenario_name: 시나리오 이름.
        validation: 검증 케이스 정보 (사업 B 등, optional).
    """
    # Screening
    screening = screen_eor(reservoir)

    # Economics — 통과한 기법만
    passed = [s["technique"] for s in screening if s["passed"]]
    economics_list = [evaluate_eor(t, reservoir, economic) for t in passed]
    for e in economics_list:
        e["passed"] = True  # rank_techniques에 필요

    # Recommendation
    rec = build_recommendation(reservoir, economic, screening, economics_list)

    return {
        "schema_version": "1.1",
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "tool_version": "0.2.0",
            "scenario_name": scenario_name,
        },
        "inputs": {
            "reservoir": reservoir,
            "economic": economic,
        },
        "screening": {"results": screening},
        "economics": {"by_technique": economics_list},
        "recommendation": rec,
        "recovery_basis": {
            "by_technique": {t: RECOVERY_FACTOR_STATS[t] for t in passed},
            "empirical_note": ALADASSANI_BAI_NOTE,
        },
        "margin_analysis": margin_per_bbl(economic),
        "cost_methodology": COST_METHODOLOGY,
        "validation": validation or {},
    }
