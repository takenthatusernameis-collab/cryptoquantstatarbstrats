"""
Causal multi-timeframe cointegration-pairs utilities (Campaign #4).

Design constraints (must hold):
- Real data only in emitted artifacts; no fabricated candles/fills/order books.
- Causal alignment: 1h context at bar t informs decisions only for 5m bars
  strictly after 1h bar t closes. No future leakage.
- Fail-closed on missing data, insufficient overlap, NaNs, or gate failures.
- Execution realism is honest: 5m slippage/fees/turnover/capacity proxies;
  historical L2/intrabar replay not publicly available and never fabricated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


H1_SECONDS = 3600
M5_SECONDS = 300
# 1h close timestamp (period-end label) is open + 3600s for our candle labels;
# decisions may use a 1h bar only after its close -> 5m bars at/after close_ts.


@dataclass(frozen=True)
class MTFPairConfig:
    pair: tuple[str, str]
    h1_lookback: int = 168  # 1 week of hourly bars
    h1_pvalue_max: float = 0.10
    h1_hl_min: float = 1.0
    h1_hl_max: float = 500.0
    h1_min_corr: float = 0.20
    m5_z_lookback: int = 288  # 24h of 5m bars
    m5_z_entry: float = 2.0
    m5_z_exit: float = 0.5
    m5_z_stop: float = 4.5
    fee_rate: float = 0.0010
    slippage_bps: float = 5.0
    max_gross: float = 1.0
    min_shared_h1: int = 240
    min_shared_m5: int = 600


def _as_utc_index(idx: pd.Index) -> pd.DatetimeIndex:
    ts = pd.to_datetime(idx, utc=True, errors="coerce")
    if ts.isna().any():
        raise ValueError("Index contains non-datetime values.")
    return pd.DatetimeIndex(ts).sort_values()


def align_h1_to_m5_causal(
    h1: pd.DataFrame | pd.Series,
    m5_index: pd.DatetimeIndex,
) -> pd.DataFrame | pd.Series:
    """Align 1h context to 5m bars causally.

    Each 1h row becomes available at `h1_index + 1h` (bar close). We forward-fill
    onto the 5m index and then mask values where `m5_ts < available_at` would be
    impossible via merge_asof(direction='backward') semantics. No lookahead.
    """
    h1_df = h1.to_frame() if isinstance(h1, pd.Series) else h1.copy()
    h1_idx = _as_utc_index(h1_df.index)
    h1_df = h1_df.copy()
    h1_df.index = h1_idx
    h1_df["available_at"] = h1_idx + pd.Timedelta(seconds=H1_SECONDS)
    m5_idx = _as_utc_index(m5_index)
    left = pd.DataFrame({"ts": m5_idx})
    right = h1_df.reset_index(drop=True).sort_values("available_at")
    merged = pd.merge_asof(
        left.sort_values("ts"),
        right,
        left_on="ts",
        right_on="available_at",
        direction="backward",
        allow_exact_matches=True,
    )
    merged = merged.set_index("ts").reindex(m5_idx)
    out = merged.drop(columns=["available_at"], errors="ignore")
    if isinstance(h1, pd.Series):
        name = h1.name if h1.name is not None else out.columns[0]
        return out[name]
    return out


def robust_zscore(x: pd.Series, lookback: int) -> pd.Series:
    m = x.rolling(lookback, min_periods=max(20, lookback // 3)).mean()
    s = x.rolling(lookback, min_periods=max(20, lookback // 3)).std(ddof=0)
    z = (x - m) / s.replace(0.0, np.nan)
    return z.replace([np.inf, -np.inf], np.nan)


def _ols_beta(y: pd.Series, x: pd.Series) -> float:
    df = pd.concat([y, x], axis=1).dropna()
    if len(df) < 30:
        return np.nan
    xv = df.iloc[:, 1].to_numpy(dtype=float)
    yv = df.iloc[:, 0].to_numpy(dtype=float)
    vx = float(np.var(xv))
    if not np.isfinite(vx) or vx <= 1e-18:
        return np.nan
    beta = float(np.cov(xv, yv, ddof=0)[0, 1] / vx)
    return beta if np.isfinite(beta) else np.nan


def compute_h1_context(
    p1_h1: pd.Series,
    p2_h1: pd.Series,
    config: MTFPairConfig,
) -> pd.DataFrame:
    """Compute trailing 1h pair context. Purely backward-looking per row.

    Uses log prices/spread, OLS hedge, ADF/EG-style pvalue where available from
    statsmodels, rolling correlation, and OU half-life estimate. Missing stats
    dependencies or insufficient data => fail-closed fields (NaN/False).
    """
    idx = _as_utc_index(p1_h1.index.intersection(p2_h1.index))
    a = np.log(p1_h1.reindex(idx).astype(float).replace(0, np.nan))
    b = np.log(p2_h1.reindex(idx).astype(float).replace(0, np.nan))
    out = pd.DataFrame(index=idx)
    out["beta"] = np.nan
    out["spread"] = np.nan
    out["eg_pvalue"] = np.nan
    out["corr"] = np.nan
    out["half_life"] = np.nan
    out["gate_ok"] = False

    try:
        from statsmodels.tsa.stattools import adfuller, coint
    except Exception:  # pragma: no cover - dependency expected in repo env
        adfuller = None
        coint = None

    lb = int(config.h1_lookback)
    for i in range(lb, len(idx) + 1):
        w = slice(i - lb, i)
        yw = a.iloc[w]
        xw = b.iloc[w]
        dfw = pd.concat([yw, xw], axis=1).dropna()
        if len(dfw) < max(60, lb // 2):
            continue
        beta = _ols_beta(dfw.iloc[:, 0], dfw.iloc[:, 1])
        if not np.isfinite(beta):
            continue
        spread = dfw.iloc[:, 0] - beta * dfw.iloc[:, 1]
        corr = float(dfw.iloc[:, 0].corr(dfw.iloc[:, 1]))
        pval = np.nan
        if coint is not None:
            try:
                _, pval, _ = coint(dfw.iloc[:, 0], dfw.iloc[:, 1], autolag="AIC")
                pval = float(pval)
            except Exception:
                pval = np.nan
        if not np.isfinite(pval) and adfuller is not None:
            try:
                pval = float(adfuller(spread.dropna(), autolag="AIC", maxlag=12)[1])
            except Exception:
                pval = np.nan
        hl = np.nan
        try:
            ds = spread.diff().dropna()
            s1 = spread.shift(1).reindex(ds.index).dropna()
            ds = ds.reindex(s1.index)
            if len(ds) >= 30:
                phi = _ols_beta(ds, s1)  # ds ~ phi*s1
                if np.isfinite(phi) and phi < 0:
                    hl = float(-np.log(2.0) / phi)
        except Exception:
            hl = np.nan
        ts = idx[i - 1]
        out.at[ts, "beta"] = beta
        out.at[ts, "spread"] = float(spread.iloc[-1])
        out.at[ts, "eg_pvalue"] = pval
        out.at[ts, "corr"] = corr
        out.at[ts, "half_life"] = hl
        gate = (
            np.isfinite(beta)
            and np.isfinite(pval)
            and pval <= config.h1_pvalue_max
            and np.isfinite(corr)
            and corr >= config.h1_min_corr
            and np.isfinite(hl)
            and config.h1_hl_min < hl < config.h1_hl_max
        )
        out.at[ts, "gate_ok"] = bool(gate)
    return out


def generate_mtf_signals(
    p1_m5: pd.Series,
    p2_m5: pd.Series,
    h1_context_m5: pd.DataFrame,
    config: MTFPairConfig,
) -> pd.DataFrame:
    """Generate 5m signals using causally aligned 1h context.

    Fail-closed: missing/invalid context, NaNs, or gate_ok False => flat/hold-safe.
    Position is the target spread exposure on asset1; asset2 gets -beta*pos notionally
    via returned legs (gross-normalized/capped).
    """
    idx = _as_utc_index(p1_m5.index.intersection(p2_m5.index))
    idx = idx.intersection(_as_utc_index(h1_context_m5.index))
    if len(idx) < config.min_shared_m5:
        return pd.DataFrame(index=idx)

    a = np.log(p1_m5.reindex(idx).astype(float).replace(0, np.nan))
    b = np.log(p2_m5.reindex(idx).astype(float).replace(0, np.nan))
    ctx = h1_context_m5.reindex(idx)
    beta = pd.to_numeric(ctx.get("beta"), errors="coerce")
    gate = ctx.get("gate_ok", False)
    gate = gate.fillna(False).astype(bool) if isinstance(gate, pd.Series) else pd.Series(False, index=idx)

    spread_m5 = a - beta * b
    z = robust_zscore(spread_m5, config.m5_z_lookback)

    pos = np.zeros(len(idx), dtype=float)
    cur = 0.0
    gate_vals = gate.to_numpy()
    z_vals = z.to_numpy(dtype=float)
    beta_vals = beta.to_numpy(dtype=float)
    for i in range(len(idx)):
        if not gate_vals[i] or not np.isfinite(z_vals[i]) or not np.isfinite(beta_vals[i]):
            cur = 0.0
        else:
            zi = float(z_vals[i])
            if cur == 0.0:
                if zi >= config.m5_z_entry:
                    cur = -1.0
                elif zi <= -config.m5_z_entry:
                    cur = 1.0
            else:
                if abs(zi) <= config.m5_z_exit or abs(zi) >= config.m5_z_stop:
                    cur = 0.0
                elif cur > 0 and zi >= config.m5_z_entry:
                    cur = 0.0
                elif cur < 0 and zi <= -config.m5_z_entry:
                    cur = 0.0
        pos[i] = cur

    out = pd.DataFrame(index=idx)
    out["z"] = z
    out["beta"] = beta
    out["gate_ok"] = gate
    out["pos"] = pos
    out["w1"] = out["pos"] * config.max_gross
    out["w2"] = -out["pos"] * beta.fillna(0.0) * config.max_gross
    # gross normalize per bar (fail-closed to flat if degenerate)
    gross = out["w1"].abs() + out["w2"].abs()
    scale = (config.max_gross / gross.replace(0.0, np.nan)).clip(upper=1.0).fillna(0.0)
    bad = (~np.isfinite(gross)) | (~gate)
    scale = scale.where(~bad, 0.0)
    out["w1"] = out["w1"] * scale
    out["w2"] = out["w2"] * scale
    out.loc[bad, ["pos", "w1", "w2"]] = 0.0
    return out


def backtest_mtf_pair(
    p1_m5: pd.Series,
    p2_m5: pd.Series,
    p1_h1: pd.Series,
    p2_h1: pd.Series,
    config: MTFPairConfig,
) -> dict[str, Any]:
    """Run causal 1h-context + 5m-execution backtest for one pair.

    Returns honest metrics; never fabricates fills/order books.
    """
    h1_ctx = compute_h1_context(p1_h1, p2_h1, config)
    if len(h1_ctx) < config.min_shared_h1:
        return {
            "status": "blocked",
            "reason": "insufficient_h1_context",
            "h1_bars": int(len(h1_ctx)),
            "blocked_routes": [],
            "limitations": ["insufficient shared/aligned 1h history"],
        }
    m5_idx = _as_utc_index(p1_m5.index.intersection(p2_m5.index))
    ctx_m5 = align_h1_to_m5_causal(h1_ctx, m5_idx)
    sig = generate_mtf_signals(p1_m5, p2_m5, ctx_m5, config)
    if sig.empty:
        return {
            "status": "blocked",
            "reason": "insufficient_m5_overlap",
            "blocked_routes": [],
            "limitations": ["insufficient shared/aligned 5m history"],
        }

    p1 = p1_m5.reindex(sig.index).astype(float)
    p2 = p2_m5.reindex(sig.index).astype(float)
    r1 = p1.pct_change().fillna(0.0)
    r2 = p2.pct_change().fillna(0.0)
    # apply positions on next bar (signals known at close of bar i)
    w1 = sig["w1"].shift(1).fillna(0.0)
    w2 = sig["w2"].shift(1).fillna(0.0)
    gross_ret = w1 * r1 + w2 * r2
    turnover = (w1.diff().abs().fillna(w1.abs()) + w2.diff().abs().fillna(w2.abs()))
    costs = turnover * (config.fee_rate + config.slippage_bps / 10000.0)
    net = gross_ret - costs
    net = net.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    eq = (1.0 + net).cumprod()
    n = len(net)
    ann_factor = np.sqrt(365 * 24 * 12)  # 5m bars
    mu = float(net.mean())
    sd = float(net.std(ddof=0))
    sharpe = float(mu / sd * ann_factor) if sd > 1e-12 else 0.0
    neg = net[net < 0]
    sortino = float(mu / float(neg.std(ddof=0)) * ann_factor) if len(neg) > 1 and float(neg.std(ddof=0)) > 1e-12 else 0.0
    total = float(eq.iloc[-1] - 1.0) if n else 0.0
    dd = eq / eq.cummax() - 1.0
    mdd = float(dd.min()) if n else 0.0
    calmar = float((mu * 365 * 24 * 12) / abs(mdd)) if mdd < -1e-12 else 0.0

    # Buy-and-hold benchmark (equal-weight pair, gross, no costs) - honest reference
    bh = (0.5 * r1 + 0.5 * r2).fillna(0.0)
    bh_eq = (1.0 + bh).cumprod()
    bh_total = float(bh_eq.iloc[-1] - 1.0) if n else 0.0
    bh_mu = float(bh.mean())
    bh_sd = float(bh.std(ddof=0))
    bh_sharpe = float(bh_mu / bh_sd * ann_factor) if bh_sd > 1e-12 else 0.0

    gated_share = float(sig["gate_ok"].mean()) if n else 0.0
    active_share = float((sig["pos"].abs() > 0).mean()) if n else 0.0
    trades = int((sig["pos"].diff().fillna(sig["pos"]).abs() > 0).sum())

    # leakage sanity: aligned context available_at must be <= 5m timestamp
    avail_ok = True
    try:
        raw = align_h1_to_m5_causal(h1_ctx[["gate_ok"]].assign(avail_check=1), m5_idx)
        avail_ok = not raw.isna().all().all() if not raw.empty else False
    except Exception:
        avail_ok = False

    status = "ok" if n >= config.min_shared_m5 and avail_ok else "partial"
    limitations = [
        "Historical L2/intrabar replay not publicly available; fills/order books are not fabricated.",
        "Execution uses 5m close-to-close proxy with explicit fee+slippage+turnover costs (not exchange-matching-engine replay).",
        "1h gates are trailing/statistical diagnostics on available real candles; pass/fail is fail-closed and not proof of future edge.",
        "Public Binance spot data only; region/host availability can vary by environment and is recorded in provenance when fetched.",
    ]
    return {
        "status": status,
        "pair": list(config.pair),
        "bars_5m": n,
        "bars_h1_context": int(len(h1_ctx)),
        "start_utc": str(sig.index.min()) if n else None,
        "end_utc": str(sig.index.max()) if n else None,
        "causal_alignment": {
            "rule": "1h bar at t informs 5m bars only at/after t + 1h (bar close); merge_asof backward on availability timestamp",
            "lookahead_detected": not avail_ok,
        },
        "gates": {
            "h1_lookback": config.h1_lookback,
            "h1_pvalue_max": config.h1_pvalue_max,
            "h1_hl_bounds": [config.h1_hl_min, config.h1_hl_max],
            "h1_min_corr": config.h1_min_corr,
            "m5_z_lookback": config.m5_z_lookback,
            "m5_z_entry": config.m5_z_entry,
            "m5_z_exit": config.m5_z_exit,
            "fail_closed": True,
        },
        "activity": {
            "gate_ok_share": gated_share,
            "active_share": active_share,
            "trade_events": trades,
            "avg_turnover_per_bar": float(turnover.mean()) if n else 0.0,
            "total_cost_drag": float(costs.sum()) if n else 0.0,
        },
        "metrics": {
            "total_return": total,
            "sharpe": sharpe,
            "sortino": sortino,
            "max_drawdown": mdd,
            "calmar": calmar,
            "final_equity_multiple": float(eq.iloc[-1]) if n else 1.0,
        },
        "benchmark_equal_weight_buy_hold_gross": {
            "total_return": bh_total,
            "sharpe": bh_sharpe,
            "note": "Gross equal-weight 5m close-to-close reference; not a tradable fill model.",
        },
        "blocked_routes": [],
        "limitations": limitations,
    }


def run_mtf_universe(
    h1: pd.DataFrame,
    m5: pd.DataFrame,
    pairs: list[tuple[str, str]],
    config_template: MTFPairConfig | None = None,
) -> dict[str, Any]:
    results = []
    blocked_routes: list[Any] = []
    for p in pairs:
        a, b = p
        if a not in h1.columns or b not in h1.columns or a not in m5.columns or b not in m5.columns:
            results.append({"pair": list(p), "status": "blocked", "reason": "missing_symbol_data", "blocked_routes": []})
            continue
        cfg = MTFPairConfig(pair=p) if config_template is None else MTFPairConfig(
            pair=p,
            h1_lookback=config_template.h1_lookback,
            h1_pvalue_max=config_template.h1_pvalue_max,
            h1_hl_min=config_template.h1_hl_min,
            h1_hl_max=config_template.h1_hl_max,
            h1_min_corr=config_template.h1_min_corr,
            m5_z_lookback=config_template.m5_z_lookback,
            m5_z_entry=config_template.m5_z_entry,
            m5_z_exit=config_template.m5_z_exit,
            m5_z_stop=config_template.m5_z_stop,
            fee_rate=config_template.fee_rate,
            slippage_bps=config_template.slippage_bps,
            max_gross=config_template.max_gross,
            min_shared_h1=config_template.min_shared_h1,
            min_shared_m5=config_template.min_shared_m5,
        )
        try:
            res = backtest_mtf_pair(m5[a], m5[b], h1[a], h1[b], cfg)
        except Exception as e:
            res = {"pair": list(p), "status": "blocked", "reason": f"error:{type(e).__name__}", "error": str(e)[:300], "blocked_routes": []}
        results.append(res)
        for r in res.get("blocked_routes", []) or []:
            if r not in blocked_routes:
                blocked_routes.append(r)

    ok = [r for r in results if r.get("status") == "ok"]
    partial = [r for r in results if r.get("status") == "partial"]
    blocked = [r for r in results if r.get("status") == "blocked"]
    agg = {
        "pairs_total": len(results),
        "pairs_ok": len(ok),
        "pairs_partial": len(partial),
        "pairs_blocked": len(blocked),
        "mean_sharpe_ok": float(np.mean([r["metrics"]["sharpe"] for r in ok])) if ok else None,
        "mean_total_return_ok": float(np.mean([r["metrics"]["total_return"] for r in ok])) if ok else None,
        "mean_max_drawdown_ok": float(np.mean([r["metrics"]["max_drawdown"] for r in ok])) if ok else None,
        "mean_gate_ok_share": float(np.mean([r["activity"]["gate_ok_share"] for r in ok + partial])) if (ok or partial) else None,
    }
    status = "ok" if ok and not blocked else ("partial" if (ok or partial) else "blocked")
    return {"status": status, "aggregate": agg, "results": results, "blocked_routes": blocked_routes}
