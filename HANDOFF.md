# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T222826Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T222826Z state; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C179 locked/verified on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_lmax_over_rr_ratio_shock_mr_costed_oos_20261107T222826Z.json`=b0ef4d614f13dbb843be1e82a5a38f3f8be3839b9ec9060eaae25865a6fc8379 (`oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=0.23703673547727355, fee5=-0.11196326452272673, fee10=-0.46096326452272673, fee20=-1.1589632645227264, fee40=-2.5549632645227267), ingest `reports/real_feed_ingest_attempt_20261107T222826Z.json`=87548b62a2c29f82215b2ad897527fc2f0a3df24f5959049d3f13c2e0f3410aa (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`), registry `reports/strategy_edge_registry_20261107T222826Z.json`=55bc25b50c145315d95591dc09bbaefe9f2969acf70b37c37925e6c9284a6737 (supersedes C178 registry b8518a3fbe2ffa106c87d037fe6bbc65d21d22ce3c25119d9b3d634c9d983591, cites C178 OOS SHA 180ca15613d812373db7cf5726e57c55323a22dc4e4606a4ab88b30272995979), summary `reports/campaign179_execution_summary_20261107T222826Z.json`=593a18c5d8f9ede45c09793a31adafbbef4a9261241224291f30097f608e2375, script `scripts/run_real_quote_volume_rqa_lmax_over_rr_ratio_shock_mr_costed_oos.py`=ee64a497dfcf864add19525646fb38ee3938feb4303ff770022eb74be486fa0a. `state.yaml` synced C179-done/C180-next.
- **C180 preselected `VOLUME_RQA_LAVG_OVER_LMAX_RATIO_SHOCK_MR` => 0 hits** (`grep -rnE 'LAVG_OVER_LMAX|lavg_over_lmax|rqa_ratio_lavg_over_lmax' scripts/ strategies/ backtest/ utils/ research_state/ HANDOFF.md reports/ 2>&1`, verified 20261107T222826Z, 0 hits). **Re-verify at C180 run time (0 non-self) before implementation.** Note: `VMAX_OVER_RR`/`RR_OVER_VMAX` tokens are NOT grep-zero (C170 RR_OVER_VMAX artifacts exist) — excluded.
- Prior C104–C179 remain locked.

## C104–C179 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T222826Z.json` (55bc25b50c145315d95591dc09bbaefe9f2969acf70b37c37925e6c9284a6737). Use it as `PRIOR_REGISTRY`; cite C179 OOS SHA b0ef4d614f13dbb843be1e82a5a38f3f8be3839b9ec9060eaae25865a6fc8379 in pre-stated refs.

## INITIAL TASK — C180 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T222826Z
**Execute C180 now. NO status-only replies. NO status summary before >= 3 NEW concrete C180 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_LAVG_OVER_LMAX_RATIO_SHOCK_MR` — RQA ratio **LAVG/LMAX** (mean diagonal line length `LAVG` = average length of diagonal lines with `l >= l_min` on `k>=1`, excluding LOI, normalized by max diagonal line length `LMAX` on the same qualifying diagonals) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `LMAX==0` or undefined/non-finite/degenerate (no qualifying diagonal lines), `LAVG` undefined/non-finite/degenerate, or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `LAVG` numerator with `LMAX` denominator — pairing not used in C125–C179. `LAVG_OVER_LMAX` tokens absent in scripts/strategies/backtest/utils/research_state/HANDOFF.md/reports at selection (grep 0 at 20261107T222826Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'LAVG_OVER_LMAX|lavg_over_lmax|rqa_ratio_lavg_over_lmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback (record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C180 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C179): `scripts/run_real_quote_volume_rqa_lavg_over_lmax_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T222826Z.json` (55bc25b50c145315d95591dc09bbaefe9f2969acf70b37c37925e6c9284a6737), cite C179 OOS SHA b0ef4d614f13dbb843be1e82a5a38f3f8be3839b9ec9060eaae25865a6fc8379. Emit `reports/real_quote_volume_rqa_lavg_over_lmax_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 180) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T222826Z.json` (55bc25b50c145315d95591dc09bbaefe9f2969acf70b37c37925e6c9284a6737). Structurally consistent; include prior + C180 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign180_execution_summary_<UTC>.json` listing **all new C180 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C180`, `next_campaign:C181`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c181_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C180, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C180 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T222826Z)
- C104–C179 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C179 `LMAX_OVER_RR` completed/verified (post-run self hits only in scripts/strategies/backtest/utils).
- C180 `LAVG_OVER_LMAX` preselect grep verified 0 — eliminates collision-search delay. `VMAX_OVER_RR`/`RR_OVER_VMAX` explicitly excluded (C170 tokens present).
- Single durable handoff + `state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'LAVG_OVER_LMAX|lavg_over_lmax|rqa_ratio_lavg_over_lmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C180 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C180-done/C181-next with grep-verified C181 preselection
```

## NEXT FOCUS CAMPAIGN — C181 (preselect at end of C180; HEAVY WORK MANDATORY)
After C180 completes, **C181 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C180 (verify by grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c181_preselected`, then execute C181 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
