#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPORTS_DIR = Path("reports")


def load_report(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    mt4 = load_report(REPORTS_DIR / "cointegration_diagnostics_oos_mt_4h.json")
    mt1 = load_report(REPORTS_DIR / "cointegration_diagnostics_oos_mt_1d.json")
    h1 = load_report(REPORTS_DIR / "cointegration_diagnostics_real.json")

    breaks_summary = {
        "type": "mt_structural_breaks_summary",
        "real_data_only": True,
        "fabricated_data": False,
        "computed_at": datetime.now(tz=timezone.utc).isoformat(),
        "timeframes": ["1h", "4h", "1d"],
        "pairs": {},
    }
    all_pairs = set(mt4["cointegration_diagnostics"].keys()) | set(
        mt1["cointegration_diagnostics"].keys()
    )
    for pname in sorted(all_pairs):
        breaks_summary["pairs"][pname] = {}
        try:
            d1 = h1["cointegration_diagnostics"][pname]
            sb = d1.get("structural_breaks", {})
            breaks_summary["pairs"][pname]["1h"] = {
                "flagged": sb.get("flagged"),
                "breaks": sb.get("breaks", []),
            }
        except Exception:
            breaks_summary["pairs"][pname]["1h"] = {"flagged": None, "breaks": []}
        d4 = mt4["cointegration_diagnostics"][pname]
        sb4 = d4.get("structural_breaks", {})
        breaks_summary["pairs"][pname]["4h"] = {
            "flagged": sb4.get("flagged"),
            "breaks": sb4.get("breaks", []),
        }
        d1d = mt1["cointegration_diagnostics"][pname]
        sb1 = d1d.get("structural_breaks", {})
        breaks_summary["pairs"][pname]["1d"] = {
            "flagged": sb1.get("flagged"),
            "breaks": sb1.get("breaks", []),
        }
    out_sb = REPORTS_DIR / "mt_structural_breaks_summary.json"
    out_sb.write_text(json.dumps(breaks_summary, indent=2, default=float), encoding="utf-8")
    print(f"Wrote {out_sb}")

    matrix = {
        "type": "mt_blocking_matrix",
        "real_data_only": True,
        "fabricated_data": False,
        "computed_at": datetime.now(tz=timezone.utc).isoformat(),
        "timeframes": ["1h", "4h", "1d"],
        "pairs": {},
    }
    for pname in sorted(all_pairs):
        matrix["pairs"][pname] = {}
        try:
            d1 = h1["cointegration_diagnostics"][pname]
            g1 = d1.get("gates", {})
            p1 = d1.get("provenance", {})
            rs1 = d1.get("rolling_stability", {})
            matrix["pairs"][pname]["1h"] = {
                "all_pass": bool(g1.get("all_pass")),
                "blocked_routes": p1.get("blocked_routes", []),
                "rolling_frac_stable": rs1.get("frac_significant"),
                "structural_breaks_flagged": d1.get("structural_breaks", {}).get("flagged"),
            }
        except Exception as e:
            matrix["pairs"][pname]["1h"] = {"error": str(e)}
        d4 = mt4["cointegration_diagnostics"][pname]
        g4 = d4.get("gates", {})
        p4 = d4.get("provenance", {})
        rs4 = d4.get("rolling_stability", {})
        matrix["pairs"][pname]["4h"] = {
            "all_pass": bool(g4.get("all_pass")),
            "blocked_routes": p4.get("blocked_routes", []),
            "rolling_frac_stable": rs4.get("frac_significant"),
            "structural_breaks_flagged": d4.get("structural_breaks", {}).get("flagged"),
        }
        d1d = mt1["cointegration_diagnostics"][pname]
        g1d = d1d.get("gates", {})
        p1d = d1d.get("provenance", {})
        rs1d = d1d.get("rolling_stability", {})
        matrix["pairs"][pname]["1d"] = {
            "all_pass": bool(g1d.get("all_pass")),
            "blocked_routes": p1d.get("blocked_routes", []),
            "rolling_frac_stable": rs1d.get("frac_significant"),
            "structural_breaks_flagged": d1d.get("structural_breaks", {}).get("flagged"),
        }
    out_m = REPORTS_DIR / "mt_blocking_matrix.json"
    out_m.write_text(json.dumps(matrix, indent=2, default=float), encoding="utf-8")
    print(f"Wrote {out_m}")


if __name__ == "__main__":
    main()
