## READ THIS FIRST — C124 INITIAL TASK (20261107T045530Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104–C122 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C123 DONE (20261107T045310Z–045317Z):** `VOLUME_ENVELOPE_ENTROPY_SHOCK_MR` (Hilbert analytic-signal amplitude/envelope distribution entropy) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_envelope_entropy_shock_mr_costed_oos_20261107T045310Z.json` (sha256 `4d5fced5db940833933fa3bf4f10683e12e41b6c2e0d7832fac957e30d67e780`, `real_data_only=true`, `fail_closed=true`; `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=0.7027041297`, `fee5_slip5=-1.4192958703`, `fee10_slip10=-3.5412958703`, `fee20_slip20=-7.7852958703`, `fee40_slip40=-16.2732958703`).
  - Script: `scripts/run_real_quote_volume_envelope_entropy_shock_mr_costed_oos.py` (sha256 `d08e57023a94cea3a3aa750538aa9914ee5e5108fc70e3f5383f92931471b9c4`). Pre-stated distinct (Hilbert-domain amplitude distribution entropy; distinct from C104–C122).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T045317Z.json` (sha256 `c1168ed9e7eb6e2ecacf122e14c0431430bbdd6d78469128307a0244088208ef`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry (latest): `reports/strategy_edge_registry_20261107T045317Z.json` (sha256 `6ca91bf20058f115c2474b828ff21211872c3b06409b3d1d7a8189b558051f5b`; supersedes C122 registry `20261107T042055Z` sha `09b4dac2185098e14be07ca9be18f9544703015cbd1ba6673c54862b9c0c1860`; includes C121–C123; `edge_claim: NONE`).
  - Summary: `reports/campaign123_execution_summary_20261107T045317Z.json` (sha256 `e73520a66418800be742c2fd04b5471871ef04021a6b98d5f0c45f99fa16921c`).
  - Pytest: `python3 -m pytest -q --tb=no` → `No module named pytest` (recorded honestly; not fabricated).
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

### Bottlenecks removed (this handoff)
- C123 marked DONE with SHAs; C104–C123 locked — no reruns.
- Registry C123 (`6ca91bf2…`) supersedes C122 (`09b4dac2…`) carried forward as latest.
- **C124 family pre-selected and grep-verified clean (20261107T045530Z):** `phase_entropy` = Hilbert instantaneous-phase distribution entropy. Grep over `scripts/ reports/ strategies/ backtest/ utils/` for `phase_entropy|instantaneous_phase|inst_phase|unwrapped_phase|hilbert_phase|analytic_phase` returns ZERO hits before C124. This is genuinely distinct from C123 `envelope_entropy` (amplitude/envelope) — phase vs amplitude of the same Hilbert/analytic-signal domain split — and distinct from C104–C122 time/frequency/complexity families. `hilbert`/`analytic_signal` usage confined to C123 envelope artifacts only.
- **Excluded (collide or used, do NOT use):** `envelope_entropy`/`hilbert` amplitude family (C123). `renyi`/`tsallis` (C75). `zcr` (C100), `autocorr` lag-1 (C51) — `acf_distribution_entropy` currently clean but do not repurpose `autocorr` constructs; prefer the pre-selected `phase_entropy`. All spectral/permutation/bubble/slope/DFA/Hurst/FD/LZ76/Hjorth/TKEO/OU/variance-ratio/ApEn/SampEn/MSE/FuzzyEn/CRE/DispEn/DistEn families treated as used per C104–C123 lineage.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### NEXT FOCUS CAMPAIGN — C124 phase_entropy shock MR (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C123 done — do NOT rerun. C124 is PENDING and must be executed. Chosen family `phase_entropy` is pre-stated and grep-verified distinct (see Bottlenecks removed). Do not re-open candidate selection.

#### Step 0 — Readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'phase_entropy\|instantaneous_phase\|inst_phase\|unwrapped_phase\|hilbert_phase\|analytic_phase' scripts/ reports/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Expect: `deps_ok`, all three cache files present, zero grep hits.

#### Step 1 — Run C124 phase_entropy (PRIORITY 1)
1. Feature pre-stated and distinct: `phase_entropy` = histogram entropy of the Hilbert analytic-signal **instantaneous phase** (e.g., `atan2(imag, real)`, optionally unwrapped/differenced as pre-stated; choose a fail-closed, causal definition and document it) over trailing window `W=168`, normalized `PhEn = H(p)/log2(M_BINS)` with `M_BINS=64` over a fixed phase range, computed causally on trailing data only. Fail-closed on degenerate/non-finite/constant-envelope/ill-defined phase.
2. Signal (fail-closed MR): `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade; `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. WF/costs/B&H (exact): `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. Emit: `reports/real_quote_volume_phase_entropy_shock_mr_costed_oos_<UTC>.json` (new C124 timestamp). Reference prior registry `reports/strategy_edge_registry_20261107T045317Z.json` (sha `6ca91bf20058f115c2474b828ff21211872c3b06409b3d1d7a8189b558051f5b`) and C123 OOS sha `4d5fced5db940833933fa3bf4f10683e12e41b6c2e0d7832fac957e30d67e780`.

#### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T045317Z.json` (sha `6ca91bf20058f115c2474b828ff21211872c3b06409b3d1d7a8189b558051f5b`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C122–C123 and add C124 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign124_execution_summary_<UTC>.json` listing all new artifact paths + sha256.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run.
- **No status summary before >= 3 new concrete report artifacts exist for C124** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'phase_entropy\|instantaneous_phase\|inst_phase\|unwrapped_phase\|hilbert_phase\|analytic_phase' scripts/ reports/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C124 `phase_entropy`, emit C124 OOS, then complete Step 2. **Do not stop until Step 2 complete with >=3 new C124 artifacts.**
