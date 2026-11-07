## READ THIS FIRST — C119 INITIAL TASK (20261107T020722Z, produced after C118 completion; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104–C117 DONE → `oos_edge_proven=false` (see registry lineage). Do NOT rerun.
- **C118 DONE (20261107T020658Z–020712Z):** `VOLUME_CUMULATIVE_RESIDUAL_ENTROPY_SHOCK_MR` (rolling cumulative residual entropy over `W_CRE=168` on log-volume returns; residuals from rolling mean, quantized into `Q=10` bins; Shannon entropy of residual distribution normalized by `log(Q)^2` clipped `[0,1]`; fade CRE shocks vs `ALB=336`; WF `720/168/168`; cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`; B&H same OOS windows) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_cumulative_residual_entropy_shock_mr_costed_oos_20261107T020658Z.json` (sha256 `431472461c4c932beba68b9ba2a64e7d9f09b40685d009c991431e6bdc1118af`, `real_data_only=true`, `fail_closed=true`).
  - Script: `scripts/run_real_quote_volume_cumulative_residual_entropy_shock_mr_costed_oos.py`.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T020706Z.json` (sha256 `e336c89c5e2231067d7bae4c5b1b9966ab0b9cfea28818fc5d1beb96103ece04`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Summary: `reports/campaign118_execution_summary_20261107T020712Z.json`.
  - Registry (latest, supersedes C117): `reports/strategy_edge_registry_20261107T020709Z.json` (sha256 `c28f530de58334ee9e56ca2a2cc8e9eba752c6040c2b15ff75074a4163a8e478`, supersedes `strategy_edge_registry_20261107T020417Z.json`; `edge_claim: NONE`). **Integrity note:** registry `campaign` field/`entries` currently reflect C117 while `campaigns[]` includes C118 — next registry MUST be structurally consistent, include C111–C118 in lineage/entries as appropriate, and add C119.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- pytest: not installed in this env (`python3 -m pytest` → `No module named pytest`). Record honestly; do not fabricate. Carry lineage test counts forward honestly.

### NEXT FOCUS CAMPAIGN — C119 R-B `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C118 done — do NOT rerun. C119 is PENDING and must be executed. Script exists: `scripts/run_real_quote_volume_dispersion_entropy_shock_mr_costed_oos.py` (header indicates campaign 109 lineage; verify it is fit for C119 spec or adapt to a fresh C119 run with correct campaign metadata). Old artifact `reports/real_quote_volume_dispersion_entropy_shock_mr_costed_oos_20261107T000606Z.json` exists — do NOT treat as C119 completion; emit a new C119-stamped OOS report. Fallback ladder only if C119 family cannot be run distinctly: `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` → `VOLUME_SAMPLE_ENTROPY_VARIANT_SHOCK_MR` (new, grep-verify) → new unused entropy/complexity family (grep-verify each). Grep-verify before impl/run.

#### Step 0 — Grep-verify distinctness + script readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -n "^\\s*\\\"campaign\\\"\\|CAMP" scripts/run_real_quote_volume_dispersion_entropy_shock_mr_costed_oos.py | head -8
grep -rl "dispersion_entropy_shock_mr.*20261107T02" reports/ 2>&1 | head -10
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
```
If script embeds wrong campaign metadata, update minimally to campaign 119 and correct prior-registry references to `reports/strategy_edge_registry_20261107T020709Z.json` (sha `c28f530de58334ee9e56ca2a2cc8e9eba752c6040c2b15ff75074a4163a8e478`) before running.

#### Step 1 — Run C119 `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. Feature must be pre-stated and distinct from C111–C118 (SVD entropy, Fisher Information, attention entropy, increment entropy, permutation variance, fluctuation complexity, range entropy, cumulative residual entropy). Dispersion entropy is based on dispersion patterns/symbolization of amplitude relationships — confirm script implements it; keep fail-closed on degenerate/non-finite.
2. Signal (fail-closed MR): `z = (DE - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade; `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. WF/costs/B&H (exact): `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. Run and emit: `reports/real_quote_volume_dispersion_entropy_shock_mr_costed_oos_<UTC>.json` (new C119 timestamp).

#### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly (`No module named pytest` is acceptable if true). Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T020709Z.json` (sha `c28f530de58334ee9e56ca2a2cc8e9eba752c6040c2b15ff75074a4163a8e478`): include C111–C119 with artifacts/SHAs/scripts where available, structurally consistent top-level `campaign`, `supersedes`, `supersedes_sha256`, lineage, and C119 result. `edge_claim: NONE` unless edge rule holds. Reference C118 OOS sha `431472461c4c932beba68b9ba2a64e7d9f09b40685d009c991431e6bdc1118af`.
4. Summary: `reports/campaign119_execution_summary_<UTC>.json` listing all new artifact paths + sha256.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run.
- **No status summary before >= 3 new concrete report artifacts exist for C119** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C118 marked DONE with SHAs; C104–C118 locked — no reruns.
- Stale HANDOFF replaced with C119-specific, execution-first instructions.
- C118 registry structural inconsistency called out explicitly — next registry must be consistent.
- Dispersion script already exists but old result must not be reused — forces fresh C119-stamped artifact.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.

### Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -n 'campaign' scripts/run_real_quote_volume_dispersion_entropy_shock_mr_costed_oos.py | head -8
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
```
Then adapt script metadata if needed, run C119 dispersion entropy costed OOS, emit OOS report, then Step 2. **Do not stop until Step 2 complete with >=3 new C119 artifacts.**
