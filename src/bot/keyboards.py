"""Inline keyboards for the Telegram bot."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ── Main menu ───────────────────────────────────────────────────

def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔍 Поиск облигаций", callback_data="search"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Обзор рынка", callback_data="market_overview"),
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Мои фильтры", callback_data="my_filters"),
        InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"),
    )
    return builder.as_markup()


# ── Filter setup ────────────────────────────────────────────────

def filter_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💰 Доходность", callback_data="f:yield"),
        InlineKeyboardButton(text="💵 Цена", callback_data="f:price"),
    )
    builder.row(
        InlineKeyboardButton(text="🎫 Купон", callback_data="f:coupon"),
        InlineKeyboardButton(text="📅 Срок", callback_data="f:maturity"),
    )
    builder.row(
        InlineKeyboardButton(text="📋 Тип бумаги", callback_data="f:type"),
        InlineKeyboardButton(text="🏷 Листинг", callback_data="f:listing"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 Квал. инвестор", callback_data="f:qualified"),
    )
    builder.row(
        InlineKeyboardButton(text="✅ Применить фильтры", callback_data="apply_filters"),
    )
    builder.row(
        InlineKeyboardButton(text="🗑 Сбросить всё", callback_data="reset_filters"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_main"),
    )
    return builder.as_markup()


# ── Bond type selection ─────────────────────────────────────────

def bond_type_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Все типы", callback_data="type:all"),
    )
    builder.row(
        InlineKeyboardButton(text="🏛 ОФЗ", callback_data="type:ofz"),
        InlineKeyboardButton(text="🏢 Корпоративные", callback_data="type:corp"),
    )
    builder.row(
        InlineKeyboardButton(text="🏘 Муниципальные", callback_data="type:muni"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад к фильтрам", callback_data="back_filters"),
    )
    return builder.as_markup()


# ── Listing level ───────────────────────────────────────────────

def listing_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1 уровень (высший)", callback_data="list:1"),
        InlineKeyboardButton(text="До 2 уровня", callback_data="list:2"),
    )
    builder.row(
        InlineKeyboardButton(text="Все уровни", callback_data="list:3"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад к фильтрам", callback_data="back_filters"),
    )
    return builder.as_markup()


# ── Qualified investor ──────────────────────────────────────────

def qualified_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Только неквал.", callback_data="qual:no"),
        InlineKeyboardButton(text="✅ Все бумаги", callback_data="qual:yes"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад к фильтрам", callback_data="back_filters"),
    )
    return builder.as_markup()


# ── Pagination ──────────────────────────────────────────────────

def pagination_kb(page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️", callback_data=f"page:{page - 1}")
        )
    nav_buttons.append(
        InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop")
    )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(text="▶️", callback_data=f"page:{page + 1}")
        )
    builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(text="⚙️ Изменить фильтры", callback_data="search"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="back_main"),
    )
    return builder.as_markup()


# ── Bond detail ─────────────────────────────────────────────────

def bond_detail_kb(page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ К списку", callback_data=f"page:{page}"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="back_main"),
    )
    return builder.as_markup()
