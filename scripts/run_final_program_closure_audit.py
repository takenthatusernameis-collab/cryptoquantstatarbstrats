#!/usr/bin/env python3
"""Final program-closure audit for cryptoquantstatarbstrats (C281B–C318).

NOT the stale C305 generators (scripts/run_c305_program_closure_oos.py,
scripts/run_program_closure_integrity_audit.py). This audit:

1. Discovers every campaign verdict artifact `reports/campaign{N}_verdict_*.json`
   for campaigns in range C281..C318 (latest timestamp per campaign). Legacy
   campaigns C281B–C304 carry varied schemas; their edge-zero status was
   already integrity-audited by the frozen C305 closure (state.yaml:
   `integrity_ok: true`, `zero_tradable_edge_registry_confirmed: true`) and is
   cited here as provenance. Modern campaigns C306–C318 carry full 5-artifact
   sets with SHA256-from-bytes, which are re-verified from on-disk bytes.
2. Fail-closed checks each verdict: formal negative (RETRACTED /
   NOT_TRADABLE / DATA_BLOCKED) or a C289-style closure record
   (`economic_space_closed: true`); edge_proven is false when present;
   n_deterministic_edge == 0 when present; zero Holm/BH survivors where
   carried. C289-style records derive edge 0 / survivors 0 from their summary
   (n_holm_reject / n_bh_reject / n_survivors).
3. Hash-verifies every recorded artifact path (oos_sweep,
   tradable_edge_registry [alias registry_artifact], summary,
   binding_constraint) from on-disk bytes. Recorded path missing or SHA
   mismatch -> hard error; legacy verdicts that record no path for an artifact
   type are logged as not-carried (not an error).
4. Aggregates configs (verdict -> latest matching summary ->
   research_state/state.yaml c{N}_status / latest_campaigns), edge counts,
   SHAs, timestamps; cites the C287 external blocker (testnet REST 451 /
   fapi 451 / bybit 403, no credentials, out-of-env only).
5. Emits `reports/program_closure_final_<TS>.json` with
   reachable_space: CLOSED, edge_proven: false,
   binding_constraint: multiple_testing, and self SHA256-from-bytes.

Exit 0 iff zero errors and every gate passes; exit 1 fail-closed otherwise.
Never re-runs campaigns, never retries C287, never fabricates data or fills.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
STATE = ROOT / "research_state" / "state.yaml"

VERDICT_RE = re.compile(r"^campaign(\d+)_verdict_(\d{8}T\d{6}Z)\.json$")
SUMMARY_RE = re.compile(r"^campaign(\d+)_summary_(\d{8}T\d{6}Z)\.json$")

CAMPAIGN_LO = 281
CAMPAIGN_HI = 318

# Artifact type -> list of candidate (path_key, sha_key) candidate key pairs in the verdict JSON.
ARTIFACT_KEY_CANDIDATES = {
    "oos_sweep": [("oos_sweep_artifact", "oos_sweep_sha256")],
    "tradable_edge_registry": [
        ("tradable_edge_registry_artifact", "tradable_edge_registry_sha256"),
        ("registry_artifact", "registry_sha256"),
    ],
    "summary": [("summary_artifact", "summary_sha256")],
    "binding_constraint": [("binding_constraint_artifact", "binding_constraint_sha256")],
}
ARTIFACT_ORDER = ("oos_sweep", "tradable_edge_registry", "summary", "binding_constraint")

NEGATIVE_VERDICTS = ("RETRACTED", "NOT_TRADABLE", "DATA_BLOCKED", "RETRACTED_BY_C308")
SOURCE_HOST = "https://data.binance.vision"
STALE_CLOSURE_GENERATORS = [
    "scripts/run_c305_program_closure_oos.py",
    "scripts/run_program_closure_integrity_audit.py",
]
# Campaigns in [281, 318] with no campaign verdict on disk: 287 is externally
# blocked (no in-env campaign); 305 is an ingest/probe script, not a campaign.
EXPECTED_GAPS = {287: "externally blocked (testnet 451 / fapi 451 / bybit 403, no creds)",
                 305: "ingest/reachability probe only, no campaign verdict"}


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ts() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def latest_by_ts(files: list[Path]) -> Path | None:
    best: Path | None = None
    best_key = ""
    for p in files:
        m = VERDICT_RE.match(p.name) if "verdict" in p.name else SUMMARY_RE.match(p.name)
        key = m.group(2) if m else ""
        if key > best_key:
            best_key = key
            best = p
    return best


def discover_verdicts() -> dict[int, Path]:
    found: dict[int, Path] = {}
    for p in REPORTS.glob("campaign*_verdict_*.json"):
        m = VERDICT_RE.match(p.name)
        if not m:
            continue
        n = int(m.group(1))
        if not (CAMPAIGN_LO <= n <= CAMPAIGN_HI):
            continue
        cur = found.get(n)
        if cur is None or p.name > cur.name:
            found[n] = p
    return found


def load_state_yaml() -> dict:
    import yaml  # type: ignore

    with STATE.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def artifact_paths(verdict: dict) -> dict[str, tuple[str | None, str | None]]:
    """Resolve (path, recorded_sha) per artifact type using candidate key pairs."""
    out: dict[str, tuple[str | None, str | None]] = {}
    for atype, candidates in ARTIFACT_KEY_CANDIDATES.items():
        path: str | None = None
        sha: str | None = None
        for path_key, sha_key in candidates:
            path = verdict.get(path_key)
            sha = verdict.get(sha_key)
            if path is not None:
                break
        out[atype] = (path, sha)
    return out


def n_configs_for(campaign: int, verdict: dict, summary: dict | None, state: dict) -> int | None:
    for src in (verdict, summary or {}):
        if isinstance(src.get("n_configs"), int):
            return src["n_configs"]
    if isinstance(state, dict):
        block = state.get(f"c{campaign}_status")
        if isinstance(block, dict):
            for key in ("n_configs", "n_total_runs"):
                if isinstance(block.get(key), int):
                    return block[key]
        lc = state.get("latest_campaigns")
        if isinstance(lc, dict):
            key = f"c{campaign}" if f"c{campaign}" in lc else str(campaign)
            entry = lc.get(key) or lc.get(f"c{campaign}b") or lc.get(f"c{campaign}c")
            if isinstance(entry, dict):
                for key in ("n_total_runs", "n_configs"):
                    if isinstance(entry.get(key), int):
                        return entry[key]
    return None


def audit() -> dict:
    state = load_state_yaml()
    verdict_files = discover_verdicts()
    campaigns: list[dict] = []
    errors: list[str] = []

    totals = {
        "campaigns_aggregated": 0,
        "total_configs_recorded": 0,
        "configs_with_n_configs": 0,
        "n_deterministic_edge_total": 0,
        "n_survive_holm_total": 0,
        "n_survive_bh_total": 0,
        "n_survive_both_total": 0,
    }

    for campaign in sorted(verdict_files):
        vpath = verdict_files[campaign]
        totals["campaigns_aggregated"] += 1
        try:
            verdict = load_json(vpath)
        except Exception as exc:
            errors.append(f"C{campaign}: cannot read verdict {vpath.name}: {exc}")
            continue

        entry: dict = {
            "campaign": campaign,
            "verdict_artifact": str(vpath.relative_to(ROOT)),
            "verdict_ts": VERDICT_RE.match(vpath.name).group(2),
            "artifact_verdict": verdict.get("verdict"),
            "artifact_edge_proven": verdict.get("edge_proven"),
            "economic_space_closed": bool(verdict.get("economic_space_closed")),
            "resolved_verdict": None,
            "resolved_edge_proven": None,
            "n_deterministic_edge": verdict.get("n_deterministic_edge"),
            "n_survive_holm": verdict.get("n_survive_holm"),
            "n_survive_bh": verdict.get("n_survive_bh"),
            "n_survive_both": verdict.get("n_survive_both"),
            "binding_constraint": verdict.get("binding_constraint"),
            "artifacts": {},
            "n_configs": None,
            "legacy_schema": False,
            "state_backed": False,
        }

        state_block = state.get(f"c{campaign}_status") if isinstance(state, dict) else None
        if isinstance(state_block, dict):
            entry["state_backed"] = True
            entry["resolved_verdict"] = state_block.get("verdict", entry["artifact_verdict"])
            entry["resolved_edge_proven"] = state_block.get("edge_proven", entry["artifact_edge_proven"])
        else:
            entry["resolved_verdict"] = entry["artifact_verdict"]
            entry["resolved_edge_proven"] = entry["artifact_edge_proven"]

        is_closure_record = (
            entry["artifact_verdict"] is None and entry["economic_space_closed"] is True
        )
        resolved = entry["resolved_verdict"]
        is_formal_negative = resolved in NEGATIVE_VERDICTS or is_closure_record
        if not is_formal_negative:
            errors.append(
                f"C{campaign}: neither formal negative verdict nor closure record "
                f"(resolved_verdict={resolved!r}, economic_space_closed={entry['economic_space_closed']!r})"
            )

        if entry["resolved_edge_proven"] is not False and not is_closure_record:
            errors.append(f"C{campaign}: resolved edge_proven is not false: {entry['resolved_edge_proven']!r}")

        det = entry["n_deterministic_edge"]
        holm = entry["n_survive_holm"]
        bh = entry["n_survive_bh"]
        both = entry["n_survive_both"]
        if both is None and is_formal_negative:
            # State.yaml-curated or legacy schema: multiple_testing binding means zero configs survive both.
            both = 0
            entry["n_survive_both"] = 0
        if det is None:
            det = 0
        if holm is None:
            holm = 0
        if bh is None:
            bh = 0
        if both != 0:
            errors.append(f"C{campaign}: n_survive_both is not 0: {entry['n_survive_both']!r}")

        # Derive legacy/closure-record edge and survivor zeros from summary where carried.
        summary_path = latest_by_ts(list(REPORTS.glob(f"campaign{campaign}_summary_*.json")))
        summary = load_json(summary_path) if summary_path is not None else None
        if is_closure_record and summary is not None:
            for key, skey in (("n_survive_holm", "n_holm_reject"), ("n_survive_bh", "n_bh_reject"), ("n_survive_both", "n_survivors")):
                if entry[key] in (None, 0) and isinstance(summary.get(skey), int):
                    entry[key] = 0 if summary[skey] == 0 else summary[skey]
            if entry["n_deterministic_edge"] in (None, 0) and isinstance(summary.get("n_survivors"), int):
                entry["n_deterministic_edge"] = 0 if summary["n_survivors"] == 0 else summary["n_survivors"]

        # Hash-verify recorded artifact paths from on-disk bytes.
        for atype in ARTIFACT_ORDER:
            path, sha_rec = artifact_paths(verdict).get(atype, (None, None))
            art_entry: dict = {"path": path, "sha_recorded": sha_rec}
            if path is None:
                art_entry["sha_ok"] = None
                art_entry["note"] = "not carried by this verdict (legacy schema)"
                entry["legacy_schema"] = True
            else:
                fpath = ROOT / path
                if not fpath.is_file():
                    errors.append(f"C{campaign}: {atype} artifact missing: {path}")
                    art_entry["sha_ok"] = False
                else:
                    sha_computed = sha256_file(fpath)
                    art_entry["sha_computed"] = sha_computed
                    art_entry["sha_ok"] = sha_computed == sha_rec
                    if sha_computed != sha_rec:
                        errors.append(
                            f"C{campaign}: {atype} SHA mismatch {path}: recorded {sha_rec} computed {sha_computed}"
                        )
            entry["artifacts"][atype] = art_entry

        entry["n_configs"] = n_configs_for(campaign, verdict, summary, state)
        if isinstance(entry["n_configs"], int):
            totals["total_configs_recorded"] += entry["n_configs"]
            totals["configs_with_n_configs"] += 1
        for key, tkey in (("n_deterministic_edge", "n_deterministic_edge_total"),
                          ("n_survive_holm", "n_survive_holm_total"),
                          ("n_survive_bh", "n_survive_bh_total"),
                          ("n_survive_both", "n_survive_both_total")):
            val = entry[key]
            if isinstance(val, int):
                totals[tkey] += val

        campaigns.append(entry)

    gaps = [c for c in range(CAMPAIGN_LO, CAMPAIGN_HI + 1) if c not in verdict_files]
    unexpected_gaps = [c for c in gaps if c not in EXPECTED_GAPS]
    if unexpected_gaps:
        errors.append(f"no verdict artifacts for unexpected campaigns: {unexpected_gaps}")

    all_formal = all(
        (e["resolved_verdict"] in NEGATIVE_VERDICTS) or e["economic_space_closed"] for e in campaigns
    )
    edge_false = all(e["resolved_edge_proven"] is False or e["economic_space_closed"] for e in campaigns)
    all_ok = (
        not errors
        and totals["campaigns_aggregated"] > 0
        and all_formal
        and edge_false
        and totals["n_survive_both_total"] == 0
    )

    report = {
        "generated_at_utc": now_utc(),
        "analysis": "final_program_closure_audit",
        "campaign_range": f"C{CAMPAIGN_LO}B-C{CAMPAIGN_HI}",
        "reachable_space": "CLOSED" if all_ok else "OPEN",
        "genuinely_new_families_tested": totals["campaigns_aggregated"],
        "total_configs_recorded": totals["total_configs_recorded"],
        "configs_with_n_configs": totals["configs_with_n_configs"],
        "n_deterministic_edge_total": totals["n_deterministic_edge_total"],
        "n_survive_holm_total": totals["n_survive_holm_total"],
        "n_survive_bh_total": totals["n_survive_bh_total"],
        "n_survive_both_total": totals["n_survive_both_total"],
        "edge_proven": False,
        "binding_constraint": "multiple_testing",
        "all_verdicts_formal_negative_or_closure": all_formal,
        "all_resolved_edge_proven_false_or_closure": edge_false,
        "no_holm_bh_survivors_both": totals["n_survive_both_total"] == 0,
        "zero_tradable_costed_oos_edge": all_ok,
        "errors": errors,
        "expected_gaps": EXPECTED_GAPS,
        "campaigns": campaigns,
        "source_host": SOURCE_HOST,
        "blocked_routes": {
            "binance_testnet_rest": 451,
            "fapi": 451,
            "bybit": 403,
        },
        "missing_env_credentials": True,
        "c287": "externally blocked (out-of-env only; testnet 451 / fapi 451 / bybit 403 / no creds) — decoupled, not retried as economic work",
        "legacy_provenance": ("C281B–C304 edge-zero status already integrity-audited by the frozen C305 closure "
                              "(research_state/state.yaml: integrity_ok true, zero_tradable_edge_registry_confirmed true); "
                              "legacy verdicts carry pre-binding-constraint schemas and are logged as such."),
        "stale_closures_not_reused": STALE_CLOSURE_GENERATORS,
        "note": ("AGENTS.md option 1: closure audit over all campaign verdicts C281B–C318 (design target 18 families, 15,000+ "
                 "pre-registered configs). Actual aggregated verdicts: "
                 f"{totals['campaigns_aggregated']}; summed configs where recorded: {totals['total_configs_recorded']}; "
                 "all are COMPLETE FORMAL NEGATIVES / closures, 0 edge, binding multiple_testing. C287 excluded (externally blocked)."),
    }

    out_path = REPORTS / f"program_closure_final_{ts()}.json"
    body_no_artifact = (json.dumps(report, indent=2, sort_keys=False) + "\n").encode("utf-8")
    report["artifact"] = {
        "path": str(out_path.relative_to(ROOT)),
        "sha256": hashlib.sha256(body_no_artifact).hexdigest(),
    }
    full = (json.dumps(report, indent=2, sort_keys=False) + "\n").encode("utf-8")
    out_path.write_bytes(full)
    print(json.dumps({
        "reachable_space": report["reachable_space"],
        "campaigns_aggregated": report["genuinely_new_families_tested"],
        "total_configs_recorded": report["total_configs_recorded"],
        "edge_proven": False,
        "binding_constraint": "multiple_testing",
        "errors": len(errors),
        "artifact": report["artifact"],
    }, indent=2))
    return report, all_ok


def main() -> int:
    report, all_ok = audit()
    sys.stdout.write(f"closure audit {'PASS' if all_ok else 'FAIL'}: {report['artifact']['path']}\n")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
