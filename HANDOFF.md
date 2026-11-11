# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Single durable handoff at repo root: `HANDOFF.md` only** (re-verified 2026-11-11T01:21:33Z UTC; no competing root TODO/NEXT/plan/handoff docs). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA (C104–C248 locked, `next_campaign: C249`, `oos_edge_proven: false`, SHA/provenance locked). Separate research line; must not be edited to block/replace C1–C12 progress.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T01:21:33Z UTC)

**Initial task (execute immediately, heavy work, no status-only work):** **Close Campaign #12** by driving the 2 remaining per-cache causal enriched-gate evaluations to completion on real caches under **unmodified gate thresholds** (no fabrication, no network refetch), then integrate all 5 cache outcomes into C12 deliverables with tests+gates green. C1–C11 exhausted the 1h `0bab5d6a...fcf7` line (`rolling_stable_ok` blocks 5112/5112). **3/5 target caches DONE with timestamped honest artifacts+SHA256 recorded; 2/5 (90d10b, 4fd3e87f) VERIFIED RUNNING at 01:21Z and must be driven to completion and their reports SHA256-recorded.** Work is not complete until every target cache has a timestamped artifact and recorded honest outcome, required C12 deliverables/tests exist, and gates are green as feasible, OR concretely evidenced `insufficient_or_blocked`.

**STATE (verified 2026-11-11T01:21:33Z UTC, `ps`/`ls`/`stat`/`sha256sum`):** `main`; only durable handoff `HANDOFF.md`. Baseline gates last verified 2026-11-10T22:43:28Z: `pytest tests/ -q` => **1080 passed, 1 skipped**; `ruff check ...` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success** (not re-run this session). Env: `/home/runner/work/_temp/kilo-tmp/c7-venv`, `PYTHONPATH=$PWD`. **C249 (RQA, locked, untouched):** `reports/strategy_edge_registry_20261110T170949Z.json` SHA `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`, `reports/campaign249_execution_summary_20261110T170949Z.json` SHA `e86e2e4b4d3014f9e6c17fddb967380b895bd891eb90305f0227fa9f996c9565`; `edge_claim:NONE`. `research_state/state.yaml` untouched.

**C12 progress (real-data-only, no refetch, thresholds unmodified, `examples/run_campaign12_causal_gates.py`):**
- **DONE (SHA-verified):**
  - `reports/campaign12_causal_per_bar_enriched_gates_595e501a_20261110T230047Z.json` — cache `595e501a...` (3sym BTC/ETH/SOL, **5m**, 26208, 2026-08-01..2026-10-30), pkl SHA `414b9cca7c785b6abf0164c0b2b2c892fbf65400631b594b84e6c17511a8c574`, meta SHA `53ce62467ea2e848d1a63d07be5d512e1b1384a67676bff6b0c5ab886c8f011f`. **Conclusion `insufficient_or_blocked`** (`edge_claim:false`). **Report SHA256 `41fb84c41518e2943f67b207aea6df2ba57a9223e7431a185d3e684d39525e1b`.**
  - `reports/campaign12_causal_per_bar_enriched_gates_4c3bc2f1_20261110T224731Z.json` — cache `4c3bc2f1...` (3sym, **1h**, 944, 2026-10-01..2026-11-09), pkl SHA `dec04f719339480ac1dce151d153d90ff385f0e7bfb95c59425ed45f5edfbb06`, meta SHA `5ad256a381afd6d1b1d39ae50092b8b8a28ebac2aab24a22ad680b5c3c7fd2b1`. **Conclusion `no_edge`** (`rolling_stable_ok` blocks all bars). **Report SHA256 `df4f561bf4a3294093ba40cad938cb6c9b25dce4dda75c70011114a8d7b2c871`.**
  - `reports/campaign12_causal_per_bar_enriched_gates_dcd5764a_20261110T224700Z.json` — cache `dcd5764a...` (3sym, **1h**, 272, 2026-10-29..2026-11-09), pkl SHA `8404aa7f7b7ee67a635f4b1d0df334c4b442cb46c84c774ea869af81dced1fe3`, meta SHA `a78255571a3b4ed56eae31f74577a4977f507b5b3414bbec354a9169d4602c90`. **Conclusion `no_edge`** (`rolling_stable_ok` blocks all bars). **Report SHA256 `25f04e95ce3fccccfeb60542ff7d1c82794bdf247d3e13c9bccd75e5036e0d45`.** No gate-pass/edge in any completed cache.
- **IN-FLIGHT (VERIFIED RUNNING 2026-11-11T01:21:33Z; must complete):**
  - `90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263` (11sym, **5m**, 26208, 2026-08-01..2026-10-30, real-only; pkl SHA `d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f`, meta SHA `e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e`). **pid 14895, ~99.8% CPU, etime ~01:31:31, ~1.1% MEM** (`--cache 90d10b...`). Log `/tmp/c12_90d10b.log` **11,568,804 bytes, mtime 2026-11-11T00:20:42Z — process alive at ~99% CPU, log size unchanged since 00:20Z but CPU high — monitor liveness (pid/CPU/size) each checkpoint; do not interrupt without concrete stall/exit evidence.** Expected output: `reports/campaign12_causal_per_bar_enriched_gates_90d10b87_<STAMP>.json`.
  - `4fd3e87f85cbd8141cbf73591bec7696ea81cbd325b8ba45baf200b56d35ca9d` (11sym, **1h**, 5064, 2026-04-01..2026-10-28, real-only; pkl SHA `4d04e74ed1338f5b7955941603d867fe3190e31696a98f170fdc6f42e578f671`, meta SHA `621346a8feebefa6dd1ffdc76995236b663662ff8ced5cd0f26793934897fa32`). Prior runs crashed/stopped mid-run (~6/55 pairs) with no report (logs `/tmp/c12_4fd3e87f.log`, `/tmp/c12_4fd3e87f_restart.log`). **Restarted 2026-11-11T00:31:59Z (pid 22493, ~99.9% CPU, etime ~07:24 at 01:21Z)**: `nohup $PY examples/run_campaign12_causal_gates.py --cache 4fd3e87f... > /tmp/c12_4fd3e87f_restart2.log 2>&1 &`. Log `/tmp/c12_4fd3e87f_restart2.log` **growing (63,089,534 bytes at 01:21Z check, mtime 2026-11-11T01:19:27Z advancing)**. **Keep running under monitoring to completion**; expected output `reports/campaign12_causal_per_bar_enriched_gates_4fd3e87f_<STAMP>.json`. If it exits/crashes, capture tail+exit evidence, diagnose concrete defect and fix if evidenced, else record honest `insufficient_or_blocked` with `blocked_routes`/rationale — never fabricate or skip.

**MANDATORY HEAVY ACTION (next session, non-deferrable):**
1. **Monitor bottlenecks:** confirm both running: `ps -p 14895,22493 -o pid,etime,pcpu,cmd` and `stat -c '%n %Y %s' /tmp/c12_90d10b.log /tmp/c12_4fd3e87f_restart2.log`. Keep both to completion (monitor/background). 90d10b log has been size-stalled since 23:40Z despite ~99% CPU — watch liveness (pid/CPU/size) and capture evidence if it exits or concretely stalls; do not interrupt without evidence. Restart 4fd3e87f if it dies; capture evidence on repeated failure.
2. **Collect reports:** when complete, record for each: report path, `sha256sum`, conclusion (`edge`/`no_edge`/`insufficient_or_blocked`), `edge_claim`, bars/gate summary, and provenance (cache/pkl/meta SHAs). Add them to this handoff.
3. **Complete C12 deliverables:** all 5 target caches must have timestamped `reports/campaign12_*` artifacts with SHA256 recorded and honest outcomes (+ `blocked_routes`/rationale where applicable). If contract requires per-cache `examples/run_campaign12_<cache8>_*.py` / `tests/test_campaign12_<cache8>.py`, add deterministic ones (may wrap `examples/run_campaign12_causal_gates.py` and assert report schema/provenance/outcome) and run targeted tests.
4. **Gates:** run `$PT tests/ -q`, `$PY -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/`, `$PY -m mypy backtest/ strategies/ utils/` and fix regressions if any.
5. **If any gate-pass/edge signal appears:** immediately run cost-aware OOS/replay validation on real data (WF splits, fee×slippage grid, B&H benchmark) and record outcome with evidence.
6. **Update this HANDOFF only** with verified UTC, commands, all artifact paths+SHA256, conclusions, gate outcomes, and next unambiguous heavy directive. **Do not** edit `research_state/state.yaml`. No fabrication, no refetch, no threshold weakening.

**Hard bans:** no status-only work; no re-runs of C1–C11 except evidence-backed defect fix; no network refetch; no synthetic data; no threshold weakening; no edits to `research_state/state.yaml`.

## BOTTLENECK REMOVAL (verified 2026-11-11T01:21:33Z UTC)

- **Environment bootstrap bottleneck:** CLEARED — `/home/runner/work/_temp/kilo-tmp/c7-venv` ready; `PYTHONPATH=$PWD`.
- **C12 target audit bottleneck:** CLEARED — all 5 target caches SHA/provenance audited (real-only, `fetch_fabricated_data:false`).
- **C12 evaluation bottleneck (actively being cleared, 3/5 done):** 3/5 caches DONE with timestamped artifacts and SHA256-verified reports (595e501a `insufficient_or_blocked` SHA `41fb84c4...`, 4c3bc2f1 `no_edge` SHA `df4f561b...`, dcd5764a `no_edge` SHA `25f04e95...`). **90d10b RUNNING** (pid 14895, ~99.8% CPU, etime ~01:31:31 at 01:21Z, `/tmp/c12_90d10b.log` 11,568,804B mtime 2026-11-11T00:20:42Z — alive at high CPU, log size unchanged since 00:20Z; **monitor liveness (pid/CPU/size) each checkpoint, do not interrupt without concrete stall/exit evidence.**) **4fd3e87f RUNNING** (pid 22493, ~99.9% CPU, etime ~07:24 at 01:21Z, `/tmp/c12_4fd3e87f_restart2.log` growing 63,089,534B, mtime 2026-11-11T01:19:27Z advancing) — restarted 2026-11-11T00:31:59Z after prior crashes; keep monitored to completion. No gate-pass/edge observed in completed caches.
- **C249 emission bottleneck:** EXECUTED — registry/summary present; `oos_edge_proven:false`, `edge_claim:NONE`. RQA line (`state.yaml`) SEPARATE and untouched.
- **Parallel lines separated:** HANDOFF C1–C12 (enriched gates) vs `state.yaml` RQA C104–C248 (locked). Do not merge/substitute.

## NEXT FOCUS CAMPAIGN — CAMPAIGN #12 (MANDATORY; HEAVY WORK)

**Objective:** Determine whether any unevaluated real cache in `data/cache/` yields a causal per-bar enriched-gate edge (any bar passes all enriched gates under **unmodified** thresholds) on any pair across trailing configs, without weakening thresholds and without fabrication — producing honest `edge`/`no_edge`/`insufficient_or_blocked` per cache.

**Targets (5 caches, all real-only/fetch_fabricated_data:false):** `90d10b...` (11sym,5m,26208,Aug–Oct) [IN-FLIGHT pid 14895, VERIFIED RUNNING 01:21Z, etime ~01:31:31, log 11,568,804B mtime 00:20:42Z — alive at 99.8% CPU, monitor liveness], `595e501...` (3sym,5m,26208,Aug–Oct) [DONE], `4fd3e87...` (11sym,1h,5064,Apr–Oct28) [IN-FLIGHT pid 22493, restarted 2026-11-11T00:31:59Z, VERIFIED RUNNING 01:21Z, etime ~07:24, log 63,089,534B growing, mtime 01:19:27Z advancing], `4c3bc2f...` (3sym,1h,944,Oct1–Nov9) [DONE], `dcd5764...` (3sym,1h,272,Oct29–Nov9) [DONE, `no_edge`].

**Mandatory deliverables per cache evaluated (no status-only work):**
- `examples/run_campaign12_<cache8>_<UTC>.py` — causal per-bar gate script (real cache only, no network refetch, no synthetic)
- `reports/campaign12_<cache8>_<UTC>.json` — timestamped artifact + SHA256 + full provenance (`real_data_only`, `fabricated_data: false`, `blocked_routes`, rationale)
- `tests/test_campaign12_<cache8>.py` — deterministic test asserting schema/provenance and recording the outcome
- SHA256 of all new artifacts recorded in this handoff

**Completion gate (non-negotiable):** Session NOT complete until every target cache is either evaluated with timestamped campaign + tests + gates green, OR concretely evidenced as `insufficient_or_blocked` with `blocked_routes` and rationale. Then update **only** `HANDOFF.md` with UTC timestamp, commands run, artifact paths + SHA256, gate outcomes, findings, and the next unambiguous heavy directive. No deferral.

**Future-agent lock:** Do not substitute status-only work, threshold weakening, fabrication, or re-runs of C1–C11 for Campaign #12. Campaign #12 cannot be deferred, bypassed, or marked complete without the per-cache deliverables above and gates green on every target cache (or evidenced `insufficient_or_blocked`).

### READY STATE (verified context)

- **Env:** `/home/runner/work/_temp/kilo-tmp/c7-venv` (python/pytest/ruff/mypy) — **bootstrapped and green**. Use `PYTHONPATH=$PWD`. Re-verified 2026-11-10T22:43:28Z UTC.
- **Cached real spot (do not refetch):** `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` + `.meta.json` (SHA256 `56075733...f5f8c9b` / `d03556ba...d2d80d`; ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP; 1h 2026-04-01..2026-10-30 UTC; 5112 bars). Volume cache present.
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


## 1) VERIFIED BASELINE SNAPSHOT (2026-11-10T21:42:29Z; baseline re-verified 2026-11-10T22:43:28Z)

- **Repo:** `main`, single durable handoff `HANDOFF.md`.
- **Campaigns #1–#11:** COMPLETE (honest/evidence-first). C11 confirms structural blocker on cached-real enriched-gate line.
- **Gates (re-verified this session):** `pytest tests/ -q` => **1080 passed, 1 skipped**; `ruff check backtest/ data/ strategies/ utils/ tests/ examples/` => **All checks passed**; `mypy backtest/ strategies/ utils/` => **Success**.
- **This session (bottleneck removal):** emitted C249 registry `reports/strategy_edge_registry_20261110T170949Z.json` (SHA `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`) and summary `reports/campaign249_execution_summary_20261110T170949Z.json` (SHA `e86e2e4b4d3014f9e6c17fddb967380b895bd891eb90305f0227fa9f996c9565`); C249 `oos_edge_proven: False`, `edge_claim: NONE`.
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

## 3) CAMPAIGN #11 — EXECUTION RECORD (COMPLETE)

**Objective:** On cached real data only, determine whether `rolling_stable_ok` trailing-window insufficiency is the sole structural blocker (no bar passes all enriched gates on any wider-universe pair under unmodified thresholds) or whether any pair/slice ever achieves a causal per-bar gate pass, across trailing sample lengths/check intervals, **without weakening gate thresholds**.

**Constraints honored:** No network refetch, no synthetic/fabricated data/labels/metrics/fills/IV/volume. Gate thresholds unmodified. `research_state/state.yaml` RQA line untouched. Campaigns #1–#10 not redone.

**Deliverables:** `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_20261110T165848Z.json` (SHA256 `899c18c5e0854347956c6b6c3c3e2aa1ba90349dab2035f37ba70f9dbd5ae9fb`), `tests/test_campaign11_rolling_stability_blocker.py`.

**Findings (honest, reproducible):** conclusion `no_edge` (edge_claim false). No bar passes all enriched gates on any wider-universe pair under swept configs with unmodified thresholds. `rolling_stable_ok` blocks **5112/5112 bars** across pairs/sweeps (structural blocker confirmed). Cached-aggregate and causal-per-bar paths agree (fail-closed). No positive OOS/replay edge; zero gate-pass slices => cost-aware evaluation not possible. Cached-real/gate research line exhausted under current gate schema/thresholds without fabricating data/trades/edge.

## 4) REPRODUCTION / GATE COMMANDS

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

## 5) KEY FILES

- **C11:** `examples/run_campaign11_rolling_stability_blocker.py`, `reports/campaign11_rolling_stability_blocker_20261110T165848Z.json` (SHA256 `899c18c5e0854347956c6b6c3c3e2aa1ba90349dab2035f37ba70f9dbd5ae9fb`), `tests/test_campaign11_rolling_stability_blocker.py`
- **C10:** `examples/run_campaign10_wider_universe_causal_gates.py`, `reports/campaign10_wider_universe_causal_gates_20261110T160625Z.json`, `tests/test_campaign10_wider_universe_causal_gates.py`
- **C9:** `examples/run_campaign9_causal_gate_edge_search.py`, `reports/campaign9_causal_gate_edge_search_20261110T125028Z.json`, `tests/test_campaign9_causal_gate_edge_search.py`
- **C8:** `examples/run_campaign8_edge_robustness.py`, `reports/campaign8_edge_robustness_20261110T115802Z.json`, `tests/test_campaign8_edge_robustness.py`
- **Strategy/gates:** `strategies/pairs_trading.py`, `utils/cointegration.py`
- **Portfolio/risk:** `examples/run_portfolio_real.py:PortfolioRiskController.apply`, `backtest/engine.py:run_portfolio`

---

**END OF DURABLE HANDOFF — 2026-11-11T01:21:33Z UTC. CAMPAIGNS #1–#11 COMPLETE (`no_edge` on cached-real enriched-gate line). C249 EXECUTED (`oos_edge_proven:false`, `edge_claim:NONE`, RQA locked/untouched). C12: 3/5 DONE SHA-verified (595e501a `insufficient_or_blocked` SHA `41fb84c41518e2943f67b207aea6df2ba57a9223e7431a185d3e684d39525e1b`, 4c3bc2f1 `no_edge` SHA `df4f561bf4a3294093ba40cad938cb6c9b25dce4dda75c70011114a8d7b2c871`, dcd5764a `no_edge` SHA `25f04e95ce3fccccfeb60542ff7d1c82794bdf247d3e13c9bccd75e5036e0d45`). 2/5 IN-FLIGHT VERIFIED RUNNING 01:21Z: 90d10b pid 14895 (~99.8% CPU, etime ~01:31:31, `/tmp/c12_90d10b.log` 11,568,804B mtime 00:20:42Z — alive, monitor liveness, do not interrupt without evidence); 4fd3e87f pid 22493 (~99.9% CPU, etime ~07:24, `/tmp/c12_4fd3e87f_restart2.log` growing 63,089,534B mtime 01:19:27Z). BOTH must run to completion. NEXT SESSION: monitor/ensure both finish, collect report paths+SHA256s+conclusions+provenance, add per-cache C12 deliverables/tests if required, run gates (`pytest/ruff/mypy`), cost-aware OOS if any edge, update HANDOFF only with next heavy directive. NO STATUS-ONLY WORK. NO FABRICATION. NO REFETCH.**
