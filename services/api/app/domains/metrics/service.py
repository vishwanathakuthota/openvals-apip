from app.domains.confidence.service import calculate_confidence
from app.domains.indexes.service import calculate_ai_reality_index

METRIC_DEFINITIONS = [
    {"key": "ai_spend", "name": "AI Spend", "unit": "usd"},
    {"key": "ai_revenue", "name": "AI Revenue", "unit": "usd"},
    {"key": "net_profit", "name": "Net Profit", "unit": "usd"},
    {"key": "roi", "name": "ROI", "unit": "ratio"},
    {"key": "ai_reality_index", "name": "AI Reality Index", "unit": "score"},
]

DEFAULT_CONFIDENCE = {
    **calculate_confidence(90, 75, 80, 70),
    "source_count": 3,
    "last_updated": "2026-06-04T09:00:00Z",
}

METRIC_VALUES = [
    {
        "id": "metric_openai_revenue_2026",
        "entity_type": "company",
        "entity_id": "company_openai",
        "metric_key": "ai_revenue",
        "value": 12_500_000_000,
        "unit": "usd",
        "period_start": "2026-01-01",
        "period_end": "2026-12-31",
        "confidence": DEFAULT_CONFIDENCE,
    },
    {
        "id": "metric_openai_spend_2026",
        "entity_type": "company",
        "entity_id": "company_openai",
        "metric_key": "ai_spend",
        "value": 16_000_000_000,
        "unit": "usd",
        "period_start": "2026-01-01",
        "period_end": "2026-12-31",
        "confidence": DEFAULT_CONFIDENCE,
    },
    {
        "id": "metric_us_revenue_2026",
        "entity_type": "country",
        "entity_id": "country_us",
        "metric_key": "ai_revenue",
        "value": 165_000_000_000,
        "unit": "usd",
        "period_start": "2026-01-01",
        "period_end": "2026-12-31",
        "confidence": DEFAULT_CONFIDENCE,
    },
    {
        "id": "metric_healthcare_roi_2026",
        "entity_type": "industry",
        "entity_id": "industry_healthcare",
        "metric_key": "roi",
        "value": 1.18,
        "unit": "ratio",
        "period_start": "2026-01-01",
        "period_end": "2026-12-31",
        "confidence": DEFAULT_CONFIDENCE,
    },
    {
        "id": "metric_gpt_margin_2026",
        "entity_type": "model",
        "entity_id": "model_gpt",
        "metric_key": "gross_margin",
        "value": 0.61,
        "unit": "ratio",
        "period_start": "2026-01-01",
        "period_end": "2026-12-31",
        "confidence": DEFAULT_CONFIDENCE,
    },
]


def entity_metrics(entity_type: str, entity_id: str) -> list[dict[str, object]]:
    return [
        metric
        for metric in METRIC_VALUES
        if metric["entity_type"] == entity_type and metric["entity_id"] == entity_id
    ]


def search_metrics(
    entity_type: str | None = None,
    entity_id: str | None = None,
    metric_key: str | None = None,
    confidence_min: float | None = None,
) -> list[dict[str, object]]:
    results = METRIC_VALUES
    if entity_type:
        results = [item for item in results if item["entity_type"] == entity_type]
    if entity_id:
        results = [item for item in results if item["entity_id"] == entity_id]
    if metric_key:
        results = [item for item in results if item["metric_key"] == metric_key]
    if confidence_min is not None:
        results = [item for item in results if item["confidence"]["score"] >= confidence_min]
    return results


def get_scoreboard() -> dict[str, object]:
    total_ai_spend = 420_000_000_000
    total_ai_revenue = 310_000_000_000
    net_profit = total_ai_revenue - total_ai_spend
    global_roi = total_ai_revenue / total_ai_spend
    reality = calculate_ai_reality_index(roi=73.81, revenue_growth=68, margin=45, adoption=61)
    return {
        "total_ai_spend": total_ai_spend,
        "total_ai_revenue": total_ai_revenue,
        "net_profit": net_profit,
        "global_roi": round(global_roi, 4),
        "profitability_gauge": "PARTIALLY",
        "companies_tracked": 50,
        "industries_tracked": 10,
        "countries_tracked": 10,
        "confidence": DEFAULT_CONFIDENCE,
        "top_ai_reality_index": [
            {"entity_type": "company", "entity_id": "company_nvidia", **reality},
            {"entity_type": "industry", "entity_id": "industry_cybersecurity", **reality},
            {"entity_type": "country", "entity_id": "country_us", **reality},
            {"entity_type": "model", "entity_id": "model_gpt", **reality},
        ],
    }
