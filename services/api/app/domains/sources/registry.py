from dataclasses import dataclass
from datetime import UTC, datetime

from app.domains.confidence.service import source_reliability_score
from app.domains.sources.credibility import source_credibility_score, source_tier


@dataclass(frozen=True)
class RegistrySource:
    key: str
    company_slug: str | None
    title: str
    source_type: str
    url: str
    publisher: str
    published_at: datetime

    @property
    def reliability_score(self) -> int:
        return source_reliability_score(self.source_type)

    @property
    def credibility_score(self) -> int:
        return source_credibility_score(self.source_type, self.published_at)

    @property
    def tier(self) -> int:
        return source_tier(self.source_type)


BETA_COMPANIES = [
    ("microsoft", "Microsoft", "MSFT", "https://www.microsoft.com"),
    ("google", "Google", "GOOGL", "https://google.com"),
    ("meta", "Meta", "META", "https://about.meta.com"),
    ("amazon", "Amazon", "AMZN", "https://amazon.com"),
    ("nvidia", "NVIDIA", "NVDA", "https://nvidia.com"),
    ("openai", "OpenAI", None, "https://openai.com"),
    ("anthropic", "Anthropic", None, "https://anthropic.com"),
    ("xai", "xAI", None, "https://x.ai"),
    ("mistral", "Mistral", None, "https://mistral.ai"),
    ("perplexity", "Perplexity", None, "https://www.perplexity.ai"),
]


SOURCE_REGISTRY = [
    RegistrySource(
        key="microsoft-sec",
        company_slug="microsoft",
        title="Microsoft SEC company filing registry",
        source_type="sec_filing",
        url="https://www.sec.gov/edgar/browse/?CIK=789019",
        publisher="SEC EDGAR",
        published_at=datetime(2026, 5, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="microsoft-ar25",
        company_slug="microsoft",
        title="Microsoft 2025 Annual Report",
        source_type="annual_report",
        url="https://www.microsoft.com/investor/reports/ar25/",
        publisher="Microsoft Investor Relations",
        published_at=datetime(2025, 7, 30, tzinfo=UTC),
    ),
    RegistrySource(
        key="alphabet-sec",
        company_slug="google",
        title="Alphabet SEC company filing registry",
        source_type="sec_filing",
        url="https://www.sec.gov/edgar/browse/?CIK=1652044",
        publisher="SEC EDGAR",
        published_at=datetime(2026, 2, 5, tzinfo=UTC),
    ),
    RegistrySource(
        key="alphabet-ir",
        company_slug="google",
        title="Alphabet investor relations filing archive",
        source_type="annual_report",
        url="https://abc.xyz/investor/",
        publisher="Alphabet Investor Relations",
        published_at=datetime(2026, 2, 5, tzinfo=UTC),
    ),
    RegistrySource(
        key="meta-sec",
        company_slug="meta",
        title="Meta SEC company filing registry",
        source_type="sec_filing",
        url="https://www.sec.gov/edgar/browse/?CIK=1326801",
        publisher="SEC EDGAR",
        published_at=datetime(2026, 2, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="meta-ir",
        company_slug="meta",
        title="Meta investor relations filing archive",
        source_type="annual_report",
        url="https://investor.atmeta.com/financials/",
        publisher="Meta Investor Relations",
        published_at=datetime(2026, 2, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="amazon-sec",
        company_slug="amazon",
        title="Amazon SEC company filing registry",
        source_type="sec_filing",
        url="https://www.sec.gov/edgar/browse/?CIK=1018724",
        publisher="SEC EDGAR",
        published_at=datetime(2026, 2, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="amazon-ir",
        company_slug="amazon",
        title="Amazon investor relations SEC filings",
        source_type="annual_report",
        url="https://ir.aboutamazon.com/sec-filings/default.aspx",
        publisher="Amazon Investor Relations",
        published_at=datetime(2026, 2, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="nvidia-sec",
        company_slug="nvidia",
        title="NVIDIA SEC company filing registry",
        source_type="sec_filing",
        url="https://www.sec.gov/edgar/browse/?CIK=1045810",
        publisher="SEC EDGAR",
        published_at=datetime(2025, 2, 26, tzinfo=UTC),
    ),
    RegistrySource(
        key="nvidia-fy2025",
        company_slug="nvidia",
        title="NVIDIA FY2025 Annual Report",
        source_type="annual_report",
        url="https://s201.q4cdn.com/141608511/files/doc_financials/2025/annual/NVIDIA-2025-Annual-Report.pdf",
        publisher="NVIDIA Investor Relations",
        published_at=datetime(2025, 2, 26, tzinfo=UTC),
    ),
    RegistrySource(
        key="openai-business",
        company_slug="openai",
        title="OpenAI business product statement",
        source_type="public_company_statement",
        url="https://openai.com/business/",
        publisher="OpenAI",
        published_at=datetime(2026, 5, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="anthropic-enterprise",
        company_slug="anthropic",
        title="Anthropic enterprise product statement",
        source_type="public_company_statement",
        url="https://www.anthropic.com/enterprise",
        publisher="Anthropic",
        published_at=datetime(2026, 5, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="xai-news",
        company_slug="xai",
        title="xAI company announcements",
        source_type="public_company_statement",
        url="https://x.ai/news",
        publisher="xAI",
        published_at=datetime(2026, 5, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="mistral-news",
        company_slug="mistral",
        title="Mistral AI company announcements",
        source_type="public_company_statement",
        url="https://mistral.ai/news",
        publisher="Mistral AI",
        published_at=datetime(2026, 5, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="perplexity-hub",
        company_slug="perplexity",
        title="Perplexity company announcements",
        source_type="public_company_statement",
        url="https://www.perplexity.ai/hub",
        publisher="Perplexity",
        published_at=datetime(2026, 5, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="stanford-ai-index",
        company_slug=None,
        title="Stanford AI Index Report",
        source_type="industry_report",
        url="https://aiindex.stanford.edu/report/",
        publisher="Stanford HAI",
        published_at=datetime(2025, 4, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="oecd-ai-observatory",
        company_slug=None,
        title="OECD AI Observatory",
        source_type="institutional_dataset",
        url="https://oecd.ai/en/",
        publisher="OECD",
        published_at=datetime(2026, 1, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="imf-ai-topic",
        company_slug=None,
        title="IMF artificial intelligence topic hub",
        source_type="institutional_dataset",
        url="https://www.imf.org/en/Topics/artificial-intelligence",
        publisher="International Monetary Fund",
        published_at=datetime(2026, 1, 1, tzinfo=UTC),
    ),
    RegistrySource(
        key="world-bank-digital",
        company_slug=None,
        title="World Bank digital development data hub",
        source_type="institutional_dataset",
        url="https://www.worldbank.org/en/topic/digitaldevelopment",
        publisher="World Bank",
        published_at=datetime(2026, 1, 1, tzinfo=UTC),
    ),
]
