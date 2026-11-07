# READ THIS FIRST — C126 INITIAL TASK (20261107T050614Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C124 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C125 DONE (20261107T050257Z–050326Z, registry integrity reconciled 20261107T050430Z):** `VOLUME_RECURRENCE_RATE_SHOCK_MR` (RQA recurrence rate %REC = density of recurrence points on delay-embedded log-volume returns) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_recurrence_rate_shock_mr_costed_oos_20261107T050257Z.json` (sha256 `c210151797cdfc57fae1418fcbcd22fc1147dca4dc6bc4b474ea7cb11b39147e`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`).
  - Script: `scripts/run_real_quote_volume_recurrence_rate_shock_mr_costed_oos.py` (sha256 `4fb5836a4478d8882412fc7f48562e01c799c350512e3c0b43c30e420b32b8a5`). Pre-stated distinct (grep-verified 20261107T050257Z zero hits `recurrence_rate|%REC|recurrence_quant|rqa_` before C125): RQA phase-space recurrence density vs C124 Hilbert phase histogram entropy; distinct from C104–C124.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T050326Z.json` (sha256 `0679390cdf6afc6e4c8ed7b1fe9e34bc6d21e2c827b81ba6ceae25155f56c0fb`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry (latest, C125 entry included): `reports/strategy_edge_registry_20261107T050326Z.json` (sha256 `afc423bfb3e50e3d7821ffd70f2f7539aef8eadd2714dfd075f1b526dd98766d`; supersedes C124 registry `20261107T045938Z` sha `3ce0643763eec09bcd47a2944f4f8ab72638643318014606cbe16c9bef12c3e7`; 16 entries incl. C121–C125; `edge_claim: NONE`).
  - Summary: `reports/campaign125_execution_summary_20261107T050326Z.json` (SHAs reconciled to disk 20261107T050430Z).
  - Pytest: unavailable (`No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C125 marked DONE with disk-verified SHAs; C104–C125 locked — no reruns. C125 registry now includes C125 entry and summary SHAs reconciled.
- Latest registry carried forward: `strategy_edge_registry_20261107T050326Z.json` (sha `afc423bf…`).
- **C126 family pre-selected & grep-verified clean (20261107T050614Z):** `VOLUME_RQA_DETERMINISM_SHOCK_MR` — RQA determinism `%DET` = (sum of diagonal lines of length >= `l_min` in the recurrence matrix) / (total recurrence points) on delay-embedded log-volume returns. Grep `recurrence_determinism|%DET|laminarity|%LAM|rqa_det` over `scripts/ strategies/ backtest/ utils/` returned **zero hits**. Distinct from C125 `%REC` (recurrence density; no line-structure) and from all C104–C124 families (Hilbert phase/envelope entropy, distribution entropy, fuzzy/multiscale/sample/approx entropy, SVD/Fisher/attention/increment/permutation-variance/fluctuation-complexity/range/CRE/DispEn, spectral/permutation/bubble/slope/DFA/Hurst/Higuchi/Petrosian/Katz FD, LZ76, Hjorth/TKEO/OU/VR/BDS, etc.) and from BDS correlation-integral dependence (no diagonal-line recurrence quantification).
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C126 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C125 done — do NOT rerun. C126 is PENDING and must be executed.

### Step 0 — Readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
```
Reconfirm grep-zero for the pre-selected C126 family (record command+result in OOS `pre_stated_distinctness`):
```bash
grep -rn 'recurrence_determinism\|%DET\|laminarity\|%LAM\|rqa_det' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```

### Step 1 — Run C126 (PRIORITY 1)
1. **Feature (pre-stated, distinct, grep-verified):** `VOLUME_RQA_DETERMINISM_SHOCK_MR`. On `r_t = ln(v_t)-ln(v_{t-1})` (log-volume changes), build delay embedding `X_i = (r_i, r_{i+tau})` with `m=2, tau=1` over trailing window `W=168`. Recurrence matrix `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, else `0`; `eps = eps_scale * std(r_window)` with **pre-stated fixed** `eps_scale=0.5` (document exact choice). `%DET = (Σ_{l>=l_min} l * P(l)) / (Σ_{i!=j} R_{ij})` where `P(l)` counts diagonal lines of length `l` (exclude main diagonal); `l_min=2` (pre-stated). `%DET` in `[0,1]` when recurrence exists; **fail-closed** to `NaN`/no-signal on non-finite, degenerate std/eps, or zero recurrence points. Compute causally (rolling window).
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_determinism_shock_mr_costed_oos_<UTC>.json` (new C126 timestamp) and `scripts/run_real_quote_volume_rqa_determinism_shock_mr_costed_oos.py`. Reference prior registry `reports/strategy_edge_registry_20261107T050326Z.json` (sha `afc423bfb3e50e3d7821ffd70f2f7539aef8eadd2714dfd075f1b526dd98766d`) and C125 OOS sha `c210151797cdfc57fae1418fcbcd22fc1147dca4dc6bc4b474ea7cb11b39147e`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T050326Z.json` (sha `afc423bfb3e50e3d7821ffd70f2f7539aef8eadd2714dfd075f1b526dd98766d`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C122–C125 and add C126 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign126_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C126 pre-selected above; reconfirm & record).
- **No status summary before >= 3 new concrete report artifacts exist for C126** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'recurrence_determinism\|%DET\|laminarity\|%LAM\|rqa_det' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C126 (RQA determinism %DET, spec above), emit C126 OOS, then complete Step 2. **Do not stop until Step 2 complete with >=3 new C126 artifacts.**
