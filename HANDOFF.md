## READ THIS FIRST — C117 INITIAL TASK (20261107T020138Z, produced after C116 completion; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104-C115 DONE → `oos_edge_proven=false` (see registry chain). Do NOT rerun.
- **C116 DONE (20261107T012033Z):** `VOLUME_FLUCTUATION_COMPLEXITY_SHOCK_MR` (rolling FC over `W_FC=168` on log-volume returns, Q=10 bins, transition matrix, normalized by `log(Q)^2`, fail-closed; fade shocks vs `ALB=336`, `entry_z>=1.5`, `exit_z<0.5`, `max_hold=24`, exec `t->t+1`; WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS) — `oos_edge_proven=false`.
  - OOS: `reports/real_quote_volume_fluctuation_complexity_shock_mr_costed_oos_20261107T012003Z.json` (sha256 `d368ea4aadb05c49bdefd9aaf917afb8c2d86ab8911bc38a633a2c225d026c28`).
  - Script: `scripts/run_real_quote_volume_fluctuation_complexity_shock_mr_costed_oos.py` (sha256 `0bc1a6126c9b3081a6d9ed1ac46aab8f8ee9b49f4b777f38eb6009b8c0c25c00`).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T012033Z.json` (sha256 `80f17a7c84b534baf2774d42deece3d043f83e03a701c60b43a1b58518993bb9`) — `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`, `rb_unblocked=true`. Does NOT block R-B.
  - Registry: `reports/strategy_edge_registry_20261107T012033Z.json` (sha256 `86a8d83e539729304aa2a4dcb90c84778706dbd12b5246fd990db676115b306d`, supersedes `20261107T011622Z`) — `edge_claim: NONE`.
  - Summary: `reports/campaign116_execution_summary_20261107T012033Z.json` (sha256 `?`).
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- pytest: not installed in this env (`python3 -m pytest` → `No module named pytest`, rc=1). Record honestly; do not fabricate. Lineage counts carried forward (928 passed/1 skipped/0 failed).

### NEXT FOCUS CAMPAIGN — C117 R-B `VOLUME_RANGE_ENTROPY_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104-C116 done — do NOT rerun. C117 is PENDING and must be executed. `VOLUME_RANGE_ENTROPY_SHOCK_MR` must be DISTINCT from prior families. Grep-verify before impl; fallback ladder if exists: `VOLUME_RANGE_ENTROPY_SHOCK_MR` → `VOLUME_CUMULATIVE_RESIDUAL_ENTROPY_SHOCK_MR` → `VOLUME_DISPERSION_ENTROPY_SHOCK_MR`.

#### Step 0 — Grep-verify distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "range_entropy\|RangeEntropy" scripts/ reports/ 2>&1 | head -20
ls scripts/run_real_quote_volume_range_entropy* reports/real_quote_volume_range_entropy* 2>&1 | head
```

#### Step 1 — Implement + run C117 `VOLUME_RANGE_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. Create `scripts/run_real_quote_volume_range_entropy_shock_mr_costed_oos.py` mirroring permutation variance shock MR script, campaign 117.
2. Feature (pre-stated, distinct): rolling range entropy over `W_RE=168` on log-volume returns; quantize returns into bins; compute Shannon entropy of range distribution; normalize; fail-closed on degenerate/non-finite.
3. Signal (fail-closed MR): `z = (RE - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade; `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
4. WF/costs/B&H (exact): `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
5. Run and emit: `reports/real_quote_volume_range_entropy_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report.
2. Pytest (record honestly).
3. Registry superseding `strategy_edge_registry_20261107T012033Z.json` (sha `86a8d83e539729304aa2a4dcb90c84778706dbd12b5246fd990db676115b306d`), include C111-C117. `edge_claim: NONE` unless edge rule holds.
4. Summary `reports/campaign117_execution_summary_<UTC>.json`.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify before implementation.
- **No status summary before >= 3 new concrete report artifacts exist for C117**.
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C116 marked DONE with SHAs; C104-C115 locked — no reruns.
- C117 feature pre-stated + grep-verify — prevents duplicate-family waste.
- Nonspot ingest decoupled from R-B — prevents blocker-loop paralysis.
- "No status before >=3 new artifacts" + mandatory impl/run — forces heavy work.
- Fallback ladder if C117 exists: `VOLUME_RANGE_ENTROPY_SHOCK_MR` → `VOLUME_CUMULATIVE_RESIDUAL_ENTROPY_SHOCK_MR` → `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` (grep-verify each).

### Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "range_entropy\|RangeEntropy" scripts/ reports/ 2>&1 | head -15
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl 2>&1 | head
```
Then implement `scripts/run_real_quote_volume_range_entropy_shock_mr_costed_oos.py` (C117 spec), run it, emit OOS report, then Step 2. **Do not stop until Step 2 complete with >=3 new C117 artifacts.**
