"""add_issuers_and_events

Этап 1 фичи «Риск-сигналы эмитента» (docs/RISK_SIGNALS_PLAN.md):
- issuers: справочник эмитентов (ИНН из MOEX ISS description)
- issuer_events: лента риск-событий (на этапе 1 — смена уровня листинга MOEX)
- bonds.issuer_inn: связь бумага → эмитент

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-07-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EVENT_TYPES = (
    "default",
    "tech_default",
    "bankruptcy_intent",
    "listing_downgrade",
    "listing_upgrade",
    "state_support_request",
    "offer",
    "restructuring",
)


def upgrade() -> None:
    op.create_table(
        "issuers",
        sa.Column("inn", sa.String(length=12), nullable=False, comment="ИНН эмитента"),
        sa.Column("name", sa.String(length=300), nullable=True),
        sa.Column("ogrn", sa.String(length=15), nullable=True),
        sa.Column("okpo", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("inn"),
    )

    issuer_event_type = sa.Enum(*EVENT_TYPES, name="issuer_event_type")
    op.create_table(
        "issuer_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("inn", sa.String(length=12), nullable=False),
        sa.Column("type", issuer_event_type, nullable=False),
        sa.Column("date", sa.Date(), nullable=False, comment="Дата события"),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("secid", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["inn"], ["issuers.inn"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("inn", "type", "date", "source", "secid", name="uq_issuer_event_fact"),
    )
    op.create_index(op.f("ix_issuer_events_inn"), "issuer_events", ["inn"], unique=False)
    op.create_index(op.f("ix_issuer_events_secid"), "issuer_events", ["secid"], unique=False)
    op.create_index("ix_issuer_events_inn_date", "issuer_events", ["inn", "date"], unique=False)

    op.add_column(
        "bonds",
        sa.Column(
            "issuer_inn",
            sa.String(length=12),
            nullable=True,
            comment="ИНН эмитента из MOEX ISS description; NULL = ещё не обогащено",
        ),
    )
    op.create_index(op.f("ix_bonds_issuer_inn"), "bonds", ["issuer_inn"], unique=False)
    op.create_foreign_key(
        "fk_bonds_issuer_inn", "bonds", "issuers", ["issuer_inn"], ["inn"], ondelete="SET NULL"
    )


def downgrade() -> None:
    op.drop_constraint("fk_bonds_issuer_inn", "bonds", type_="foreignkey")
    op.drop_index(op.f("ix_bonds_issuer_inn"), table_name="bonds")
    op.drop_column("bonds", "issuer_inn")
    op.drop_index("ix_issuer_events_inn_date", table_name="issuer_events")
    op.drop_index(op.f("ix_issuer_events_secid"), table_name="issuer_events")
    op.drop_index(op.f("ix_issuer_events_inn"), table_name="issuer_events")
    op.drop_table("issuer_events")
    op.drop_table("issuers")
    sa.Enum(name="issuer_event_type").drop(op.get_bind(), checkfirst=True)
