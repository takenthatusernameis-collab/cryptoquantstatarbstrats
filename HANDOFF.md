# READ THIS FIRST — C125 INITIAL TASK (20261107T045938Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C123 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C124 DONE (20261107T045907Z–045938Z):** `VOLUME_PHASE_ENTROPY_SHOCK_MR` (Hilbert analytic-signal instantaneous phase histogram entropy) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_phase_entropy_shock_mr_costed_oos_20261107T045907Z.json` (sha256 `4b876ec7f9212502affacf82c9f8e504f2833533810bbee9a0d8c22ad6107410`, `real_data_only=true`, `fail_closed=true`; `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=0.4518594428`, `fee5_slip5=-4.0421405572`, `fee10_slip10=-8.5361405572`, `fee20_slip20=-17.5241405572`, `fee40_slip40=-35.5001405572`; exposure present).
  - Script: `scripts/run_real_quote_volume_phase_entropy_shock_mr_costed_oos.py` (sha256 `77d8c7cc63466d2e9f675738385d33d2b253e18116bf795b18121cc9f13a2e87`). Pre-stated distinct (grep-verified 20261107T045530Z zero hits `phase_entropy|instantaneous_phase|inst_phase|unwrapped_phase|hilbert_phase|analytic_phase` before C124): Hilbert phase vs C123 amplitude/envelope; distinct from C104–C123.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T045938Z.json` (sha256 `3ecc6818f8d4ea8b3c1b25d60eda99fd28247f44710cfbd9b3b6f2c0161423a3`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry (latest): `reports/strategy_edge_registry_20261107T045938Z.json` (sha256 `3ce0643763eec09bcd47a2944f4f8ab72638643318014606cbe16c9bef12c3e7`; supersedes C123 registry `20261107T045317Z` sha `6ca91bf20058f115c2474b828ff21211872c3b06409b3d1d7a8189b558051f5b`; includes C121–C124; `edge_claim: NONE`).
  - Summary: `reports/campaign124_execution_summary_20261107T045938Z.json` (sha256 `2037dd583ff3ae2f2e2fb3eb706e3d6e8ce50cf9b02bcee8a86b030c94fc207c`).
  - Pytest: `python3 -m pytest -q --tb=no` → `No module named pytest` (recorded honestly; not fabricated).
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C124 marked DONE with SHAs; C104–C124 locked — no reruns.
- Registry C124 (`3ce06437…`) supersedes C123 (`6ca91bf2…`) carried forward as latest.
- **C125 family must be pre-selected and grep-verified clean before implementation:** prefer `recurrence_rate` / `recurrence_quantification` (RQA recurrence rate %REC on phase-space/thresholded recurrence over trailing window) OR, if grep shows collision, another genuinely novel time-series complexity family. Candidate `phase_entropy`/Hilbert-phase family now USED (C124). C123 `envelope_entropy`/Hilbert-amplitude USED. `renyi`/`tsallis` (C75). `zcr` (C100). DistEn/DispEn/ApEn/SampEn/MSE/FuzzyEn/CRE/FC/range entropy/spectral/permutation/bubble/slope/DFA/Hurst/FD/LZ76/Hjorth/TKEO/OU/variance-ratio families USED per C104–C124 lineage. **Grep-verify the chosen name against `scripts/ reports/ strategies/ backtest/ utils/` and record zero hits (or explain) before coding.**
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C125 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C124 done — do NOT rerun. C125 is PENDING and must be executed.

### Step 0 — Readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
```
Then **pre-state + grep-verify** a distinct C125 feature family (record the grep command and zero-hit result in the OOS artifact `pre_stated_distinctness` / notes). Do not implement until grep is clean.

### Step 1 — Run C125 (PRIORITY 1)
1. Feature pre-stated and distinct (grep-verified before run): e.g. `recurrence_rate` = RQA %REC (density of recurrence points under threshold ε on delay-embedded log-volume returns, m=2,τ=1, ε as fraction of std or fixed per pre-stated rule) over trailing window `W=168`, computed causally; fail-closed on degenerate/non-finite. **Document exact definition.** Alternatively choose any genuinely novel complexity/stat family that passes grep (e.g. `lempel_ziv_2d`-style not applicable 1D — pick a valid 1D family; avoid reusing `lz76`).
2. Signal (fail-closed MR): `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade; `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. WF/costs/B&H (exact): `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. Emit: `reports/real_quote_volume_<family>_shock_mr_costed_oos_<UTC>.json` (new C125 timestamp). Reference prior registry `reports/strategy_edge_registry_20261107T045938Z.json` (sha `3ce0643763eec09bcd47a2944f4f8ab72638643318014606cbe16c9bef12c3e7`) and C124 OOS sha `4b876ec7f9212502affacf82c9f8e504f2833533810bbee9a0d8c22ad6107410`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T045938Z.json` (sha `3ce0643763eec09bcd47a2944f4f8ab72638643318014606cbe16c9bef12c3e7`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C122–C124 and add C125 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign125_execution_summary_<UTC>.json` listing all new artifact paths + sha256.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run.
- **No status summary before >= 3 new concrete report artifacts exist for C125** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# choose & grep-verify a novel C125 family (example):
grep -rn 'recurrence_rate\|recurrence_quant\|%REC\|rqa_' scripts/ reports/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C125, emit C125 OOS, then complete Step 2. **Do not stop until Step 2 complete with >=3 new C125 artifacts.**
