"""Unit tests for backend.collector.issuer_client (парсеры описания бумаги MOEX)."""

from backend.collector.issuer_client import (
    derive_issuer_name,
    extract_issuer_fields,
    parse_description,
)


class TestParseDescription:
    def test_parses_name_value_pairs(self):
        payload = {
            "description": {
                "columns": ["name", "value"],
                "data": [["SECID", "RU000A0TEST"], ["INN", "7707083893"], ["OKPO", "00032537"]],
            }
        }
        assert parse_description(payload) == {
            "SECID": "RU000A0TEST",
            "INN": "7707083893",
            "OKPO": "00032537",
        }

    def test_empty_or_malformed_payload(self):
        assert parse_description({}) == {}
        assert parse_description({"description": {"columns": ["x"], "data": []}}) == {}

    def test_skips_null_values(self):
        payload = {"description": {"columns": ["name", "value"], "data": [["INN", None]]}}
        assert parse_description(payload) == {}


class TestExtractIssuerFields:
    def test_valid_inn_10_digits(self):
        fields = extract_issuer_fields({"INN": "7707083893", "OKPO": "00032537"})
        assert fields == {"inn": "7707083893", "okpo": "00032537", "ogrn": None}

    def test_valid_inn_12_digits(self):
        assert extract_issuer_fields({"INN": "770708389312"})["inn"] == "770708389312"

    def test_missing_or_garbage_inn(self):
        assert extract_issuer_fields({}) is None
        assert extract_issuer_fields({"INN": ""}) is None
        assert extract_issuer_fields({"INN": "нет данных"}) is None
        assert extract_issuer_fields({"INN": "123"}) is None  # неверная длина

    def test_empty_okpo_becomes_none(self):
        assert extract_issuer_fields({"INN": "7707083893", "OKPO": " "})["okpo"] is None


class TestDeriveIssuerName:
    def test_strips_series_tails(self):
        assert derive_issuer_name("Сегежа Групп ПАО БО-002P 01R", None) == "Сегежа Групп ПАО"
        assert derive_issuer_name("ГК Самолет выпуск 12", None) == "ГК Самолет"
        assert derive_issuer_name("Тест ПАО обл. серии 3", None) == "Тест ПАО"

    def test_falls_back_to_short_name(self):
        assert derive_issuer_name(None, "Короткое имя") == "Короткое имя"

    def test_none_when_nothing(self):
        assert derive_issuer_name(None, None) is None

    def test_no_tail_keeps_name(self):
        assert derive_issuer_name("Просто Эмитент ООО", None) == "Просто Эмитент ООО"
