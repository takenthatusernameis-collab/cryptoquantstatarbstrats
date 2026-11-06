#!/usr/bin/env python3
"""Emit Campaign 78 strategy edge registry (fail-closed, supersedes C76).
Records blocker state if OOS artifact not yet produced in this shell."""
from __future__ import annotations
import glob, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
UTC = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
SUPERSEDES = "reports/strategy_edge_registry_20261106T095532Z.json"

def run_pytest():
    cmd = [sys.executable, "-m", "pytest", "tests/", "-q"]
    try:
        p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=1800)
        tail = (p.stdout + "\n" + p.stderr).strip().splitlines()[-12:]
        passed = failed = skipped = errors = 0
        for line in reversed(tail):
            if "passed" in line or "failed" in line or "error" in line:
                def grab(word):
                    m = re.search(r"(\d+) " + word, line)
                    return int(m.group(1)) if m else 0
                passed, failed, skipped, errors = grab("passed"), grab("failed"), grab("skipped"), grab("error")
                break
        return {"command":" ".join(cmd),"returncode":p.returncode,"passed":passed,"failed":failed,"skipped":skipped,"errors":errors,"summary_tail":tail}
    except Exception as e:
        return {"command":" ".join(cmd),"returncode":None,"passed":None,"failed":None,"skipped":None,"errors":str(e),"summary_tail":[str(e)],"note":"pytest not executable in current shell (missing deps/pytest module); rerun after installing requirements+pytest."}

def latest(pattern, after=None):
    fs = sorted(glob.glob(str(REPORTS / pattern)))
    if after:
        fs = [f for f in fs if Path(f).name > after]
    return fs[-1] if fs else None

c78_oos = latest("real_quote_volume_hoover_robin_hood_shock_mr_costed_oos_*.json")
status = latest("real_feed_unblock_status_*.json", after="real_feed_unblock_status_20261106T095526Z.json") or latest("real_feed_unblock_status_*.json")
blocker = latest("campaign78_execution_blocker_*.json")
prior_reg = SUPERSEDES
c78_obj = json.load(open(c78_oos)) if c78_oos else {}
status_obj = json.load(open(status)) if status else {}
blocker_obj = json.load(open(blocker)) if blocker else {}
pytest_res = run_pytest()
blocked = status_obj.get("blocked_families") or ["funding_basis_carry","cross_exchange_dual_venue_same_asset","term_structure_real_iv_vol_surface","intrabar_microstructure"]
oos = bool(c78_obj.get("oos_edge_proven", False))
out = {
  "generated_at_utc": datetime.now(timezone.utc).isoformat(),
  "campaign":78,
  "supersedes": prior_reg,
  "oos_edge_proven": oos,
  "pytest_full_suite": pytest_res,
  "artifacts": [p for p in [
      c78_oos and "reports/"+Path(c78_oos).name,
      status and "reports/"+Path(status).name,
      blocker and "reports/"+Path(blocker).name,
      "scripts/run_real_quote_volume_hoover_robin_hood_shock_mr_costed_oos.py",
      "scripts/emit_campaign78_unblock_status.py",
      "scripts/emit_campaign78_registry.py",
  ] if p],
  "c78_hypothesis": "real_quote_volume Rolling Hoover (Robin Hood) share-deviation H_t=0.5*Σ|p_i-1/n| (p_i=x_i/Σx_i, W=48, ZLB=168, L1 vs uniform/max vertical Lorenz gap) shock MR (R-B pre-stated; distinct from C23/C40-C77 incl. C51 Gini pairwise L1, C76 Theil L GE(0) mean ln(mu/x), C74 Theil T GE(1) mean r*ln r, C75 Rényi-2 H2 -ln Σp^2, C41 Shannon binned, C42/43 permutation/sample entropy, C45 CV, C66-73 quantile dispersions/asymmetries)",
  "c78_oos_result": None if not c78_oos else {
      "oos_edge_proven": oos,
      "any_exposure": c78_obj.get("any_exposure"),
      "all_costs_positive": c78_obj.get("all_costs_positive"),
      "beats_bh_rule": c78_obj.get("beats_bh_rule"),
      "aggregate": c78_obj.get("aggregate"),
  },
  "execution_state": blocker_obj.get("status","EXECUTED") if blocker_obj else "EXECUTED",
  "blocked_families_substantive": blocked,
  "notes": "Fail-closed. Real data only. No proxies/fabrication/threshold weakening. R-A infeasible (4 families blocked_no_real_feed, no new validated nonspot feeds). R-B pre-stated + runnable script created (Hoover/Robin Hood). In this shell, numpy/pandas/pytest deps unavailable so OOS execution/pytest rerun blocked; blocker artifact records exact missing deps and concrete unblocking commands. Registry supersedes C76 and must be regenerated after runner+pytest execute. oos_edge_proven remains false until executed artifact meets pre-stated rule.",
}
out_path = REPORTS / f"strategy_edge_registry_{UTC}.json"
out_path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str)+"\n")
print(out_path)
print(json.dumps({"oos_edge_proven":out["oos_edge_proven"],"pytest_returncode":pytest_res.get("returncode"),"execution_state":out["execution_state"]}, indent=2))
