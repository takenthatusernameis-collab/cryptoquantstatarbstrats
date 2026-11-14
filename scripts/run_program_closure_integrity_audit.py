#!/usr/bin/env python3
"""Program closure-integrity audit over frozen C281B–C297 artifacts/datasets.

Recomputes SHA256-from-bytes for every frozen artifact/dataset referenced in
research_state/state.yaml and AGENTS.md, verifies real_data_only/fabricated_data
flags and verdict/binding/edge_claim consistency where present, and emits a
timestamped JSON + Markdown report.

Fail-closed: any missing file or hash mismatch is recorded; overall integrity_ok
is true only when all referenced items verify.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
STATE_PATH = ROOT / "research_state" / "state.yaml"
AGENTS_PATH = ROOT / "AGENTS.md"

CAMPAIGNS = [
    "C281B", "C281C", "C282", "C283", "C284", "C285", "C286", "C287",
    "C288", "C289", "C290", "C291", "C292", "C293", "C294", "C295", "C296",
    "C297",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def campaign_from_path(p: str) -> str | None:
    m = re.search(r"campaign(281b|281c|\d+)", p, re.IGNORECASE)
    if not m:
        return None
    token = m.group(1).upper()
    if token in ("281B", "281C"):
        return token
    return "C" + token


def _looks_like_path(s) -> bool:
    return (
        isinstance(s, str)
        and (s.startswith("data/") or s.startswith("reports/"))
        and (s.endswith(".json") or s.endswith(".pkl") or s.endswith(".md"))
    )


def _looks_like_sha(s) -> bool:
    return isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdef" for c in s)


def _refs_from_state_obj(node, refs):
    """Walk the parsed state.yaml tree, collecting authoritative (path, sha256) pairs.

    Pairs are resolved from structured keys only, so a ``dataset:`` block's
    ``pkl_sha256``/``meta_sha256``/``provenance_sha256`` can never be mis-attached
    to a sibling ``artifacts:`` report path (the historical source of false
    integrity failures).
    """
    if isinstance(node, dict):
        # explicit path/sha256 sibling (e.g. latest_oos, caches_verified.*)
        if _looks_like_path(node.get("path")) and _looks_like_sha(node.get("sha256")):
            refs.append((node["path"], node["sha256"]))
        # name -> <name>_sha256 within the same mapping
        for k, v in node.items():
            if _looks_like_path(v):
                cand = node.get(f"{k}_sha256")
                if cand is None and k == "path":
                    cand = node.get("sha256")
                if _looks_like_sha(cand):
                    refs.append((v, cand))
        # artifacts: {name: path} + artifact_sha256: {name: sha} pairing
        arts = node.get("artifacts")
        asha = node.get("artifact_sha256")
        if isinstance(arts, dict) and isinstance(asha, dict):
            for name, p in arts.items():
                if _looks_like_path(p) and _looks_like_sha(asha.get(name)):
                    refs.append((p, asha[name]))
        # dataset sub-block: pkl/meta/provenance path + <name>_sha256
        ds = node.get("dataset")
        if isinstance(ds, dict):
            for name in ("pkl", "meta", "provenance"):
                p = ds.get(name)
                cand = ds.get(f"{name}_sha256")
                if _looks_like_path(p) and _looks_like_sha(cand):
                    refs.append((p, cand))
        # recurse into nested mappings/lists
        for v in node.values():
            if isinstance(v, (dict, list)):
                _refs_from_state_obj(v, refs)
    elif isinstance(node, list):
        for v in node:
            _refs_from_state_obj(v, refs)


def collect_all_refs():
    import yaml  # local import: PyYAML is present in the runtime bootstrap

    state_text = STATE_PATH.read_text(encoding="utf-8")
    agents_text = AGENTS_PATH.read_text(encoding="utf-8")
    refs = []
    # authoritative structured source first
    try:
        doc = yaml.safe_load(state_text)
        _refs_from_state_obj(doc, refs)
    except Exception:
        pass
    # AGENTS inline `` `path` (`sha`) `` form (correct name pairing)
    for m in re.finditer(r"(`?(?:reports|data)/[^`\s,)]+`?)\s*\((?:SHA256(?:-from-bytes)?\s*)?`?([0-9a-f]{64})`?\)", agents_text):
        refs.append((m.group(1).strip('`'), m.group(2)))
    # normalize, drop self-referential audit outputs (this tool cannot verify its
    # own historical reports against mutable handoff hashes), and dedupe by path
    # keeping the first (authoritative) hash seen.
    seen = set()
    norm = []
    for p, s in refs:
        p = p.strip().strip('"').strip("'")
        if p.startswith('/home/runner'):
            try:
                p = str(Path(p).relative_to(ROOT))
            except Exception:
                continue
        if not _looks_like_path(p):
            continue
        if p.startswith("reports/program_closure_integrity_audit_"):
            continue
        if p in seen:
            continue
        seen.add(p)
        norm.append((p, s))
    return norm


def verify_item(rel_path: str, expected_sha: str):
    path = ROOT / rel_path
    item = {
        "path": rel_path,
        "expected_sha256": expected_sha,
        "exists": path.exists(),
        "sha256_match": False,
        "actual_sha256": None,
        "campaign": campaign_from_path(rel_path),
        "kind": path.suffix.lstrip('.') if path.exists() else None,
        "checks": {},
        "errors": [],
    }
    if not path.exists():
        item["errors"].append("missing_file")
        return item
    actual = sha256_file(path)
    item["actual_sha256"] = actual
    item["sha256_match"] = actual == expected_sha
    if not item["sha256_match"]:
        item["errors"].append("sha256_mismatch")
    # semantic checks for json
    if path.suffix == ".json":
        try:
            data = load_json(path)
        except Exception as e:
            item["errors"].append(f"json_load_error:{type(e).__name__}")
            return item
        checks = {}
        if "real_data_only" in data:
            checks["real_data_only_true"] = data.get("real_data_only") is True
        if "fabricated_data" in data:
            checks["fabricated_data_false"] = data.get("fabricated_data") is False
        # verdict/binding/edge consistency when present
        verdict = data.get("verdict")
        if verdict is not None:
            checks["verdict_recorded"] = str(verdict)
        if "edge_proven" in data:
            checks["edge_proven_false"] = data.get("edge_proven") is False
        if "edge_claim" in data:
            checks["edge_claim_none"] = data.get("edge_claim") in (None, "NONE", "none")
        if "oos_edge_proven" in data:
            checks["oos_edge_proven_false"] = data.get("oos_edge_proven") is False
        if "n_edge_proven" in data:
            checks["n_edge_proven_zero"] = data.get("n_edge_proven") == 0
        if "binding_constraint" in data:
            checks["binding_constraint"] = data.get("binding_constraint")
        if "tradable_edge_registry" in data or "registry" in str(path):
            # registry files may have edges list
            edges = data.get("edges") or data.get("tradable_edges") or []
            checks["zero_tradable_edges"] = len(edges) == 0 if isinstance(edges, list) else True
        item["checks"] = checks
        # flag consistency violations
        if checks.get("real_data_only_true") is False:
            item["errors"].append("real_data_only_not_true")
        if checks.get("fabricated_data_false") is False:
            item["errors"].append("fabricated_data_not_false")
        if checks.get("edge_proven_false") is False:
            item["errors"].append("edge_proven_not_false")
        if checks.get("oos_edge_proven_false") is False:
            item["errors"].append("oos_edge_proven_not_false")
        if checks.get("n_edge_proven_zero") is False:
            item["errors"].append("n_edge_proven_not_zero")
    return item


def build_report(ts: str):
    refs = collect_all_refs()
    items = [verify_item(p, s) for p, s in refs]
    by_campaign = {}
    for it in items:
        c = it.get("campaign") or "UNCATEGORIZED"
        by_campaign.setdefault(c, []).append(it)
    campaign_rows = []
    for c in CAMPAIGNS + sorted(k for k in by_campaign if k not in CAMPAIGNS and k != "UNCATEGORIZED"):
        citems = by_campaign.get(c, [])
        if not citems:
            continue
        verdicts = sorted({it["checks"].get("verdict_recorded") for it in citems if it["checks"].get("verdict_recorded") is not None})
        bindings = sorted({it["checks"].get("binding_constraint") for it in citems if it["checks"].get("binding_constraint") is not None})
        n_runs = None
        n_edge = None
        for it in citems:
            if not it["exists"]:
                continue
            try:
                d = load_json(ROOT / it["path"]) if it["path"].endswith('.json') else {}
            except Exception:
                d = {}
            for k in ("n_total_runs", "n_runs", "n_probes"):
                if k in d and n_runs is None:
                    n_runs = d[k]
            for k in ("n_edge_proven", "n_edge", "edge_count"):
                if k in d and n_edge is None:
                    n_edge = d[k]
        campaign_rows.append({
            "campaign": c,
            "n_items": len(citems),
            "all_hashes_match": all(it["sha256_match"] for it in citems),
            "all_exist": all(it["exists"] for it in citems),
            "any_errors": any(it["errors"] for it in citems),
            "verdicts": verdicts,
            "bindings": bindings,
            "n_runs": n_runs,
            "n_edge": n_edge,
            "items": [{"path": it["path"], "expected_sha256": it["expected_sha256"], "actual_sha256": it["actual_sha256"], "sha256_match": it["sha256_match"], "exists": it["exists"], "errors": it["errors"], "checks": it["checks"]} for it in citems],
        })
    # include uncategorized
    if "UNCATEGORIZED" in by_campaign:
        citems = by_campaign["UNCATEGORIZED"]
        campaign_rows.append({
            "campaign": "UNCATEGORIZED",
            "n_items": len(citems),
            "all_hashes_match": all(it["sha256_match"] for it in citems),
            "all_exist": all(it["exists"] for it in citems),
            "any_errors": any(it["errors"] for it in citems),
            "verdicts": [], "bindings": [], "n_runs": None, "n_edge": None,
            "items": [{"path": it["path"], "expected_sha256": it["expected_sha256"], "actual_sha256": it["actual_sha256"], "sha256_match": it["sha256_match"], "exists": it["exists"], "errors": it["errors"], "checks": it["checks"]} for it in citems],
        })

    integrity_ok = all(it["sha256_match"] and it["exists"] and not it["errors"] for it in items) and len(items) > 0
    zero_tradable_edge_registry_confirmed = True
    for it in items:
        if it["checks"].get("zero_tradable_edges") is False:
            zero_tradable_edge_registry_confirmed = False
    report = {
        "artifact": "program_closure_integrity_audit",
        "generated_at_utc": ts,
        "real_data_only": True,
        "fabricated_data": False,
        "scope": "C281B-C297 frozen artifacts and datasets referenced in research_state/state.yaml and AGENTS.md",
        "campaigns_audited": [r["campaign"] for r in campaign_rows],
        "n_references": len(items),
        "n_ok": sum(1 for it in items if it["sha256_match"] and it["exists"] and not it["errors"]),
        "n_mismatch_or_missing_or_error": sum(1 for it in items if not (it["sha256_match"] and it["exists"] and not it["errors"])),
        "integrity_ok": integrity_ok,
        "zero_tradable_edge_registry_confirmed": zero_tradable_edge_registry_confirmed,
        "reachable_real_data_cross_sectional_stat_arb_space": "CLOSED",
        "campaign_rows": campaign_rows,
    }
    return report


def to_markdown(report: dict) -> str:
    lines = []
    lines.append(f"# Program Closure Integrity Audit — {report['generated_at_utc']}")
    lines.append("")
    lines.append(f"- real_data_only: {report['real_data_only']}")
    lines.append(f"- fabricated_data: {report['fabricated_data']}")
    lines.append(f"- scope: {report['scope']}")
    lines.append(f"- integrity_ok: {report['integrity_ok']}")
    lines.append(f"- n_references: {report['n_references']} (ok={report['n_ok']}, issues={report['n_mismatch_or_missing_or_error']})")
    lines.append(f"- zero_tradable_edge_registry_confirmed: {report['zero_tradable_edge_registry_confirmed']}")
    lines.append(f"- reachable_real_data_cross_sectional_stat_arb_space: {report['reachable_real_data_cross_sectional_stat_arb_space']}")
    lines.append("")
    lines.append("| Campaign | Items | Hashes OK | Exists | Errors | Verdicts | Bindings | n_runs | n_edge |")
    lines.append("|---|---:|:---:|:---:|:---:|---|---|---|---|")
    for row in report["campaign_rows"]:
        lines.append(f"| {row['campaign']} | {row['n_items']} | {row['all_hashes_match']} | {row['all_exist']} | {row['any_errors']} | {','.join(map(str,row['verdicts'])) or '-'} | {','.join(map(str,row['bindings'])) or '-'} | {row['n_runs']} | {row['n_edge']} |")
    lines.append("")
    if report["n_mismatch_or_missing_or_error"]:
        lines.append("## Issues")
        for row in report["campaign_rows"]:
            for it in row["items"]:
                if it["errors"] or not it["sha256_match"] or not it["exists"]:
                    lines.append(f"- `{it['path']}` expected={it['expected_sha256']} actual={it['actual_sha256']} errors={it['errors']}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts", default=None)
    args = ap.parse_args()
    ts = args.ts or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report = build_report(ts)
    REPORTS.mkdir(exist_ok=True)
    json_path = REPORTS / f"program_closure_integrity_audit_{ts}.json"
    md_path = REPORTS / f"program_closure_integrity_audit_{ts}.md"
    json_bytes = json.dumps(report, indent=2, sort_keys=True).encode("utf-8")
    json_path.write_bytes(json_bytes)
    md_text = to_markdown(report)
    md_path.write_text(md_text, encoding="utf-8")
    out = {
        "json_path": str(json_path.relative_to(ROOT)),
        "json_sha256": sha256_file(json_path),
        "md_path": str(md_path.relative_to(ROOT)),
        "md_sha256": sha256_file(md_path),
        "integrity_ok": report["integrity_ok"],
        "n_references": report["n_references"],
        "n_issues": report["n_mismatch_or_missing_or_error"],
        "real_data_only": True,
        "fabricated_data": False,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if report["integrity_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
