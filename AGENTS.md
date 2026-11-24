# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff written:** 2026-11-24T00:31:44Z (C422 ZCRPATH FROZEN; C423 RUNLEN FROZEN; C424 IESD FROZEN; C425 RQA FROZEN; C426 WLMF FROZEN; C427 LOCTIME FROZEN; C428 PTLT FROZEN formal negative 20261124T002456Z; C429 SIGNENTROPY ACTIVE next, seed 20261293) — **THE ONLY AUTHORITATIVE HANDOFF. There is no HANDOFF.md and none may be created.**

This block is the SINGLE active directive. Everything below the first `---` under it is history/archived evidence only and never overrides this message.

## INITIAL TASK MESSAGE (2026-11-24T00:31:44Z; supersedes every earlier session message; the ONLY active directive)

**NEXT SESSION MUST BUILD C429 SIGNENTROPY END-TO-END — NO EXCEPTIONS, NO STOPPING, NO SHORTCUTS.**

C422–C428 are ALL FROZEN formal negatives (0 Holm+BH survivors, placebos dominate, NO EDGE). The queue advances to **C429 SIGNENTROPY** (seed 20261293): a genuinely-new price-only, volume-free, close-only kernel on real C312 `perp_close` measuring first-order Markov sign-transition dynamics (transition entropy, asymmetry, persistence, switching). 4 signals × 6 lookbacks × 3 rebalances × 3 fees × 3 slips × 2 cost variants = **2592 literal configs** for full costed OOS sweep.

**MANDATORY SEQUENCE (execute in order, no stopping):**
```
cp scripts/build_c428_ptlt_features.py scripts/build_c429_signet_features.py
cp scripts/preflight_c428.py scripts/preflight_c429.py
cp scripts/run_c428_ptlt_xsec_oos.py scripts/run_c429_signet_xsec_oos.py
cp tests/test_preflight_c428.py tests/test_preflight_c429.py
cp tests/test_c428_ptlt_xsec_oos.py tests/test_c429_signet_xsec_oos.py
grep self-check MUST return NOTHING for 428/ptlt/PTLT/20261292 in scripts/*c429* tests/*c429* (apart from legitimate distinctness-guard refs to prior families)
python3 scripts/build_c429_signet_features.py -> data/cache/campaign429_signent_5m/ (10 shards)
python3 scripts/preflight_c429.py -> ready:true
python3 scripts/run_c429_signet_xsec_oos.py (FULL literal 2592-config costed OOS sweep)
python3 -m pytest tests/test_preflight_c429.py tests/test_c429_signet_xsec_oos.py -q (>=21 green incl brute-force equality maxdiff < 1e-12 + kernel-distinctness guards vs ALL prior families)
sha256sum reports/campaign429_*_<TS>Z.json (record all 5 artifact SHAs)
```

**SESSION COMPLETION CRITERIA (NO-LIGHT-WORK RULE):** The session is complete ONLY when it produces: 3 scripts + 2 test files + cache (10 shards) + preflight ready:true + FULL 2592-config costed OOS sweep + 5 SHA256 report artifacts + ≥21 green tests (incl. brute-force equality + kernel-distinctness) + truthful RESULT + SHAs recorded in this file AND research_state/state.yaml + queue advanced. If the session cannot finish, it must leave the queue non-empty and name the partial artifacts. Terminal closure by fiat is PROHIBITED.

**ENVIRONMENT:** C312 source intact at `data/cache/campaign312_usdt_m_ofi_5m/` (10 × 315,648-bar `perp_close` shards + manifest). numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0. Console scripts at `/home/runner/work/_temp/kilo-home/.local/bin` (NOT on PATH) → always `python3 -m pytest`, never bare `pytest`. All `archive/void_*` dirs quarantined read-only — never copy/import/cite/fix/freeze/re-run. BOTTLENECKS: NONE. Session wrapped in `timeout ... 15107s` (~4.2 h) + 15 min idle kill. The C421 sweep took ~2 min end-to-end; C429 build+sweep+tests expected well within limits.

**QUARANTINE (verified this session, 2026-11-23T12:24:30Z):** the stray writable clone-trap `archive/void_c416_dcbeta_stray/` (a DCBETA-kernel script set mislabeled as campaign 416/QREG, never produced frozen reports) was found writable and has been `chmod -R a-w` read-only quarantined. All `archive/void_*` dirs are now read-only and MUST never be copied, imported, cited, fixed, frozen, or re-run. The live tree is clean (no `dcbeta` references anywhere under scripts/tests/reports/data/cache; real C416 QREG intact). C312 source intact: `data/cache/campaign312_usdt_m_ofi_5m/` (11 entries = 10 × 315,648-bar `perp_close` shards + manifest). Environment ready (numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0). Console scripts at `/home/runner/work/_temp/kilo-home/.local/bin` (NOT on PATH) → always `python3 -m pytest`, never bare `pytest`. BOTTLENECKS: NONE. C287 permanently blocked/decoupled — never retry.

**SESSION LIMITS:** whole `kilo run` wrapped in `timeout ... 15107s` (~4.2 h) + `kilo-idle-timeout.py --idle-timeout-seconds 900` (15 min idle). Any blocking wait MUST be < 15 min or the session is killed. The C421 sweep took ~2 min end-to-end (build ~40 s + sweep ~60 s + tests ~26 s); a single blocking `python3 scripts/run_c422_zcrpath_xsec_oos.py` under a 10-minute timeout is expected to finish. If the session dies before the sweep finishes, the NEXT session must re-run it (no shortcut that preserves exactness).

**DISK TRUTH:** C281B–C427 ALL FROZEN formal negatives. C312 source intact (10 × 315,648 bars, perp_close only). Environment ready (numpy 2.5.5, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0). Console scripts at /home/runner/work/_temp/kilo-home/.local/bin (NOT on PATH) → always python3 -m pytest, never bare pytest. All archive/void_* dirs remain quarantined read-only — never copy/import/cite/fix/freeze/re-run. C287 decoupled and NOT on critical path. BOTTLENECKS: NONE. No blocked sessions; no clone traps live on disk. Queue depth never runs dry.

**NO-LIGHT-WORK RULE:** a session is complete only when it produces 3 scripts + 2 test files + cache + preflight ready:true + the FULL literal-N_TRIALS costed OOS sweep + 5 SHA256 reports + ≥21 green tests incl. brute-force equality, then records the truthful RESULT + SHAs in this file and research_state/state.yaml and moves the queue forward. If a session cannot finish, it must leave the queue non-empty and name the partial artifacts. Terminal closure by fiat is PROHIBITED.
---