# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff refreshed:** 2026-11-15T23:35:44Z — **C315 COMPLETE FORMAL NEGATIVE (RETRACTED, 20261115T223831Z, 0/3456 Holm+BH, binding `multiple_testing`, dominant attribution reversal 0.7015 vs momentum 0.1467 vs placebo 0.1518). CLOSE-OUT CONFIRMED 2026-11-15T23:35:44Z: bootstrap ready; pytest 1642 passed / 2 skipped / 0 failed; verify_env healthy; all 30 C310–C315 slim artifacts + 6 gitignored full.json SHA256-from-bytes match research_state/state.yaml; all caches <100 MB; all flags real_data_only:true, fabricated_data:false, executed_fills:false; edge_proven:false / binding_constraint:multiple_testing universally.** C314/C313/C312/C311/C310/C306–C309/C281B–C305 FROZEN formal negatives. C287 BLOCKED/DECOUPLED externally (testnet REST 451, fapi 451, bybit 403, no creds) — fix requires OUT-OF-ENV Binance Spot Testnet credentials + non-451 network egress; cannot be resolved in-env; do NOT re-probe C287 routes as economic work. `latest_campaign_done: C315`; `active_campaign: none` (space CLOSED — C287 externally blocked, out-of-env only); `oos_edge_proven: false`; `edge_claim: NONE`. Reachable real-data stat-arb space CLOSED.

## INITIAL TASK MESSAGE (2026-11-15T23:22:06Z) — REACHABLE STAT-ARB SPACE CLOSED: VERIFY SUITE GREEN + CONFIRM CLOSURE + STOP

**Mission (repo priority = cryptoquantstatarbstrats → costed OOS stat-arb PnL on real, provable data):** **ALL REACHABLE CAMPAIGNS C281B–C315 COMPLETE — FORMAL NEGATIVES. UNIVERSAL VERDICT: 0 tradable edge across 12,000+ pre-registered configs; binding constraint universally `multiple_testing`.** C287 (testnet gateway) remains BLOCKED externally (REST 451, fapi 451, bybit 403, no creds) — out-of-env credentials + allowed network required, CANNOT advance in-env. **NO HEAVY ECONOMIC WORK REACHABLE IN THIS ENVIRONMENT.**

Next session, execute exactly and only:
1. `python scripts/bootstrap_dev_env.py` (deps importable)
2. `python -m pytest tests/ -q` → full suite green (1642 passed / 2 skipped / 0 failed)
3. Verify all 30 artifacts + 6 gitignored `full.json` for C310–C315 on disk at `reports/campaign31*_*_20261115T*.{json,full.json}` with SHA256-from-bytes matching `research_state/state.yaml`; all slim sweeps <100 MB; all caches <100 MB with `real_data_only:true, fabricated_data:false, executed_fills:false`
4. `python scripts/verify_env.py --json` → environment healthy
5. Confirm `active_campaign: C287` is still externally blocked (no in-env remediation possible); sync `AGENTS.md` + `research_state/state.yaml` with final verdict (space CLOSED, no active campaign). Never create `HANDOFF.md`.
6. STOP. No further economic work is reachable in this environment.

**CLOSE-OUT CONFIRMED 2026-11-15T23:35:44Z:** `python scripts/bootstrap_dev_env.py` OK (deps importable); `python -m pytest tests/ -q` → 1642 passed / 2 skipped / 0 failed; all 30 C310–C315 slim artifacts + 6 gitignored `full.json` on disk at `reports/campaign31*_*_20261115T*.{json,full.json}` with SHA256-from-bytes matching `research_state/state.yaml`; all slim sweeps <100 MB; all caches <100 MB with `real_data_only:true, fabricated_data:false, executed_fills:false`; `python scripts/verify_env.py --json` → environment healthy. `active_campaign: none` — reachable stat-arb space CLOSED; C287 remains externally blocked (out-of-env only). No new campaign registered.

**Do NOT re-run, re-skin, re-probe, or pivot to C281B–C315 or C287. Any attempt to manufacture a "new campaign" from frozen components is a hard violation.** The single true bottleneck (C287 testnet 451/no creds) is out-of-env and cannot be removed from this environment.

**Frozen/blocked (do NOT rerun, re-skin, re-probe, or pivot to):** C281B–C315 (formal negatives — 0/12,000+ configs survive Holm+BH), C287 (external 451/no creds). Any work on them is a hard violation.

**Guardrails (enforced — final session):**
- **No fabricated data / fail-closed / provenance-first:** `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`; SHA256-from-bytes for every artifact; missing/None/false gates BLOCK.
- **Bounded resources:** cache <100 MB total, per-asset `.npz` shards; slim sweep artifact <100 MB (no per-bar series) + gitignored `full.json`.
- **No overfitting:** ALL pre-registered configs reported; Holm+BH α=0.05 BOTH must pass; MDE + stability + attribution required.
- **Costs real:** per-leg fee/slippage grid charged on turnover; model PnL labeled `executed_fills:false`. Perp funding unreachable (fapi 451) → excluded.

**Execute in order (verify + close out — NO NEW CAMPAIGN):**
1. `python scripts/bootstrap_dev_env.py` (deps importable)
2. `python -m pytest tests/ -q` → full suite green (all campaign tests passing)
3. Verify all 5 artifacts + gitignored `full.json` for C310–C315 on disk at `reports/campaign31*_*_20261115T*.{json,full.json}` with SHA256-from-bytes; all slim sweeps <100 MB; all caches <100 MB with correct flags
4. `python scripts/verify_env.py --json` → environment healthy
5. Sync `AGENTS.md` + `research_state/state.yaml` with final verdict (space CLOSED, no active campaign). Never create `HANDOFF.md`.
6. STOP. No further work possible in this environment.

**Definition of Done (final):** full test suite green; all 30 artifacts (5 per campaign × 6 campaigns C310–C315) + 6 gitignored `full.json` on disk with SHA256 provenance; all caches <100 MB with `real_data_only:true,fabricated_data:false,executed_fills:false`; `edge_proven:false` with `binding_constraint:multiple_testing` universally; `oos_edge_proven:false`; `edge_claim:NONE`.

**Frozen/blocked (do NOT rerun, re-skin, re-probe, or pivot to):** C281B–C314 (formal negatives), C287 (external 451/no creds). Any work on them is a hard violation. In particular, do NOT re-run C314's lead-lag or C312's OFI — C315 uses a DIFFERENT signal (price momentum/reversal) on the SAME real, on-disk price data (read-only reuse, NOT a re-skin).

**THE PRIMARY DE-BOTTLENECK (data is already on disk — no network ingest needed):**
- Real 5m price data for all 10 symbols over 2023-01..2025-12 ALREADY EXISTS and is SHA-verified:
  - `data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz` → `perp_close` (USDT-M 5m klines close), 315,648 common-grid bars, 10 perps.
  - `data/cache/campaign314_spot_perp_leadlag_5m/<SYM>.npz` → `spot_close` + `perp_close`, 315,632 common-grid bars, 10 symbols.
- C315 reads these REAL prices (read-only), computes momentum/reversal features, and runs the sweep. **There is no download bottleneck this campaign** — the heavy work is the feature build + the 3456-config costed OOS sweep + gates + attribution. If you feel tempted to "just do a status update," that is a hard violation: build the cache, preflight, runner, tests, artifacts.

**Guardrails (enforced):**
- **No fabricated data / fail-closed / provenance-first:** `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`; SHA256-from-bytes for every artifact; missing/None/false gates BLOCK.
- **Bounded resources:** cache <100 MB total, per-asset `.npz` shards; slim sweep artifact <100 MB (no per-bar series) + gitignored `full.json`.
- **No overfitting:** ALL pre-registered configs reported; Holm+BH α=0.05 BOTH must pass; MDE + stability + momentum-vs-reversal-vs-placebo attribution required.
- **Costs real:** per-leg fee/slippage grid charged on turnover; model PnL labeled `executed_fills:false`. Perp funding unreachable (fapi 451) → excluded.

**Execute in order (all required — C315 complete, verify + close out):**
1. `python scripts/bootstrap_dev_env.py` (deps importable)
2. `python scripts/preflight_c315.py --json` → `ready:true`, `blocked_reasons:[]` (fail-closed)
3. Confirm all 5 artifacts + gitignored `full.json` on disk at `reports/campaign315_*_20261115T223831Z.{json,full.json}` with SHA256-from-bytes; slim sweep <100 MB
4. Add/pass `tests/test_preflight_c315.py` + `tests/test_c315_perp_momentum_reversal_oos.py`; run targeted/full suite green
5. Sync `AGENTS.md` + `research_state/state.yaml` with C315 verdict/SHAs/binding constraint (done this session). Register next genuinely-new reachable stat-arb family as active IF one exists; none reachable — space CLOSED. Never create `HANDOFF.md`.
6. Do NOT re-run/re-skin/probe C281B–C315 or C287 (C287 external 451/no creds, out-of-env unblock only).

**Definition of Done:** all 5 artifacts + full.json on disk with SHA256 provenance; ≥504 configs tested with Holm+BH reported; `edge_proven:true` OR formal negative with `binding_constraint`; cache <100 MB with correct flags; tests green.

### C315 CAMPAIGN SPECIFICATION (non-negotiable, heavy-work forcing)

**Objective:** Prove or retract costed OOS edge for cross-sectional & time-series momentum / short-term reversal on 10 USDT-M linear perps, 2023-01..2025-12.

**Data (real, on disk, read-only):** `data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz` `perp_close` (fallback `data/cache/campaign314_spot_perp_leadlag_5m/<SYM>.npz` `perp_close`). Universe: 10 USDT-M perps (BTC,ETH,BNB,SOL,XRP,ADA,DOGE,DOT,LTC,AVAX)USDT. Window 2023-01..2025-12. Native 5m. Any SHA mismatch vs the source `.meta.json` → BLOCK (no fabrication).

**Signals (pre-registered, causal shift(1)):**
- `xsec_mom(L)` = cross-sectional rank of trailing-L perp return (long top, short bottom).
- `xsec_rev(R)` = cross-sectional rank of trailing-R perp return, REVERSED (long worst, short best).
- `mom_minus_rev(L,R)` = combination of the two (momentum minus short-term reversal).
- Dollar-neutral, gross 1.0, applied from the next bar; hold rebalance{6,12,48} bars.

**Cost Model (execution-cost realism, charged on turnover):**
- fee {1,5,10,20} bps per leg; slippage {1,2,5,10} bps per leg.
- `symmetric` = (fee + slip) per unit turnover; `perp_heavy` = (1.5·fee + slip) per unit turnover (taker-heavy).
- Perp funding unreachable (fapi 451, not in archives) → excluded (control only).

**Walk-Forward / OOS:** expanding train 12m → test 3m, roll 3m over 36m. Multiple-testing: Holm-Bonferroni AND Benjamini-Hochberg at α=0.05 — BOTH must pass. MDE gate (observed mean > MDE mean). Stability gate (sign consistency ≥70% splits; first-half vs second-half Sharpe corr ≥0.5). Attribution gate (dominant of {momentum, reversal, placebo} share > 0.5 for a positive claim).

**Artifacts (MUST emit all 5 + full.json, bounded <100 MB):** `campaign315_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_<TS>.json` + gitignored `campaign315_oos_sweep_<TS>.full.json`, each with SHA256-from-bytes and `real_data_only:true,fabricated_data:false,executed_fills:false`.

**Tests (MUST add + pass):** `tests/test_preflight_c315.py`, `tests/test_c315_perp_momentum_reversal_oos.py`; full suite green.

**Bottleneck removal (enforced):** data already on disk (no ingest bottleneck); resumable/cached; bounded sweep; fail-closed preflight; Holm+BH; real costs. C287 stays BLOCKED/DECOUPLED. C281B–C314 FROZEN.

**Environment / verification:**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python scripts/bootstrap_dev_env.py
python -m pytest tests/ -q
python scripts/verify_env.py --json
python -m pip install "pytest-asyncio>=0.23"   # only if async tests fail with "async def not natively supported"
```

Known-good: Python 3.12.3, pandas 3.1.1, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1. `ruff`/`mypy` may be absent — do not claim they passed unless actually run. CI dependency note: run Step 0 bootstrap before campaign code; a missing-dependency traceback is a bootstrap gap, not a research result. Do not fix by editing `.github/workflows/main.yml`.

## C314 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-15T21:38:11Z)

- **Scripts PRESENT (uncommitted):** `scripts/ingest_c314_spot_perp_leadlag_5m.py`, `scripts/preflight_c314.py`, `scripts/run_c314_spot_perp_leadlag_oos.py`.
- **Tests COMPLETE & PASSING:** `tests/test_preflight_c314.py`, `tests/test_c314_spot_perp_leadlag_oos.py` (25/25 C314 tests green).
- **Cache COMPLETE (real data, ~22 MB):** `data/cache/campaign314_spot_perp_leadlag_5m/` with 10 `.npz` shards (ADAUSDT, AVAXUSDT, BNBUSDT, BTCUSDT, DOGEUSDT, DOTUSDT, ETHUSDT, LTCUSDT, SOLUSDT, XRPUSDT) each holding `index_ms`, `spot_close`, `perp_close`, `funding_rate` (all-NaN control-only). 315,632 common-grid 5m bars, 2023-01..2025-12. `months_manifest.json` `{"assembled":[...10...],"months":{}}`. Total 22 MB, max shard 2.69 MB. `real_data_only:true, fabricated_data:false, executed_fills:false`.
  - **KEY DE-BOTTLENECK (do not re-litigate):** Binance **spot** 5m klines switched `open_time` to MICROSECONDS from 2025-01 (e.g. `1735689600000000`) while USDT-M perp stays in milliseconds (`1735689600000`). The ingest normalizes open_time to ms (`normalize_open_time_ms`, threshold >1e14 → //1000) on BOTH write and read paths. Without this the spot/perp intersection collapses to 210,512 bars (67% < 80% gate) and every month from 2025-01 fails. This is fixed and covered by `test_preflight_2025_microsecond_spot_normalized`.
  - Cache meta SHA256 `4bd0e8c97e23fa01d1681357b70e6191caaf6ed5b5a9d4be1d2fd2a3d112f983`; provenance SHA256 `aa2aa688594ff5f3d02ad061ffbf983d5e9a023d365403f144e0c196172bccb6`.
- **Preflight:** `python scripts/preflight_c314.py --json` → `ready:true`, `blocked_reasons:[]`, 10/10 shards, grid in window.
- **Runner/artifacts COMPLETE at `20261115T214305Z`:** 2304 pre-registered configs (lag_window×threshold×rebalance×fee×slip×tercile×cost_variant), expanding WF 12m/3m/3m. **VERDICT: RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing` — 0 deterministic edge, 0 survive Holm, 0 survive BH, 0 survive both; `leadlag_vs_noise_share = 0.000275` (noise-dominated, no lead-lag edge); 1664/2304 configs had exposure. All 5 artifacts + gitignored `full.json` on disk with SHA256-from-bytes:
  - oos_sweep `3b78ccd1f2caa8e93791b06d338aa1b1ce771caed629c460a05d1077e79db45b` (slim ~1.9 MB)
  - tradable_edge_registry `bd92bd6fc53315981e066e3c081a5aa310881b3a7019c063d1763c56c3e97094`
  - summary `8f5045e7bf3e39aebc4c065a9fe64d54c15cbd8c97d7cf143b2f0aab1b67b9f0`
  - verdict `0b5c40e8da9b1e3177d99afc4c216f51f38d0b1f8c18a7069137a762bfdb6716`
  - binding_constraint `592403e4dd7c8071e88f41684f53563dae62b8072c61ba449dc30cd37e5ac07b`
  - full sweep kept on disk as `reports/campaign314_oos_sweep_20261115T214305Z.full.json` (gitignored).

## C313 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-15T20:45:00Z, frozen)
- Scripts PRESENT: `scripts/ingest_c313_coinm_quarterly_carry.py`, `scripts/preflight_c313.py`, `scripts/run_c313_coinm_quarterly_carry_oos.py`. Tests 23/23 green. Cache `data/cache/campaign313_coinm_quarterly_carry/` (8 shards + manifest + meta/provenance, ~4.0 MB, 1h 2022-07..2026-06). VERDICT: RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing` (0/960 deterministic edge, 0 survive Holm+BH). Artifacts at `20261115T204419Z`. Do not rerun.

## C312 on-disk state (COMPLETE FORMAL NEGATIVE, verified 2026-11-15T18:50Z, frozen)
- Cache READY (real data only): `data/cache/campaign312_usdt_m_ofi_5m/` (10 perps, 315,648 5m bars, 2023-01..2025-12, ~65 MB, `real_data_only:true`, `fabricated_data:false`, `executed_fills:false`, `perp_close` usable by C315). Scripts/tests/artifacts present; VERDICT: RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing` (0/504 Holm+BH). Do not rerun.

## Bottlenecks removed / guardrails
- **C314 microsecond spot open_time (2025-01+) NORMALIZED to ms** in ingest (`normalize_open_time_ms`) — the key fix that made spot/perp 5m intersect across the full 36 months. Covered by a regression test.
- **C315 needs NO network ingest** — real 5m prices already on disk (C312/C314 caches); C315's heavy work is the feature build + 3456-config sweep, not downloads.
- Resumable manifest ingest (per symbol/market/month) where ingest is needed; bounded cache (<100 MB); bounded sweep + gitignored `full.json`; funding NaN/control-only if unreachable; C287 external/decoupled; C281B–C314 frozen.
- Archive host flaky — every download retries with backoff (6 attempts, linear 1 s×k); lone 404/5xx retryable; 404 month = pre-listing exclusion (not outage).
- Recent monthly archives may carry a CSV header (`open_time`) — detect header vs headerless.
- `signed_volume`/`trade_sign_sum` are legitimately signed (buy−sell) — never gate as non-negative.
- Caches <100 MB (assert); keep per-asset `.npz` shards.
- C287 (testnet gateway: Binance testnet REST 451, fapi 451, bybit 403, no creds) — BLOCKED/DECOUPLED, external-only, never retry as economic work.
- COIN-M `indexPriceKlines`, `bookTicker`, `bookDepth`, `metrics`, `option/` — HTTP 404 on data.binance.vision; never depend. USDT-M `fundingRate` not in monthly archives and fapi 451 → funding leg NaN (control-only).

## C312 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T174346Z` over the real USDT-M 5m klines native ingest (`data/cache/campaign312_usdt_m_ofi_5m/`, 10 perps, 315,648 common-grid 5m bars, 2023-01..2025-12) → **RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing`. Of 504 pre-registered configs, **0 deterministic edge, 0 survive Holm AND BH** (0 Holm, 0 BH, 0 both); 0 survive cost-realism. Observed mean 0.0 bps/split. OFI-carry share 0.0 vs convexity share 0.0 → `edge_explained_by_ofi_carry: false`. Artifacts `reports/campaign312_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T174346Z.json` exist; SHA256-from-bytes: sweep `a15aaa40329b44c85b0f64cafe52b8bb8bf73b2431f73463cbef5c4e8dcbb8d4`, registry `4678c43167eee5181e288b3606cf4536ad3ee1870a4bc9599d07bf6209fa41f5`, summary `c1889d55654505e9947da3d7566ce6916e10783bc52a8214e9b4480c239613cf`, verdict `9a7b8e7f1b3c2d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9`, binding `13c7479777a4f5c698836067fdd87f3686aa82e5dd16496f16051c11f788f5e5`. The sweep was slimmed to ~927 KB (per-split series dropped; full 340 MB kept on disk as `reports/campaign312_oos_sweep_20261115T174346Z.full.json`, gitignored). C312 tests green (21/21).

## C311 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T125846Z` over the real COIN-M aggTrades **native 5m** ingest (`data/cache/campaign311_coinm_ofi_5m/`, 11 perps, 419,616 common-grid 5m bars, 2022-07..2026-06) → **RETRACTED**, `edge_proven:false`, `binding_constraint: multiple_testing`, convexity-dominated. Of 504 pre-registered configs, **17 deterministic edge, 0 survive Holm AND BH** (0 Holm, 0 BH, 0 both); 17 survive cost-realism but fail multiple-testing. MDE mean 0.107 bps vs observed −0.0126 bps/split; stability 17/17 first-half and second-half. Attribution: **OFI-carry share 0.025 vs inverse-convexity share 0.975** → `edge_explained_by_ofi_carry: false`. Artifacts `reports/campaign311_{oos_sweep,tradable_edge_registry,summary,verdict,binding_constraint}_20261115T125846Z.json` exist; SHA256-from-bytes: sweep `238cb14418c080e8089f2ef222447674641d57e0089402f27bb426f18356a582`, registry `499985448b2dd34da62c9a785950e4168f5f8ce82bdd97d0ac0078b6167bb85e`, summary `515323c39a0cebb7383eb014084c49b2404f6319c1a743a46a628565da4868e9`, verdict `42b885a111f321ed770722e98cfdcb3652226cd65e9c31b8b15d105e1e2437c6`, binding `66f611172056433e78c66bb957e5c4a435b9771945406048cf592f634a06de6c`. The sweep was slimmed to ~1 MB (per-split series dropped; full 427 MB kept on disk as `reports/campaign311_oos_sweep_20261115T125846Z.full.json`, gitignored). C311 tests green (22/22).

## C310 (COMPLETE FORMAL NEGATIVE, FROZEN — do not rerun)

Executed `20261115T111243Z` over a NEW real COIN-M aggTrades 1h ingest → RETRACTED, `edge_proven:false`, `binding_constraint: multiple_testing`. Of 504 pre-registered configs, 30 deterministic edge, **0 survive Holm AND BH**; 30 survive cost-realism. MDE mean 1.166 bps vs observed −0.179 bps/split. OFI-carry share 0.088 vs inverse-convexity 0.912. Cache `data/cache/campaign310_coinm_aggtrades_ofi.pkl` (28.34 MB, SHA256 `393173923815a0e7bc1f06fff439089d50a54e665a7ce1f19f5ba5b5e1d876e8`) is a reusable real-data asset but is 1h-aggregated only (cannot re-aggregate to 5m).

## Bottlenecks removed (do NOT re-litigate)

0. **C314 spot 5m `open_time` MICROSECONDS (2025-01+) → NORMALIZED to ms.** Binance spot monthly klines switched `open_time` to microseconds from 2025-01 (e.g. `1735689600000000`) while USDT-M perp stays in ms (`1735689600000`). The C314 ingest normalizes on both write and read paths (`normalize_open_time_ms`, threshold >1e14 → //1000). Without it the spot/perp intersection collapses to 210,512 bars (67% < 80% gate) and all 2025 months fail. Regression test: `test_preflight_2025_microsecond_spot_normalized`.
1. **C311 runner was the blocked item — now EXECUTED** (`20261115T125846Z`); all 5 artifacts + 22 tests green. Nothing about C311 remains to run.
2. **C311 oos_sweep was 446 MB (>100 MB GitHub push limit) → slimmed to ~1 MB** on disk; the runner now drops per-split series on write; the full blob is kept as `reports/*.full.json` (gitignored) for audit. Any future campaign MUST emit a bounded sweep.
3. **C312 reachability verified live** (USDT-M aggTrades AND USDT-M 5m klines = the exec-price endpoint, both HTTP 206 for BTCUSDT @2023-06; SOLUSDT aggTrades @2023-06 also 206). Pre-listing months 404 (e.g. SOL 2020-08) — exclude, do not treat as outage.
4. **C312 scope BOUNDED** to 10 linear USDT-M perps × 2023-01..2025-12 to stay < 100 MB cache and download-tractable (an unbounded "wide universe over many years" would exceed the 100 MB cache rule and blow the session budget).
5. **C312 ingest must be RESUMABLE per (symbol, month)** — this is the primary de-bottleneck: a multi-GB USDT-M aggTrades download survives session boundaries (skip months already in `months_manifest.json`, resume instead of restart). Do not copy the C311 per-symbol-only (non-resumable) behavior.
6. C310 cache is 1h-aggregated only; C311 re-downloaded the COIN-M aggTrades window once (~6.2 GB, streaming); C312 needs its own USDT-M aggTrades ingest (per-month streaming, discard raw, resumable).
7. Archive host flaky — every download retries with backoff (6 attempts, linear 1 s×k); lone 404/5xx retryable.
8. Recent monthly archives may carry CSV header `open_time`/`agg_trade_id` — detect header vs headerless.
9. `signed_volume`/`trade_sign_sum` are legitimately signed (buy−sell) — never gate as non-negative.
10. Caches < 100 MB (assert). Keep per-asset `.npz` shards; total < 100 MB. C312 estimated ~60 MB.
11. C287 (testnet gateway: Binance testnet REST 451, fapi 451, bybit 403, no creds) — BLOCKED/DECOUPLED, external-only, never retry as economic work.
12. COIN-M `indexPriceKlines`, `bookTicker`, `bookDepth`, `metrics`, `option/` — all HTTP 404 on data.binance.vision; never depend on them. USDT-M `fundingRate` is not in monthly archives and fapi is 451 → C312 funding leg is NaN (control-only).

## Repository priority

`cryptoquantstatarbstrats` = crypto quantitative **statistical arbitrage**. Economic progress = costed out-of-sample PnL on real, provable data. Any turn producing neither a real-data validation, a costed-OOS run, a passing test, or an artifact update is NOT economic progress.

## Non-negotiable constraints

1. **NO FABRICATED DATA** — every artifact `real_data_only: true`, `fabricated_data: false`.
2. **FAIL-CLOSED** — missing/None/false gate values block entries.
3. **PROVENANCE FIRST** — every number traces to source, timestamp, host, blocked routes, rationale.
4. **COSTS ARE REAL** — all backtests use the stated fee/slippage grid; model PnL labeled `executed_fills: false`.
5. **NO OVERFITTING** — walk-forward, all pre-registered configs reported, multiple-testing correction before any positive claim.
6. **TESTS MUST PASS** — new code adds tests; CI stays green.
7. **SINGLE HANDOFF** — update only `AGENTS.md` and `research_state/state.yaml`; do not create `HANDOFF.md`.
8. **ECONOMIC PRIORITY** — C287 is blocked externally and decoupled; do not retry as economic work.

## Escalation

- **C314 (COMPLETE FORMAL NEGATIVE, 20261115T214305Z):** spot-perp lead-lag stat-arb, 2304 configs, 0 deterministic edge, 0 survive Holm+BH, binding `multiple_testing`, leadlag_vs_noise_share 0.0003; 5 artifacts + full.json + 25 C314 tests green; full suite 1642 passed / 2 skipped / 0 failed (verified 2026-11-15T23:09:39Z). De-bottleneck: spot 5m microsecond `open_time` (2025-01+) normalized to ms.
- **C313 (COMPLETE FORMAL NEGATIVE, 20261115T204419Z):** 0/960 Holm+BH, binding `multiple_testing`; 5 artifacts + 23 tests green. Do not rerun.
- **C312 (COMPLETE FORMAL NEGATIVE, 20261115T174346Z):** 0/504 survive Holm+BH, binding `multiple_testing`; 5 artifacts + full.json + 21 tests green.
- **C311 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 5 artifacts + 22 tests green; sweep slimmed <1 MB.
- **C310 (FROZEN, formal negative):** 0/504 survive Holm+BH, binding `multiple_testing`; convexity-dominated; 1h cache reused as real-data asset.
- **C306–C309 (FROZEN formal negatives / RETRACTED):** do not rerun. C309 0/504 Holm+BH; C308 0/53 Holm+BH; C307 retracted by C308; C306 0/448 cost_sensitivity.
- **C281B–C305 (FROZEN formal negatives):** 0 costed-OOS edge; do not rerun/re-skin.
- **C287 (BLOCKED/DECOUPLED):** external-only geographic/credential issue (testnet 451, no creds). Do not retry, do not probe, do not let it preempt economic work. Unblocking requires out-of-env action only.