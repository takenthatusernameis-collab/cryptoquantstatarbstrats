## READ THIS FIRST — C123 INITIAL TASK (20261107T042732Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104–C121 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C122 DONE (20261107T041843Z–042055Z):** `VOLUME_DISTRIBUTION_ENTROPY_SHOCK_MR` — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_distribution_entropy_shock_mr_costed_oos_20261107T041843Z.json` (sha256 `a18bb64d7f0f5b5dde049032a92d6503e9dc726ded273e658f2db1c9151cfba3`, `real_data_only=true`, `fail_closed=true`; `n_assets=11`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; sums `fee0_slip0=0.0981282200`, `fee5_slip5=-1.3708717800`, `fee10_slip10=-2.8398717800`, `fee20_slip20=-5.7778717800`, `fee40_slip40=-11.6538717800`).
  - Script: `scripts/run_real_quote_volume_distribution_entropy_shock_mr_costed_oos.py` (sha256 `0608fd06ae895e3878f9dd714d1d9b0b2ea31c7491d082c883942ab64e0baa0a`). Pre-stated: Distribution Entropy (Li 2015) on log-volume returns — phase-space reconstruct `m=2,delay=1`, histogram entropy of all inter-vector Chebyshev distances into `M_BINS=64` over `[0,d_max]`, `DistEn=H(p)/log2(M)`; `W_DE=168`, fade shocks vs `ALB=336` (z>=1.5 short, <=-1.5 long, exit |z|<0.5/max_hold=24/flip), `t->t+1`.
  - Distinctness (grep-verified before impl): `distribution_entropy/dist_en` absent from scripts/reports before C122. DistEn uses empirical *distribution* (histogram entropy) of inter-vector distances — distinct from ApEn/SampEn/MSE/FuzzyEn C102/C106/C120/C121 and dispersion entropy C119.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T042055Z.json` (sha256 `c43778aadd806e3c72a624a22cd814dc9932a6a655d47b06301361359d0256ef`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry (latest): `reports/strategy_edge_registry_20261107T042055Z.json` (sha256 `09b4dac2185098e14be07ca9be18f9544703015cbd1ba6673c54862b9c0c1860`; supersedes C121 registry `20261107T041147Z` sha `dd5492697d70ff3f79d0e8dbb8b0a72eb6cfa230eb4143f757f185c22392d684`; includes C121–C122; `edge_claim: NONE`).
  - Summary: `reports/campaign122_execution_summary_20261107T042055Z.json` (sha256 `6199ee09b8825fc21f47ca3814c999c994276f20a826c95b38cf86f40edbdf5d`).
  - Pytest: `python3 -m pytest -q --tb=no` → `No module named pytest` (recorded honestly; not fabricated).
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

### Bottlenecks removed (this handoff)
- C122 marked DONE with SHAs; C104–C122 locked — no reruns.
- Registry C122 supersedes C121 (`09b4dac2…` → `dd549269…`) carried forward as latest.
- **C123 family pre-selected and grep-verified clean:** `envelope_entropy` (Hilbert analytic-signal amplitude/envelope distribution entropy). `phase_entropy`, `envelope_entropy`, `compressibility_ratio`, `zlib`, `lzma` all return ZERO hits across scripts/reports/strategies/backtest/utils. `hilbert`/`analytic_signal` also unused repo-wide → genuinely distinct Hilbert-domain family, no overlap with C104–C122 time-domain/frequency-domain/complexity families.
- **Excluded (collide, do NOT use):** `renyi`/`tsallis` — already used as `*_shock_mr` feature family (`rolling_renyi2_collision_entropy_volume_shock_mr`, C75 artifacts `real_quote_volume_renyi2_collision_entropy_shock_mr_costed_oos_*.json`). All spectral/permutation/bubble/slope/DFA/Higuchi/Petrosian/Katz/LZ76/Hjorth/TKEO/ZCR/OU/variance-ratio families treated as used per prior lineage.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### NEXT FOCUS CAMPAIGN — C123 envelope_entropy shock MR (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C122 done — do NOT rerun. C123 is PENDING and must be executed. Chosen family `envelope_entropy` is pre-stated and grep-verified distinct (see Bottlenecks removed). Do not re-open candidate selection.

#### Step 0 — Readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'envelope_entropy\|phase_entropy\|hilbert\|analytic_signal' scripts/ reports/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Expect: `deps_ok`, all three cache files present, zero grep hits.

#### Step 1 — Run C123 envelope_entropy (PRIORITY 1)
1. Feature pre-stated and distinct: `envelope_entropy` = histogram entropy of the Hilbert-analytic-signal envelope (amplitude) distribution over trailing window `W=168`, normalized `En=H(p)/log2(M_BINS)` with `M_BINS=64`, computed causally on trailing data only. Fail-closed on degenerate/non-finite.
2. Signal (fail-closed MR): `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade; `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. WF/costs/B&H (exact): `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. Emit: `reports/real_quote_volume_envelope_entropy_shock_mr_costed_oos_<UTC>.json` (new C123 timestamp). Reference prior registry `reports/strategy_edge_registry_20261107T042055Z.json` (sha `09b4dac2185098e14be07ca9be18f9544703015cbd1ba6673c54862b9c0c1860`) and C122 OOS sha `a18bb64d7f0f5b5dde049032a92d6503e9dc726ded273e658f2db1c9151cfba3`.

#### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T042055Z.json` (sha `09b4dac2185098e14be07ca9be18f9544703015cbd1ba6673c54862b9c0c1860`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C121–C122 and add C123 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign123_execution_summary_<UTC>.json` listing all new artifact paths + sha256.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run.
- **No status summary before >= 3 new concrete report artifacts exist for C123** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
```
Then implement/run C123 `envelope_entropy`, emit C123 OOS, then complete Step 2. **Do not stop until Step 2 complete with >=3 new C123 artifacts.**
