# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff written:** 2026-11-24T05:48:18Z (repo = `cryptoquantstatarbstrats` = crypto quant **stat-arb strategies** → top priority is the next costed OOS stat-arb EDGE campaign; C422–C428 ALL FROZEN formal negatives; **C429 SIGNENTROPY ACTIVE next, placebo seed 20261293**) — **THE ONLY AUTHORITATIVE HANDOFF. There is no HANDOFF.md and none may be created.**

This block is the SINGLE active directive. Everything below the first `---` under it is history/archived evidence only and never overrides this message.

## INITIAL TASK MESSAGE (2026-11-24T01:17:08Z; supersedes every earlier session message; the ONLY active directive)

**PRIORITY (derived from repo name `cryptoquantstatarbstrats` = crypto quant stat-arb strategies): the single most relevant next unit of work is the next pre-registered, fully-costed, real-data-only, walk-forward OOS stat-arb EDGE campaign on the C312 USDT-M 5m `perp_close` universe. The queue's next such campaign is C429 SIGNENTROPY.**

**NEXT SESSION MUST BUILD C429 SIGNENTROPY END-TO-END — NO EXCEPTIONS, NO STOPPING, NO SHORTCUTS, NO LIGHT-WORK.**

C422–C428 are ALL FROZEN formal negatives (0 Holm+BH survivors, placebos dominate, NO EDGE). The queue advances to **C429 SIGNENTROPY** (placebo seed **20261293**): a genuinely-new price-only, volume-free, close-only kernel on real C312 `perp_close` measuring **first-order (order-1) Markov sign-transition dynamics** — per-bar sign `s[t]=sign(r[t])` from causal `r[t]=log(c[t]/c[t-1])`, estimated over a trailing window:
  1. **transition entropy** `H_trans = -Σ_{i,j} p_ij log p_ij` (order-1 Markov transition-matrix entropy),
  2. **transition asymmetry** (up→down vs down→up flip asymmetry),
  3. **persistence** `P_stay = P(s[t+1]=s[t])` (transition-matrix diagonal),
  4. **switching** `P_switch = 1 - P_stay` (off-diagonal flip mass).

**GRID (CORRECTED — the prior handoff's "4 signals = 2592" was arithmetically wrong; 4×6×3×3×3×2 = 1296, NOT 2592):** 4 kernel concepts × 2 variants each (dev + matched placebo) = **8 signals** × 6 lookbacks {60,120,240,480,960,1920} × 3 rebalances {1,4,12} × 3 fees {0.0004,0.0007,0.0010} × 3 slips {0.0,0.0001,0.0002} × 2 cost variants {taker, maker_blend} = **2592 literal configs** for the FULL costed OOS sweep (identical structure to C428, which used 8 signals = 2592). Placebo = recorded-seed phase randomization only (never market data).

**KERNEL-DISTINCTNESS (MUST hold, else the campaign is a clone and is void):** C429 order-1 Markov *transition* dynamics is DISTINCT from the prior **C329 SIGNENTROPY** (which used sign-COUNT Shannon entropy = directional disorder/balance, plus historical max same-sign run length — count/level statistics, NOT transition probabilities), and from C328 signstreak (current run length ending at t), C422 ZCRPATH (zero-crossing rate/path), C423 RUNLEN (run-length distribution), C424 IESD (inter-event/occupation entropy), C426 WLMF (windowed level/width moments), C358/425 RQA, C349 permutation entropy, C356 multiscale entropy, C355 sample entropy. C429 is the FIRST campaign to estimate an order-1 Markov transition matrix (entropy/asymmetry/persistence/switching) on the perp sign sequence. The test file MUST include a kernel-distinctness guard vs C329 (and the other named families) and a brute-force equality check (maxdiff < 1e-12) against an independent reference implementation.

**MANDATORY SEQUENCE (execute in order, no stopping):**
```
cp scripts/build_c428_ptlt_features.py scripts/build_c429_signet_features.py
cp scripts/preflight_c428.py scripts/preflight_c429.py
cp scripts/run_c428_ptlt_xsec_oos.py scripts/run_c429_signet_xsec_oos.py
cp tests/test_preflight_c428.py tests/test_preflight_c429.py
cp tests/test_c428_ptlt_xsec_oos.py tests/test_c429_signet_xsec_oos.py
# edit each copied file: replace PTLT peak/trough-occupancy logic with order-1 Markov sign-transition logic;
# change all 428/ptlt/PTLT/20261292 self-references, cache dir -> data/cache/campaign429_signent_5m, seed -> 20261293, signals -> 8 (4 dev + 4 placebo)
grep self-check MUST return NOTHING for 428/ptlt/PTLT/20261292 in scripts/*c429* tests/*c429* (apart from legitimate distinctness-guard refs to prior families)
python3 scripts/build_c429_signet_features.py -> data/cache/campaign429_signent_5m/ (10 shards + meta + provenance)
python3 scripts/preflight_c429.py -> ready:true
python3 scripts/run_c429_signet_xsec_oos.py (FULL literal 2592-config costed OOS sweep)
python3 -m pytest tests/test_preflight_c429.py tests/test_c429_signet_xsec_oos.py -q (>=21 green incl brute-force equality maxdiff < 1e-12 + kernel-distinctness guards vs ALL prior families, esp. C329)
sha256sum reports/campaign429_*_<TS>Z.json (record all 5 artifact SHAs: oos_sweep, tradable_edge_registry, summary, verdict, binding_constraint)
```

**SESSION COMPLETION CRITERIA (NO-LIGHT-WORK RULE):** The session is complete ONLY when it produces: 3 scripts + 2 test files + cache (10 shards + meta + provenance) + preflight ready:true + FULL 2592-config costed OOS sweep + 5 SHA256 report artifacts + ≥21 green tests (incl. brute-force equality maxdiff < 1e-12 + kernel-distinctness guards vs ALL prior families) + truthful RESULT + SHAs recorded in THIS file AND research_state/state.yaml + queue advanced to C430. If the session cannot finish, it must leave the queue non-empty and name the partial artifacts. Terminal closure by fiat is PROHIBITED.

**ENVIRONMENT:** C312 source intact at `data/cache/campaign312_usdt_m_ofi_5m/` (10 × 315,648-bar `perp_close` shards + manifest). numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0. Console scripts at `/home/runner/work/_temp/kilo-home/.local/bin` (NOT on PATH) → always `python3 -m pytest`, never bare `pytest`. BOTTLENECKS: NONE. Session wrapped in `timeout ... 15107s` (~4.2 h) + 15 min idle kill. The C421/C428 sweeps ran ~2 min end-to-end; C429 build+sweep+tests expected well within limits.

**QUARANTINE (re-verified + RE-APPLIED this session 2026-11-24T01:17:08Z):** the stray writable clone-trap `archive/void_c416_dcbeta_stray/` (a DCBETA-kernel script set mislabeled as campaign 416/QREG, never produced frozen reports) plus all 8 other `archive/void_*` dirs were found WRITABLE (`drwxr-xr-x`) and have been `chmod -R a-w` read-only quarantined (now `dr-xr-xr-x`, owner-write cleared). NOTE: git tracks only the executable bit, NOT write bits, so a fresh `git checkout` restores default umask and these dirs become writable again — the next session MUST re-run `chmod -R a-w archive/void_*` if it finds any `archive/void_*` writable, and treat quarantine as a POLICY regardless: never copy/import/cite/fix/freeze/re-run anything under `archive/void_*`. Live tree verified clean (zero `dcbeta` references under scripts/tests/reports/data/cache; real C416 QREG intact).

**SESSION LIMITS:** whole `kilo run` wrapped in `timeout ... 15107s` (~4.2 h) + `kilo-idle-timeout.py --idle-timeout-seconds 900` (15 min idle). Any blocking wait MUST be < 15 min or the session is killed. Prior single-campaign sweeps finished in ~2 min (build ~40 s + sweep ~60 s + tests ~26 s); a single blocking `python3 scripts/run_c429_signet_xsec_oos.py` under a 10-minute timeout is expected to finish. If the session dies before the sweep finishes, the NEXT session must re-run it (no shortcut that preserves exactness).

**DISK TRUTH:** C281B–C428 ALL FROZEN formal negatives. C312 source intact (10 × 315,648 bars, `perp_close` only). Environment ready (numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0). Console scripts at /home/runner/work/_temp/kilo-home/.local/bin (NOT on PATH) → always python3 -m pytest, never bare pytest. All `archive/void_*` dirs re-quarantined read-only this session — never copy/import/cite/fix/freeze/re-run. C287 permanently decoupled/blocked — never retry. BOTTLENECKS: NONE. No blocked sessions; no clone traps live on disk. Queue depth never runs dry.

**NO-LIGHT-WORK RULE:** a session is complete only when it produces 3 scripts + 2 test files + cache + preflight ready:true + the FULL literal-2592-config costed OOS sweep + 5 SHA256 reports + ≥21 green tests incl. brute-force equality, then records the truthful RESULT + SHAs in this file and research_state/state.yaml and moves the queue forward. If a session cannot finish, it must leave the queue non-empty and name the partial artifacts. Terminal closure by fiat is PROHIBITED.
---