"""Unit tests for MOEX ISS data transformation (backend/collector/moex_client.py)."""

from datetime import date, timedelta

from backend.collector.moex_client import (
    _build_bond_dict,
    _calc_coupon_frequency,
    _calc_days_to_maturity,
    _classify_board,
    _is_qualified_only,
    _parse_date,
    _rows_to_dicts,
    _safe_float,
    _safe_int,
)


class TestHelpers:
    def test_parse_date_valid(self):
        assert _parse_date("2027-06-29") == date(2027, 6, 29)

    def test_parse_date_invalid(self):
        assert _parse_date("0000-00-00") is None
        assert _parse_date("") is None
        assert _parse_date(None) is None

    def test_safe_float(self):
        assert _safe_float("98.92") == 98.92
        assert _safe_float("") is None
        assert _safe_float(None) is None
        assert _safe_float("abc") is None

    def test_safe_int(self):
        assert _safe_int("182") == 182
        assert _safe_int("") is None
        assert _safe_int(None) is None

    def test_classify_board(self):
        assert _classify_board("TQOB") == "ofz"
        assert _classify_board("TQCB") == "corp"
        assert _classify_board("TQIR") == "muni"
        assert _classify_board("XXXX") == "other"

    def test_coupon_frequency(self):
        assert _calc_coupon_frequency(182) == 2
        assert _calc_coupon_frequency(91) == 4
        assert _calc_coupon_frequency(30) == 12
        assert _calc_coupon_frequency(0) is None
        assert _calc_coupon_frequency(None) is None

    def test_days_to_maturity(self):
        future = date.today() + timedelta(days=100)
        assert _calc_days_to_maturity(future) == 100
        past = date.today() - timedelta(days=5)
        assert _calc_days_to_maturity(past) == 0  # не отрицательное
        assert _calc_days_to_maturity(None) is None

    def test_qualified_only(self):
        assert _is_qualified_only(3) is True
        assert _is_qualified_only(1) is False
        assert _is_qualified_only(None) is None

    def test_rows_to_dicts(self):
        cols = ["SECID", "PREVPRICE"]
        rows = [["SU26238RMFS", 64.5], ["RU000A10A9Z1", 98.92]]
        result = _rows_to_dicts(cols, rows)
        assert result == [
            {"SECID": "SU26238RMFS", "PREVPRICE": 64.5},
            {"SECID": "RU000A10A9Z1", "PREVPRICE": 98.92},
        ]


class TestBuildBondDict:
    SEC = {
        "SECID": "RU000A10A9Z1",
        "ISIN": "RU000A10A9Z1",
        "SHORTNAME": "Магнит4P05",
        "SECNAME": "Магнит ПАО БО-004P-05",
        "BOARDID": "TQCB",
        "PREVPRICE": "98.92",
        "FACEVALUE": "1000",
        "ACCRUEDINT": "7.625",
        "LOTSIZE": "1",
        "COUPONPERCENT": "12.5",
        "COUPONVALUE": "38.01",
        "COUPONPERIOD": "182",
        "MATDATE": "2027-06-29",
        "OFFERDATE": None,
        "LISTLEVEL": "1",
    }
    MARKET = {"SECID": "RU000A10A9Z1", "YIELD": "16.85", "DURATION": "420.5", "VALTODAY": "15000000"}

    def test_full_merge(self):
        b = _build_bond_dict(self.SEC, self.MARKET)
        assert b["secid"] == "RU000A10A9Z1"
        assert b["security_type"] == "corp"
        assert b["prev_price"] == 98.92
        assert b["yield_at_prev_wa_price"] == 16.85
        assert b["coupon_frequency"] == 2
        assert b["mat_date"] == date(2027, 6, 29)
        assert b["qualified_only"] is False
        assert b["duration"] == 420.5

    def test_without_marketdata(self):
        b = _build_bond_dict(self.SEC, None)
        assert b["yield_at_prev_wa_price"] is None
        assert b["duration"] is None
        assert b["volume_today"] is None
        # Данные из securities не теряются
        assert b["coupon_percent"] == 12.5
