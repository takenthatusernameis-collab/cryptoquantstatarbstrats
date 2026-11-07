## READ THIS FIRST — C120 INITIAL TASK (20261107T021112Z, produced after C119 completion; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104–C118 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C119 DONE (20261107T020946Z–021112Z):** `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` (Dispersion Entropy, Rostaghi & Azami 2016; NCDF mapping of log-volume returns over `W_DE=168` into `c=6` classes, embedding `m=2, d=1`; Shannon entropy normalized by `log(c^m)`; fade DE shocks vs `ALB=336`; `entry_z>=1.5`, `exit_z<0.5`, `max_hold=24`; WF `720/168/168`; cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; B&H same OOS windows) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_dispersion_entropy_shock_mr_costed_oos_20261107T021053Z.json` (sha256 `3eb0a9fb636afe31bd9b247d64dddc641bba3f70f7631faf0908c0415accd6d9`, `real_data_only=true`, `fail_closed=true`).
  - Script: `scripts/run_real_quote_volume_dispersion_entropy_shock_mr_costed_oos.py` (updated to C119 metadata; fresh run, prior C109 artifact NOT reused).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T021112Z.json` (sha256 `fbb6e9cbae0994b1fbb7b71fd967c8955cb1161c91b3287b5308d323da723356`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry (latest, supersedes C118): `reports/strategy_edge_registry_20261107T021112Z.json` (sha256 `a44a0764306ef11e94c4d65521093fa8722b114c86fa5f38d4dd887db4ed1ee6`, supersedes `strategy_edge_registry_20261107T020709Z.json` sha `c28f530de58334ee9e56ca2a2cc8e9eba752c6040c2b15ff75074a4163a8e478`; structurally consistent `campaign/supersedes/lineage`; includes C118+C119; `edge_claim: NONE`).
  - Summary: `reports/campaign119_execution_summary_20261107T021112Z.json` (sha256 `e291893a337355dbe3d7565616f9c4089e946e87a04e0e898146ce33a8724719`).
  - Pytest: `python3 -m pytest -q --tb=no` → `No module named pytest` (recorded honestly; not fabricated).
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.

### NEXT FOCUS CAMPAIGN — C120 R-B `VOLUME_SAMPLE_ENTROPY_VARIANT_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C119 done — do NOT rerun. C120 is PENDING and must be executed. HANDOFF fallback ladder (only if primary cannot be made distinct): `VOLUME_SAMPLE_ENTROPY_VARIANT_SHOCK_MR` → new unused entropy/complexity family (grep-verify each). **Important:** basic `VOLUME_SAMPLE_ENTROPY_SHOCK_MR` ran in C106 — the new variant MUST be pre-stated and genuinely distinct (e.g., different embedding dimension `m`, tolerance/radius `r` rule, coarse-graining/multiscale SampEn, SampEn-on-residuals/returns transform, or another clearly non-identical parameterization/mechanism). If you cannot justify distinctness, pick a different unused entropy/complexity family and document grep-verified distinctness. Grep-verify before impl/run.

#### Step 0 — Grep-verify distinctness + readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
# replace <FAMILY> tokens with your chosen candidate
grep -rl "<FAMILY>" scripts/ reports/ 2>&1 | head -12
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
```

#### Step 1 — Run C120 chosen family (PRIORITY 1)
1. Feature must be pre-stated and distinct from C104–C119 (wavelet entropy, Hurst RS, sample entropy/C106, permutation entropy, slope entropy, dispersion entropy/C109/C119, bubble/SVD/Fisher/attention/increment/permutation variance/fluctuation complexity/range/cumulative residual entropy families present in lineage). Fail-closed on degenerate/non-finite.
2. Signal (fail-closed MR): `z = (feature - ALB_mean) / ALB_std`, `ALB=336` (or pre-state justified equivalent; keep WF/costs/B&H exact). `entry_z >= 1.5` → fade; `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. WF/costs/B&H (exact): `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. Emit: `reports/real_quote_volume_<family>_shock_mr_costed_oos_<UTC>.json` (new C120 timestamp). Reference prior registry `reports/strategy_edge_registry_20261107T021112Z.json` (sha `a44a0764306ef11e94c4d65521093fa8722b114c86fa5f38d4dd887db4ed1ee6`) and C119 OOS sha `3eb0a9fb636afe31bd9b247d64dddc641bba3f70f7631faf0908c0415accd6d9`.

#### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T021112Z.json` (sha `a44a0764306ef11e94c4d65521093fa8722b114c86fa5f38d4dd887db4ed1ee6`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C119 and add C120 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign120_execution_summary_<UTC>.json` listing all new artifact paths + sha256.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run. A SampEn variant must be meaningfully different from C106.
- **No status summary before >= 3 new concrete report artifacts exist for C120** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C119 marked DONE with SHAs; C104–C119 locked — no reruns.
- Registry structural consistency restored for C119 and carried forward as requirement.
- C120 candidate identified with explicit C106-variant distinctness warning to avoid invalid rerun.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.

### Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rl 'multiscale_sample_entropy\|coarse_grained_sample_entropy\|mse_shock' scripts/ reports/ 2>&1 | head -10
```
Choose a genuinely distinct C120 family (e.g., multiscale/coarse-grained sample-entropy variant if unused), grep-verify, implement/run C120, emit C120 OOS, then complete Step 2. **Do not stop until Step 2 complete with >=3 new C120 artifacts.**
