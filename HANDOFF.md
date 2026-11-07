## READ THIS FIRST — C122 INITIAL TASK (20261107T041255Z, refreshed for next agentic session; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104–C120 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C121 DONE (20261107T040732Z–041147Z):** `VOLUME_FUZZY_ENTROPY_SHOCK_MR` — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_fuzzy_entropy_shock_mr_costed_oos_20261107T040732Z.json` (sha256 `ff6d75383bb7d07772712a39d7eb4bcb1ac65e8ab34fd7f1190a3ea0a2e198b3`, `real_data_only=true`, `fail_closed=true`; `n_assets=11`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; sums `fee0_slip0=1.554174…`, `fee5_slip5=-0.311826…`, `fee10_slip10=-2.177826…`, `fee20_slip20=-5.909826…`, `fee40_slip40=-13.373826…`).
  - Script: `scripts/run_real_quote_volume_fuzzy_entropy_shock_mr_costed_oos.py` (sha256 `138be16505e2235184a1fbaf58c73deda5d4ccb2ac058621fbcb7cd546ed1337`). Pre-stated: FuzzyEn (Chen 2007/2009) on log-volume returns, W_FE=168, m=2, r=0.2*std, n=2, demeaned m-vectors Chebyshev, `A=exp(-(d/r)^n)`, self-matches excluded, `FuzzyEn=ln(phi^m)-ln(phi^(m+1))`, fade shocks vs ALB=336.
  - Distinctness (grep-verified before impl): `fuzzy_entropy/fuzzyen/FuzzyEn` absent from scripts/ and reports/. Distinct from C102 ApEn (hard Heaviside, includes self-matches) and C106/C120 SampEn/MSE (hard tolerance, `-ln(A/B)`; C120 coarse-grains `tau={2,3,5}`): continuous exponential membership on demeaned vectors — different similarity functional, not monotonic. Distinct from C104–C120 lineage (wavelet entropy, Hurst RS, SampEn/MSE, SVD, Fisher Information, attention, increment, permutation variance, fluctuation complexity, range entropy, cumulative residual entropy, dispersion entropy).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T041147Z.json` (sha256 `c17549a5160034a0c129febdcd25866436b5ce4746b86b9d89b7762861965971`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry (latest): `reports/strategy_edge_registry_20261107T041147Z.json` (sha256 `dd5492697d70ff3f79d0e8dbb8b0a72eb6cfa230eb4143f757f185c22392d684`; supersedes C120 registry `20261107T030825Z` sha `0b5aa8bd669e31480ffdc5ff0b34fd5f328e914fc9e0854adab538f54147836a`; includes C118–C121; `edge_claim: NONE`).
  - Summary: `reports/campaign121_execution_summary_20261107T041147Z.json` (sha256 `3aaf5245888d133724045a8869a55939e33ff0d10c682e9a66ef6b17fd40c5f0`).
  - Pytest: `python3 -m pytest -q --tb=no` → `No module named pytest` (recorded honestly; not fabricated).
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed (`No module named pytest`); record honestly.

### NEXT FOCUS CAMPAIGN — C122 R-B new unused entropy/complexity family (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C121 done — do NOT rerun. C122 is PENDING and must be executed. **Already used in recent lineage (C111–C121):** SVD entropy, Fisher Information, attention entropy, increment entropy, permutation variance, fluctuation complexity, range entropy, cumulative residual entropy, dispersion entropy, multiscale sample entropy, fuzzy entropy. **Also present in repo scripts/reports (treat as used unless you grep-verify and justify true non-overlap):** ApEn, SampEn, spectral/permutation/bubble/slope/wavelet entropy, DFA, Hurst/RS, Higuchi/Petrosian/Katz FD, LZ76, Hjorth mobility/complexity, TKEO, ZCR, OU halflife, variance ratio. **Viable C122 candidates to grep-verify first:** Rényi entropy (order `q!=1`, distinct from Shannon/spectral), Tsallis entropy (non-extensive `q`, distinct), phase entropy / instantaneous-phase (Hilbert transform), envelope entropy (Hilbert amplitude distribution), distribution entropy (eCDF-bin distances; distinct from dispersion/sample families), or a genuinely distinct compressibility proxy (e.g., `zlib/gzip` length ratio on quantized series) — **only if grep shows zero prior `*_shock_mr_costed_oos` use** and you pre-state distinctness. If a candidate collides, pick another unused family and document.

#### Step 0 — Grep-verify distinctness + readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
# replace <FAMILY> with chosen candidate (e.g. renyi_entropy|tsallis_entropy|phase_entropy|envelope_entropy|distribution_entropy)
grep -rl "<FAMILY>" scripts/ reports/ 2>&1 | head -12
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
```

#### Step 1 — Run C122 chosen family (PRIORITY 1)
1. Feature must be pre-stated and distinct from C104–C121 (and grep-verified against repo history). Fail-closed on degenerate/non-finite.
2. Signal (fail-closed MR): `z = (feature - ALB_mean) / ALB_std`, `ALB=336` (or pre-state justified equivalent; keep WF/costs/B&H exact). `entry_z >= 1.5` → fade; `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. WF/costs/B&H (exact): `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. Emit: `reports/real_quote_volume_<family>_shock_mr_costed_oos_<UTC>.json` (new C122 timestamp). Reference prior registry `reports/strategy_edge_registry_20261107T041147Z.json` (sha `dd5492697d70ff3f79d0e8dbb8b0a72eb6cfa230eb4143f757f185c22392d684`) and C121 OOS sha `ff6d75383bb7d07772712a39d7eb4bcb1ac65e8ab34fd7f1190a3ea0a2e198b3`.

#### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T041147Z.json` (sha `dd5492697d70ff3f79d0e8dbb8b0a72eb6cfa230eb4143f757f185c22392d684`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C120–C121 and add C122 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign122_execution_summary_<UTC>.json` listing all new artifact paths + sha256.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run.
- **No status summary before >= 3 new concrete report artifacts exist for C122** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C121 marked DONE with SHAs; C104–C121 locked — no reruns.
- Registry C121 supersedes C120 (`dd549269…` → `0b5aa8bd…`) carried forward as latest.
- Explicit "used family" list expanded (incl. fuzzy entropy, ApEn/SampEn/spectral/permutation/bubble/slope/wavelet/DFA/Hurst/FDs/LZ76/Hjorth/TKEO/ZCR/OU/VR) to reduce collision risk; viable C122 candidates pre-listed with grep-first requirement.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.

### Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rl 'renyi_entropy\|tsallis_entropy\|phase_entropy\|envelope_entropy\|distribution_entropy' scripts/ reports/ 2>&1 | head -12
```
Choose a genuinely distinct C122 family (e.g., Rényi entropy with fixed pre-stated `q`, or phase/envelope entropy via Hilbert transform — only if grep-clean for `*_shock_mr`), grep-verify, implement/run C122, emit C122 OOS, then complete Step 2. **Do not stop until Step 2 complete with >=3 new C122 artifacts.**
