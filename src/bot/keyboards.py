"""Inline keyboards — old-style single-window UX."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# ── Helpers ─────────────────────────────────────────────────────

def _btn(text: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=data)


# Common navigation buttons
BTN_BACK = _btn("Назад 🔙", "back_settings")
BTN_PARAMS = _btn("Мои параметры 📋", "my_params")
BTN_MENU = _btn("Главное меню ↩️", "menu")


# ── Main menu ───────────────────────────────────────────────────

def kb_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("Настройки ⚙️", "settings")],
        [_btn("О нас ℹ️", "info"), _btn("Оплатить 💳", "payment")],
        [_btn("Получить бумаги 🗃️", "get_bonds")],
    ])


# ── Settings menu ──────────────────────────────────────────────

def kb_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("🔸 Доходность к погашению 🔸", "set:yield")],
        [_btn("🔸 Купонная доходность 🔸", "set:coupon")],
        [_btn("Котировка\nоблигаций", "set:price"), _btn("Частота\nкупона", "set:frequency")],
        [_btn("Дней до\nпогашения", "set:days"), _btn("Статус квал?", "set:qualified")],
        [_btn("Тип бумаги", "set:type"), _btn("Уровень листинга", "set:listing")],
        [BTN_PARAMS, BTN_MENU],
    ])


# ── After setting saved ────────────────────────────────────────

def kb_after_setting() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [BTN_BACK],
        [BTN_PARAMS, BTN_MENU],
    ])


# ── Yield presets ───────────────────────────────────────────────

def kb_yield() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("Больше 5%", "v:yield:5"), _btn("Больше 10%", "v:yield:10")],
        [_btn("Больше 15%", "v:yield:15"), _btn("Больше 20%", "v:yield:20")],
        [_btn("Очистить значение", "v:yield:clear")],
        [BTN_BACK],
        [BTN_PARAMS, BTN_MENU],
    ])


# ── Coupon percent presets ──────────────────────────────────────

def kb_coupon() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("Больше 5%", "v:coupon:5"), _btn("Больше 10%", "v:coupon:10")],
        [_btn("Больше 15%", "v:coupon:15"), _btn("Больше 20%", "v:coupon:20")],
        [_btn("Очистить значение", "v:coupon:clear")],
        [BTN_BACK],
        [BTN_PARAMS, BTN_MENU],
    ])


# ── Price (quotation) presets ───────────────────────────────────

def kb_price() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("Больше 25%", "v:price:25"), _btn("Больше 50%", "v:price:50")],
        [_btn("Больше 75%", "v:price:75"), _btn("Больше 90%", "v:price:90")],
        [_btn("Очистить значение", "v:price:clear")],
        [BTN_BACK],
        [BTN_PARAMS, BTN_MENU],
    ])


# ── Frequency presets ───────────────────────────────────────────

def kb_frequency() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("2", "v:freq:2"), _btn("4", "v:freq:4"),
         _btn("6", "v:freq:6"), _btn("12", "v:freq:12")],
        [_btn("Очистить значение", "v:freq:clear")],
        [BTN_BACK],
        [BTN_PARAMS, BTN_MENU],
    ])


# ── Days to maturity presets ────────────────────────────────────

def kb_days() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("До недели", "v:days:7"), _btn("До месяца", "v:days:31"),
         _btn("До квартала", "v:days:90")],
        [_btn("До полугода", "v:days:182"), _btn("До года", "v:days:366"),
         _btn("Год и более", "v:days:365+")],
        [_btn("Очистить значение", "v:days:clear")],
        [BTN_BACK],
        [BTN_PARAMS, BTN_MENU],
    ])


# ── Qualified investor ──────────────────────────────────────────

def kb_qualified() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("Да ✅", "v:qual:yes"), _btn("Нет ❌", "v:qual:no")],
        [_btn("Очистить значение", "v:qual:clear")],
        [BTN_BACK],
        [BTN_PARAMS, BTN_MENU],
    ])


# ── Bond type ───────────────────────────────────────────────────

def kb_type() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("🏛 ОФЗ", "v:type:ofz"), _btn("🏢 Корпоративные", "v:type:corp")],
        [_btn("🏘 Муниципальные", "v:type:muni")],
        [_btn("Очистить значение", "v:type:clear")],
        [BTN_BACK],
        [BTN_PARAMS, BTN_MENU],
    ])


# ── Listing level ───────────────────────────────────────────────

def kb_listing() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [_btn("1 уровень", "v:list:1"), _btn("До 2 уровня", "v:list:2")],
        [_btn("Все уровни", "v:list:3")],
        [_btn("Очистить значение", "v:list:clear")],
        [BTN_BACK],
        [BTN_PARAMS, BTN_MENU],
    ])


# ── Bond list (compact) with "Подробнее" buttons ───────────────

def kb_bond_list(page: int, total_pages: int, secids: list[str], names: dict[str, str] | None = None) -> InlineKeyboardMarkup:
    rows = []

    # Detail buttons for each bond on this page
    for i, secid in enumerate(secids):
        name = (names or {}).get(secid, secid)
        rows.append([_btn(f"📄 {name}", f"detail:{secid}")])

    # Pagination
    nav = []
    if page > 1:
        nav.append(_btn("◀️ Пред.", f"page:{page - 1}"))
    nav.append(_btn(f"{page} из {total_pages}", "noop"))
    if page < total_pages:
        nav.append(_btn("След. ▶️", f"page:{page + 1}"))
    rows.append(nav)

    rows.append([BTN_PARAMS, BTN_MENU])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Bond detail — single bond, with prev/next navigation ───────

def kb_bond_detail(
    secids: list[str],
    current_idx: int,
    list_page: int,
) -> InlineKeyboardMarkup:
    nav = []
    if current_idx > 0:
        nav.append(_btn("◀️ Пред.", f"detail:{secids[current_idx - 1]}"))
    nav.append(_btn(f"{current_idx + 1} из {len(secids)}", "noop"))
    if current_idx < len(secids) - 1:
        nav.append(_btn("След. ▶️", f"detail:{secids[current_idx + 1]}"))

    return InlineKeyboardMarkup(inline_keyboard=[
        nav,
        [_btn("◀️ К списку", f"page:{list_page}")],
        [BTN_PARAMS, BTN_MENU],
    ])
