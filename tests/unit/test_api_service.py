"""Unit tests for the bonds service query builder (backend/api/service.py).

Проверяем формирование SQL без подключения к БД — компилируем
запросы в текст и смотрим на WHERE / ORDER BY.
"""

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from backend.api.schemas import BondFilterParams
from backend.api.service import _apply_filters, _apply_sorting
from backend.db.models.bond import Bond


def compile_sql(params: BondFilterParams) -> str:
    query = _apply_sorting(_apply_filters(select(Bond), params), params)
    return str(query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


class TestFilters:
    def test_no_filters(self):
        sql = compile_sql(BondFilterParams())
        assert "WHERE" not in sql

    def test_yield_range(self):
        sql = compile_sql(BondFilterParams(yield_min=10, yield_max=20))
        assert "yield_at_prev_wa_price >= 10" in sql
        assert "yield_at_prev_wa_price <= 20" in sql

    def test_single_security_type(self):
        sql = compile_sql(BondFilterParams(security_type="ofz"))
        assert "security_type = 'ofz'" in sql

    def test_multi_security_type_csv(self):
        sql = compile_sql(BondFilterParams(security_type="corp,muni"))
        assert "security_type IN ('corp', 'muni')" in sql

    def test_multi_security_type_with_spaces(self):
        sql = compile_sql(BondFilterParams(security_type=" corp , muni "))
        assert "IN ('corp', 'muni')" in sql

    def test_qualified_false_filters_out(self):
        sql = compile_sql(BondFilterParams(qualified=False))
        assert "qualified_only = false" in sql

    def test_qualified_true_no_filter(self):
        # qualified=true — показывать все бумаги, WHERE-условия нет
        sql = compile_sql(BondFilterParams(qualified=True))
        assert "WHERE" not in sql

    def test_search_matches_name_secid_isin(self):
        sql = compile_sql(BondFilterParams(search="ОФЗ"))
        assert "ILIKE" in sql
        for col in ("short_name", "full_name", "secid", "isin"):
            assert col in sql

    def test_search_empty_ignored(self):
        sql = compile_sql(BondFilterParams(search=""))
        assert "ILIKE" not in sql

    def test_days_and_listing(self):
        sql = compile_sql(BondFilterParams(days_min=30, days_max=365, list_level_max=2))
        assert "days_to_maturity >= 30" in sql
        assert "days_to_maturity <= 365" in sql
        assert "list_level <= 2" in sql


class TestSorting:
    def test_default_sort(self):
        sql = compile_sql(BondFilterParams())
        assert "ORDER BY bonds.yield_at_prev_wa_price DESC NULLS LAST" in sql

    def test_asc_sort(self):
        sql = compile_sql(BondFilterParams(sort_by="coupon_percent", sort_order="asc"))
        assert "ORDER BY bonds.coupon_percent NULLS LAST" in sql

    def test_unknown_sort_field_falls_back(self):
        # Защита от SQL-инъекций через sort_by: неизвестное поле → дефолт
        sql = compile_sql(BondFilterParams(sort_by="; DROP TABLE bonds"))
        assert "DROP" not in sql
        assert "ORDER BY bonds.yield_at_prev_wa_price" in sql


class TestSchemaValidation:
    def test_page_bounds(self):
        with pytest.raises(ValidationError):
            BondFilterParams(page=0)
        with pytest.raises(ValidationError):
            BondFilterParams(per_page=101)

    def test_sort_order_pattern(self):
        with pytest.raises(ValidationError):
            BondFilterParams(sort_order="sideways")

    def test_list_level_bounds(self):
        with pytest.raises(ValidationError):
            BondFilterParams(list_level_max=4)

    def test_search_max_length(self):
        with pytest.raises(ValidationError):
            BondFilterParams(search="x" * 101)
