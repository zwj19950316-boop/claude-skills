"""
Google Trends integration module using pytrends.

Provides:
- get_trends_data(keywords, timeframe, geo) -> dict
- test_fetch() -> prints sample results
"""

import time
import logging
from typing import List, Dict, Any

import pandas as pd
from pytrends.request import TrendReq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _build_pytrends_client() -> TrendReq:
    """Initialize a pytrends TrendReq client."""
    # hl=en-US, tz=360 (US timezone offset in minutes)
    return TrendReq(hl="en-US", tz=360, retries=2, backoff_factor=0.5)


def _handle_rate_limit(func):
    """Decorator-like helper to retry on 429 / TooManyRequests."""
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                # pytrends raises generic Exception with "429" text on rate-limit
                err_msg = str(exc)
                if "429" in err_msg or "Too many requests" in err_msg:
                    wait = 2 ** attempt
                    logger.warning(
                        "Rate limit hit (attempt %s/%s). Sleeping %ss ...",
                        attempt,
                        max_retries,
                        wait,
                    )
                    time.sleep(wait)
                else:
                    raise
        raise RuntimeError("Max retries exceeded for Google Trends request.")

    return wrapper


@_handle_rate_limit
def _fetch_interest_over_time(
    client: TrendReq, keywords: List[str], timeframe: str, geo: str
) -> pd.DataFrame:
    """Fetch interest-over-time DataFrame."""
    client.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
    return client.interest_over_time()


@_handle_rate_limit
def _fetch_related_queries(
    client: TrendReq, keywords: List[str], timeframe: str, geo: str
) -> Dict[str, Any]:
    """Fetch related queries dict."""
    client.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
    return client.related_queries()


@_handle_rate_limit
def _fetch_interest_by_region(
    client: TrendReq, keywords: List[str], timeframe: str, geo: str
) -> pd.DataFrame:
    """Fetch interest-by-region DataFrame."""
    client.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
    return client.interest_by_region()


def get_trends_data(
    keywords: List[str],
    timeframe: str = "now 7-d",
    geo: str = "US",
) -> Dict[str, Any]:
    """
    Retrieve Google Trends data for a list of keywords.

    Parameters
    ----------
    keywords : List[str]
        Up to 5 keywords (Google Trends limit per payload).
    timeframe : str, optional
        e.g. 'now 7-d', 'today 1-m', 'today 12-m', 'today 5-y'.
    geo : str, optional
        ISO country code, e.g. 'US', 'GB', '' for worldwide.

    Returns
    -------
    dict
        {
            "interest_over_time": {keyword: {date: score, ...}, ...},
            "related_queries":    {keyword: {"top": [...], "rising": [...]}},
            "interest_by_region": {keyword: {region: score, ...}, ...},
        }
    """
    if not keywords:
        raise ValueError("keywords list must not be empty.")

    client = _build_pytrends_client()

    # 1) Interest over time
    iot_df = _fetch_interest_over_time(client, keywords, timeframe, geo)
    interest_over_time: Dict[str, Dict[str, int]] = {}
    if iot_df is not None and not iot_df.empty:
        # Drop 'isPartial' column if present
        if "isPartial" in iot_df.columns:
            iot_df = iot_df.drop(columns=["isPartial"])
        for keyword in keywords:
            if keyword in iot_df.columns:
                series = iot_df[keyword].dropna()
                interest_over_time[keyword] = {
                    str(date): int(score) for date, score in series.items()
                }

    # 2) Related queries
    related_raw = _fetch_related_queries(client, keywords, timeframe, geo)
    related_queries: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    if related_raw:
        for keyword in keywords:
            entry = related_raw.get(keyword, {})
            top_df = entry.get("top")
            rising_df = entry.get("rising")
            related_queries[keyword] = {
                "top": (
                    top_df.to_dict("records")
                    if top_df is not None and not top_df.empty
                    else []
                ),
                "rising": (
                    rising_df.to_dict("records")
                    if rising_df is not None and not rising_df.empty
                    else []
                ),
            }

    # 3) Interest by region
    ibr_df = _fetch_interest_by_region(client, keywords, timeframe, geo)
    interest_by_region: Dict[str, Dict[str, int]] = {}
    if ibr_df is not None and not ibr_df.empty:
        for keyword in keywords:
            if keyword in ibr_df.columns:
                series = ibr_df[keyword].dropna()
                interest_by_region[keyword] = {
                    str(region): int(score) for region, score in series.items()
                }

    return {
        "interest_over_time": interest_over_time,
        "related_queries": related_queries,
        "interest_by_region": interest_by_region,
    }


def test_fetch() -> None:
    """Run a sample fetch with test keywords and print results."""
    test_keywords = ["Windows 11 update", "data recovery", "partition manager"]
    logger.info("Fetching trends for: %s", test_keywords)
    result = get_trends_data(test_keywords, timeframe="now 7-d", geo="US")

    print("\n=== Interest Over Time ===")
    for kw, data in result["interest_over_time"].items():
        print(f"\n{kw}: {len(data)} data points")
        # Print first/last few entries for brevity
        items = list(data.items())
        for date, score in items[:3]:
            print(f"  {date}: {score}")
        if len(items) > 6:
            print("  ...")
        for date, score in items[-3:]:
            print(f"  {date}: {score}")

    print("\n=== Related Queries (Top) ===")
    for kw, data in result["related_queries"].items():
        top = data.get("top", [])
        print(f"\n{kw}: {len(top)} top queries")
        for item in top[:5]:
            print(f"  {item.get('query', 'N/A')} -> {item.get('value', 'N/A')}")

    print("\n=== Interest By Region (sample) ===")
    for kw, data in result["interest_by_region"].items():
        print(f"\n{kw}: {len(data)} regions")
        # Print top 5 regions by score
        sorted_regions = sorted(data.items(), key=lambda x: x[1], reverse=True)[:5]
        for region, score in sorted_regions:
            print(f"  {region}: {score}")


if __name__ == "__main__":
    test_fetch()
