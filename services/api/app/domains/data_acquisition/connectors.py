import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Protocol
from urllib.request import Request, urlopen

from app.domains.data_acquisition.registry import AcquisitionTarget


class HttpClient(Protocol):
    def get_json(self, url: str, headers: dict[str, str] | None = None) -> dict[str, object]:
        ...

    def get_text(self, url: str, headers: dict[str, str] | None = None) -> str:
        ...


class UrlLibHttpClient:
    def get_json(self, url: str, headers: dict[str, str] | None = None) -> dict[str, object]:
        request = Request(url, headers=headers or {})
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_text(self, url: str, headers: dict[str, str] | None = None) -> str:
        request = Request(url, headers=headers or {})
        with urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8", errors="ignore")


@dataclass(frozen=True)
class AcquiredMetric:
    company_slug: str
    metric_key: str
    value: Decimal
    unit: str
    currency: str | None
    period_start: date
    period_end: date
    source_name: str
    source_type: str
    source_url: str
    publisher: str
    published_at: datetime | None
    retrieved_at: datetime
    methodology_note: str
    raw_payload: dict[str, object]


@dataclass(frozen=True)
class ConnectorResult:
    connector: str
    source_name: str
    target: AcquisitionTarget
    retrieved_at: datetime
    metrics: list[AcquiredMetric]
    source_url: str
    raw_payload: dict[str, object]


class YahooFinanceConnector:
    name = "yahoo_finance"
    source_name = "Yahoo Finance"
    source_type = "market_data"

    def __init__(self, http_client: HttpClient | None = None) -> None:
        self.http_client = http_client or UrlLibHttpClient()

    def collect(self, target: AcquisitionTarget, now: datetime | None = None) -> ConnectorResult:
        retrieved_at = now or datetime.now(UTC)
        url = (
            "https://query1.finance.yahoo.com/v10/finance/quoteSummary/"
            f"{target.ticker}?modules=price,financialData,defaultKeyStatistics"
        )
        payload = self.http_client.get_json(url)
        result = extract_quote_summary_result(payload)
        metrics = [
            metric
            for metric in [
                self._metric(
                    target,
                    "market_cap",
                    raw_number(result, "price", "marketCap"),
                    url,
                    retrieved_at,
                    result,
                ),
                self._metric(
                    target,
                    "revenue",
                    raw_number(result, "financialData", "totalRevenue"),
                    url,
                    retrieved_at,
                    result,
                ),
                self._metric(
                    target,
                    "cash_flow",
                    raw_number(result, "financialData", "operatingCashflow"),
                    url,
                    retrieved_at,
                    result,
                ),
            ]
            if metric is not None
        ]
        return ConnectorResult(
            connector=self.name,
            source_name=self.source_name,
            target=target,
            retrieved_at=retrieved_at,
            metrics=metrics,
            source_url=url,
            raw_payload={"ticker": target.ticker},
        )

    def _metric(
        self,
        target: AcquisitionTarget,
        metric_key: str,
        value: Decimal | None,
        source_url: str,
        retrieved_at: datetime,
        raw_payload: dict[str, object],
    ) -> AcquiredMetric | None:
        if value is None:
            return None
        return AcquiredMetric(
            company_slug=target.slug,
            metric_key=metric_key,
            value=value,
            unit="usd",
            currency="USD",
            period_start=retrieved_at.date(),
            period_end=retrieved_at.date(),
            source_name=f"Yahoo Finance {target.ticker} quote summary",
            source_type=self.source_type,
            source_url=source_url,
            publisher="Yahoo Finance",
            published_at=retrieved_at,
            retrieved_at=retrieved_at,
            methodology_note=(
                f"{metric_key} collected from Yahoo Finance quote summary for {target.ticker}; "
                "used for market and trailing financial dashboard refresh."
            ),
            raw_payload={"module": raw_payload},
        )


class SecEdgarConnector:
    name = "sec_edgar"
    source_name = "SEC EDGAR"
    source_type = "sec_filing"
    user_agent = "OpenVals APIP beta data acquisition contact@openvalidations.com"

    metric_tags = {
        "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
        "operating_income": ["OperatingIncomeLoss"],
        "cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
        "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
        "eps": ["EarningsPerShareDiluted"],
    }

    def __init__(self, http_client: HttpClient | None = None) -> None:
        self.http_client = http_client or UrlLibHttpClient()

    def collect(self, target: AcquisitionTarget, now: datetime | None = None) -> ConnectorResult:
        retrieved_at = now or datetime.now(UTC)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{target.cik}.json"
        payload = self.http_client.get_json(url, headers={"User-Agent": self.user_agent})
        metrics: list[AcquiredMetric] = []
        for metric_key, tags in self.metric_tags.items():
            fact = latest_fact(payload, tags)
            if not fact:
                continue
            end_date = date.fromisoformat(str(fact["end"]))
            start_date = date(end_date.year, 1, 1)
            metrics.append(
                AcquiredMetric(
                    company_slug=target.slug,
                    metric_key=metric_key,
                    value=Decimal(str(fact["val"])),
                    unit="usd_per_share" if metric_key == "eps" else "usd",
                    currency="USD",
                    period_start=start_date,
                    period_end=end_date,
                    source_name=f"SEC EDGAR company facts for {target.name}",
                    source_type=self.source_type,
                    source_url=url,
                    publisher="SEC EDGAR",
                    published_at=end_date_to_datetime(end_date),
                    retrieved_at=retrieved_at,
                    methodology_note=(
                        f"{metric_key} collected from SEC EDGAR company facts for "
                        f"CIK {target.cik}; "
                        "latest annual USD fact is selected for dashboard refresh."
                    ),
                    raw_payload={
                        "tag": fact["tag"],
                        "fy": fact.get("fy"),
                        "form": fact.get("form"),
                    },
                )
            )
        return ConnectorResult(
            connector=self.name,
            source_name=self.source_name,
            target=target,
            retrieved_at=retrieved_at,
            metrics=metrics,
            source_url=url,
            raw_payload={"cik": target.cik},
        )


class InvestorRelationsConnector:
    name = "investor_relations"
    source_name = "Company Investor Relations"
    source_type = "investor_relations"

    def __init__(self, http_client: HttpClient | None = None) -> None:
        self.http_client = http_client or UrlLibHttpClient()

    def collect(self, target: AcquisitionTarget, now: datetime | None = None) -> ConnectorResult:
        retrieved_at = now or datetime.now(UTC)
        html = self.http_client.get_text(target.investor_relations_url)
        return ConnectorResult(
            connector=self.name,
            source_name=self.source_name,
            target=target,
            retrieved_at=retrieved_at,
            metrics=[],
            source_url=target.investor_relations_url,
            raw_payload={"content_length": len(html), "title": extract_title(html)},
        )


def extract_quote_summary_result(payload: dict[str, object]) -> dict[str, object]:
    summary = payload.get("quoteSummary")
    if not isinstance(summary, dict):
        return {}
    results = summary.get("result")
    if not isinstance(results, list) or not results:
        return {}
    first = results[0]
    return first if isinstance(first, dict) else {}


def raw_number(payload: dict[str, object], module: str, key: str) -> Decimal | None:
    module_payload = payload.get(module)
    if not isinstance(module_payload, dict):
        return None
    value = module_payload.get(key)
    if isinstance(value, dict) and "raw" in value:
        return Decimal(str(value["raw"]))
    if isinstance(value, int | float | str):
        return Decimal(str(value))
    return None


def latest_fact(payload: dict[str, object], tags: list[str]) -> dict[str, object] | None:
    facts = payload.get("facts")
    if not isinstance(facts, dict):
        return None
    us_gaap = facts.get("us-gaap")
    if not isinstance(us_gaap, dict):
        return None
    candidates: list[dict[str, object]] = []
    for tag in tags:
        tag_payload = us_gaap.get(tag)
        if not isinstance(tag_payload, dict):
            continue
        units = tag_payload.get("units")
        if not isinstance(units, dict):
            continue
        unit_key = "USD/shares" if tag == "EarningsPerShareDiluted" else "USD"
        facts_for_unit = units.get(unit_key)
        if not isinstance(facts_for_unit, list):
            continue
        for fact in facts_for_unit:
            if isinstance(fact, dict) and fact.get("form") in {"10-K", "10-Q"} and "val" in fact:
                candidates.append({**fact, "tag": tag})
    if not candidates:
        return None
    return max(candidates, key=lambda item: str(item.get("end", "")))


def end_date_to_datetime(value: date) -> datetime:
    return datetime(value.year, value.month, value.day, tzinfo=UTC)


def extract_title(html: str) -> str | None:
    lower = html.lower()
    start = lower.find("<title>")
    end = lower.find("</title>")
    if start == -1 or end == -1 or end <= start:
        return None
    return html[start + len("<title>") : end].strip()
