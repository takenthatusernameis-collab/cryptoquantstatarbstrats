# DURABLE HANDOFF | 2026-10-31T10:19:50Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW)
- Repo: `cryptoquantstatarbstrats` — Crypto Quant Stat Arb Strategies
- **CORE = COINTEGRATION/PAIRS TRADING.** Everything else supports it. Prioritize cointegration rigor above all else.
- Real data only: Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, and logs.
- **Network BLOCKED (HTTP 451 on api.binance.com).** Adapt via existing artifacts + `blocked_or_insufficient_data` + `blocked_routes` + full provenance. NEVER FABRICATE. Do not retry Binance to "fix" this; work around it.

## CURRENT VERIFIED STATE (2026-10-31T10:17:49Z)
- Branch: `main` (clean). Working tree clean.
- Green baseline (re-verified 2026-10-31T10:19:11Z): `ruff check` passes | `pytest tests/ -q` → **529 passed, 1 skipped** | `mypy backtest/ strategies/ utils/` → success.
- Artifact: `reports/portfolio_real.json` (177005 bytes). `real_data_only: true`, `fabricated_data: false`.
- `cointegration_diagnostics`: **17 pairs**, all in minimal form (`status: "computed_from_existing_results"`, EG/Johansen/rolling/half-life/structural breaks mostly missing/unpopulated). **This is THE bottleneck.**
- Modules ready: `utils/cointegration.py`, `strategies/pairs_trading.py`, `examples/run_portfolio_real.py`.
- Existing CI noise (not your scope): historical `fix/causal-pairs-validation-2026-10-27` branch failures/cancellations from missing dev deps in CI — ignore; `main` is green locally.

## BOTTLENECK REMOVAL (READ BEFORE ANY WORK)
1. **Network 451 on api.binance.com is hard-blocked.** Do not attempt live Binance fetches as a primary path. Reuse `reports/portfolio_real.json` + `utils/cointegration.py` functions on the series already embedded in the artifact/replays; where series are unreconstructible, mark `status: "blocked_or_insufficient_data"`, list `blocked_routes`, add rationale + full provenance, and move on. This removes the bottleneck instead of stalling on it.
2. **Single durable handoff = this file.** Do not spawn parallel competing sessions or split the campaign. One session, one focus: cointegration diagnostics for all 17 pairs.
3. **Preserve green.** Every change must keep `ruff` clean, `pytest >= 529 passed / 0 new failures`, and `mypy` clean.

## NEXT SESSION START POINT (initial task message)
The next agentic session MUST begin here, in order, without drift:

### 0) VERIFY GREEN (mandatory gate, do not skip)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
Must be >=529 passed / 0 new failures / mypy clean. If broken, fix first.

### 1) INVENTORY
- Read `reports/portfolio_real.json` → `cointegration_diagnostics` for all 17 pairs vs the target schema (Section 2).
- Read `utils/cointegration.py`, `strategies/pairs_trading.py:get_cointegration_diagnostics`, `examples/run_portfolio_real.py`.
- Confirm raw price series are unreconstructible via Binance (451) — plan the enrich-from-existing-results + `blocked_or_insufficient_data` path.

### 2) ENRICH COINTEGRATION DIAGNOSTICS (EVERY PAIR — HEAVY, NO SKIPPING)
Target schema per pair:
```json
{
  "pair":["LEG1","LEG2"],
  "status":"computed_from_existing_results"|"blocked_or_insufficient_data",
  "engle_granger":{"available":bool,"stat":null|number,"pvalue":null|number,"critical_values":null|{}, "pass/fail":null|bool,"method":"engle_granger"|null,"provenance":{}},
  "johansen":{"available":bool,"trace_stat":null|[],"max_eig_stat":null|[],"cv_90":null|[],"cv_95":null|[],"cv_99":null|[],"rank":null|int,"pass/fail":null|bool,"provenance":{}},
  "adf_leg1":{...},"adf_leg2":{...},"kpss_leg1":{...},"kpss_leg2":{...},
  "spread":{"hedge_ratio":null|number,"adf_spread":null|{},"kpss_spread":null|{},"half_life_ou":null|number,"hurst_exponent":null|number,"mr_favorable":null|bool,"provenance":{}},
  "rolling_stability":{"windows":[int],"frac_significant":null|number,"stable":null|bool,"details":[],"notes":null,"provenance":{}},
  "structural_breaks":{"breaks":[],"flagged":bool,"notes":null,"provenance":{}},
  "gates":{"all_pass":null|bool,"eg_pass":null|bool,"johansen_pass":null|bool,"spread_mr_pass":null|bool,"hl_bounds_pass":null|bool,"leg_stationarity_ok":null|bool,"rolling_stable_ok":null|bool},
  "provenance":{"source":string,"real_data_only":true,"fabricated_data":false,"computed_at":"ISO8601","blocked_routes":[],"rationale":string}
}
```
Rules: if unreconstructible → `status: "blocked_or_insufficient_data"`, include `blocked_routes` + rationale + full provenance. Never fabricate. Enforce `1 < half_life_ou < 500` if computed. Use `utils.cointegration` functions; extend if needed. Update `examples/run_portfolio_real.py` and `strategies/pairs_trading.py.get_cointegration_diagnostics`. Preserve `pair_metrics`.

### 3) ENRICH PARAMETER STABILITY & TAIL RISK
- `parameter_stability`: per-pair + portfolio with scores/degradation/regime notes + provenance.
- `tail_risk.portfolio`: VaR/CVaR/CDaR at 95/99/99.9, add `regime_conditioned` if possible, ensure `permutation_test` complete.
- Harmonize bootstraps to `n_simulations >= 3000`.

### 4) HARDEN, TEST, ENFORCE NO-FABRICATION
- Harden gates/bounds/logging/determinism.
- Add network-independent tests: schema validity for all 17 pairs; fail if fabricated without `fabricated_data: true` in isolated tests; validate hl bounds (1<hl<500), EG/Johansen gates, rolling/structural structure; blocked case must have `status` + `blocked_routes` + provenance.
- Keep >=529 passed, 0 new failures.

### 5) DOCS & PROVENANCE
- Update `README.md` with cointegration rigor, gates, reproduction, 451 handling.
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
**Make cointegration diagnostics publication-grade for ALL 17 pairs in `reports/portfolio_real.json`.** Deepen EG/Johansen, per-leg ADF/KPSS, spread (hedge ratio, spread tests, half-life OU 1<hl<500, Hurst), rolling stability, structural breaks, tighten gates. Enrich `parameter_stability`/`tail_risk`. Harden tests against fabrication. All with full provenance. Work around Binance 451 via existing artifacts + `blocked_or_insufficient_data` + `blocked_routes`.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — isolated tests only with explicit `fabricated_data: true`
- **NO SHORTCUTS** — omit+document with full provenance if unavailable
- **PRESERVE GREEN** — >=529 passed, 0 new failures
- **HEAVY MANDATE** — complete full campaign
- **BOTTLENECK REMOVAL** — eliminate inefficiencies, work around 451 explicitly
- **COINTEGRATION IS LAW** — prioritize above all
- **UNBUFFERED** — use `python -u`, deterministic ordering
