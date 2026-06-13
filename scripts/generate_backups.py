"""대표 시나리오의 JSON + 백업 MD/PDF 사전 생성 (발표 라이브 데모 fallback).

제출본 워크플로우 = 사용자가 임의 저류층 물성을 입력 → 추천·경제성.
따라서 백업도 대표 데모 입력(깊은 경질유)으로 생성한다.
(영일만/Weyburn 시나리오는 제출본 scope 밖이라 제거됨, 2026-06-13.)
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROTOTYPE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROTOTYPE_DIR))

from export import build_export_dict
from constants import DEFAULT_ECONOMIC

PROJECT_ROOT = PROTOTYPE_DIR
BACKUP_DIR = PROJECT_ROOT / "results" / "backup"
MD_TO_PDF = PROJECT_ROOT / "scripts" / "md_to_pdf.sh"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# 대표 데모 입력: 깊은 경질유 (CO2 미시블 통과 시나리오)
SAMPLE_RESERVOIR = {
    "api_gravity_deg": 35,
    "viscosity_cp": 5.0,
    "depth_ft": 8200,
    "permeability_md": 50.0,
    "temperature_f": 150,
    "oil_saturation_pct": 60,
    "ooip_million_bbl": 100,
}


def generate_markdown_report(scenario_name: str, export_data: dict) -> str:
    """제출본 8섹션 기반 간이 백업 MD (Claude Code 없이도 fallback 가능)."""
    rec = export_data["recommendation"]
    eco = export_data["inputs"]["economic"]
    res = export_data["inputs"]["reservoir"]
    margin = export_data["margin_analysis"]
    economics = export_data["economics"]["by_technique"]

    md = f"""---
title: "EOR 기법 선정과 경제성 평가의 통합 의사결정 — 분석 보고서"
author: "도구 v0.2 (백업 자동 생성)"
date: "{datetime.now().strftime('%Y-%m-%d')}"
---

# 1. 경영 요약

- **추천 기법**: {rec.get('primary', '—')}
- **근거**: {rec.get('rationale_short', '—')}

# 2. 입력 시나리오

| 항목 | 값 |
|---|---|
| API gravity | {res['api_gravity_deg']}° |
| 깊이 | {res['depth_ft']} ft |
| OOIP | {res['ooip_million_bbl']} million bbl |
| 유가 | ${eco['oil_price_usd_per_bbl']}/bbl |
| 할인율 | {eco['discount_rate_pct']}% |

기준(제출본 § 3-(3)): {export_data['cost_methodology']}

# 3. 공학적 스크리닝 (제출본 § 3-(1), Taber 1997 SPE 35385)

Taber의 7개 적용범위표(Tables 1-7) 기준, CO2 미시블/비미시블 분리로 총 8개 후보 기법 스크리닝.

| 기법 | 통과 | 출처 |
|---|---|---|
"""
    for r in export_data["screening"]["results"]:
        passed = "✅" if r["passed"] else "❌"
        md += f"| {r['technique']} | {passed} | {r['source']} |\n"

    md += "\n# 4. 회수율 분석 (제출본 § 3-(2))\n\n"
    md += export_data["recovery_basis"]["empirical_note"] + "\n\n"

    md += "# 5. 비용 구조 및 마진 (제출본 § 3-(3))\n\n"
    md += (
        f"- 유가 ${margin['oil_price']}/bbl − 총비용 ${margin['total_cost_per_bbl']}/bbl "
        f"= **마진 ${margin['margin_per_bbl']:.2f}/bbl ({margin['margin_pct']:.1f}%)**\n"
        f"- CO2 비용 비율: **{margin['co2_cost_ratio_pct']:.1f}%** "
        f"(제출본 § 3-(3) 25-50% 범위 {'안' if 25 <= margin['co2_cost_ratio_pct'] <= 50 else '밖'})\n\n"
    )

    md += "# 6. 경제성 평가 (제출본 § 3-(4), 교재 식 7.4-7.6)\n\n"
    md += "| 기법 | 회수율(%) | NPV ($M) | IRR (%) | PIR | PBP (년) |\n"
    md += "|---|---|---|---|---|---|\n"
    for e in economics:
        irr_str = f"{e['irr_pct']:.2f}" if e['irr_pct'] is not None else "N/A"
        pir_str = f"{e['pir']:.2f}" if e['pir'] is not None else "N/A"
        pbp_str = str(e['pbp_years']) if e['pbp_years'] is not None else "N/A"
        md += (
            f"| {e['technique']} | {e['incremental_recovery_pct']} | "
            f"{e['npv_million_usd']} | {irr_str} | {pir_str} | {pbp_str} |\n"
        )
    md += "\n*생산 프로파일: 6장 Arps 감퇴(식 6.6/6.9) + CO2 fill-up + CAPEX 0~2년 분산.*\n"
    md += "*도구 검증: 교재 표 7.4 사업 B(NPV 101.8/IRR 20.28%/PIR 1.20/PBP 3) ±0.1 재현.*\n\n"

    md += "# 7. 민감도 분석\n\n유가만 변동, 비용은 NETL Primer 2010 p.13 고정.\n\n"

    md += "# 8. 한계\n\n"
    md += "- Aladassani-Bai 기법별 회수율 중앙값 미입수, CAPEX 총액은 사업규모별 별도 산정.\n"
    md += "- 허수/복수 IRR 가능성 (교재 식 7.5 한계). 비용은 2010 NETL 기준(2026 인플레 미반영).\n"
    return md


if __name__ == "__main__":
    name = "sample_deep_light_oil"
    print(f"🚀 [{name}] 백업 생성 시작")
    export_data = build_export_dict(SAMPLE_RESERVOIR, DEFAULT_ECONOMIC, scenario_name=name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    json_path = BACKUP_DIR / f"result_{timestamp}_{name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ JSON: {json_path.name}")

    md_path = BACKUP_DIR / f"report_{timestamp}_{name}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(generate_markdown_report(name, export_data))
    print(f"  ✅ Markdown: {md_path.name}")

    try:
        subprocess.run([str(MD_TO_PDF), str(md_path)], check=True, capture_output=True, text=True)
        print(f"  ✅ PDF: {md_path.with_suffix('.pdf').name}")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️ PDF 생성 실패 (pandoc/xelatex 확인): {e.stderr[:200]}")
    except FileNotFoundError:
        print("  ⚠️ md_to_pdf.sh 실행 불가 (pandoc/xelatex 미설치 가능)")

    print("\n🎉 백업 생성 완료. results/backup/ 확인.")
