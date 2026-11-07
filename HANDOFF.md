# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T222314Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T222314Z state; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C178 locked/verified on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_lmax_over_lam_ratio_shock_mr_costed_oos_20261107T222314Z.json`=180ca15613d812373db7cf5726e57c55323a22dc4e4606a4ab88b30272995979 (`oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=0.6452691541049826, fee5=0.2842691541049824, fee10=-0.07673084589501773, fee20=-0.7987308458950176, fee40=-2.2427308458950175), ingest `reports/real_feed_ingest_attempt_20261107T222314Z.json`=8ffa7a111b168cafd4cd7bb87ee4d33569d3ef9da3f618fc3c620c89208470f2 (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`), registry `reports/strategy_edge_registry_20261107T222314Z.json`=b8518a3fbe2ffa106c87d037fe6bbc65d21d22ce3c25119d9b3d634c9d983591 (supersedes C177 registry 85d34f8b20a4b8a20044879e46281d2546d917028ccb04036b2506d8ddbad0c4, cites C177 OOS SHA 3305fe26f199d29aba85a931ac47cebe831b0e428191fadfbde938adacef2933), summary `reports/campaign178_execution_summary_20261107T222314Z.json`=fcd7059205071d67acd2afe083113792296243ac76eb33771b0c7e04a6af770a, script `scripts/run_real_quote_volume_rqa_lmax_over_lam_ratio_shock_mr_costed_oos.py`=7d1e0727ee3b3c15b3da419e11cc1048f266376a3e942a4dd07a2f842930fced. `state.yaml` synced C178-done/C179-next.
- **C179 preselected `VOLUME_RQA_LMAX_OVER_RR_RATIO_SHOCK_MR` => 0 hits** (`grep -rnE 'LMAX_OVER_RR|lmax_over_rr|rqa_ratio_lmax_over_rr' scripts/ strategies/ backtest/ utils/ research_state/ HANDOFF.md reports/ 2>&1`, verified 20261107T222314Z, 0 hits). **Re-verify at C179 run time (0 non-self) before implementation.**
- Prior C104–C178 remain locked.

## C104–C178 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T222314Z.json` (b8518a3fbe2ffa106c87d037fe6bbc65d21d22ce3c25119d9b3d634c9d983591). Use it as `PRIOR_REGISTRY`; cite C178 OOS SHA 180ca15613d812373db7cf5726e57c55323a22dc4e4606a4ab88b30272995979 in pre-stated refs.

## INITIAL TASK — C179 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T222314Z
**Execute C179 now. NO status-only replies. NO status summary before >= 3 NEW concrete C179 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_LMAX_OVER_RR_RATIO_SHOCK_MR` — RQA ratio **LMAX/RR** (max diagonal line length `LMAX` = maximum length of diagonal lines with `l >= l_min` on `k>=1`, excluding LOI, normalized by recurrence rate `RR = sum(R) / M^2`, where `M` is the embedding point count and `sum(R)` is the full recurrence-matrix sum including LOI) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `RR==0` or undefined/non-finite/degenerate (`sum(R)<=0` or `M<=0`), `LMAX` undefined/non-finite/degenerate (no qualifying diagonal lines), or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `LMAX` numerator with `RR` denominator — pairing not used in C125–C178. `LMAX_OVER_RR` tokens absent in scripts/strategies/backtest/utils/research_state/HANDOFF.md/reports at selection (grep 0 at 20261107T222314Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'LMAX_OVER_RR|lmax_over_rr|rqa_ratio_lmax_over_rr' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback (record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C179 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C178): `scripts/run_real_quote_volume_rqa_lmax_over_rr_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T222314Z.json` (b8518a3fbe2ffa106c87d037fe6bbc65d21d22ce3c25119d9b3d634c9d983591), cite C178 OOS SHA 180ca15613d812373db7cf5726e57c55323a22dc4e4606a4ab88b30272995979. Emit `reports/real_quote_volume_rqa_lmax_over_rr_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 179) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T222314Z.json` (b8518a3fbe2ffa106c87d037fe6bbc65d21d22ce3c25119d9b3d634c9d983591). Structurally consistent; include prior + C179 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign179_execution_summary_<UTC>.json` listing **all new C179 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C179`, `next_campaign:C180`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c180_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C179, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C179 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T222314Z)
- C104–C178 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C178 `LMAX_OVER_LAM` completed/verified (post-run self hits only).
- C179 `LMAX_OVER_RR` preselect grep verified 0 — eliminates collision-search delay.
- Single durable handoff + `state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'LMAX_OVER_RR|lmax_over_rr|rqa_ratio_lmax_over_rr' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C179 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C179-done/C180-next with grep-verified C180 preselection
```

## NEXT FOCUS CAMPAIGN — C180 (preselect at end of C179; HEAVY WORK MANDATORY)
After C179 completes, **C180 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C179 (verify by grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c180_preselected`, then execute C180 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**

(End of file)
