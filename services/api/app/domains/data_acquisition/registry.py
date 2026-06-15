from dataclasses import dataclass


@dataclass(frozen=True)
class AcquisitionTarget:
    slug: str
    name: str
    ticker: str
    cik: str
    investor_relations_url: str


ACQUISITION_TARGETS = [
    AcquisitionTarget(
        slug="microsoft",
        name="Microsoft",
        ticker="MSFT",
        cik="0000789019",
        investor_relations_url="https://www.microsoft.com/en-us/Investor",
    ),
    AcquisitionTarget(
        slug="nvidia",
        name="NVIDIA",
        ticker="NVDA",
        cik="0001045810",
        investor_relations_url="https://investor.nvidia.com/",
    ),
    AcquisitionTarget(
        slug="alphabet",
        name="Alphabet",
        ticker="GOOGL",
        cik="0001652044",
        investor_relations_url="https://abc.xyz/investor/",
    ),
]

METRIC_REGISTRY = {
    "revenue": {"name": "Revenue", "unit": "usd", "higher_is_better": 1},
    "market_cap": {"name": "Market Cap", "unit": "usd", "higher_is_better": 1},
    "operating_income": {"name": "Operating Income", "unit": "usd", "higher_is_better": 1},
    "cash_flow": {"name": "Operating Cash Flow", "unit": "usd", "higher_is_better": 1},
    "capex": {"name": "Capital Expenditure", "unit": "usd", "higher_is_better": 0},
    "eps": {"name": "Diluted EPS", "unit": "usd_per_share", "higher_is_better": 1},
}

SOURCE_REGISTRY = [
    {
        "key": "yahoo_finance",
        "name": "Yahoo Finance",
        "source_type": "market_data",
        "priority": 1,
        "metrics": ["market_cap", "revenue", "cash_flow"],
    },
    {
        "key": "sec_edgar",
        "name": "SEC EDGAR",
        "source_type": "sec_filing",
        "priority": 1,
        "metrics": ["revenue", "operating_income", "cash_flow", "capex", "eps"],
    },
    {
        "key": "investor_relations",
        "name": "Company Investor Relations",
        "source_type": "investor_relations",
        "priority": 2,
        "metrics": [],
    },
]
