from app.domains.calculator.service import calculate_roi
from app.domains.confidence.service import calculate_confidence
from app.domains.indexes.service import calculate_ai_reality_index


def test_confidence_formula_matches_prd_weights():
    result = calculate_confidence(100, 90, 80, 70)
    assert result["score"] == 88.5
    assert result["label"] == "High Confidence"


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
