# Durable Handoff — cryptoquantstatarbstrats (single authoritative)

**Handoff written:** 2026-11-24T17:25:00Z (re-verified on disk this session: `ls scripts/*432* tests/*432*` -> 5 files present; `data/cache/campaign432_edfgof_5m/` -> 10 shards + meta + provenance + metrics.npz; `reports/campaign432_*` -> 5 artifacts; `python3 -m pytest tests/test_preflight_c432.py tests/test_c432_edfgof_xsec_oos.py -q` -> 65 passed; C432 is COMPLETE_FORMAL_NEGATIVE) — **THE ONLY AUTHORITATIVE HANDOFF. There is no HANDOFF.md and none may be created.**

This block is the SINGLE active directive. Everything below the first `---` under it is history/archived evidence only and never overrides this message.

## INITIAL TASK MESSAGE (2026-11-24T17:25:00Z; supersedes every earlier session message; the ONLY active directive)

**PRIORITY (derived from repo name `cryptoquantstatarbstrats` = crypto quant stat-arb strategies): the single most relevant next unit of work is the next pre-registered, fully-costed, real-data-only, walk-forward OOS stat-arb EDGE campaign on the C312 USDT-M 5m `perp_close` universe. C430 DISTCOR is DONE (RETRACTED formal negative 20261124T071440Z). C431 CQ (cross-quantilogram) is DONE (RETRACTED formal negative 20261124T080617Z). C432 EDF-GOF is DONE (RETRACTED formal negative 20261124T163545Z). The queue advances to **C433**.

**NEXT SESSION MUST BUILD C433 END-TO-END — NO EXCEPTIONS, NO STOPPING, NO SHORTCUTS, NO LIGHT-WORK.**

**TRUE DISK STATE AT HANDOFF (2026-11-24T17:25:00Z) — READ THIS FIRST, IT CHANGES WHAT YOU DO:**
C432 is COMPLETE and there is **NO clone-trap on disk**. Verified this session: `ls scripts/*432* tests/*432*` shows 5 properly implemented EDF-GOF files (not clones), `data/cache/campaign432_edfgof_5m/` exists with 10 shards + meta + provenance + metrics.npz, `reports/campaign432_*_20261124T163545Z.json` exists (5 artifacts), 65 tests green. The queue has advanced to **C433**. C422–C432 are ALL FROZEN formal negatives (0 Holm+BH survivors, placebos dominate, NO EDGE through C432). The next campaign **C433** must be a genuinely-new price-only, volume-free, close-only kernel on real C312 `perp_close` with a distinct statistical family not yet tested.

**C432 RESULT (frozen — do not re-run; for record):**
  - verdict RETRACTED, edge_proven false, binding multiple_testing, n_survive_holm=0, n_survive_bh=0, n_survive_both=0, n_deterministic_edge=0
  - dominant attribution edf_ks_dev (share 0.1736), attribution_ok false
  - artifacts (20261124T163545Z): oos_sweep b3694b4345f74cf80a31e3da636e290c81f2b9d1b2fc6750a722a00efffd9792; tradable_edge_registry 6b743bdb9c13f4fe6f000737251fe6dada823eefbc7c08f004836d157ad38f93; summary 641645c7594c1cd5e9508f25cd5dcfd476d54d6283e8a805d2642ee63850bfea; verdict da547e0309a7eccda956af632c9d334a1db9c603cad6ac4f76f4110411704586; binding_constraint 96bb777569bf48dbafacc34095886722110d62923c3c80233610be3d640023f6
  - cache SHAs: meta dd38a0a5718d2406f1850209749b3de1056870df1221325aabbdd744958af3a0; provenance ab079d6eaa0d7877590ccb36b65c749bfa252f8a7aa4df6de38ef50e058eb490; manifest ed77576cbee8a1579f080428750c6a40b6f45488cc818c22d2971a97eb00479f

**C430 RESULT (frozen — do not re-run; for record):**
  - verdict RETRACTED, edge_proven false, binding multiple_testing, n_survive_holm=0, n_survive_bh=0, n_survive_both=0, n_deterministic_edge=0
  - dominant attribution dcor_signmag_dev (share 0.1684), attribution_ok false
  - artifacts (20261124T071440Z): oos_sweep 76b8450d994a0eab5ee18ba164311c71e5b6d63ac0c3480aa14591f1babd9032; tradable_edge_registry 69d336bb2e0f89cd9eddc07d22ce5aeffcdba769ee54c8862f9823e3931d1a56; summary 78f9dcbdebf74e87ab29b75ae8ebf7c4599931d85f00ad3d38f9a3a942f6ad44; verdict 2703142d76914f1673b5f0ca4157edbf329f89dcd79db82e565e5dfddd1ffa4e; binding_constraint ddc4fdc08cf0dc98454862ec741885483e9cb5454024263157b9932adae90fbb
  - cache SHAs: meta 0c2bfaea1deb3952fe0a9bcbaaebb58d9ea7ec0f14b22adcc2d8c60bf4cc1c7f; provenance 477c55e46db09110836573fa93e55850ab291b6d5e987b9b5522a7b2b877fd0d

**C431 RESULT (frozen — do not re-run; for record):**
  - verdict RETRACTED, edge_proven false, binding multiple_testing, n_survive_holm=0, n_survive_bh=0, n_survive_both=0, n_deterministic_edge=0
  - dominant attribution cq_market_placebo (share 0.2057), attribution_ok false
  - artifacts (20261124T080617Z): oos_sweep 3ecb08f188abea5c3e4778e981d2fc157be49d572f972de37ae59d97d10dc069; tradable_edge_registry 931889ff8b21989122b78bb655405dbfcb14e504419ad5c6efe87f06b0ba2791; summary 43e7e021d9bee391390ac9a79fcfff22632afa9f7707e067594a033d9d2b00e6; verdict e7453343e2f19e4ea7a3ee31fdcdb0479fd88942f37c1950411c2156a902201a; binding_constraint 60971bbe4d61ccc05a9c7c7383238fb941a52935bb3ab2b74a768e8e3d4fff1e
  - cache SHAs: meta 208e824b6a88531e347067bfc9aa15cdb083819e26600b35920baa9b2ea0e87c; provenance 9d6f970d1903711eed222533305a18017d1d0108519ca5bd9bf28398f8afc0fb

**NO-LIGHT-WORK RULE:** a session is complete only when it produces 3 scripts + 2 test files + cache + preflight ready:true + the FULL literal-2592-config costed OOS sweep + 5 SHA256 reports + ≥21 green tests incl. brute-force equality, then records the truthful RESULT + SHAs in this file and research_state/state.yaml and moves the queue forward (C433 → C434). If a session cannot finish, it must leave the queue non-empty and name the partial artifacts. Terminal closure by fiat is PROHIBITED.
---