"""Issuer models — эмитенты и риск-события (фича «Риск-сигналы эмитента»).

Связка: у бумаги есть SECID, у эмитента — ИНН. Маппинг берём из MOEX ISS:
/iss/securities/{secid}.json → блок description содержит поле INN.

issuer_events — единая лента событий по эмитенту. На этапе 1 источник один
(MOEX: смена уровня листинга), но enum типов сразу покрывает этапы 2-4
(рейтинги, e-disclosure, Федресурс), чтобы не менять схему при их подключении.
"""

import enum
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base


class IssuerEventType(str, enum.Enum):
    """Типы риск-событий (см. docs/RISK_SIGNALS_PLAN.md)."""

    DEFAULT = "default"                      # дефолт по обязательствам
    TECH_DEFAULT = "tech_default"            # техдефолт по купону/оферте
    BANKRUPTCY_INTENT = "bankruptcy_intent"  # сообщение о намерении банкротства (Федресурс)
    LISTING_DOWNGRADE = "listing_downgrade"  # понижение уровня листинга MOEX
    LISTING_UPGRADE = "listing_upgrade"      # повышение уровня листинга MOEX
    STATE_SUPPORT_REQUEST = "state_support_request"
    OFFER = "offer"                          # оферта (e-disclosure)
    RESTRUCTURING = "restructuring"          # реструктуризация


# Типы, которые считаем «тяжёлыми» для красного бейджа в скринере
SEVERE_EVENT_TYPES = (
    IssuerEventType.DEFAULT,
    IssuerEventType.TECH_DEFAULT,
    IssuerEventType.BANKRUPTCY_INTENT,
    IssuerEventType.RESTRUCTURING,
)


class Issuer(Base):
    __tablename__ = "issuers"

    inn: Mapped[str] = mapped_column(String(12), primary_key=True, comment="ИНН эмитента")
    name: Mapped[str | None] = mapped_column(
        String(300),
        comment="Название эмитента (этап 1: эвристика из имени бумаги; этап 2: каноническое из пресс-релизов агентств)",
    )
    ogrn: Mapped[str | None] = mapped_column(String(15), comment="ОГРН (если доступен в источнике)")
    okpo: Mapped[str | None] = mapped_column(String(10), comment="ОКПО из MOEX ISS description")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    events: Mapped[list["IssuerEvent"]] = relationship(back_populates="issuer")

    def __repr__(self) -> str:
        return f"<Issuer(inn={self.inn}, name={self.name})>"


class IssuerEvent(Base):
    __tablename__ = "issuer_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    inn: Mapped[str] = mapped_column(
        String(12), ForeignKey("issuers.inn", ondelete="CASCADE"), nullable=False, index=True
    )

    type: Mapped[IssuerEventType] = mapped_column(
        Enum(IssuerEventType, name="issuer_event_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, comment="Дата события")
    title: Mapped[str] = mapped_column(String(500), nullable=False, comment="Человекочитаемое описание")
    url: Mapped[str | None] = mapped_column(String(1000), comment="Ссылка на первоисточник")
    source: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="moex / acra / raexpert / e-disclosure / fedresurs"
    )
    secid: Mapped[str | None] = mapped_column(
        String(50), index=True, comment="SECID бумаги, если событие привязано к конкретному выпуску"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    issuer: Mapped[Issuer] = relationship(back_populates="events")

    __table_args__ = (
        # Дедупликация: один и тот же факт из одного источника не должен дублироваться
        UniqueConstraint("inn", "type", "date", "source", "secid", name="uq_issuer_event_fact"),
        Index("ix_issuer_events_inn_date", "inn", "date"),
    )

    def __repr__(self) -> str:
        return f"<IssuerEvent(inn={self.inn}, type={self.type}, date={self.date})>"
