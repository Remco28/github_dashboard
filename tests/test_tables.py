from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from ui import tables


def test_format_relative_date_handles_none():
    assert tables.format_relative_date(None) == "N/A"


def test_format_relative_date_just_now():
    now = datetime.now(timezone.utc)
    label = tables.format_relative_date(now)
    assert label == "Just now" or label.endswith("minutes ago")


def test_format_relative_date_hours_days_weeks_months_years():
    now = datetime.now(timezone.utc)
    assert "hours ago" in tables.format_relative_date(now - timedelta(hours=3))
    assert tables.format_relative_date(now - timedelta(days=1)) == "Yesterday"
    assert tables.format_relative_date(now - timedelta(days=5)) == "5 days ago"
    assert tables.format_relative_date(now - timedelta(days=21)) == "3 weeks ago"
    assert tables.format_relative_date(now - timedelta(days=150)).startswith("5 months ago")
    assert tables.format_relative_date(now - timedelta(days=400)).startswith("1 year ago")


def test_format_relative_date_marks_stale():
    now = datetime.now(timezone.utc)
    label = tables.format_relative_date(now - timedelta(days=200))
    assert "(stale)" in label


def test_format_relative_date_handles_strings():
    now = datetime.now(timezone.utc)
    iso_value = now.isoformat().replace("+00:00", "Z")
    label = tables.format_relative_date(iso_value)
    assert label == "Just now" or label.endswith("minutes ago")


def test_calculate_days_since_returns_none_for_invalid():
    assert tables.calculate_days_since(None) is None
    assert tables.calculate_days_since("not-a-date") is None


@pytest.mark.parametrize(
    "days",
    [0, 1, 5, 200],
)
def test_calculate_days_since_valid(days: int):
    base = datetime.now(timezone.utc) - timedelta(days=days)
    value = tables.calculate_days_since(base.isoformat().replace("+00:00", "Z"))
    expected = days if days > 0 else 0
    assert value == expected


def test_parse_iso_datetime_handles_various_formats():
    dt1 = tables._parse_iso_datetime("2025-01-01T12:00:00Z")
    dt2 = tables._parse_iso_datetime("2025-01-01")
    dt3 = tables._parse_iso_datetime("2025-01-01T12:00:00+02:00")

    assert dt1 is not None and dt1.tzinfo is not None
    assert dt2 is not None and dt2.tzinfo is not None
    assert dt3 is not None and dt3.tzinfo is not None


def test_format_relative_date_handles_nat():
    assert tables.format_relative_date(pd.NaT) == "N/A"
