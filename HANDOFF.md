# DURABLE HANDOFF | 2026-10-31T11:18:14Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION/PAIRS TRADING.** This is the primary edge. All other work (regime, tail risk, portfolio construction) MUST serve cointegration rigor. Prioritize cointegration diagnostics above everything else.
- Real data only: Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication anywhere.
- **NETWORK BLOCKED (HTTP 451 on api.binance.com).** You CANNOT rely on live Binance fetches. Adapt via existing artifacts (`reports/portfolio_real.json`) + `utils/cointegration.py` functions on series already embedded/reconstructible from artifacts; where series are unreconstructible, mark `status: "blocked_or_insufficient_data"`, populate `blocked_routes[]`, add detailed rationale + full provenance, and MOVE ON. Never fabricate. Do not waste turns retrying blocked hosts.
- **Coasting = failure.** Every action must produce checkable artifacts, tests, provenance, and logs. No speculative "maybe later" without concrete next steps.

## CURRENT VERIFIED STATE (2026-10-31T11:18:14Z)
- Branch: `main` (clean). Working tree clean. Up to date with `origin/main`.
- **GREEN BASELINE (verified just now):** `ruff check` passes | `pytest tests/ -q` → **529 passed, 1 skipped** | `mypy backtest/ strategies/ utils/` → success.
- Artifact: `reports/portfolio_real.json` (177005 bytes). `real_data_only: true`, `fabricated_data: false`, `n_bars: 5112`.
- `cointegration_diagnostics`: **17 pairs**, all currently minimal (`status: "computed_from_existing_results"`, many fields missing/unpopulated). **THIS IS THE BOTTLENECK.**
- Modules ready: `utils/cointegration.py` (full diagnostics API), `strategies/pairs_trading.py:get_cointegration_diagnostics`, `examples/run_portfolio_real.py`.
- Existing CI noise (ignore): historical branch failures from missing deps — `main` is green locally.

## BOTTLENECK REMOVAL (MANDATORY BEFORE/WHILE WORKING)
1. **Remove network dependency.** Network to api.binance.com returns HTTP 451. Do NOT attempt live fetches as primary path. Reuse existing artifacts + `utils.cointegration` on whatever series exist in artifacts/replays. If impossible to reconstruct full series, use `blocked_or_insufficient_data` with `blocked_routes` + full provenance.
2. **Single session, single focus.** Do not split into parallel campaigns. One agent session must complete the cointegration campaign end-to-end. Previous sessions checkpointed without finishing; this session closes the loop.
3. **Preserve green always.** Every change must keep `ruff` clean, `pytest >= 529 passed / 0 new failures`, `mypy` clean. Run gates after meaningful changes.
4. **Eliminate inefficiencies.** If you find blocked/inefficient paths, fix them or route around them explicitly with documentation.

## NEXT SESSION START POINT (INITIAL TASK MESSAGE — EXECUTE IN ORDER, NO DRIFT)

### 0) VERIFY GREEN (MANDATORY GATE - DO NOT SKIP)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
Must be >=529 passed / 0 new failures / mypy clean. If broken, fix first before any enrichment.

### 1) INVENTORY (UNDERSTAND FULL SCOPE)
- Read `reports/portfolio_real.json` fully - focus on `cointegration_diagnostics` for ALL 17 pairs. Compare each to target schema in section 2.
- Read `utils/cointegration.py` (all functions), `strategies/pairs_trading.py::get_cointegration_diagnostics`, `examples/run_portfolio_real.py` (how diagnostics are attached).
- Understand what data is actually available in artifacts vs what needs to be computed from reconstructible series. Plan `blocked_or_insufficient_data` cases explicitly.

### 2) ENRICH COINTEGRATION DIAGNOSTICS FOR ALL 17 PAIRS (HEAVY WORK - NO SKIPPING)
Target schema per pair (publication-grade):
```json
{
  "pair":["LEG1","LEG2"],
  "status":"computed_from_existing_results"|"blocked_or_insufficient_data",
  "engle_granger":{"available":bool,"stat":null|number,"pvalue":null|number,"critical_values":{},"pass/fail":null|bool,"method":"engle_granger"|null,"provenance":{}},
  "johansen":{"available":bool,"trace_stat":null|[],"max_eig_stat":null|[],"cv_90":null|[],"cv_95":null|[],"cv_99":null|[],"rank":null|int,"pass/fail":null|bool,"provenance":{}},
  "adf_leg1":{...},"adf_leg2":{...},"kpss_leg1":{...},"kpss_leg2":{...},
  "spread":{"hedge_ratio":null|number,"adf_spread":{},"kpss_spread":{},"half_life_ou":null|number,"hurst_exponent":null|number,"mr_favorable":null|bool,"provenance":{}},
  "rolling_stability":{"windows":[int],"frac_significant":null|number,"stable":null|bool,"details":[],"notes":null,"provenance":{}},
  "structural_breaks":{"breaks":[],"flagged":bool,"notes":null,"provenance":{}},
  "gates":{"all_pass":null|bool,"eg_pass":null|bool,"johansen_pass":null|bool,"spread_mr_pass":null|bool,"hl_bounds_pass":null|bool,"leg_stationarity_ok":null|bool,"rolling_stable_ok":null|bool},
  "provenance":{"source":string,"real_data_only":true,"fabricated_data":false,"computed_at":"ISO8601","blocked_routes":[],"rationale":string}
}
```
Rules:
- If unreconstructible from existing artifacts → `status: "blocked_or_insufficient_data"`, include `blocked_routes[]` + detailed rationale + full provenance. **NEVER FABRICATE.**
- Enforce `1 < half_life_ou < 500` if computed.
- Use `utils.cointegration` functions; extend them if needed for missing pieces.
- Update `examples/run_portfolio_real.py` and `strategies/pairs_trading.py::get_cointegration_diagnostics` as needed.
- Preserve `pair_metrics` if present.

### 3) ENRICH PARAMETER STABILITY & TAIL RISK
- `parameter_stability`: per-pair + portfolio with scores/degradation/regime notes + provenance.
- `tail_risk.portfolio`: VaR/CVaR/CDaR at 95/99/99.9, add `regime_conditioned` if possible, ensure `permutation_test` complete.
- Harmonize bootstraps to `n_simulations >= 3000`.

### 4) HARDEN, TEST, ENFORCE NO-FABRICATION
- Harden gates/bounds/logging/determinism.
- Add network-independent tests: schema validity for all 17 pairs; fail if fabricated without `fabricated_data: true` in isolated tests; validate hl bounds (1<hl<500), EG/Johansen gates, rolling/structural structure; blocked case must have `status` + `blocked_routes` + provenance.
- Keep >=529 passed, 0 new failures.

### 5) DOCS & PROVENANCE
- Update `README.md` with cointegration rigor, gates, reproduction, 451/network-block handling.
- Full provenance everywhere added/enriched.

### 6) VERIFY & DELIVER
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -u examples/run_portfolio_real.py
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
All must pass. Zero regressions. Do not commit unless explicitly requested.

## SINGLE MANDATORY OBJECTIVE (HEAVY WORK REQUIRED)
**Make cointegration diagnostics publication-grade for ALL 17 pairs in `reports/portfolio_real.json`.** Deepen EG/Johansen, per-leg ADF/KPSS, spread (hedge ratio, spread tests, half-life OU with 1<hl<500, Hurst), rolling stability, structural breaks, tighten gates. Enrich `parameter_stability`/`tail_risk`. Harden tests against fabrication. All with full provenance. Work around Binance 451 via existing artifacts + `blocked_or_insufficient_data` + `blocked_routes`. This is the core of cryptoquantstatarbstrats - do the heavy lifting.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — isolated tests only with explicit `fabricated_data: true`
- **NO SHORTCUTS / NO FABRICATION** — omit+document with full provenance if unavailable
- **PRESERVE GREEN** — >=529 passed, 0 new failures
- **HEAVY MANDATE** — complete full campaign, no coasting
- **BOTTLENECK REMOVAL** — eliminate inefficiencies, explicitly route around 451
- **COINTEGRATION IS LAW** — prioritize above all else
- **UNBUFFERED** — use `python -u`, deterministic ordering
