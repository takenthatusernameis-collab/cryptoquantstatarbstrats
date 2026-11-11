# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (re-verified 2026-11-11T03:36:05Z UTC; no competing root TODO/NEXT/plan/handoff docs). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Separate research line; must not be edited to block/replace C1–C13 progress.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T03:36:05Z UTC)

**Initial task (execute immediately, heavy work, no status-only work):** **Complete Campaign #13 by finishing cache `0bab5d6a` (11sym/55 pairs/5112 bars, 1h).** Campaign #12 is COMPLETE (5/5). Campaign #13 is **2/3 evaluated** with timestamped artifacts+SHA256; `0bab5d6a` is **in progress with durable resumable progress** but no final report yet. You must drive `0bab5d6a` to a timestamped `reports/campaign13_causal_per_bar_enriched_gates_0bab5d6a_<UTC>.json` with SHA256 + full provenance (`real_data_only`, `fabricated_data:false`, `blocked_routes`/rationale) and honest conclusion (`edge_signal`/`no_edge`/`insufficient_or_blocked`), OR to a concretely evidenced `insufficient_or_blocked` artifact with `blocked_routes`/rationale if completion is impossible without fabrication — **no deferral, no status-only work**.

**STATE (verified 2026-11-11T03:36:05Z UTC):** `main`. Baseline gates last fully verified 2026-11-11T03:14:43Z: `pytest tests/ -q` => **1089 passed, 2 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success**. **Env/bootstrap bottleneck CLEARED this session:** rebuilt venv at `/home/runner/work/_temp/kilo-tmp/c7-venv` (Python 3.12.3), installed deps incl. `pandas/numpy/scipy/statsmodels/pytest/ruff/mypy/hmmlearn` (`deps_ok`). Use `export PYTHONPATH=$PWD` and `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python`. **C249 (RQA, locked, untouched):** `reports/strategy_edge_registry_20261110T170949Z.json` SHA `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`, `reports/campaign249_execution_summary_20261110T170949Z.json` SHA `e86e2e4b4d3014f9e6c17fddb967380b895bd891eb90305f0227fa9f996c9565`; `edge_claim:NONE`. `research_state/state.yaml` untouched.

**C13 progress (real-data-only, no refetch, thresholds unmodified):**
- **DONE (SHA-verified):**
  - `reports/campaign13_causal_per_bar_enriched_gates_385aae3f_20261111T013410Z.json` — cache `385aae3f022b2d7bba4ec502cb8e7399d26cb31b961a016aebf7d165450fd4ba` (2sym BTC,ETH, **1h**, 5064 bars, 2026-04-01..2026-10-28). pkl SHA `d0885c3c5165fb33d6ef9731ac1cb557a353b8783bb65572031005287fbf4095`, meta SHA `1f60d88faa43a87d5881e28544573fed28d59e54926a3acc915add1a88658f26`. **Conclusion `no_edge`** (`edge_claim:false`, `honest:true`). **Report SHA256 `53397daf5e60af0ad960214b06b0b68b361cbb78ce589d0ba15d94dd3df5de52`**.
  - `reports/campaign13_causal_per_bar_enriched_gates_6d2e08d4_20261111T013412Z.json` — cache `6d2e08d4d7b969d92b61773c7eead387a52ad74b1c3fb0c69552bd6402dd4383` (2sym POL,BTC, **1h**, 5112 bars, 2026-04-01..2026-10-30). pkl SHA `977ba2e94a40e4423197ce43377e229cf7d428b0d8a9cb1daf2531383f26fa28`, meta SHA `85ba6c631e3e79b8b9e1c391b7dbaafdb014e044a399c9726dad949c63778504`. **Conclusion `insufficient_or_blocked`** (`edge_claim:false`, `honest:true`). **Report SHA256 `90bba86d82fa05b4cf8a37c80f75fd8f3dd7d03d31caa3afa7c1ef94bc9a9284`**.
- **IN PROGRESS (durable, resumable; bottleneck mitigated):**
    - `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7` (11sym ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP, **1h**, 5112 bars, 2026-04-01..2026-10-30). pkl SHA `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b`, meta SHA `d03556baeef34eae18d2122f4a17ec14e30fdd14e0a5616d914c5d0832d2d80d`. **No final `reports/campaign13_causal_per_bar_enriched_gates_0bab5d6a_<UTC>.json` yet.**
    - **Chunked resumable runner created:** `scripts/run_campaign13_0bab5d6a_chunked.py` (real cached data only; unmodified thresholds; per-pair partial save; emits final timestamped report+sha on completion). Executes 55 curated pairs deterministically with lookbacks [120,240], check_intervals [24,48], strict enriched gates.
    - **Partial progress persisted:** `reports/campaign13_0bab5d6a_partial_all.json` — **12/55 pairs completed, 0 errors** as of `2026-11-11T03:36:05Z` (keys include BTC/ETH,ETH/SOL,BTC/SOL,ADA/ETH,XRP/BTC,BNB/ETH,ADA/BTC,XRP/ETH,BNB/BTC,SOL/BNB,DOT/BTC,DOT/ETH). **Partial SHA256 `cfc39a1f4b7741a3481fafcb62ffdfca05330a1b37b33d91784d0d2840806ab7`** (updated 2026-11-11T03:36Z snapshot). Runner may be actively continuing; if not, it is fully resumable (skips completed pairs). Prior monolithic attempts died ~6-7/55 with no artifact; chunked partials remove that evidence/progress bottleneck.

## MANDATORY HEAVY ACTION (next session, non-deferrable)

1. **Finish C13 `0bab5d6a` to a final artifact:** `cd ... && export PYTHONPATH=$PWD && /home/runner/work/_temp/kilo-tmp/c7-venv/bin/python scripts/run_campaign13_0bab5d6a_chunked.py` (monitor until it prints `FINAL_REPORT ... <sha> <conclusion>` and writes `reports/campaign13_causal_per_bar_enriched_gates_0bab5d6a_<UTC>.json` + `.sha256`). It resumes from `reports/campaign13_0bab5d6a_partial_all.json`. If it dies, restart (progress preserved) and capture concrete evidence (exit, last pair, log tail, resources). If completion is genuinely impossible without fabrication, emit an honest `insufficient_or_blocked` final artifact with `blocked_routes`/rationale and the partial evidence (do not leave unevidenced).
2. **Record deliverables:** final report path, `sha256sum`, conclusion (`edge_signal`/`no_edge`/`insufficient_or_blocked`), `edge_claim`, bars/gate aggregate, provenance (cache/pkl/meta SHAs). Ensure C13 per-cache deliverables exist for 0bab5d6a: timestamped artifact+SHA256 recorded; `examples/run_campaign13_0bab5d6a_causal_gates.py` and `tests/test_campaign13_0bab5d6a.py` present/deterministic and targeted tests run.
3. **Gates:** `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest tests/ -q`, `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python -m mypy backtest/ strategies/ utils/` and fix regressions if any.
4. **If any gate-pass/edge signal appears:** immediately run cost-aware OOS/replay validation on real data (WF splits, fee×slippage grid, B&H benchmark) and record outcome with evidence.
5. **Update this HANDOFF only** with verified UTC, commands, all artifact paths+SHA256, conclusions, gate outcomes, and next unambiguous heavy directive. **Do not** edit `research_state/state.yaml`. No fabrication, no refetch, no threshold weakening.

**Hard bans:** no status-only work; no re-runs of C1–C12 except evidence-backed defect fix; no network refetch; no synthetic data; no threshold weakening; no edits to `research_state/state.yaml`.

## BOTTLENECK REMOVAL (verified 2026-11-11T03:36:05Z UTC)

- **Environment bootstrap:** CLEARED — `/home/runner/work/_temp/kilo-tmp/c7-venv` rebuilt with required deps.
- **C12:** COMPLETE (5/5).
- **C13 385aae3f, 6d2e08d4:** CLEARED — evaluated with timestamped artifacts+SHA256 and honest conclusions.
- **C13 0bab5d6a "dies with no evidence" runtime bottleneck:** MITIGATED — `scripts/run_campaign13_0bab5d6a_chunked.py` provides deterministic, resumable per-pair execution persisting `reports/campaign13_0bab5d6a_partial_all.json` (12/55 done, 0 errors, SHA `cfc39a1f4b7741a3481fafcb62ffdfca05330a1b37b33d91784d0d2840806ab7` at 2026-11-11T03:36Z). Final report not yet emitted; continue to completion or evidenced blocker.
- **C249 emission (RQA):** EXECUTED; `oos_edge_proven:false`, `edge_claim:NONE`. `state.yaml` SEPARATE and untouched.

## REPRODUCTION / GATE COMMANDS

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest

# C13 0bab5d6a (finish/resume to final artifact)
$PY scripts/run_campaign13_0bab5d6a_chunked.py

# gates
$PT tests/ -q
$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
$PY -m mypy backtest/ strategies/ utils/
```

## KEY FILES

- **C13:** `scripts/run_campaign13_0bab5d6a_chunked.py`, `examples/run_campaign13_{0bab5d6a,385aae3f,6d2e08d4}_causal_gates.py`, `tests/test_campaign13_{0bab5d6a,385aae3f,6d2e08d4}.py`, `reports/campaign13_causal_per_bar_enriched_gates_{385aae3f,6d2e08d4}_*.json`, `reports/campaign13_0bab5d6a_partial_all.json` (in-progress)
- **C12:** `examples/run_campaign12_causal_gates.py`, `reports/campaign12_*.json`, `tests/test_campaign12_*.py`
- **Strategy/gates:** `strategies/pairs_trading.py`, `utils/cointegration.py`
- **Caches (real-only, do not refetch):** `data/cache/{0bab5d6a,385aae3f,6d2e08d4}*.{pkl,meta.json}`

---

**END OF DURABLE HANDOFF — 2026-11-11T03:36:05Z UTC. C12 COMPLETE (5/5). C13: 385aae3f `no_edge` (SHA `53397daf5e60af0ad960214b06b0b68b361cbb78ce589d0ba15d94dd3df5de52`), 6d2e08d4 `insufficient_or_blocked` (SHA `90bba86d82fa05b4cf8a37c80f75fd8f3dd7d03d31caa3afa7c1ef94bc9a9284`), **0bab5d6a IN PROGRESS — resumable chunked run 12/55 pairs done, partial SHA `cfc39a1f4b7741a3481fafcb62ffdfca05330a1b37b33d91784d0d2840806ab7`, final report pending**. Env/bootstrap and evidence-bottleneck cleared (venv rebuilt, `scripts/run_campaign13_0bab5d6a_chunked.py`). NEXT SESSION: run chunked script to completion, emit final timestamped artifact+SHA256+honest conclusion (or evidenced blocker), run gates. NO STATUS-ONLY WORK. NO FABRICATION. NO REFETCH. NO STATE.YAML EDITS.**
