# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T223451Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T223451Z state; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C180 locked/verified on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_lavg_over_lmax_ratio_shock_mr_costed_oos_20261107T223451Z.json`=9701e5560c8c6708251be9860411e1a2912201cd406316ec50f243741a7ad50a (`oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=-0.36014632770704036, fee5=-0.6531463277070406, fee10=-0.9461463277070408, fee20=-1.5321463277070406, fee40=-2.7041463277070403), ingest `reports/real_feed_ingest_attempt_20261107T223451Z.json`=29d23b21e13b6682e7ec42960991599f087334de62fb97e92059017a9f183e59 (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`), registry `reports/strategy_edge_registry_20261107T223451Z.json`=40e405929037363f538a487ebb5ca7c6f9ffcd6ebd1922ee3ad4235ec7442247 (supersedes C179 registry 55bc25b50c145315d95591dc09bbaefe9f2969acf70b37c37925e6c9284a6737, cites C179 OOS SHA b0ef4d614f13dbb843be1e82a5a38f3f8be3839b9ec9060eaae25865a6fc8379), summary `reports/campaign180_execution_summary_20261107T223451Z.json`=295d450de12f9b0c0c3173e7cee990f0f3ac9a399c9fef9490f6e9e2b1062422, script `scripts/run_real_quote_volume_rqa_lavg_over_lmax_ratio_shock_mr_costed_oos.py`=6fe934cc5dae7a6eff323f444f0a4dc51fb23e17a38b5886aa2f71e06f0666a7. `state.yaml` synced C180-done/C181-next.
- **C181 preselected `VOLUME_RQA_VMAX_OVER_LAVG_RATIO_SHOCK_MR` => 0 hits** (`grep -rnE 'VMAX_OVER_LAVG|vmax_over_lavg|rqa_ratio_vmax_over_lavg' scripts/ strategies/ backtest/ utils/ research_state/ HANDOFF.md reports/ 2>&1`, verified 20261107T223451Z, 0 hits across all dirs including reports/state/handoff context). **Re-verify at C181 run time (0 non-self) before implementation.** Excluded due to prior token presence: `VMAX_OVER_LMAX` appears in C177 distinctness grep text (`scripts/run_real_quote_volume_rqa_lmax_over_vmax_ratio_shock_mr_costed_oos.py:71` and C177 artifacts), `DET_OVER_TT`/`TT_OVER_DET`/`ENTR_OVER_LMAX`/`LMAX_OVER_ENT` present in prior artifacts.
- Prior C104–C180 remain locked.

## C104–C180 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T223451Z.json` (40e405929037363f538a487ebb5ca7c6f9ffcd6ebd1922ee3ad4235ec7442247). Use it as `PRIOR_REGISTRY`; cite C180 OOS SHA 9701e5560c8c6708251be9860411e1a2912201cd406316ec50f243741a7ad50a in pre-stated refs.

## INITIAL TASK — C181 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T223451Z
**Execute C181 now. NO status-only replies. NO status summary before >= 3 NEW concrete C181 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_VMAX_OVER_LAVG_RATIO_SHOCK_MR` — RQA ratio **VMAX/LAVG** (max vertical line length `VMAX` normalized by mean diagonal line length `LAVG`) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. `VMAX` = max vertical line length over qualifying vertical lines (consecutive 1s along columns) with `l>=l_min`. `LAVG` = average length of qualifying diagonal lines (`k>=1`, excluding LOI) with `l>=l_min` on the **same** recurrence matrix (same qualifying diagonal set semantics as used elsewhere). **Fail-closed NaN/no-signal** if `LAVG==0` or undefined/non-finite/degenerate (no qualifying diagonal lines), `VMAX` undefined/non-finite/degenerate (no qualifying vertical lines), or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `VMAX` numerator with `LAVG` denominator — pairing not used in C125–C180. `VMAX_OVER_LAVG` tokens absent across scripts/strategies/backtest/utils/research_state/HANDOFF.md/reports at selection (grep 0 at 20261107T223451Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'VMAX_OVER_LAVG|vmax_over_lavg|rqa_ratio_vmax_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback (e.g., `LAVG_OVER_RR`, `LAVG_OVER_LAM`, `LAVG_OVER_DET`, `LAVG_OVER_TT`, `LAVG_OVER_VMAX`, `ENT_OVER_LMAX`; record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C181 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C180): `scripts/run_real_quote_volume_rqa_vmax_over_lavg_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T223451Z.json` (40e405929037363f538a487ebb5ca7c6f9ffcd6ebd1922ee3ad4235ec7442247), cite C180 OOS SHA 9701e5560c8c6708251be9860411e1a2912201cd406316ec50f243741a7ad50a. Emit `reports/real_quote_volume_rqa_vmax_over_lavg_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 181) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T223451Z.json` (40e405929037363f538a487ebb5ca7c6f9ffcd6ebd1922ee3ad4235ec7442247). Structurally consistent; include prior + C181 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign181_execution_summary_<UTC>.json` listing **all new C181 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C181`, `next_campaign:C182`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c182_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C181, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C181 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T223451Z)
- C104–C180 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C180 `LAVG_OVER_LMAX` completed/verified (exposure OOS, no edge proven; all cost slices negative cross-asset net).
- C181 `VMAX_OVER_LAVG` preselect grep verified 0 across all dirs — eliminates collision-search delay. `VMAX_OVER_LMAX`/`DET_OVER_TT`/`TT_OVER_DET`/`ENTR_OVER_LMAX`/`LMAX_OVER_ENT` explicitly excluded (prior token presence).
- Single durable handoff + `state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'VMAX_OVER_LAVG|vmax_over_lavg|rqa_ratio_vmax_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C181 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C181-done/C182-next with grep-verified C182 preselection
```

## NEXT FOCUS CAMPAIGN — C182 (preselect at end of C181; HEAVY WORK MANDATORY)
After C181 completes, **C182 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C181 (verify by grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c182_preselected`, then execute C182 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
