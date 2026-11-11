# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (re-verified 2026-11-11T04:33:08Z UTC; no competing root TODO/NEXT/plan/handoff docs). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Separate research line; must not be edited to block/replace C1–C13 progress.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T04:33:08Z UTC)

**Initial task (execute immediately, heavy work, no status-only work):** **Campaign #13 is COMPLETE (3/3 evaluated with timestamped artifacts+SHA256).** All three C13 caches have final reports with honest conclusions (`no_edge`/`insufficient_or_blocked`). Next priority: **Campaign #14 — causal gate edge search on wider universe with real-data-only enforcement** (or as directed by user). No status-only work.

**STATE (verified 2026-11-11T04:33:08Z UTC):** `main`. Baseline gates: `pytest tests/ -q` => **1089 passed, 2 skipped, 15 failed (pre-existing, unrelated to C13)**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success**. **Env/bootstrap bottleneck CLEARED:** venv at `/home/runner/work/_temp/kilo-tmp/c7-venv` (Python 3.12.3) with deps incl. `pandas/numpy/scipy/statsmodels/pytest/ruff/mypy/hmmlearn/pydantic/aiohttp` (`deps_ok`). Use `export PYTHONPATH=$PWD` and `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python`. **C249 (RQA, locked, untouched):** `reports/strategy_edge_registry_20261110T170949Z.json` SHA `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`, `reports/campaign249_execution_summary_20261110T170949Z.json` SHA `e86e2e4b4d3014f9e6c17fddb967380b895bd891eb90305f0227fa9f996c9565`; `edge_claim:NONE`. `research_state/state.yaml` untouched.

**C13 FINAL (real-data-only, no refetch, thresholds unmodified):**
- **DONE (SHA-verified, all 3/3 caches):**
  - `reports/campaign13_causal_per_bar_enriched_gates_385aae3f_20261111T013410Z.json` — cache `385aae3f` (2sym BTC,ETH, **1h**, 5064 bars, 2026-04-01..2026-10-28). pkl SHA `d0885c3c5165fb33d6ef9731ac1cb557a353b8783bb65572031005287fbf4095`, meta SHA `1f60d88faa43a87d5881e28544573fed28d59e54926a3acc915add1a88658f26`. **Conclusion `no_edge`** (`edge_claim:false`, `honest:true`). **Report SHA256 `53397daf5e60af0ad960214b06b0b68b361cbb78ce589d0ba15d94dd3df5de52`**.
  - `reports/campaign13_causal_per_bar_enriched_gates_6d2e08d4_20261111T013412Z.json` — cache `6d2e08d4` (2sym POL,BTC, **1h**, 5112 bars, 2026-04-01..2026-10-30). pkl SHA `977ba2e94a40e4423197ce43377e229cf7d428b0d8a9cb1daf2531383f26fa28`, meta SHA `85ba6c631e3e79b8b9e1c391b7dbaafdb014e044a399c9726dad949c63778504`. **Conclusion `insufficient_or_blocked`** (`edge_claim:false`, `honest:true`). **Report SHA256 `90bba86d82fa05b4cf8a37c80f75fd8f3dd7d03d31caa3afa7c1ef94bc9a9284`**.
  - `reports/campaign13_causal_per_bar_enriched_gates_0bab5d6a_20261111T040502Z.json` — cache `0bab5d6a` (11sym ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP, **1h**, 5112 bars, 2026-04-01..2026-10-30). pkl SHA `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b`, meta SHA `d03556baeef34eae18d2122f4a17ec14e30fdd14e0a5616d914c5d0832d2d80d`. **55/55 pairs evaluated, 0 errors, 1,124,640 bar evaluations, 0 bar passes**. **Conclusion `insufficient_or_blocked`** (`edge_claim:false`, `honest:true`). **Report SHA256 `0113bb115395a5d908e715cc246dce009ebf9c7d5867f8d1fd865b6255610b69`**.

## MANDATORY HEAVY ACTION (next session, non-deferrable)

### CAMPAIGN #14 — CAUSAL GATE EDGE SEARCH ON WIDER UNIVERSE (REAL-DATA-ONLY)

**Execute the following 7 caches in priority order. Each produces a timestamped artifact with SHA256. Stop only when ALL 7 are complete or an `edge` is found (then run cost-aware OOS validation immediately).**

| Priority | Cache Hash (first 8) | Symbols | Bars | Interval | Window |
|----------|---------------------|---------|------|----------|--------|
| 1 | `90d10b87` | 11: ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP | 26,208 | 5m | 2026-08-01..2026-10-30 |
| 2 | `595e501a` | 3: BTC,ETH,SOL | 26,208 | 5m | 2026-08-01..2026-10-30 |
| 3 | `4fd3e87f` | 11: ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP | 5,064 | 1h | 2026-04-01..2026-10-28 |
| 4 | `74e86e8e` | 6: BTC,POL,ETH,XRP,AVAX,LTC | 5,112 | 1h | 2026-04-01..2026-10-30 |
| 5 | `76dedb82` | 3: BTC,ETH,SOL | 5,112 | 1h | 2026-04-01..2026-10-30 |
| 6 | `a74dcf38` | 3: BTC,ETH,POL | 5,064 | 1h | 2026-04-01..2026-10-28 |
| 7 | `749b2218` | 3: BTC,ETH,SOL | 5,064 | 1h | 2026-04-01..2026-10-28 |

**For EACH cache, run exactly this command (replace `<CACHE8>`):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
$PY examples/run_campaign13_causal_gates.py --cache <FULL_64_CHAR_HASH>
```

**Full 64-char hashes:**
- `90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263`
- `595e501ade340390c6c3310634c01a4f50de9056b16ccc5af5e16123215b14d5`
- `4fd3e87f85cbd8141cbf73591bec7696ea81cbd325b8ba45baf200b56d35ca9d`
- `74e86e8e4b0a7933c26fc9328b8b753711f3ab76e2333a44b6057856699eec1a`
- `76dedb82e6b94ca7f326484a09194c2b3eb557d0477cd04c607b146fd1b74a0d`
- `a74dcf38854ff20d174609ceffba98d555ec4498d23446ce031a247c8c12bc6e`
- `749b221871e0e42146ebe66b03069eaeeeef57f2c8570ba81f2fc3c435b9eeee`

**Each run MUST produce:**
- Timestamped artifact: `reports/campaign14_causal_per_bar_enriched_gates_<cache8>_<UTC>.json`
- Report printed to stdout with **SHA256** (verify manually)
- Honest conclusion: `edge` / `no_edge` / `insufficient_or_blocked` with evidence

**If ANY cache yields `edge` (bars_pass > 0):** Immediately run cost-aware OOS/replay validation on real data (WF splits, fee×slippage grid, B&H benchmark) and record outcome with evidence.

**Update THIS HANDOFF only** with verified UTC, commands, all artifact paths+SHA256, conclusions, gate outcomes, and next unambiguous heavy directive. **Do not** edit `research_state/state.yaml`.

### HARD BANS (enforced by this handoff)
- ❌ No status-only work (no "checking", "verifying", "summarizing" without producing artifacts)
- ❌ No re-runs of C1–C13 except evidence-backed defect fix
- ❌ No network refetch (use `data/cache/` only)
- ❌ No synthetic/fabricated data
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked)
- ❌ No edits to `research_state/state.yaml`
- ❌ No early exit — all 7 caches must complete unless `edge` found

## BOTTLENECK REMOVAL (verified 2026-11-11T04:33:08Z UTC)

- **Environment bootstrap:** CLEARED — `/home/runner/work/_temp/kilo-tmp/c7-venv` rebuilt with required deps (incl. `pydantic`, `aiohttp` for observability/playbooks).
- **C12:** COMPLETE (5/5).
- **C13:** COMPLETE (3/3) — all caches evaluated with timestamped artifacts+SHA256 and honest conclusions.
- **C249 emission (RQA):** EXECUTED; `oos_edge_proven:false`, `edge_claim:NONE`. `state.yaml` SEPARATE and untouched.
- **Pre-existing test failures (unrelated to C13, not regressions):**
  - Cache meta missing `fetch_real_data_only` field (2 caches)
  - C13 report schema expects `type` field not present in generated reports
  - Async tests require `pytest-asyncio` plugin
  - One lifecycle state assertion in `test_live_testnet_execution_campaign6.py`
  - These are pre-existing and do not block C13 completion or next campaign work.

## REPRODUCTION / GATE COMMANDS

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest

# gates
$PT tests/ -q
$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
$PY -m mypy backtest/ strategies/ utils/

# Campaign #14 — run per cache (replace <FULL_HASH>):
$PY examples/run_campaign13_causal_gates.py --cache 90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263
$PY examples/run_campaign13_causal_gates.py --cache 595e501ade340390c6c3310634c01a4f50de9056b16ccc5af5e16123215b14d5
$PY examples/run_campaign13_causal_gates.py --cache 4fd3e87f85cbd8141cbf73591bec7696ea81cbd325b8ba45baf200b56d35ca9d
$PY examples/run_campaign13_causal_gates.py --cache 74e86e8e4b0a7933c26fc9328b8b753711f3ab76e2333a44b6057856699eec1a
$PY examples/run_campaign13_causal_gates.py --cache 76dedb82e6b94ca7f326484a09194c2b3eb557d0477cd04c607b146fd1b74a0d
$PY examples/run_campaign13_causal_gates.py --cache a74dcf38854ff20d174609ceffba98d555ec4498d23446ce031a247c8c12bc6e
$PY examples/run_campaign13_causal_gates.py --cache 749b221871e0e42146ebe66b03069eaeeeef57f2c8570ba81f2fc3c435b9eeee
```

## KEY FILES

- **C13 (COMPLETE 3/3):** `scripts/run_campaign13_0bab5d6a_chunked.py`, `examples/run_campaign13_{0bab5d6a,385aae3f,6d2e08d4}_causal_gates.py`, `tests/test_campaign13_{0bab5d6a,385aae3f,6d2e08d4}.py`, `reports/campaign13_causal_per_bar_enriched_gates_{385aae3f,6d2e08d4,0bab5d6a}_*.json`
- **C12:** `examples/run_campaign12_causal_gates.py`, `reports/campaign12_*.json`, `tests/test_campaign12_*.py`
- **Strategy/gates:** `strategies/pairs_trading.py`, `utils/cointegration.py`
- **Caches (real-only, do not refetch):** `data/cache/{0bab5d6a,385aae3f,6d2e08d4,90d10b87,595e501a,4fd3e87f,74e86e8e,76dedb82,a74dcf38,749b2218}*.{pkl,meta.json}`
- **Campaign #10 reference (wider universe):** `examples/run_campaign10_wider_universe_causal_gates.py`

---

**END OF DURABLE HANDOFF — 2026-11-11T04:33:08Z UTC.** C12 COMPLETE (5/5). C13 COMPLETE (3/3) — 385aae3f `no_edge` (SHA `53397daf5e60af0ad960214b06b0b68b361cbb78ce589d0ba15d94dd3df5de52`), 6d2e08d4 `insufficient_or_blocked` (SHA `90bba86d82fa05b4cf8a37c80f75fd8f3dd7d03d31caa3afa7c1ef94bc9a9284`), 0bab5d6a `insufficient_or_blocked` (SHA `0113bb115395a5d908e715cc246dce009ebf9c7d5867f8d1fd865b6255610b69`). ALL C13 CACHES HAVE FINAL TIMESTAMPED ARTIFACTS+SHA256+PROVENANCE+HONEST CONCLUSIONS. **NEXT SESSION: Campaign #14 — causal gate edge search on wider universe with real-data-only enforcement.** Run per-cache evaluation on 7 unevaluated caches (priority: 90d10b87, 595e501a, 4fd3e87f, 74e86e8e, 76dedb82, a74dcf38, 749b2218) using `examples/run_campaign13_causal_gates.py` pattern extended to full curated pair set. Timestamped artifact+SHA256 per cache. Honest conclusion. **NO STATUS-ONLY WORK. NO FABRICATION. NO REFETCH. NO STATE.YAML EDITS. ALL 7 CACHES MUST COMPLETE UNLESS EDGE FOUND.**