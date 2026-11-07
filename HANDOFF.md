## READ THIS FIRST — C121 INITIAL TASK (20261107T030900Z, refreshed for next agentic session; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104–C119 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C120 DONE (20261107T030455Z–030825Z):** `VOLUME_MULTISCALE_SAMPLE_ENTROPY_SHOCK_MR` (Multiscale Sample Entropy, Costa et al. 2005; coarse-grain log-volume returns at scales tau={2,3,5}, SampEn m=2, r=0.2*std excluding self-matches, feature=mean finite SampEn across scales; fade MSE shocks vs ALB=336; entry_z>=1.5, exit_z<0.5, max_hold=24; WF 720/168/168; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]]; B&H same OOS windows) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_multiscale_sample_entropy_shock_mr_costed_oos_20261107T030455Z.json` (sha256 `53103aa54e3f937c42904a6e3aaa1e2b3a6bb1f5562cd89d551fa77699e9b382`, `real_data_only=true`, `fail_closed=true`).
  - Script: `scripts/run_real_quote_volume_multiscale_sample_entropy_shock_mr_costed_oos.py` (sha256 `e85cc6de5487238e2e2a67f2a58e5ead34029020268f2ff2d2013c8fc6da52c7`; fresh C120 run).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T030825Z.json` (sha256 `4643ee44272b54d22df7c8f6e0b009cf42588a9e84ad58ee4c90ee14fe7360f2`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry (latest, supersedes C119): `reports/strategy_edge_registry_20261107T030825Z.json` (sha256 `0b5aa8bd669e31480ffdc5ff0b34fd5f328e914fc9e0854adab538f54147836a`, supersedes `strategy_edge_registry_20261107T021112Z.json` sha `a44a0764306ef11e94c4d65521093fa8722b114c86fa5f38d4dd887db4ed1ee6`; structurally consistent `campaign/supersedes/lineage`; includes C118+C119+C120; `edge_claim: NONE`).
  - Summary: `reports/campaign120_execution_summary_20261107T030825Z.json` (sha256 `8cda15ea8a517d651e15419a13e75d36a294b25b8446c62f7d8a47b9686f284e`).
  - Pytest: `python3 -m pytest -q --tb=no` → `No module named pytest` (recorded honestly; not fabricated).
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.

### NEXT FOCUS CAMPAIGN — C121 R-B new unused entropy/complexity family (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C120 done — do NOT rerun. C121 is PENDING and must be executed. HANDOFF fallback ladder (only if primary cannot be made distinct): grep-verify each candidate before impl/run. **Important:** `VOLUME_SAMPLE_ENTROPY_SHOCK_MR` (C106) and `VOLUME_MULTISCALE_SAMPLE_ENTROPY_SHOCK_MR` (C120) already ran — the new candidate MUST be pre-stated and genuinely distinct (e.g., Approximate Entropy/ApEn which INCLUDES self-matches unlike SampEn/MSE, spectral entropy, permutation entropy/Bandt-Pompe distinct from C115 permutation variance, LZ76 complexity, Higuchi/Petrosian/Katz fractal dimension, BDS statistic). If you cannot justify distinctness, pick a different unused entropy/complexity family and document grep-verified distinctness. Grep-verify before impl/run.

#### Step 0 — Grep-verify distinctness + readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
# replace <FAMILY> tokens with your chosen candidate (e.g. approximate_entropy|spectral_entropy|permutation_entropy|lz76|higuchi|bds)
grep -rl "<FAMILY>" scripts/ reports/ 2>&1 | head -12
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
```

#### Step 1 — Run C121 chosen family (PRIORITY 1)
1. Feature must be pre-stated and distinct from C104–C120 (wavelet entropy, Hurst RS, sample entropy/C106, multiscale sample entropy/C120, SVD/C111, Fisher Information/C112, attention/C113, increment/C114, permutation variance/C115, fluctuation complexity/C116, range entropy/C117, cumulative residual entropy/C118, dispersion entropy/C119 present in lineage). Fail-closed on degenerate/non-finite.
2. Signal (fail-closed MR): `z = (feature - ALB_mean) / ALB_std`, `ALB=336` (or pre-state justified equivalent; keep WF/costs/B&H exact). `entry_z >= 1.5` → fade; `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. WF/costs/B&H (exact): `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. Emit: `reports/real_quote_volume_<family>_shock_mr_costed_oos_<UTC>.json` (new C121 timestamp). Reference prior registry `reports/strategy_edge_registry_20261107T030825Z.json` (sha `0b5aa8bd669e31480ffdc5ff0b34fd5f328e914fc9e0854adab538f54147836a`) and C120 OOS sha `53103aa54e3f937c42904a6e3aaa1e2b3a6bb1f5562cd89d551fa77699e9b382`.

#### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T030825Z.json` (sha `0b5aa8bd669e31480ffdc5ff0b34fd5f328e914fc9e0854adab538f54147836a`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C120 and add C121 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign121_execution_summary_<UTC>.json` listing all new artifact paths + sha256.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run.
- **No status summary before >= 3 new concrete report artifacts exist for C121** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C120 marked DONE with SHAs; C104–C120 locked — no reruns.
- Registry structural consistency restored for C120 and carried forward as requirement.
- C121 candidate guidance with explicit distinctness requirement to avoid invalid rerun.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.

### Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rl 'approximate_entropy\|apen\|spectral_entropy\|permutation_entropy\|lz76\|higuchi\|petrosian\|bds' scripts/ reports/ 2>&1 | head -10
```
Choose a genuinely distinct C121 family (e.g., Approximate Entropy which includes self-matches unlike SampEn/MSE), grep-verify, implement/run C121, emit C121 OOS, then complete Step 2. **Do not stop until Step 2 complete with >=3 new C121 artifacts.**
