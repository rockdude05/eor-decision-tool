"""EOR Screening 엔진 (Taber Tables 1-7).

출처: Taber, Martin, Seright (1997) Part 2, PRRC PDF.
"""


def co2_miscible_depth_threshold(api_gravity: float) -> int | None:
    """Taber Table 3 — API gravity별 CO2-Miscible 최소 깊이.

    Args:
        api_gravity: API gravity (°)

    Returns:
        최소 깊이 (ft). 미시블 불가 시 None.
    """
    if api_gravity > 40:
        return 2500
    elif api_gravity >= 32:
        return 2800
    elif api_gravity >= 28:
        return 3300
    elif api_gravity >= 22:
        return 4000
    else:
        return None


# Taber Tables 1-7 임계값. 출처: PRRC PDF, research-notes/taber-1997-part2.pdf
SCREENING_TABLE = {
    "N2_Flue_Gas": {  # Table 1
        "api_min": 35,
        "viscosity_max": 0.4,
        "oil_sat_min": 40,
        "depth_min": 6000,
        "formation_type": ["sandstone", "carbonate"],
        "source": "Taber Table 1 (N2/Flue Gas Flooding)",
    },
    "HC_Miscible": {  # Table 2
        "api_min": 23,
        "viscosity_max": 3.0,
        "oil_sat_min": 30,
        "depth_min": 4000,
        "source": "Taber Table 2 (HC-Miscible Flooding)",
    },
    "CO2_Miscible": {  # Table 3 — 특수: 깊이는 API 함수
        "api_min": 22,
        "viscosity_max": 10,
        "oil_sat_min": 20,
        "depth_fn": co2_miscible_depth_threshold,
        "source": "Taber Table 3 (CO2 Miscible)",
    },
    "CO2_Immiscible": {  # Table 3
        "api_min": 13,
        "api_max": 21.9,
        "viscosity_max": 600,
        "oil_sat_min": 30,
        "depth_min": 1800,
        "source": "Taber Table 3 (CO2 Immiscible)",
    },
    "ASP_Micellar": {  # Table 4
        "api_min": 20,
        "viscosity_max": 35,
        "oil_sat_min": 35,
        "depth_max": 9000,
        "temperature_max": 200,
        "permeability_min": 10,
        "source": "Taber Table 4 (Micellar/ASP/Polymer)",
    },
    "Polymer": {  # Table 5
        "api_min": 15,
        "viscosity_max": 150,
        "oil_sat_min": 50,
        "depth_max": 9000,
        "temperature_max": 200,
        "permeability_min": 10,
        "source": "Taber Table 5 (Polymer Flooding)",
    },
    "In_Situ_Combustion": {  # Table 6
        "api_min": 10,
        "api_max": 27,
        "viscosity_max": 5000,
        "oil_sat_min": 50,
        "depth_max": 11500,
        "permeability_min": 50,
        "source": "Taber Table 6 (In-Situ Combustion)",
    },
    "Steamflood": {  # Table 7
        "api_min": 8,
        "api_max": 25,
        "viscosity_max": 100000,
        "oil_sat_min": 40,
        "depth_max": 5000,
        "permeability_min": 200,
        "source": "Taber Table 7 (Steamflood)",
    },
}


def evaluate_technique(reservoir: dict, rules: dict) -> tuple[bool, dict, list[str]]:
    """한 기법 rule set에 reservoir를 매칭.

    Returns:
        (통과 여부, 검사 결과 dict, 탈락 사유 list)
    """
    checks = {}
    fails = []

    # API min/max
    api = reservoir.get("api_gravity_deg")
    if "api_min" in rules and api is not None:
        passed = api >= rules["api_min"]
        checks["api_min"] = {"value": api, "rule": f">={rules['api_min']}", "pass": passed}
        if not passed:
            fails.append(f"API {api}° < {rules['api_min']}° (최소)")
    if "api_max" in rules and api is not None:
        passed = api <= rules["api_max"]
        checks["api_max"] = {"value": api, "rule": f"<={rules['api_max']}", "pass": passed}
        if not passed:
            fails.append(f"API {api}° > {rules['api_max']}° (최대)")

    # 점도 max
    visc = reservoir.get("viscosity_cp")
    if "viscosity_max" in rules and visc is not None:
        passed = visc <= rules["viscosity_max"]
        checks["viscosity_max"] = {
            "value": visc, "rule": f"<={rules['viscosity_max']}", "pass": passed
        }
        if not passed:
            fails.append(f"점도 {visc} cp > {rules['viscosity_max']} cp (최대)")

    # Oil saturation min
    sat = reservoir.get("oil_saturation_pct")
    if "oil_sat_min" in rules and sat is not None:
        passed = sat >= rules["oil_sat_min"]
        checks["oil_sat_min"] = {
            "value": sat, "rule": f">={rules['oil_sat_min']}%", "pass": passed
        }
        if not passed:
            fails.append(f"Oil saturation {sat}% < {rules['oil_sat_min']}% (최소)")

    # 깊이 — depth_fn 특수 처리 (CO2-Miscible)
    depth = reservoir.get("depth_ft")
    if "depth_fn" in rules and depth is not None:
        min_depth = rules["depth_fn"](api) if api is not None else None
        if min_depth is None:
            checks["depth_fn"] = {"value": depth, "rule": "API too low for miscible", "pass": False}
            fails.append(f"API {api}° 미시블 불가 (API<22°)")
        else:
            passed = depth >= min_depth
            checks["depth_fn"] = {
                "value": depth, "rule": f">={min_depth}ft (API {api}°)", "pass": passed
            }
            if not passed:
                fails.append(f"깊이 {depth}ft < {min_depth}ft (API {api}° 기준)")

    # 깊이 min/max
    if "depth_min" in rules and depth is not None:
        passed = depth >= rules["depth_min"]
        checks["depth_min"] = {
            "value": depth, "rule": f">={rules['depth_min']}ft", "pass": passed
        }
        if not passed:
            fails.append(f"깊이 {depth}ft < {rules['depth_min']}ft (최소)")
    if "depth_max" in rules and depth is not None:
        passed = depth <= rules["depth_max"]
        checks["depth_max"] = {
            "value": depth, "rule": f"<={rules['depth_max']}ft", "pass": passed
        }
        if not passed:
            fails.append(f"깊이 {depth}ft > {rules['depth_max']}ft (최대)")

    # 온도 max
    temp = reservoir.get("temperature_f")
    if "temperature_max" in rules and temp is not None:
        passed = temp <= rules["temperature_max"]
        checks["temperature_max"] = {
            "value": temp, "rule": f"<={rules['temperature_max']}°F", "pass": passed
        }
        if not passed:
            fails.append(f"온도 {temp}°F > {rules['temperature_max']}°F (최대)")

    # 투과율 min
    perm = reservoir.get("permeability_md")
    if "permeability_min" in rules and perm is not None:
        passed = perm >= rules["permeability_min"]
        checks["permeability_min"] = {
            "value": perm, "rule": f">={rules['permeability_min']}md", "pass": passed
        }
        if not passed:
            fails.append(f"투과율 {perm}md < {rules['permeability_min']}md (최소)")

    all_passed = all(c["pass"] for c in checks.values()) if checks else False
    return all_passed, checks, fails


def screen_eor(reservoir: dict) -> list[dict]:
    """모든 기법에 대해 screening 실행.

    Returns:
        list of dicts (spec § 2.4 schema의 screening.results[] 항목)
    """
    results = []
    for technique, rules in SCREENING_TABLE.items():
        passed, checks, fails = evaluate_technique(reservoir, rules)
        results.append({
            "technique": technique,
            "passed": passed,
            "criteria_checks": checks,
            "fail_reasons": fails,
            "source": rules["source"],
        })
    return results
