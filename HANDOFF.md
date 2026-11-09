# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (Next Agentic Session)

> **SINGLE DURABLE HANDOFF. NEXT AGENT: START HERE. HEAVY WORK ONLY. NO EXCEPTIONS.**
> Repo priority (name-inferred): `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. **Campaign #1 COMPLETE. Campaign #2 COMPLETE. Campaign #3 COMPLETE** (required artifacts present/verified; real data+provenance; honest). Competing handoff/TODO docs at repo root: **NONE** (only `HANDOFF.md`). **No fabrication.** `research_state/state.yaml` (C249 RQA/volume line, `oos_edge_proven: false`, locked C104-C248) is a **separate/locked line — DO NOT work it** unless explicitly requested by the user. **Forbidden:** docs-only edits as the session outcome, cleanup/refactors without requested value, status-only bookkeeping, alternate handoffs/TODOs/plans, rerunning C104-C248, rerunning completed Campaigns #1-#3 without a concrete defect, or fabricating data/fills/order books/labels/metrics.

## 0) Timestamped initial task message (single durable directive for next session)

**[2026-11-09T19:09:21Z | VERIFIED NOW | `HANDOFF.md` is the ONLY root handoff/TODO. C1-C3 artifacts present+honest: `reports/funding_carry_real.json` (ok,true,false), `reports/execution_lob_real.json` (partial,true,false; historical L2 replay infeasible from public routes), `reports/regime_adaptive_sweep.json` (present), `reports/ml_gated_pairs.json` (ok,true,false). `reports/pairs_mtf_5m_1h.json` MISSING. No `pairs_mtf*` implementation outside reports. Deps import OK (numpy/pandas/scipy/statsmodels/sklearn). 5m real-data fetch VERIFIED WORKING now via `DataLoader.load_binance_data(['BTC','ETH'],'2026-10-01','2026-10-03',interval='5m')` → 864 bars, no blocked routes. 11-symbol 1h cache exists (2026-04-01→2026-10-30); no 5m/15m cache files — fetch real 5m/15m with provenance/cache. Last recorded full gates (pre-change baseline): `940 passed, 1 skipped, 0 failures`; ruff/mypy clean — RERUN after any source change. EXPLICIT DIRECTIONS ABSENT => EXECUTE CAMPAIGN #4 IMMEDIATELY.]**

**NEXT AGENTIC SESSION: EXECUTE CAMPAIGN #4 NOW (HEAVY WORK, NON-OPTIONAL).**
- **First substantive actions MUST produce code + tests + real-data validation + artifact emission** for Campaign #4 (or a user-explicit override). Do **NOT** stop after reading, summarizing, status-checking, planning, or refreshing docs. Planning/summaries/exploratory reading without implementation = **failure**.
- **Do NOT redo Campaigns #1-#3** unless you find a concrete defect and fix it with evidence. Do NOT touch `research_state/state.yaml` / C249 / locked C104-C248.
- **No fabrication. Ever.** No synthetic/fabricated candles, IV, volume, fills, order books, labels, or metrics presented as real evidence. If a real route is blocked/insufficient, record exact `blocked_routes`/limitations, keep `real_data_only`/`fabricated_data` honest, and still ship the **heaviest valid implementation/tests/artifact possible** under fail-closed rules.
- **Bottlenecks removed (2026-11-09T19:09:21Z): NONE blocking start.** Competing handoffs/TODOs: none. Deps OK. 5m fetch verified. `data.loader.DataLoader` supports 5m/15m; `data.cache.load_cached` + `fetch_with_provenance` available for provenance. Known constraint (not an excuse): historical L2/intrabar replay not publicly available — record honestly; do not fabricate; use feasible 5m realism (slippage/impact/volume/LOB-snapshot-aware proxies where justified) with explicit limitations.

**Campaign #4 target (execute now): HF/multi-timeframe cointegration (HIGH)**
1. **Strategy/logic (causal, no lookahead):** Multi-timeframe pairs — 1h cointegration/hedge/spread context + 5m (and/or 15m where useful/feasible) entry/exit signals on **real Binance spot candles**. Universe: cached 11-symbol 1h frame (ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP) where 5m/15m real data is available.
   - Causal alignment only: 1h state at bar `t` may inform decisions only for 5m bars strictly after 1h bar `t` closes (or equivalent documented causal rule). No future leakage.
   - Enforce fail-closed on missing data, insufficient overlap, NaNs, or gate failures.
2. **Execution realism (honest):** 5m costs/slippage/impact/turnover realism; LOB-aware where feasible from available public snapshot evidence/proxies. Historical L2/intrabar replay not available — **do not fabricate fills/order books**; document limitations in artifact.
3. **Validation:** Purged walk-forward / leakage controls consistent with repo practice; evaluate across 1h/4h/1d-equivalent horizons where data permits (honest if constrained). Cost sensitivity required.
4. **Required artifact:** `reports/pairs_mtf_5m_1h.json` with schema keys at minimum: `real_data_only`, `fabricated_data`, `generated_at_utc` (UTC ISO), `campaign` (`Campaign #4 - HF/multi-timeframe cointegration`), `status` (`ok`/`partial`/`blocked` — honest), `blocked_routes`, `data_sources` (providers, symbols, intervals, windows, cache/fetch provenance, checksums/hashes where feasible), `method` (causal alignment, gates, WF/leakage controls, cost model, limitations), `results` (per-pair/horizon metrics, exposures, OOS vs B&H if computed honestly), `limitations`, `notes`. **Never set `real_data_only:true` if any fabricated evidence is used.**
5. **Minimum viable heavy deliverables (all required):**
   - Implementation: e.g. `strategies/pairs_mtf.py` and/or `utils/mtf_pairs.py` (causal multi-TF alignment + signals) and runner `examples/run_pairs_mtf_5m_1h_real.py` (or equivalent) that fetches/loads real data with provenance and emits `reports/pairs_mtf_5m_1h.json`.
   - Tests: `tests/test_pairs_mtf.py` (and any focused tests) covering causal alignment/no-lookahead, fail-closed behavior, signal/gating logic; synthetic fixtures in tests only if explicitly flagged and never written as real-data artifacts.
   - Real-data run: produce the artifact from real Binance public spot data (cached/fetched) with honest provenance.
6. **Quality gates before declaring C4 complete (rerun after changes):**
   ```bash
   cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
   PYTHONPATH=. python -m pytest tests/ -q
   python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
   python -m mypy backtest/ strategies/ utils/
   ```
   Fix regressions caused by your changes. Record outcomes truthfully.
7. **Handoff update:** Update **only** `HANDOFF.md` at material checkpoint/completion with verified truth (timestamp, artifact path/status, gate results, any honest blocked routes/limitations, next focus). Keep this file the **single durable handoff**.

**This directive remains active until** `reports/pairs_mtf_5m_1h.json` exists with honest schema/provenance **and** Campaign #4 implementation/tests/gates are materially complete. Then advance to the follow-on.

## 1) Verified state (2026-11-09T19:09:21Z)

- **Deps**: numpy/pandas/scipy/statsmodels/scikit-learn/hmmlearn/pytest/ruff/mypy importable.
- **Gates (last fresh full baseline)**: `940 passed, 1 skipped, 0 failures`; `ruff` all passed; `mypy` success (34 source files). **Rerun after any source change.**
- **Real data**: Binance public host chain works; 451 routes handled/recorded where encountered. **5m fetch verified working (2026-11-09).** Never fabricate.
- **Artifacts (C1-C3):** `reports/funding_carry_real.json` ok/true/false; `reports/execution_lob_real.json` partial/true/false (historical L2 replay infeasible, honest); `reports/regime_adaptive_sweep.json` present; `reports/ml_gated_pairs.json` ok/true/false.
- **Cache:** 11-symbol 1h real frame `2026-04-01→2026-10-30` in `data/cache/` (`0bab5d6a...pkl`, 5112×11) plus per-symbol 1h series and volume files. **No 5m/15m cache files** — C4 must fetch/cache real 5m/15m with provenance or record `blocked_routes`.
- **Bottlenecks:** **NONE** blocking Campaign #4 start.

## 1.1) Parallel-track caution
`research_state/state.yaml` (updated `20261109T032725Z`, `next_campaign: C249`, `oos_edge_proven: false`, C104-C248 locked) is a separate locked line. **Do not** work C249/registry/status instead of Campaign #4 unless explicitly requested.

## 2) Campaign outcomes summary

| Campaign | State | Key artifacts / notes |
|---|---|---|
| #1 Regime-Adaptive Signal Generation | COMPLETE | `reports/regime_adaptive_sweep.json`, `examples/run_regime_detection_real.py`. Honest (held-out proxy 0.473 < 0.65; best OOS mean return 0.0). |
| #2 Funding/Basis-Carry + LOB/Intrabar Feasibility | COMPLETE (honest) | `reports/funding_carry_real.json` (ok, 2296 real rows). `reports/execution_lob_real.json` (partial; snapshots ok; historical L2 replay infeasible; no fabricated fills/order books). |
| #3 ML-augmented signal filtering | COMPLETE | `reports/ml_gated_pairs.json` (ok, real-data-only, 544 labeled rows, cv_ok). `strategies/ml_gated_pairs.py`, `utils/ml_gating.py`, tests, runner. |
| #4 HF/multi-timeframe cointegration | **NOT STARTED / REQUIRED NEXT** | `reports/pairs_mtf_5m_1h.json` missing. Execute §0 immediately. |

## 3) Next focus campaign — HF/multi-timeframe cointegration (HIGH)
Execute immediately. See §0. Required artifact: `reports/pairs_mtf_5m_1h.json` (or honest `blocked`/`partial` with full schema/provenance). Real data only; causal alignment/no lookahead; purged WF/leakage controls; fail-closed; cost realism; honest metrics regardless of outcome.

## 4) Follow-on campaign (only after Campaign #4 complete + artifact exists)
**Production bridge (MEDIUM)** — Paper trading/testnet path, OMS primitives, risk dashboard. Artifact: `examples/run_paper_trading_live.py` (or equivalent honest deliverable).

## 5) Reproduction / gate commands

```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
PYTHONPATH=. python -m pytest tests/ -q
python -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python -m mypy backtest/ strategies/ utils/
```

## 6) Handoff contract
- Start with Campaign #4 immediately. Do not redo #1-#3 unless fixing a concrete defect.
- Produce real artifacts with provenance. If blocked, record exact `blocked_routes`/rationale — do not fabricate.
- At material checkpoint/completion, update **only** `HANDOFF.md` with verified truth. Keep it the single durable handoff.
