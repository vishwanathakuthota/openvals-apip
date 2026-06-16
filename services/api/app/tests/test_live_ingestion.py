from app.domains.ingestion.connectors import SecEdgarConnector, YahooFinanceConnector
from app.workers.celery_app import celery_app


class FakeTicker:
    fast_info = {"market_cap": 3_100_000_000_000, "last_price": 425.25}
    financials = {
        "Total Revenue": {"2025-06-30": 245_000_000_000},
        "Operating Income": {"2025-06-30": 109_000_000_000},
        "Diluted EPS": {"2025-06-30": 11.8},
    }
    cashflow = {
        "Operating Cash Flow": {"2025-06-30": 118_000_000_000},
        "Capital Expenditure": {"2025-06-30": -44_000_000_000},
    }


def test_yahoo_connector_returns_normalized_records_from_mocked_response():
    connector = YahooFinanceConnector(ticker_factory=lambda _symbol: FakeTicker())

    records = connector.fetch("microsoft", "MSFT")

    metrics = {record.metric_type: record for record in records}
    assert metrics["market_cap"].value == 3_100_000_000_000
    assert metrics["stock_price"].value == 425.25
    assert metrics["revenue"].source_type == "yahoo_finance"
    assert metrics["capex"].source_url.endswith("/cash-flow")
    assert metrics["market_cap"].raw_payload_hash


def test_sec_connector_returns_normalized_records_from_mocked_response():
    def fake_fetch_json(url: str, _headers: dict[str, str]):
        if "companyfacts" in url:
            return {
                "facts": {
                    "us-gaap": {
                        "Revenues": {
                            "units": {
                                "USD": [
                                    {
                                        "val": 245_000_000_000,
                                        "fy": 2025,
                                        "fp": "FY",
                                        "form": "10-K",
                                        "filed": "2025-07-30",
                                        "end": "2025-06-30",
                                        "accn": "0000789019-25-000123",
                                    }
                                ]
                            }
                        },
                        "OperatingIncomeLoss": {
                            "units": {
                                "USD": [
                                    {
                                        "val": 109_000_000_000,
                                        "fy": 2025,
                                        "fp": "FY",
                                        "form": "10-K",
                                        "filed": "2025-07-30",
                                        "end": "2025-06-30",
                                        "accn": "0000789019-25-000123",
                                    }
                                ]
                            }
                        },
                    }
                }
            }
        return {
            "filings": {
                "recent": {
                    "accessionNumber": ["0000789019-25-000123"],
                    "form": ["10-K"],
                    "filingDate": ["2025-07-30"],
                    "reportDate": ["2025-06-30"],
                }
            }
        }

    connector = SecEdgarConnector(
        user_agent="OpenVals APIP tests admin@openvalidations.com",
        fetch_json=fake_fetch_json,
    )

    records = connector.fetch("microsoft", "789019")

    metrics = {record.metric_type: record for record in records}
    assert metrics["revenue"].value == 245_000_000_000
    assert metrics["operating_income"].source_type == "sec_edgar"
    assert metrics["sec_filing_metadata"].filing_form == "10-K"
    assert metrics["revenue"].filing_accession == "0000789019-25-000123"
    assert metrics["revenue"].raw_payload_hash


def test_scheduler_config_runs_live_ingestion_every_30_minutes():
    schedule = celery_app.conf.beat_schedule["live-data-ingestion-every-30-minutes"]

    assert schedule["task"] == "apip.ingest_live_data"
    assert schedule["schedule"] == 30 * 60
