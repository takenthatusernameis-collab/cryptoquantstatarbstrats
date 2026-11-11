# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. Core mission: real-data-only edge search (fail-closed enriched cointegration gates), no fabrication, no status-only work. **Single durable handoff at repo root: `HANDOFF.md` only** (updated 2026-11-11T12:09:49Z UTC, this session). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line (stale at `latest_campaign_done: C248` / `next_campaign: C249`; C249/C250/C251 complete). Separate research line; must not be edited to block/replace C1–C15 progress. Syncing `state.yaml` only if explicitly requested by the user.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T12:09:49Z UTC)

**DO THIS FIRST (heavy execution, no status-only, no planning substitute): Campaign #252 — real-data-only fail-closed volume RQA shock mean-reversion costed-OOS edge search. Primary strategy: `RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW` (Pearson's skewness coefficient on qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0; define feature as Pearson skewness, e.g. 3*(mean-median)/std or mean-mode/std — pick one pre-stated fixed form consistent with "Pearson skewness", document exact formula in script, fail-closed if denominator/std/mode undefined or insufficient qualifying segments). Verify distinctness before implementation/run. Use `python3` (3.12.3); deps `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1 available.**

**State (verified 2026-11-11T12:09:49Z UTC):** C12 5/5, C13 3/3, C14 7/7 (zero edge), C15 7/7 (zero edge). C249 COMPLETE (research line, NONE). **C250 COMPLETE** (`YULE_K`, NONE). **C251 COMPLETE** (`MIDRANGE`, NONE) — all 5 artifacts + SHA256 from bytes on disk (see C251 section). **C252 NOT STARTED** — zero C252 artifacts in `reports/`/`scripts/`. Caches present in `data/cache/` (68 files incl. `.pkl`+`.meta.json`); no network refetch. **Bottlenecks cleared:** `python3`+deps OK (no c7-venv blocker); grep-zero re-verified `PEARSON_SKEW`=0 hits (scripts/strategies/backtest/utils); no blocking background process. No status-only work. Stop only if `oos_edge_proven: true`; otherwise record honest `edge_claim: NONE` with evidence and update this handoff. Do not edit `research_state/state.yaml` unless explicitly requested by user.

**C252 plan (non-deferrable):**
- **Preselected strategy:** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW` (Pearson skewness of qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0; pre-state exact formula, fail-closed on undefined/degenerate/insufficient segments per C250/C251 conventions).
- **Distinctness gate (must re-confirm before implementation/run):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW|WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW' scripts/ strategies/ backtest/ utils/` → **0 nonself hits required**.
- **If blocked/fails distinctness:** select next grep-zero distinct fallback (e.g. another untried RQA statistic on white diag line lengths), record evidence, and proceed (no status-only stop).
- **Implement by adapting C251 pattern:** `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos.py` → new script for chosen strategy; preserve fail-closed, real-data-only, SHA256-from-bytes, and artifact/registry/summary/ingest emission patterns.
- **Required outputs (all SHA256 from bytes):** timestamped costed-OOS artifact, script, ingest attempt, strategy-edge-registry entry, campaign execution summary.
- **Edge rule (honest, fail-closed):** `oos_edge_proven: true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows (real data only). Otherwise `edge_claim: NONE` with evidence: `cross_asset_oos_net_sums`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`.
- **Stop only if `oos_edge_proven: true`.** Otherwise record honest blocked/no-edge conclusion with evidence and update this handoff (paths, SHA256s, conclusion, next directive). No planning/researching as substitute for execution. Do **not** edit `research_state/state.yaml` unless explicitly requested by user.

## C251 (MAIN LINE — COMPLETE, 2026-11-11T11:24:30Z UTC)

- Campaign 251, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE_SHOCK_MR` (midrange = (max+min)/2 of qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0), edge_claim **NONE**, oos_edge_proven **false**, all_new_c251_artifact_paths_sha256_from_bytes **true**.
- **Distinctness (pre-run, required):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE|WHITE_DIAG_LINE_LENGTH_MIDRANGE' scripts/ strategies/ backtest/ utils/` → 0 nonself hits at run (`grep_hits_nonself_at_run: 0`; self + own campaign emit/ingest scripts excluded in-script per fail-closed pattern).
- **Commands run (from repo root):** distinctness grep; created `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos.py`, `scripts/run_real_feed_ingest_attempt_251.py`, `scripts/emit_campaign251_registry.py`, `scripts/emit_campaign251_summary.py`; `python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos.py` (patched distinctness filter to exclude own C251 helper scripts after initial self-collision fail-close); `python3 scripts/run_real_feed_ingest_attempt_251.py`; `python3 scripts/emit_campaign251_registry.py`; `python3 scripts/emit_campaign251_summary.py`.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos_20261111T111904Z.json` — `8764897cf3b1b7746568bb43f6c088c504f167d10c12ccdfdd18c990c77883ef`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos.py` — `794807178d5f60649d533c531d02e24e40f44c0ccef992e9c721f5e64c26331a`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T112426Z.json` — `ca2efb4b27fb4902e3f8b9be8bb4983c59b28be32b15a76b12e7ad0f4b896638`
  - Registry: `reports/strategy_edge_registry_20261111T112426Z.json` — `e1c8ba8c8382daedebc22e75c19a218fe7e0d9d8d5d2a0953e929c348d02eecd`
  - Summary: `reports/campaign251_execution_summary_20261111T112427Z.json` — `fb89eb1c1c45f67311ad9dbdccedd1ff7c0584988f4e7a12fbd673b2c74df837`
- **Evidence (real data, WF 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]]):**
  - `cross_asset_oos_net_sums`: fee0_slip0=-2.033769597261822, fee5_slip5=-2.763769597261823, fee10_slip10=-3.4937695972618235, fee20_slip20=-4.953769597261823, fee40_slip40=-7.8737695972618225
  - `any_exposure_oos: true`
  - `all_cost_slices_positive_oos_net_sum: false`
  - `all_cost_slices_beat_bh_mean_rule: false`
  - **Conclusion:** `oos_edge_proven: false`, `edge_claim: NONE`. No edge found; honest no-edge recorded.

## C250 (MAIN LINE — COMPLETE)

- Campaign 250, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K_SHOCK_MR`, edge_claim NONE, oos_edge_proven false.
- OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos_20261111T103421Z.json` (sha256 `af1e3767a474fe28f839a42cc7662fd2f933aadd72df57a4ae76249af211bd7b`)
- Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos.py` (sha256 `1f94dc35ae8bda2f94e933ed90bee5f34ccde81efacee9ae8cb6352a1764828b`)
- Ingest: `reports/real_feed_ingest_attempt_20261111T104044Z.json` (sha256 `eed9819368d4c5106fa6aab1c01e0a0cd5bb22fcdc62e23e22614b797480d903`)
- Registry: `reports/strategy_edge_registry_20261111T104048Z.json` (sha256 `37d4a9b6f418c7dcf180c39e02bf89aeb3751c060b6d75b510c19bec4ec6b4d7`)
- Summary: `reports/campaign250_execution_summary_20261111T104050Z.json` (sha256 `facee955b68c9498aac50631a3bda06097042f9e44a1175f226b3da69a66729f`)
- Evidence: cross_asset_oos_net_sums all negative; `any_exposure_oos: true`; `all_cost_slices_positive_oos_net_sum: false`; `all_cost_slices_beat_bh_mean_rule: false`.

## C249 (RESEARCH LINE — COMPLETE)

- `reports/campaign249_execution_summary_20261110T170949Z.json`, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW_SHOCK_MR`, edge_claim NONE, oos_edge_proven false.
- OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_groeneveld_meeden_skew_shock_mr_costed_oos_20261109T034759Z.json` (sha256 `042fa8fb58b1b2976869cb0508396325d7d25eed075b38ecbf4043033f2615b4`)
- Registry: `reports/strategy_edge_registry_20261110T170949Z.json` (sha256 `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`)

## C14/C15 (COMPLETE, zero edge)

- C14 7/7 `insufficient_or_blocked`/`no_edge`; no cost-aware OOS triggered. C15 7/7 `no_edge`/`insufficient_or_blocked`; no cost-aware OOS triggered. No re-runs except evidence-backed defect fix.

## BOTTLENECK REMOVAL (pre-cleared — 2026-11-11T11:24:30Z UTC)

- C12/C13/C14/C15/C249/C250/C251 complete — no re-runs permitted except evidence-backed defect fix.
- All caches `.pkl`+`.meta.json` present in `data/cache/`; no network refetch (real cached spot/volume only).
- **Python/deps:** `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1 (missing c7-venv not a blocker).
- `research_state/state.yaml` locked/stale — do not touch; does not block C252.
- **Grep-zero re-verified:** `PEARSON_SKEW` = 0 hits (primary for C252).
- No blocking background process. No status-only work.

## HARD BANS

- ❌ No status-only work
- ❌ No re-runs of C1–C15 or C249–C251 except evidence-backed defect fix
- ❌ No network refetch (use `data/cache/` only)
- ❌ No synthetic/fabricated data
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15)
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user
- ❌ No early exit — C252 run must complete unless `oos_edge_proven: true`
- ❌ No "planning" or "researching" as substitute for running the script and producing artifacts

## KEY FILES

- C251 (latest pattern): `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos.py`, `scripts/run_real_feed_ingest_attempt_251.py`, `scripts/emit_campaign251_registry.py`, `scripts/emit_campaign251_summary.py`, `reports/campaign251_execution_summary_20261111T112427Z.json`, `reports/strategy_edge_registry_20261111T112426Z.json`
- C250 pattern: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos.py`, `reports/campaign250_execution_summary_20261111T104050Z.json`
- Strategy/gates (C1–C15 line): `strategies/pairs_trading.py`, `utils/cointegration.py`
- Caches (real-only): `data/cache/*.{pkl,meta.json}`
- Locked separate line (do not edit): `research_state/state.yaml`

## EXACT COMMANDS TO RUN FOR C252 (from repo root)

```bash
# 1. Re-verify grep-zero distinctness for PEARSON_SKEW (MUST return 0 nonself hits)
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW|WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW' scripts/ strategies/ backtest/ utils/

# 2. Copy C251 pattern script and adapt for PEARSON_SKEW
cp scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos.py \
   scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_skew_shock_mr_costed_oos.py

# 3. Edit: replace MIDRANGE/midrange with PEARSON_SKEW/pearson_skew; update strategy_id, feature docstring/formula
#    (pre-state exact Pearson skewness formula on qualifying WHITE diagonal segment lengths), grep-distinctness strings,
#    artifact/report naming, campaign=252, prior registry -> strategy_edge_registry_20261111T112426Z.json (sha e1c8ba8c8382daedebc22e75c19a218fe7e0d9d8d5d2a0953e929c348d02eecd).
#    Update own_campaign exclusion set in distinctness grep to include C252 helper stems.

# 4. Run script (heavy work) and emit ingest/registry/summary artifacts
python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_skew_shock_mr_costed_oos.py
python3 scripts/run_real_feed_ingest_attempt_252.py
python3 scripts/emit_campaign252_registry.py
python3 scripts/emit_campaign252_summary.py

# 5. Record SHA256-from-bytes for: OOS artifact, script, ingest attempt, registry, summary.

# 6. Update THIS HANDOFF.md with: UTC timestamp, commands run, artifact paths+SHA256, conclusion, next directive.
#    Do NOT edit research_state/state.yaml unless explicitly requested by user.
```

**If PEARSON_SKEW fails grep-zero or is blocked:** pick next grep-zero distinct fallback, record evidence, implement/run it (no status-only stop).

**END OF DURABLE HANDOFF — updated 2026-11-11T12:09:49Z UTC.** C12–C15 complete (zero edge). C249/C250 complete (NONE). C251 COMPLETE (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE`, `edge_claim: NONE`, `oos_edge_proven: false`) — 5 artifacts+SHA256 from bytes recorded above. **C252 NOT STARTED.** **IMMEDIATE NEXT ACTION (non-deferrable): Campaign #252 — implement/run `RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW` (grep-zero 0) via `python3` from C251 pattern, produce timestamped OOS/script/ingest/registry/summary artifacts with SHA256-from-bytes, record honest edge/no-edge with evidence, then update this handoff. Do not stop at planning. No status-only work.**
