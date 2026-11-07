## READ THIS FIRST — C118 INITIAL TASK (20261107T020445Z, produced after C117 completion; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104-C115 DONE → `oos_edge_proven=false` (see registry chain). Do NOT rerun.
- **C116 DONE (20261107T012033Z):** `VOLUME_FLUCTUATION_COMPLEXITY_SHOCK_MR` — `oos_edge_proven=false`.
- **C117 DONE (20261107T020310Z / summary+registry 20261107T020417Z):** `VOLUME_RANGE_ENTROPY_SHOCK_MR` (rolling Range Entropy over W_RE=168 on log-volume returns; Q=10 equal-width bins; adjacent transition matrix T_ij and marginals p_i; FC=sum T_ij*(log(p_j/p_i))^2 normalized by log(Q)^2 clipped [0,1]; fade FC shocks vs ALB=336; WF 720/168/168; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]]; B&H same OOS) — `oos_edge_proven=false`, edge_claim: NONE.
  - OOS report: `reports/real_quote_volume_range_entropy_shock_mr_costed_oos_20261107T020310Z.json` (sha256 `868acc4a4f1bca5ee9d411cff834afa4cdaa2d8c622a0ad3327071d8eccb70b7`).
  - Script: `scripts/run_real_quote_volume_range_entropy_shock_mr_costed_oos.py` (sha256 `5a88e61c2b98f74a178941745408f7c00e6d2a50401136bbe4da516fc810eeea`).
  - Summary: `reports/campaign117_execution_summary_20261107T020417Z.json`.
  - Registry (supersedes C116): `reports/strategy_edge_registry_20261107T020417Z.json` (sha256 `3b241c1e1f9b5864d8d3eb19b9956b55c07609f110153c4461d666b631e60e79`, supersedes `strategy_edge_registry_20261107T012033Z.json` sha `86a8d83e539729304aa2a4dcb90c84778706dbd12b5246fd990db676115b306d`) — includes C111-C117, `edge_claim: NONE`.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T012033Z.json` — `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`, `rb_unblocked=true`. Does NOT block R-B.
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- pytest: not installed in this env (`python3 -m pytest` → `No module named pytest`, rc=1). Record honestly; do not fabricate. Lineage counts carried forward (928 passed/1 skipped/0 failed).

### NEXT FOCUS CAMPAIGN — C118 R-B `VOLUME_CUMULATIVE_RESIDUAL_ENTROPY_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104-C117 done — do NOT rerun. C118 is PENDING and must be executed. `VOLUME_CUMULATIVE_RESIDUAL_ENTROPY_SHOCK_MR` must be DISTINCT from prior families C111-C117. Grep-verify before impl; fallback ladder if exists: `VOLUME_CUMULATIVE_RESIDUAL_ENTROPY_SHOCK_MR` → `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` → new unused entropy/complexity family (grep-verify each).

#### Step 0 — Grep-verify distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "cumulative_residual\|CumulativeResidual" scripts/ reports/ 2>&1 | head -20
ls scripts/run_real_quote_volume_cumulative_residual_entropy* reports/real_quote_volume_cumulative_residual_entropy* 2>&1 | head
grep -rl "dispersion_entropy\|DispersionEntropy" scripts/ reports/ 2>&1 | head -20
```

#### Step 1 — Implement + run C118 `VOLUME_CUMULATIVE_RESIDUAL_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. Create `scripts/run_real_quote_volume_cumulative_residual_entropy_shock_mr_costed_oos.py` mirroring the range entropy shock MR script, campaign 118.
2. Feature (pre-stated, distinct): rolling cumulative residual entropy over `W_CRE=168` on log-volume returns; compute residuals from a rolling mean model, quantize residuals into bins, compute Shannon entropy of residual distribution; normalize by log(Q)^2; fail-closed on degenerate/non-finite.
3. Signal (fail-closed MR): `z = (CRE - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade; `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
4. WF/costs/B&H (exact): `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
5. Run and emit: `reports/real_quote_volume_cumulative_residual_entropy_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report.
2. Pytest (record honestly).
3. Registry superseding `strategy_edge_registry_20261107T020417Z.json` (sha `3b241c1e1f9b5864d8d3eb19b9956b55c07609f110153c4461d666b631e60e79`), include C111-C118. `edge_claim: NONE` unless edge rule holds.
4. Summary `reports/campaign118_execution_summary_<UTC>.json`.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify before implementation.
- **No status summary before >= 3 new concrete report artifacts exist for C118**.
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C117 marked DONE with SHAs; C104-C116 locked — no reruns.
- Stale HANDOFF corrected: C117 was already complete at 020310Z/020417Z; next is C118.
- C118 feature pre-stated + grep-verify — prevents duplicate-family waste.
- Nonspot ingest decoupled from R-B — prevents blocker-loop paralysis.
- "No status before >=3 new artifacts" + mandatory impl/run — forces heavy work.
- Fallback ladder if C118 exists: `VOLUME_CUMULATIVE_RESIDUAL_ENTROPY_SHOCK_MR` → `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` → new unused family (grep-verify each).

### Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "cumulative_residual\|CumulativeResidual" scripts/ reports/ 2>&1 | head -15
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl 2>&1 | head
```
Then implement `scripts/run_real_quote_volume_cumulative_residual_entropy_shock_mr_costed_oos.py` (C118 spec), run it, emit OOS report, then Step 2. **Do not stop until Step 2 complete with >=3 new C118 artifacts.**
