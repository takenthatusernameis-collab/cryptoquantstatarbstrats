"""Tests for the C287 testnet gateway fail-closed behavior.

Covers: fail-closed gates (missing/None/false never permissive), kill-switch
thresholds, audit hash-chain integrity, and the --blocker-artifacts path emitting
formal BLOCKED artifacts from real preflight evidence (no fabricated fills).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_c287_testnet_gateway.py"
PREFLIGHT = ROOT / "scripts" / "preflight_c287.py"

SYMBOLS = ("ADAUSDT", "AVAXUSDT", "BNBUSDT", "BTCUSDT", "DOTUSDT", "ETHUSDT",
           "LINKUSDT", "LTCUSDT", "POLUSDT", "SOLUSDT", "XRPUSDT")
ASSETS = tuple(s.replace("USDT", "") for s in SYMBOLS)


def test_gateway_script_exists_and_is_runnable(tmp_path) -> None:
    assert SCRIPT.exists(), f"missing C287 gateway script: {SCRIPT}"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--blocker-artifacts", "--reports-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    assert proc.returncode in (0, 2), f"unexpected exit {proc.returncode}: {proc.stderr}"
    result = json.loads(proc.stdout)
    assert result["campaign"] == "C287"
    assert result["mode"] == "BLOCKED_ARTIFACTS"
    assert "artifacts" in result
    names = {"gateway_spec", "live_run", "drift_report",
             "kill_switch_test", "summary"}
    assert set(result["artifacts"].keys()) == names, result["artifacts"].keys()


def test_blocker_artifacts_have_paths_and_sha256(tmp_path) -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--blocker-artifacts", "--reports-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    result = json.loads(proc.stdout)
    for kind, info in result["artifacts"].items():
        assert "path" in info and "sha256" in info, kind
        p = Path(info["path"])
        assert p.exists(), f"missing artifact {p}"
        actual = __import__("hashlib").sha256(p.read_bytes()).hexdigest()
        assert actual == info["sha256"], f"sha mismatch {p}"
        # Each artifact JSON carries real-data flags and blocker marker.
        obj = json.loads(p.read_text(encoding="utf-8"))
        assert obj.get("real_data_only") is True, kind
        assert obj.get("fabricated_data") is False, kind
        assert obj.get("blocker") is True, kind


def test_blocker_artifacts_no_fabricated_fills_no_simulated_gateway(tmp_path) -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--blocker-artifacts", "--reports-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    result = json.loads(proc.stdout)
    live = result["artifacts"]["live_run"]
    obj = json.loads(Path(live["path"]).read_text(encoding="utf-8"))
    assert obj.get("fabricated_fills") is False
    assert obj.get("simulated_gateway_presented_as_real") is False
    assert obj.get("run_status") == "BLOCKED_NO_LIVE_EXECUTION"


def test_blocker_artifacts_blockers_enumerated_with_cache_shas(tmp_path) -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--blocker-artifacts", "--reports-dir", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    result = json.loads(proc.stdout)
    spec = json.loads(Path(result["artifacts"]["gateway_spec"]["path"]).
                      read_text(encoding="utf-8"))
    assert spec.get("blocker") is True
    assert isinstance(spec.get("preflight_blockers"), list)
    assert len(spec["preflight_blockers"]) >= 1
    assert spec.get("spot_5m_sha256") == "d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f"
    assert spec.get("volume_1h_sha256") == "4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c"


def test_fail_closed_gates_reject_permissive_missing() -> None:
    sys.path.insert(0, str(ROOT))
    from scripts.run_c287_testnet_gateway import fail_closed_gates  # noqa: E402

    spot_df = pd.DataFrame({s: np.random.uniform(1, 100, 10) for s in SYMBOLS})
    volume_aligned = {"all_finite_positive": True}
    signal = pd.Series(1.0, index=ASSETS)

    rest_unhealthy = {"healthy": False, "endpoints": {}, "latency_ms": {}}
    ws_down = {"connected": False}
    g = fail_closed_gates(rest_unhealthy, ws_down, spot_df, volume_aligned,
                          signal, 2, True, 0, 100.0)
    assert g["all_pass"] is False
    assert "rest_healthy" in g["gates"] and g["gates"]["rest_healthy"]["pass"] is False
    assert "ws_connected" in g["gates"] and g["gates"]["ws_connected"]["pass"] is False

    # Missing signal -> not permissive
    g2 = fail_closed_gates({"healthy": True, "endpoints": {},
                            "latency_ms": {}},
                           {"connected": True}, spot_df, volume_aligned,
                           None, 2, True, 0, 100.0)
    assert g2["all_pass"] is False
    assert g2["gates"]["signal_finite_min_2k"]["pass"] is False


def test_kill_switch_trigger_and_flatten() -> None:
    sys.path.insert(0, str(ROOT))
    from scripts.run_c287_testnet_gateway import (  # noqa: E402
        AuditLogger, KillSwitch)

    audit_path = ROOT / ".c287_test_audit.jsonl"
    if audit_path.exists():
        audit_path.unlink()
    try:
        audit = AuditLogger(audit_path)
        ks = KillSwitch(audit)
        tripped, reasons = ks.check(
            {"consecutive_failures": 5}, 600.0, True)
        assert tripped is True
        assert len(reasons) >= 1
        assert ks.triggered is True
        assert ks.armed is False
        flatten = ks.flatten_positions()
        assert flatten["event"] == "flatten_positions"
        assert all(v == 0.0 for v in flatten["final_positions"].values())
        # Manual reset with wrong confirmation must fail.
        assert ks.require_manual_reset("wrong") is False
        assert ks.triggered is True
        # Correct confirmation derived from trigger time + reason.
        import hashlib
        expected = hashlib.sha256(
            f"c287-kill-reset:{ks.trigger_time}:{ks.trigger_reason}".encode(
                "utf-8")).hexdigest()[:16]
        assert ks.require_manual_reset(expected) is True
        assert ks.armed is True
        assert ks.triggered is False
        # Audit hash-chain integrity holds.
        assert audit.chain_integrity() is True
    finally:
        if audit_path.exists():
            audit_path.unlink()


def test_audit_hash_chain_tamper_evident() -> None:
    sys.path.insert(0, str(ROOT))
    from scripts.run_c287_testnet_gateway import AuditLogger  # noqa: E402

    audit_path = ROOT / ".c287_test_audit2.jsonl"
    if audit_path.exists():
        audit_path.unlink()
    try:
        audit = AuditLogger(audit_path)
        audit.emit(event="e1", bar=1, asset="BTC", side="buy", qty=1.0,
                   price=100.0, fee=0.1, slippage_bps=1.0, latency_ms=10.0,
                   gate_reasons=[])
        audit.emit(event="e2", bar=2, asset="ETH", side="sell", qty=1.0,
                   price=200.0, fee=0.2, slippage_bps=1.0, latency_ms=12.0,
                   gate_reasons=[])
        assert audit.chain_integrity() is True
        # Tamper with a line breaks the chain.
        lines = audit_path.read_text(encoding="utf-8").splitlines()
        rec = json.loads(lines[0])
        rec["price"] = 999.0
        lines[0] = json.dumps(rec, sort_keys=True)
        audit_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert audit.chain_integrity() is False
    finally:
        if audit_path.exists():
            audit_path.unlink()


def test_preflight_c287_exists_and_ready_captured() -> None:
    assert PREFLIGHT.exists()
    proc = subprocess.run(
        [sys.executable, str(PREFLIGHT), "--json"],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    result = json.loads(proc.stdout)
    assert "ready" in result and "blockers" in result
