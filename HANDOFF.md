# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (re-verified 2026-11-11T02:06:09Z UTC; no competing root TODO/NEXT/plan/handoff docs). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Separate research line; must not be edited to block/replace C1–C13 progress.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T02:06:09Z UTC)

**Initial task (execute immediately, heavy work, no status-only work):** **Execute Campaign #13.** Campaign #12 is COMPLETE (5/5) — every target cache evaluated with timestamped honest artifact + SHA256 + honest outcome, no edge/insufficient_or_blocked across all caches, gates green (pytest 1089 passed/2 skipped, ruff all passed, mypy Success). **No gate-pass/edge signal appeared, so cost-aware OOS is NOT required.** Drive Campaign #13 targets to completion under monitoring: each target cache needs a timestamped `reports/campaign13_*` artifact + SHA256 + full provenance (`real_data_only`, `fabricated_data:false`, `blocked_routes`, rationale), a deterministic `examples/run_campaign13_<cache8>_<UTC>.py`, a deterministic `tests/test_campaign13_<cache8>.py`, and gates green, OR concretely evidenced `insufficient_or_blocked` with `blocked_routes` and rationale. **Campaign #13 cannot be deferred, bypassed, or marked complete without the per-cache deliverables above.**

**STATE (verified 2026-11-11T02:06:09Z UTC, `ps`/`ls`/`stat`/`sha256sum`):** `main`; only durable handoff `HANDOFF.md`. Baseline gates re-verified 2026-11-11T02:06:09Z: `pytest tests/ -q` => **1089 passed, 2 skipped**; `ruff check ...` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success**. Env: `/home/runner/work/_temp/kilo-tmp/c7-venv`, `PYTHONPATH=$PWD`. **C249 (RQA, locked, untouched):** `reports/strategy_edge_registry_20261110T170949Z.json` SHA `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`, `reports/campaign249_execution_summary_20261110T170949Z.json` SHA `e86e2e4b4d3014f9e6c17fddb967380b895bd891eb90305f0227fa9f996c9565`; `edge_claim:NONE`. `research_state/state.yaml` untouched.

**C12 progress (real-data-only, no refetch, thresholds unmodified, `examples/run_campaign12_causal_gates.py`) — COMPLETE 5/5:**
- **DONE (SHA-verified):**
  - `reports/campaign12_causal_per_bar_enriched_gates_595e501a_20261110T230047Z.json` — cache `595e501a...` (3sym BTC/ETH/SOL, **5m**, 26208, 2026-08-01..2026-10-30), pkl SHA `414b9cca7c785b6abf0164c0b2b2c892fbf65400631b594b84e6c17511a8c574`, meta SHA `53ce62467ea2e848d1a63d07be5d512e1b1384a67676bff6b0c5ab886c8f011f`. **Conclusion `insufficient_or_blocked`** (`edge_claim:false`). **Report SHA256 `41fb84c41518e2943f67b207aea6df2ba57a9223e7431a185d3e684d39525e1b`.**
  - `reports/campaign12_causal_per_bar_enriched_gates_4c3bc2f1_20261110T224731Z.json` — cache `4c3bc2f1...` (3sym, **1h**, 944, 2026-10-01..2026-11-09), pkl SHA `dec04f719339480ac1dce151d153d90ff385f0e7bfb95c59425ed45f1edfbb06`, meta SHA `5ad256a381afd6d1b1d39ae50092b8b8a28ebac2aab24a22ad680b5c3c7fd2b1`. **Conclusion `no_edge`** (`rolling_stable_ok` blocks all bars). **Report SHA256 `df4f561bf4a3294093ba40cad938cb6c9b25dce4dda75c70011114a8d7b2c871`.**
  - `reports/campaign12_causal_per_bar_enriched_gates_dcd5764a_20261110T224700Z.json` — cache `dcd5764a...` (3sym, **1h**, 272, 2026-10-29..2026-11-09), pkl SHA `8404aa7f7b7ee67a635f4b1d0df334c4b442cb46c84c774ea869af81dced1fe3`, meta SHA `a78255571a3b4ed56eae31f74577a4977f507b5b3414bbec354a9169d4602c90`. **Conclusion `no_edge`** (`rolling_stable_ok` blocks all bars). **Report SHA256 `25f04e95ce3fccccfeb60542ff7d1c82794bdf247d3e13c9bccd75e5036e0d45`.**
  - `reports/campaign12_causal_per_bar_enriched_gates_90d10b87_20261111T004633Z.json` — cache `90d10b87...` (11sym, **5m**, 26208, 2026-08-01..2026-10-30), pkl SHA `d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f`, meta SHA `e1a71f481cb4ad07881d132aba4ff7b47fc8194c697701035efcf6e492ce4e`. **Conclusion `insufficient_or_blocked`** (`edge_claim:false`). **Report SHA256 `dccdd0ede8d3782a46d1aa5ff318bfdf75fea01d900a76e8a0ac51c548880ad1`.** Process exited cleanly 00:46Z.
  - `reports/campaign12_causal_per_bar_enriched_gates_4fd3e87f_20261111T005009Z.json` — cache `4fd3e87f85cbd8141cbf73591bec7696ea81cbd325b8ba45baf200b56d35ca9d` (11sym, **1h**, 5064, 2026-04-01..2026-10-28), pkl SHA `4d04e74ed1338f5b7955941603d867fe3190e31696a98f170fdc6f42e578f671`, meta SHA `621346a8feebefa6dd1ffdc76995236b663662ff8ced5cd0f26793934897fa32`, 55 pairs, 2 sweeps, thresholds unmodified. **Conclusion `insufficient_or_blocked`** (`edge_claim:false`, `honest:true`, `cache_bars_min:5064`, reason `Mixed blocker pattern / unassessable gates on real data.`). **Report SHA256 `3f973601d24cbfc4a475edb4d05a067d3fde4784735187fece526bdac91d6ac4`, computed_at 2026-11-11T00:50:09Z.** Process pid 22493 exited cleanly at 00:50Z after writing its report — **in-flight bottleneck removed.** No gate-pass/edge. No gate-pass/edge in any completed cache.

**MANDATORY HEAVY ACTION (next session, non-deferrable):**
1. **Execute Campaign #13** (targets below) — drive each to completion under monitoring; restart on death, capture evidence on repeated failure.
2. **Collect reports:** for each target, record report path, `sha256sum`, conclusion (`edge`/`no_edge`/`insufficient_or_blocked`), `edge_claim`, bars/gate summary, and provenance (cache/pkl/meta SHAs). Add them to this handoff.
3. **Complete C13 deliverables:** every target cache must have a timestamped `reports/campaign13_*` artifact with SHA256 recorded and honest outcome (+ `blocked_routes`/rationale where applicable), plus `examples/run_campaign13_<cache8>_<UTC>.py` and `tests/test_campaign13_<cache8>.py` (deterministic; may wrap `examples/run_campaign12_causal_gates.py` and assert report schema/provenance/outcome) and run targeted tests.
4. **Gates:** run `$PT tests/ -q`, `$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `$PY -m mypy backtest/ strategies/ utils/` and fix regressions if any.
5. **If any gate-pass/edge signal appears:** immediately run cost-aware OOS/replay validation on real data (WF splits, fee×slippage grid, B&H benchmark) and record outcome with evidence.
6. **Update this HANDOFF only** with verified UTC, commands, all artifact paths+SHA256, conclusions, gate outcomes, and next unambiguous heavy directive. **Do not** edit `research_state/state.yaml`. No fabrication, no refetch, no threshold weakening.

**Hard bans:** no status-only work; no re-runs of C1–C12 except evidence-backed defect fix; no network refetch; no synthetic data; no threshold weakening; no edits to `research_state/state.yaml`.

## BOTTLENECK REMOVAL (verified 2026-11-11T02:06:09Z UTC)

- **Environment bootstrap bottleneck:** CLEARED — `/home/runner/work/_temp/kilo-tmp/c7-venv` ready; `PYTHONPATH=$PWD`.
- **C12 target audit bottleneck:** CLEARED — all 5 target caches SHA/provenance audited (real-only, `fetch_fabricated_data:false`).
- **C12 evaluation bottleneck (5/5 DONE):** all 5 caches DONE with timestamped artifacts and SHA256-verified reports (595e501a `insufficient_or_blocked` SHA `41fb84c4...`; 4c3bc2f1 `no_edge` SHA `df4f561b...`; dcd5764a `no_edge` SHA `25f04e95...`; 90d10b87 `insufficient_or_blocked` SHA `dccdd0ede8d3782a46d1aa5ff318bfdf75fea01d900a76e8a0ac51c548880ad1`; **4fd3e87f `insufficient_or_blocked` SHA `3f973601d24cbfc4a475edb4d05a067d3fde4784735187fece526bdac91d6ac4`**). Process exited cleanly 00:50Z — no stall. **Bottleneck removed.**
- **Lint bottleneck (regression from C12 deliverables):** CLEARED — 10 E501 line-too-long errors across `tests/test_campaign12_*.py` (×5) and `examples/run_campaign12_*_causal_gates.py` + `run_campaign12_causal_gates.py` (×5) fixed; `ruff check` now **All checks passed**.
- **C249 emission bottleneck:** EXECUTED — registry/summary present; `oos_edge_proven:false`, `edge_claim:NONE`. RQA line (`state.yaml`) SEPARATE and untouched.
- **Parallel lines separated:** HANDOFF C1–C13 (enriched gates) vs `state.yaml` RQA C104–C248 (locked). Do not merge/substitute.

## NEXT FOCUS CAMPAIGN — CAMPAIGN #13 (MANDATORY; HEAVY WORK)

**Objective:** Determine whether any remaining unevaluated real cache yields a causal per-bar enriched-gate edge (any bar passes all enriched gates under **unmodified** thresholds) on any pair, without weakening thresholds and without fabrication — producing honest `edge`/`no_edge`/`insufficient_or_blocked` per cache. Campaign #12 exhausted its 5 targets (all `no_edge`/`insufficient_or_blocked`, no edge signal). Campaign #13 continues on the remaining real multi-symbol caches that powered C1–C11 but never received a C12-style timestamped enriched-gates report.

**Targets (real-only, `fetch_fabricated_data:false`):**
- `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7` (`0bab5d6a`) — **11sym ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP**, **1h**, 5112 bars, 2026-04-01..2026-10-30 — baseline C1–C11 cache (`rolling_stable_ok` blocks 5112/5112 per C11); **unevaluated with C12-style timestamped report** — PRIMARY. pkl SHA `5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b`, meta SHA `d03556baeef34eae18d2122f4a17ec14e30fdd14e0a5616d914c5d0832d2d80d`.
- `385aae3f022b2d7bba4ec502cb8e7399d26cb31b961a016aebf7d165450fd4ba` (`385aae3f`) — **2sym BTC,ETH**, **1h**, 5064 bars, 2026-04-01..2026-10-28, `fetch_real_data_only:true` — unevaluated. pkl SHA `d0885c3c5165fb33d6ef9731ac1cb557a353b8783bb65572031005287fbf4095`, meta SHA `1f60d88faa43a87d5881e28544573fed28d59e54926a3acc915add1a88658f26`.
- `6d2e08d4d7b969d92b61773c7eead387a52ad74b1c3fb0c69552bd6402dd4383` (`6d2e08d4`) — **2sym POL,BTC**, **1h**, 5112 bars, 2026-04-01..2026-10-30 — unevaluated. pkl SHA `977ba2e94a40e4423197ce43377e229cf7d428b0d8a9cb1daf2531383f26fa28`, meta SHA `85ba6c631e3e79b8b9e1c391b7dbaafdb014e044a399c9726dad949c63778504`.

**Mandatory deliverables per cache evaluated (no status-only work):**
- `examples/run_campaign13_<cache8>_<UTC>.py` — causal per-bar gate script (real cache only, no network refetch, no synthetic)
- `reports/campaign13_<cache8>_<UTC>.json` — timestamped artifact + SHA256 + full provenance (`real_data_only`, `fabricated_data: false`, `blocked_routes`, rationale)
- `tests/test_campaign13_<cache8>.py` — deterministic test asserting schema/provenance and recording the outcome
- SHA256 of all new artifacts recorded in this handoff

**Completion gate (non-negotiable):** Session NOT complete until every Campaign #13 target cache is either evaluated with timestamped campaign + tests + gates green, OR concretely evidenced as `insufficient_or_blocked` with `blocked_routes` and rationale. Then update **only** `HANDOFF.md` with UTC timestamp, commands run, artifact paths + SHA256, gate outcomes, concrete findings (`edge`/`no_edge`/`insufficient_or_blocked`), and the next unambiguous heavy directive. No deferral.

**Future-agent lock:** Do not substitute status-only work, threshold weakening, fabrication, or re-runs of C1–C12 for Campaign #13. Campaign #13 cannot be deferred, bypassed, or marked complete without the per-cache deliverables above and gates green on every target cache (or evidenced `insufficient_or_blocked`).

### READY STATE (verified context)

- **Env:** `/home/runner/work/_temp/kilo-tmp/c7-venv` (python/pytest/ruff/mypy) — **bootstrapped and green**. Use `PYTHONPATH=$PWD`. Re-verified 2026-11-11T02:06:09Z UTC.
- **Cached real spot (do not refetch):** `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` + `.meta.json` (11 sym ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP; 1h 2026-04-01..2026-10-30 UTC; 5112 bars). Volume cache present. Also `385aae3f...` (2sym, 5064 bars) and `6d2e08d4...` (2sym, 5112 bars).
- **No exchange/testnet creds and no public historical L2/intrabar replay.** Honest `blocked_or_insufficient_data`/partial artifacts with `blocked_routes` and rationale only — never fabricate.

#### BOOTSTRAP

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest
# if env missing: python -m venv /home/runner/work/_temp/kilo-tmp/c7-venv && $PY -m pip install -e ".[dev]" pydantic aiohttp pytest-asyncio
```

#### SESSION COMPLETION CONTRACT (NON-NEGOTIABLE)

- **NOT COMPLETE** until you produce verified real-data artifacts/tests/code with gates green, **OR** every remaining blocker is concretely evidenced and unblocked as far as possible without fabrication/credentials/threshold-weakening.
- At material checkpoint/completion, update **only** `HANDOFF.md` with: verified UTC timestamp, commands run, created artifact paths (+ SHA256 if new), exact gate outcomes, concrete findings (`edge`/`no_edge`/`insufficient_or_blocked`), and the next unambiguous heavy directive. No deferral.

## 1) VERIFIED BASELINE SNAPSHOT (2026-11-10T21:42:29Z; baseline re-verified 2026-11-10T22:43:28Z; C12 gates re-verified 2026-11-11T00:51:59Z; all re-verified 2026-11-11T02:06:09Z)

- **Repo:** `main`, single durable handoff `HANDOFF.md`.
- **Campaigns #1–#11:** COMPLETE (honest/evidence-first). C11 confirms structural blocker on cached-real enriched-gate line.
- **Campaign #12:** COMPLETE (5/5, all `no_edge`/`insufficient_or_blocked`, no edge signal).
- **Gates (re-verified this session):** `pytest tests/ -q` => **1089 passed, 2 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success**.
- **This session (bottleneck removal):** env bootstrap re-verified green; C12 audit/eval/lint all cleared; C249 executed (`oos_edge_proven:false`, `edge_claim:NONE`).
- **RQA locked (separate, untouched):** `research_state/state.yaml` C104–C248, `next_campaign: C249`, `oos_edge_proven: false`. NOT edited.

## 2) CAMPAIGN OUTCOMES (REFERENCE)

| Campaign | State | Notes / key artifacts |
|---|---|---|
| #1 Regime-adaptive signal generation | COMPLETE | `reports/regime_adaptive_sweep.json` |
| #2 Funding/basis-carry + LOB/intrabar feasibility | COMPLETE (honest) | `reports/funding_carry_real.json`; `reports/execution_lob_real.json` partial/blocked where required |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json`, `strategies/ml_gated_pairs.py`, `utils/ml_gating.py` |
| #4 HF/multi-timeframe cointegration | COMPLETE (honest) | `reports/pairs_mtf_5m_1h.json`, `utils/mtf_pairs.py` |
| #5 Production bridge (paper OMS + risk) | COMPLETE (bounded/paper) | `reports/paper_trading_session.json`, `reports/risk_dashboard.json` |
| #6 Live/testnet execution validation | COMPLETE (honest/paper/bounded) | `reports/live_testnet_readiness.json`, `reports/testnet_order_lifecycle.json`, `reports/paper_microstructure_validation.json` |
| #7 Operator deployment hardening | COMPLETE | config/observability/playbooks/reconciliation + artifacts; gates green |
| #8 Stat-arb edge hardening & honest real-data extension | COMPLETE (`no_edge`) | `examples/run_campaign8_edge_robustness.py`, `reports/campaign8_edge_robustness_20261110T115802Z.json`, `tests/test_campaign8_edge_robustness.py` |
| #9 Enriched-gate causal/per-bar edge discovery & robustness | COMPLETE (`no_edge`) | `examples/run_campaign9_causal_gate_edge_search.py`, `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json` (SHA256 `7e48865eab5b478a4c9d810901ec9edd6a91352ae71e29cbb647955842ad43b0`), `tests/test_campaign9_causal_gate_edge_search.py` |
| #10 Wider-universe causal per-bar gate validation | COMPLETE (`insufficient_or_blocked`) | `examples/run_campaign10_wider_universe_causal_gates.py`, `reports/campaign10_wider_universe_causal_gates_20261110T160625Z.json` (SHA256 `8c3c5d5785c0d7bd33c805f939528771809494dba400e6f990d269dd3369b895`), `tests/test_campaign10_wider_universe_causal_gates.py` |
| **#11 Rolling-stability blocker diagnosis & gate-pass feasibility** | **COMPLETE (`no_edge`)** | `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_20261110T165848Z.json` (SHA256 `899c18c5e0854347956c6b6c3c3e2aa1ba90349dab2035f37ba70f9dbd5ae9fb`), `tests/test_campaign11_rolling_stability_blocker.py` |
| **#12 Causal per-bar enriched gates on 5 target caches** | **COMPLETE (5/5, all `no_edge`/`insufficient_or_blocked`)** | 5 timestamped `reports/campaign12_*` artifacts + SHA256; per-cache `examples/run_campaign12_*_causal_gates.py` + `tests/test_campaign12_*.py`; no edge signal |

## 3) REPRODUCTION / GATE COMMANDS

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
export PYTHONPATH=$PWD
PY=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/python
PT=/home/runner/work/_temp/kilo-tmp/c7-venv/bin/pytest

$PT tests/ -q
$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
$PY -m mypy backtest/ strategies/ utils/
```

## 4) KEY FILES

- **C12:** `examples/run_campaign12_causal_gates.py` + per-cache `examples/run_campaign12_<cache8>_causal_gates.py`, `reports/campaign12_*.json` (SHA-verified), `tests/test_campaign12_<cache8>.py`
- **C11:** `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_20261110T165848Z.json` (SHA256 `899c18c5e0854347956c6b6c3c3e2aa1ba90349dab2035f37ba70f9dbd5ae9fb`), `tests/test_campaign11_rolling_stability_blocker.py`
- **Strategy/gates:** `strategies/pairs_trading.py`, `utils/cointegration.py`
- **Portfolio/risk:** `examples/run_portfolio_real.py:PortfolioRiskController.apply`, `backtest/engine.py:run_portfolio`

---

**END OF DURABLE HANDOFF — 2026-11-11T02:06:09Z UTC. CAMPAIGNS #1–#11 COMPLETE (`no_edge` on cached-real enriched-gate line). CAMPAIGN #12 COMPLETE (5/5: 595e501a `insufficient_or_blocked` SHA `41fb84c41518e2943f67b207aea6df2ba57a9223e7431a185d3e684d39525e1b`; 4c3bc2f1 `no_edge` SHA `df4f561bf4a3294093ba40cad938cb6c9b25dce4dda75c70011114a8d7b2c871`; dcd5764a `no_edge` SHA `25f04e95ce3fccccfeb60542ff7d1c82794bdf247d3e13c9bccd75e5036e0d45`; 90d10b87 `insufficient_or_blocked` SHA `dccdd0ede8d3782a46d1aa5ff318bfdf75fea01d900a76e8a0ac51c548880ad1`; **4fd3e87f `insufficient_or_blocked` SHA `3f973601d24cbfc4a475edb4d05a067d3fde4784735187fece526bdac91d6ac4`, report `reports/campaign12_causal_per_bar_enriched_gates_4fd3e87f_20261111T005009Z.json`, process exited cleanly 00:50Z**). C249 EXECUTED (`oos_edge_proven:false`, `edge_claim:NONE`, RQA locked/untouched). Gates green (1089 passed/2 skipped, ruff all passed, mypy Success). NEXT SESSION: execute Campaign #13 targets (`0bab5d6a`, `385aae3f`, `6d2e08d4`) — timestamped artifacts + SHA256 + tests + gates green per cache, or evidenced `insufficient_or_blocked`. NO STATUS-ONLY WORK. NO FABRICATION. NO REFETCH.**
