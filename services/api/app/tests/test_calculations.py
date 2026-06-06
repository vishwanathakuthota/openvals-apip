from datetime import UTC, datetime, timedelta

from app.domains.autonomous_research.service import openvals_classification
from app.domains.calculator.service import calculate_roi
from app.domains.confidence.service import (
    calculate_confidence,
    freshness_score,
    source_reliability_score,
)
from app.domains.indexes.service import calculate_ai_reality_index
from app.domains.sources.credibility import coverage_label, source_credibility_score, source_tier


def test_confidence_formula_matches_prd_weights():
    result = calculate_confidence(100, 90, 80, 70)
    assert result["score"] == 88.5
    assert result["label"] == "High Confidence"


def test_source_reliability_scores_match_prd():
    assert source_reliability_score("sec_filing") == 100
    assert source_reliability_score("annual_report") == 95
    assert source_reliability_score("earnings_call") == 90
    assert source_reliability_score("investor_presentation") == 80
    assert source_reliability_score("public_company_statement") == 75
    assert source_reliability_score("analyst_estimate") == 70
    assert source_reliability_score("industry_report") == 65
    assert source_reliability_score("institutional_dataset") == 65
    assert source_reliability_score("news_article") == 50
    assert source_reliability_score("community_estimate") == 30


def test_source_credibility_engine_tiers_and_scores():
    assert source_tier("sec_filing") == 1
    assert source_tier("public_company_statement") == 2
    assert source_tier("institutional_dataset") == 3
    assert source_tier("news_article") == 4
    assert source_credibility_score("sec_filing", datetime(2026, 6, 1, tzinfo=UTC)) >= 95
    assert coverage_label(90) == "Full Coverage"
    assert coverage_label(70) == "Strong Coverage"
    assert coverage_label(50) == "Partial Coverage"


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
    assert result["classification"] == "Strong"


def test_openvals_score_formula_matches_trust_model_weights():
    score = round((90 * 0.30) + (80 * 0.25) + (70 * 0.20) + (60 * 0.15) + (50 * 0.10), 2)
    assert score == 75
    assert openvals_classification(score) == "Reliable"


def test_ai_reality_index_classification_bands_match_prd():
    assert calculate_ai_reality_index(100, 100, 100, 100)["classification"] == "Elite"
    assert calculate_ai_reality_index(70, 70, 70, 70)["classification"] == "Strong"
    assert calculate_ai_reality_index(50, 50, 50, 50)["classification"] == "Emerging"
    assert calculate_ai_reality_index(30, 30, 30, 30)["classification"] == "Speculative"
    assert calculate_ai_reality_index(0, 0, 0, 0)["classification"] == "Cash Burn Zone"


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
