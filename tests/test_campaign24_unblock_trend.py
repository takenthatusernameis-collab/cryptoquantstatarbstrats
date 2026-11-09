"""Campaign #24 (fail-closed infra audit): invariants for unblock trend + status delta.

Real tested code (no fabrication, no edge claim). Ensures the concrete C24
artifacts remain honest/fail-closed and that trend aggregation over repo-style
reports never proves an edge.
"""
from __future__ import annotations

import json
from pathlib import Path

from data.real_feed_loader import (
    build_unblock_trend_report,
    compare_unblock_status,
    generate_unblock_status_report,
)


def test_compare_unblock_status_fails_closed_on_none():
    d = compare_unblock_status(None, {"blocked_families": ["x"], "campaign": 24})
    assert d["fail_closed"] is True
    assert d["real_data_only"] is True
    assert d["fabricated_data"] is False
    assert d["oos_edge_proven"] is False
    assert d["prior_available"] is False
    assert d["changed"] is None


def test_build_unblock_trend_report_never_proves_edge(tmp_path: Path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "real_feed_unblock_status_20261105T182936Z.json").write_text(
        json.dumps(
            {
                "campaign": 23,
                "path_r_triggered": True,
                "conclusion": "PATH_R_ELIGIBLE_VALID_NONSPOT_FEED_PRESENT",
                "blocked_families": [
                    "cross_exchange_dual_venue_same_asset",
                    "funding_basis_carry",
                    "intrabar_microstructure",
                    "term_structure_real_iv_vol_surface",
                ],
                "scan_summary": {"candidate_hits": 1, "meta_files_scanned": 21},
                "campaign_delta": {
                    "changed": True,
                    "honest_assessment": "UNBLOCK_STATE_CHANGED_REVIEW_REQUIRED",
                },
            }
        ),
        encoding="utf-8",
    )
    (reports / "real_feed_unblock_status_20261105T184300Z.json").write_text(
        json.dumps(
            {
                "campaign": 25,
                "path_r_triggered": True,
                "conclusion": "PATH_R_ELIGIBLE_VALID_NONSPOT_FEED_PRESENT",
                "blocked_families": [
                    "cross_exchange_dual_venue_same_asset",
                    "funding_basis_carry",
                    "intrabar_microstructure",
                    "term_structure_real_iv_vol_surface",
                ],
                "scan_summary": {"candidate_hits": 1, "meta_files_scanned": 21},
                "campaign_delta": {
                    "changed": False,
                    "honest_assessment": "NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED",
                },
            }
        ),
        encoding="utf-8",
    )
    trend = build_unblock_trend_report(reports, campaign=24)
    assert trend["fail_closed"] is True
    assert trend["oos_edge_proven"] is False
    assert trend["fabricated_data"] is False
    assert trend["status_reports_read"] == 2
    assert trend["path_r_ever_triggered"] is True
    assert trend["any_observable_state_change_across_reports"] is False
    assert "honest_assessment" in trend


def test_generate_unblock_status_with_prior_is_honest(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    prior = generate_unblock_status_report(cache, campaign=23)
    prior_path = tmp_path / "prior.json"
    prior_path.write_text(json.dumps(prior), encoding="utf-8")
    cur = generate_unblock_status_report(cache, campaign=24, prior_report=prior_path)
    assert cur["campaign_delta"]["prior_available"] is True
    assert cur["campaign_delta"]["changed"] is False
    assert cur["oos_edge_proven"] is False
    assert cur["fail_closed"] is True
