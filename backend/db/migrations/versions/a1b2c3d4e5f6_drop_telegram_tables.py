"""drop_telegram_tables

Telegram-бот удалён из проекта. Таблицы users/user_filters/payments были
завязаны на telegram_id и использовались только ботом (веб-API их не читал).
Веб-авторизация и подписки будут спроектированы заново (см. docs/PROJECT.md).

ВНИМАНИЕ: downgrade восстанавливает схему, но не данные.

Revision ID: a1b2c3d4e5f6
Revises: d301ddf5306f
Create Date: 2026-07-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "d301ddf5306f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("user_filters")
    op.drop_table("payments")
    op.drop_index(op.f("ix_users_telegram_id"), table_name="users")
    op.drop_table("users")


def downgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("is_qualified", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("subscription_until", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_telegram_id"), "users", ["telegram_id"], unique=True)
    op.create_table(
        "payments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("payload", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payments_user_id"), "payments", ["user_id"], unique=False)
    op.create_table(
        "user_filters",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("price_min", sa.Float(), nullable=True),
        sa.Column("price_max", sa.Float(), nullable=True),
        sa.Column("yield_min", sa.Float(), nullable=True),
        sa.Column("yield_max", sa.Float(), nullable=True),
        sa.Column("coupon_min", sa.Float(), nullable=True),
        sa.Column("coupon_max", sa.Float(), nullable=True),
        sa.Column("coupon_frequency", sa.Integer(), nullable=True),
        sa.Column("days_min", sa.Integer(), nullable=True),
        sa.Column("days_max", sa.Integer(), nullable=True),
        sa.Column("qualified_ok", sa.Boolean(), nullable=False),
        sa.Column("list_level_max", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
