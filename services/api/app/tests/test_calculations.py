from datetime import UTC, datetime, timedelta

from app.domains.calculator.service import calculate_roi
from app.domains.confidence.service import (
    calculate_confidence,
    freshness_score,
    source_reliability_score,
)
from app.domains.indexes.service import calculate_ai_reality_index


def test_confidence_formula_matches_prd_weights():
    result = calculate_confidence(100, 90, 80, 70)
    assert result["score"] == 88.5
    assert result["label"] == "High Confidence"


def test_source_reliability_scores_match_prd():
    assert source_reliability_score("sec_filing") == 100
    assert source_reliability_score("annual_report") == 95
    assert source_reliability_score("earnings_call") == 90
    assert source_reliability_score("investor_presentation") == 80
    assert source_reliability_score("analyst_estimate") == 70
    assert source_reliability_score("industry_report") == 65
    assert source_reliability_score("news_article") == 50
    assert source_reliability_score("community_estimate") == 30


def test_freshness_scores_match_prd_buckets():
    now = datetime(2026, 6, 4, tzinfo=UTC)
    assert freshness_score(now - timedelta(days=29), now=now) == 100
    assert freshness_score(now - timedelta(days=89), now=now) == 90
    assert freshness_score(now - timedelta(days=179), now=now) == 75
    assert freshness_score(now - timedelta(days=364), now=now) == 60
    assert freshness_score(now - timedelta(days=365), now=now) == 40


def test_ai_reality_index_formula_matches_prd_weights():
    result = calculate_ai_reality_index(roi=80, revenue_growth=70, margin=60, adoption=50)
    assert result["score"] == 70
    assert result["label"] == "Strong"


def test_roi_calculator_returns_break_even_users():
    result = calculate_roi(
        users=2500,
        tokens_per_user=120000,
        provider="OpenAI",
        infrastructure_cost=15000,
        employees=8,
        subscription_price=49,
    )
    assert result["revenue"] == 122500
    assert result["break_even_users"] > 0
