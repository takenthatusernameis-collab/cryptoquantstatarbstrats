#!/usr/bin/env python3
"""C305 preflight: fail-closed verification of the program-closure evidence
before the C305 closure runner executes.

Verifies (stdlib + yaml only, no market data):

- The C305 reachability-exhaustion probe cache (`data/cache/campaign305_reachability_probe.json`)
  and report (`reports/c305_reachability_probe_20261115T030618Z.json`) exist on disk and their
  SHA256-from-bytes match the values recorded in research_state/state.yaml
  (cache 3a395393d08170976b95022e746fd890076bc6e3cdbada7e917019d402ef1c27;
  provenance 7099d5bf39242f9a5513fed841adaa50779d23fb4a6cf153a65de2389beb8a04).
- The probe JSON carries path_b_recommended:true and genuinely_new_reachable_families:[],
  real_data_only:true, fabricated_data:false, executed_fills:false.
- research_state/state.yaml records latest_campaign_done: C304 (about to become C305),
  reachable_real_data_cross_sectional_stat_arb_space: CLOSED, and the C305 probe evidence
  block with matching SHA256s.

The script never fetches market data and never fabricates data. Exit 0 iff every check
passes (ready:true); any missing file, stale/missing SHA256, or falsified gate is a
fail-closed blocker (exit 1).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "research_state" / "state.yaml"
CACHE = ROOT / "data" / "cache" / "campaign305_reachability_probe.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign305_reachability_probe.provenance.json"
PROBE_REPORT = ROOT / "reports" / "c305_reachability_probe_20261115T030618Z.json"

# SHA256-from-bytes recorded in research_state/state.yaml (c305_reachability_probe block).
PROBE_CACHE_SHA = "3a395393d08170976b95022e746fd890076bc6e3cdbada7e917019d402ef1c27"
PROBE_PROV_SHA = "7099d5bf39242f9a5513fed841adaa50779d23fb4a6cf153a65de2389beb8a04"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    def rec(name: str, ok: bool, detail: dict | None = None, reason: str | None = None) -> None:
        checks[name] = {"ok": bool(ok), **(detail or {})}
        if not ok:
            blocked.append(reason or name)

    # --- state.yaml -----------------------------------------------------
    try:
        state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
        state_ok = isinstance(state, dict)
    except Exception as exc:  # noqa: BLE001
        state = {}
        state_ok = False
        rec("state_yaml_readable", False, reason=f"state.yaml unreadable: {exc}")
    rec("state_yaml_readable", state_ok, detail={"path": str(STATE)})

    latest_campaign = state.get("latest_campaign_done") if isinstance(state, dict) else None
    rec(
        "latest_campaign_done_c304_or_c305",
        latest_campaign in ("C304", "C305"),
        detail={"latest_campaign_done": latest_campaign},
        reason="latest_campaign_done must be C304 (pre-closure) or C305 (post-closure)",
    )

    reachable_space = state.get("reachable_real_data_cross_sectional_stat_arb_space") if isinstance(state, dict) else None
    rec(
        "reachable_space_closed",
        reachable_space == "CLOSED",
        detail={"reachable_real_data_cross_sectional_stat_arb_space": reachable_space},
        reason="reachable_real_data_cross_sectional_stat_arb_space must be CLOSED",
    )

    probe_block = state.get("c305_reachability_probe") if isinstance(state, dict) else None
    rec(
        "probe_block_present",
        isinstance(probe_block, dict),
        reason="state.yaml c305_reachability_probe block missing",
    )

    # --- probe cache (bytes -> sha256) ----------------------------------
    cache_exists = CACHE.exists()
    rec("probe_cache_exists", cache_exists, detail={"path": str(CACHE)}, reason="probe cache missing")
    cache_sha = sha256_file(CACHE) if cache_exists else None
    rec(
        "probe_cache_sha256_from_bytes",
        cache_sha == PROBE_CACHE_SHA,
        detail={"actual": cache_sha, "expected": PROBE_CACHE_SHA},
        reason="probe cache SHA256-from-bytes mismatch",
    )

    # --- probe provenance (bytes -> sha256) ------------------------------
    prov_exists = CACHE_PROV.exists()
    rec("probe_provenance_exists", prov_exists, detail={"path": str(CACHE_PROV)}, reason="probe provenance missing")
    prov_sha = sha256_file(CACHE_PROV) if prov_exists else None
    rec(
        "probe_provenance_sha256_from_bytes",
        prov_sha == PROBE_PROV_SHA,
        detail={"actual": prov_sha, "expected": PROBE_PROV_SHA},
        reason="probe provenance SHA256-from-bytes mismatch",
    )

    # --- probe report (bytes -> sha256 + contents) -----------------------
    report_exists = PROBE_REPORT.exists()
    rec("probe_report_exists", report_exists, detail={"path": str(PROBE_REPORT)}, reason="probe report missing")
    report_sha = sha256_file(PROBE_REPORT) if report_exists else None
    rec(
        "probe_report_sha256_from_bytes",
        report_sha == PROBE_CACHE_SHA,
        detail={"actual": report_sha, "expected": PROBE_CACHE_SHA},
        reason="probe report SHA256-from-bytes mismatch",
    )

    probe = None
    if report_exists:
        try:
            probe = json.loads(PROBE_REPORT.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            rec("probe_report_parseable", False, reason=f"probe report unparseable: {exc}")
    rec("probe_report_parseable", probe is not None, reason="probe report not parseable")

    if isinstance(probe, dict):
        summary = probe.get("summary") or {}
        rec(
            "probe_path_b_recommended",
            summary.get("path_b_recommended") is True,
            detail={"path_b_recommended": summary.get("path_b_recommended")},
            reason="path_b_recommended must be true",
        )
        rec(
            "probe_genuinely_new_empty",
            summary.get("genuinely_new_reachable_families") == [],
            detail={"genuinely_new_reachable_families": summary.get("genuinely_new_reachable_families")},
            reason="genuinely_new_reachable_families must be empty (no Path A)",
        )
        rec(
            "probe_flags",
            probe.get("real_data_only") is True
            and probe.get("fabricated_data") is False
            and probe.get("executed_fills") is False,
            detail={
                "real_data_only": probe.get("real_data_only"),
                "fabricated_data": probe.get("fabricated_data"),
                "executed_fills": probe.get("executed_fills"),
            },
            reason="probe real-data flags invalid",
        )

    # --- state.yaml probe block vs on-disk bytes -------------------------
    if isinstance(probe_block, dict):
        rec(
            "state_probe_report_sha256",
            probe_block.get("report_sha256") == PROBE_CACHE_SHA,
            detail={"recorded": probe_block.get("report_sha256"), "expected": PROBE_CACHE_SHA},
            reason="state.yaml probe report_sha256 mismatch",
        )
        rec(
            "state_probe_cache_sha256",
            probe_block.get("cache_sha256") == PROBE_CACHE_SHA,
            detail={"recorded": probe_block.get("cache_sha256"), "expected": PROBE_CACHE_SHA},
            reason="state.yaml probe cache_sha256 mismatch",
        )
        rec(
            "state_probe_provenance_sha256",
            probe_block.get("provenance_sha256") == PROBE_PROV_SHA,
            detail={"recorded": probe_block.get("provenance_sha256"), "expected": PROBE_PROV_SHA},
            reason="state.yaml probe provenance_sha256 mismatch",
        )
        rec(
            "state_probe_path_b",
            probe_block.get("path_b_recommended") is True,
            detail={"path_b_recommended": probe_block.get("path_b_recommended")},
            reason="state.yaml path_b_recommended must be true",
        )
        rec(
            "state_probe_genuinely_new_empty",
            probe_block.get("genuinely_new_reachable_families") == [],
            detail={"genuinely_new_reachable_families": probe_block.get("genuinely_new_reachable_families")},
            reason="state.yaml genuinely_new_reachable_families must be empty",
        )
    else:
        for nm in ("state_probe_report_sha256", "state_probe_cache_sha256", "state_probe_provenance_sha256",
                   "state_probe_path_b", "state_probe_genuinely_new_empty"):
            rec(nm, False, reason="probe block missing")

    ready = not blocked
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "campaign": 305,
        "part": "preflight",
        "as_of_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "checks": checks,
        "blocked_reasons": blocked,
        "state_yaml": str(STATE),
        "probe_cache": str(CACHE),
        "probe_provenance": str(CACHE_PROV),
        "probe_report": str(PROBE_REPORT),
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
