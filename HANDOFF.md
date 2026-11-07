# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T221848Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T215740Z state; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C177 locked/verified on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_lmax_over_vmax_ratio_shock_mr_costed_oos_20261107T215616Z.json`=3305fe26f199d29aba85a931ac47cebe831b0e428191fadfbde938adacef2933 (`oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=0.40428387890362316, fee5=0.11728387890362292, fee10=-0.16971612109637713, fee20=-0.743716121096377, fee40=-1.891716121096377), ingest `reports/real_feed_ingest_attempt_20261107T215740Z.json`=90efcd130fcc77200fff92164292666fe24ce93956010796158e0d0fda5ecc42 (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`), registry `reports/strategy_edge_registry_20261107T215740Z.json`=85d34f8b20a4b8a20044879e46281d2546d917028ccb04036b2506d8ddbad0c4 (supersedes C176 registry 61d402b2b696b724637259e37f93ad4c1ba8633eb5d177c9d155cec5b4e0b649, cites C176 OOS SHA 28b9a7e03a1c695bbfda9c99e7a0c195daf08249de8c41a4b8348fc4122e23c0), summary `reports/campaign177_execution_summary_20261107T215740Z.json`=3b689d60487fc069c2c3e72052b868e4282e0b7116472fe8da5c517db51f9ba4, script `scripts/run_real_quote_volume_rqa_lmax_over_vmax_ratio_shock_mr_costed_oos.py`=73c3f1feec0c059e86eedd5b4f72ed86de1284144a219d3b3eeaeac811750070. `state.yaml` synced C177-done/C178-next.
- **C178 preselected `VOLUME_RQA_LMAX_OVER_LAM_RATIO_SHOCK_MR` => 0 hits** (`grep -rn 'LMAX_OVER_LAM\|lmax_over_lam\|rqa_ratio_lmax_over_lam' scripts/ strategies/ backtest/ utils/ research_state/ HANDOFF.md reports/ 2>&1`, verified 20261107T215740Z, 0 hits). **Re-verify at C178 run time (0 non-self) before implementation.**
- Prior C104–C177 remain locked.

## C104–C177 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T215740Z.json` (85d34f8b20a4b8a20044879e46281d2546d917028ccb04036b2506d8ddbad0c4). Use it as `PRIOR_REGISTRY`; cite C177 OOS SHA 3305fe26f199d29aba85a931ac47cebe831b0e428191fadfbde938adacef2933 in pre-stated refs.

## INITIAL TASK — C178 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T215740Z
**Execute C178 now. NO status-only replies. NO status summary before >= 3 NEW concrete C178 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_LMAX_OVER_LAM_RATIO_SHOCK_MR` — RQA ratio **LMAX/LAM** (max diagonal line length `LMAX` = maximum length of diagonal lines with `l >= l_min` on `k>=1`, excluding LOI, normalized by laminarity `LAM = (sum of lengths of vertical lines with v >= l_min) / sum(R)`) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `LAM==0` or undefined/non-finite/degenerate (no qualifying vertical lines or `sum(R)<=0`), `LMAX` undefined/non-finite/degenerate (no qualifying diagonal lines), `sum(R)<=0`, or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `LMAX` numerator with `LAM` denominator — pairing not used in C125–C177. `LMAX_OVER_LAM` tokens absent in scripts/strategies/backtest/utils/research_state/HANDOFF.md/reports at selection (grep 0).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rn 'LMAX_OVER_LAM\|lmax_over_lam\|rqa_ratio_lmax_over_lam' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback (record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C178 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C177): `scripts/run_real_quote_volume_rqa_lmax_over_lam_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T215740Z.json` (85d34f8b20a4b8a20044879e46281d2546d917028ccb04036b2506d8ddbad0c4), cite C177 OOS SHA 3305fe26f199d29aba85a931ac47cebe831b0e428191fadfbde938adacef2933. Emit `reports/real_quote_volume_rqa_lmax_over_lam_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 178) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T215740Z.json` (85d34f8b20a4b8a20044879e46281d2546d917028ccb04036b2506d8ddbad0c4). Structurally consistent; include prior + C178 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign178_execution_summary_<UTC>.json` listing **all new C178 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C178`, `next_campaign:C179`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c179_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C178, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C178 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T215740Z)
- C104–C177 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C177 `LMAX_OVER_VMAX` completed/verified (0 non-self pre/post self-only).
- C178 `LMAX_OVER_LAM` preselect grep verified 0 — eliminates collision-search delay.
- Single durable handoff + `state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'LMAX_OVER_LAM\|lmax_over_lam\|rqa_ratio_lmax_over_lam' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C178 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C178-done/C179-next with grep-verified C179 preselection
```

## NEXT FOCUS CAMPAIGN — C179 (preselect at end of C178; HEAVY WORK MANDATORY)
After C178 completes, **C179 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C178 (verify by grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c179_preselected`, then execute C179 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**

(End of file)
