from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date, datetime
from typing import Any
from urllib.request import Request, urlopen

from app.domains.ingestion.records import NormalizedLiveRecord, utc_now

SEC_BASE_URL = "https://data.sec.gov"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data"

SEC_FACT_MAP = {
    "revenue": ("us-gaap", "Revenues"),
    "operating_income": ("us-gaap", "OperatingIncomeLoss"),
    "cash_flow": ("us-gaap", "NetCashProvidedByUsedInOperatingActivities"),
    "capex": ("us-gaap", "PaymentsToAcquirePropertyPlantAndEquipment"),
    "eps": ("us-gaap", "EarningsPerShareDiluted"),
}


class YahooFinanceConnector:
    source_type = "yahoo_finance"

    def __init__(self, ticker_factory: Callable[[str], Any] | None = None):
        if ticker_factory is None:
            import yfinance as yf

            ticker_factory = yf.Ticker
        self.ticker_factory = ticker_factory

    def fetch(self, company_slug: str, symbol: str) -> list[NormalizedLiveRecord]:
        ticker = self.ticker_factory(symbol)
        retrieved_at = utc_now()
        info = _to_dict(getattr(ticker, "fast_info", None)) or _to_dict(getattr(ticker, "info", {}))
        records: list[NormalizedLiveRecord] = []

        for metric_type, key in {
            "market_cap": "market_cap",
            "stock_price": "last_price",
        }.items():
            value = _number(info.get(key) or info.get(_camel_case(key)))
            if value is not None:
                records.append(
                    _record(
                        company_slug=company_slug,
                        metric_type=metric_type,
                        value=value,
                        symbol=symbol,
                        source_url=f"https://finance.yahoo.com/quote/{symbol}",
                        source_type=self.source_type,
                        retrieved_at=retrieved_at,
                        raw_payload={"fast_info": info, "field": key},
                        confidence_score=82,
                    )
                )

        records.extend(
            _statement_records(
                company_slug=company_slug,
                symbol=symbol,
                source_url=f"https://finance.yahoo.com/quote/{symbol}/financials",
                source_type=self.source_type,
                retrieved_at=retrieved_at,
                table=_to_statement(getattr(ticker, "financials", None)),
                mappings={
                    "revenue": ["Total Revenue", "TotalRevenue"],
                    "operating_income": ["Operating Income", "OperatingIncome"],
                    "eps": ["Diluted EPS", "DilutedEPS"],
                },
            )
        )
        records.extend(
            _statement_records(
                company_slug=company_slug,
                symbol=symbol,
                source_url=f"https://finance.yahoo.com/quote/{symbol}/cash-flow",
                source_type=self.source_type,
                retrieved_at=retrieved_at,
                table=_to_statement(getattr(ticker, "cashflow", None)),
                mappings={
                    "cash_flow": [
                        "Operating Cash Flow",
                        "Total Cash From Operating Activities",
                    ],
                    "capex": ["Capital Expenditure", "CapitalExpenditure"],
                },
            )
        )
        return records


class SecEdgarConnector:
    source_type = "sec_edgar"

    def __init__(
        self,
        user_agent: str,
        fetch_json: Callable[[str, dict[str, str]], dict[str, Any]] | None = None,
    ):
        self.user_agent = user_agent
        self.fetch_json = fetch_json or self._fetch_json

    def fetch(self, company_slug: str, cik: str) -> list[NormalizedLiveRecord]:
        cik_padded = cik.zfill(10)
        headers = {"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"}
        retrieved_at = utc_now()
        facts_url = f"{SEC_BASE_URL}/api/xbrl/companyfacts/CIK{cik_padded}.json"
        submissions_url = f"{SEC_BASE_URL}/submissions/CIK{cik_padded}.json"
        facts = self.fetch_json(facts_url, headers)
        submissions = self.fetch_json(submissions_url, headers)

        records: list[NormalizedLiveRecord] = []
        for metric_type, (taxonomy, fact_name) in SEC_FACT_MAP.items():
            unit_payload = (
                facts.get("facts", {})
                .get(taxonomy, {})
                .get(fact_name, {})
                .get("units", {})
            )
            unit, item = _latest_sec_unit_item(unit_payload)
            if not item:
                continue
            records.append(
                _record(
                    company_slug=company_slug,
                    metric_type=metric_type,
                    value=_number(item.get("val")),
                    source_url=_sec_filing_url(cik, item),
                    source_type=self.source_type,
                    retrieved_at=retrieved_at,
                    raw_payload={"unit": unit, "fact": fact_name, "item": item},
                    confidence_score=96,
                    filing_accession=item.get("accn"),
                    filing_form=item.get("form"),
                    fiscal_year=_int(item.get("fy")),
                    fiscal_period=item.get("fp"),
                    period_end=_parse_date(item.get("end")),
                )
            )

        recent = submissions.get("filings", {}).get("recent", {})
        for index, accession in enumerate(recent.get("accessionNumber", [])[:10]):
            form = _list_value(recent, "form", index)
            if form not in {"10-K", "10-Q"}:
                continue
            records.append(
                _record(
                    company_slug=company_slug,
                    metric_type="sec_filing_metadata",
                    value=None,
                    source_url=_sec_archive_url(cik, accession),
                    source_type=self.source_type,
                    retrieved_at=retrieved_at,
                    raw_payload={
                        "accessionNumber": accession,
                        "form": form,
                        "filingDate": _list_value(recent, "filingDate", index),
                        "reportDate": _list_value(recent, "reportDate", index),
                    },
                    confidence_score=100,
                    filing_accession=accession,
                    filing_form=form,
                    period_end=_parse_date(_list_value(recent, "reportDate", index)),
                )
            )
        return records

    def _fetch_json(self, url: str, headers: dict[str, str]) -> dict[str, Any]:
        request = Request(url, headers=headers)
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))


def _record(
    *,
    company_slug: str,
    metric_type: str,
    value: float | None,
    source_url: str,
    source_type: str,
    retrieved_at: datetime,
    raw_payload: dict[str, Any],
    confidence_score: float,
    symbol: str | None = None,
    fiscal_year: int | None = None,
    fiscal_period: str | None = None,
    filing_accession: str | None = None,
    filing_form: str | None = None,
    period_end: date | None = None,
) -> NormalizedLiveRecord:
    return NormalizedLiveRecord(
        company_slug=company_slug,
        symbol=symbol,
        metric_type=metric_type,
        value=value,
        currency="USD",
        source_url=source_url,
        source_type=source_type,
        retrieved_at=retrieved_at,
        freshness_score=100,
        confidence_score=confidence_score,
        raw_payload=raw_payload,
        fiscal_year=fiscal_year,
        fiscal_period=fiscal_period,
        filing_accession=filing_accession,
        filing_form=filing_form,
        period_end=period_end,
    )


def _statement_records(
    *,
    company_slug: str,
    symbol: str,
    source_url: str,
    source_type: str,
    retrieved_at: datetime,
    table: dict[str, dict[str, Any]],
    mappings: dict[str, list[str]],
) -> list[NormalizedLiveRecord]:
    records: list[NormalizedLiveRecord] = []
    for metric_type, labels in mappings.items():
        row = next((table[label] for label in labels if label in table), None)
        if not row:
            continue
        period, value = next(iter(row.items()))
        records.append(
            _record(
                company_slug=company_slug,
                metric_type=metric_type,
                value=_number(value),
                symbol=symbol,
                source_url=source_url,
                source_type=source_type,
                retrieved_at=retrieved_at,
                raw_payload={"row": labels[0], "period": period, "value": value},
                confidence_score=80,
                period_end=_parse_date(period),
            )
        )
    return records


def _to_statement(value: Any) -> dict[str, dict[str, Any]]:
    if value is None:
        return {}
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return value
    return {}


def _to_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return value
    return {}


def _latest_sec_unit_item(
    unit_payload: dict[str, list[dict[str, Any]]],
) -> tuple[str | None, dict[str, Any] | None]:
    for preferred_unit in ("USD", "USD/shares", "shares"):
        items = unit_payload.get(preferred_unit)
        if items:
            return preferred_unit, _latest_sec_item(items)
    for unit, items in unit_payload.items():
        if items:
            return unit, _latest_sec_item(items)
    return None, None


def _latest_sec_item(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    filtered = [item for item in items if item.get("form") in {"10-K", "10-Q"}]
    candidates = filtered or items
    return max(candidates, key=lambda item: str(item.get("filed") or item.get("end") or ""))


def _sec_filing_url(cik: str, item: dict[str, Any]) -> str:
    accession = str(item.get("accn") or "").replace("-", "")
    if not accession:
        return f"{SEC_BASE_URL}/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
    return f"{SEC_ARCHIVES_URL}/{int(cik)}/{accession}/"


def _sec_archive_url(cik: str, accession: str) -> str:
    return f"{SEC_ARCHIVES_URL}/{int(cik)}/{accession.replace('-', '')}/"


def _list_value(payload: dict[str, list[Any]], key: str, index: int) -> Any:
    values = payload.get(key, [])
    if index >= len(values):
        return None
    return values[index]


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _camel_case(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])
