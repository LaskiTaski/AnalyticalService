"""Telegram bot handlers — commands and callbacks."""

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import structlog

from src.bot import api_client
from src.bot.formatters import (
    format_bond_detail,
    format_bond_list,
    format_current_filters,
    format_market_overview,
)
from src.bot.keyboards import (
    bond_detail_kb,
    bond_type_kb,
    filter_menu_kb,
    listing_kb,
    main_menu_kb,
    pagination_kb,
    qualified_kb,
)

logger = structlog.get_logger()
router = Router()


# ── FSM States ──────────────────────────────────────────────────

class FilterInput(StatesGroup):
    """States for manual filter value input."""
    yield_min = State()
    yield_max = State()
    price_min = State()
    price_max = State()
    coupon_min = State()
    coupon_max = State()
    days_min = State()
    days_max = State()


# ── Helpers ─────────────────────────────────────────────────────

def _get_filters(data: dict) -> dict:
    """Extract filter params from FSM data."""
    keys = [
        "yield_min", "yield_max", "price_min", "price_max",
        "coupon_min", "coupon_max", "days_min", "days_max",
        "security_type", "list_level_max", "qualified",
        "coupon_frequency", "board_id",
    ]
    return {k: data.get(k) for k in keys}


async def _show_bonds(callback: CallbackQuery, state: FSMContext, page: int = 1) -> None:
    """Fetch and display bonds with current filters."""
    data = await state.get_data()
    filters = _get_filters(data)
    filters["page"] = page
    filters["per_page"] = 5
    filters["sort_by"] = data.get("sort_by", "yield_at_prev_wa_price")
    filters["sort_order"] = data.get("sort_order", "desc")

    try:
        result = await api_client.fetch_bonds(filters)
    except Exception:
        logger.exception("api_fetch_error")
        await callback.answer("❌ Ошибка при загрузке данных", show_alert=True)
        return

    items = result.get("items", [])
    total = result.get("total", 0)
    pages = result.get("pages", 0)

    text = format_bond_list(items, total, page, pages)

    # Store secids for detail view
    secids = [b["secid"] for b in items]
    await state.update_data(current_page=page, current_secids=secids)

    kb = pagination_kb(page, pages) if pages > 0 else main_menu_kb()

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


# ── /start ──────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "👋 <b>Добро пожаловать в Bond Screener!</b>\n\n"
        "Я помогу найти облигации на Московской бирже "
        "по вашим параметрам: доходности, купону, сроку и другим.\n\n"
        "Выберите действие:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "📖 <b>Как пользоваться ботом:</b>\n\n"
        "1️⃣ Нажмите <b>🔍 Поиск облигаций</b>\n"
        "2️⃣ Настройте фильтры (доходность, цена, купон, срок)\n"
        "3️⃣ Нажмите <b>✅ Применить фильтры</b>\n"
        "4️⃣ Листайте результаты кнопками ◀️ ▶️\n\n"
        "📊 <b>Обзор рынка</b> — общая статистика\n"
        "⚙️ <b>Мои фильтры</b> — текущие настройки\n\n"
        "Команды:\n"
        "/start — главное меню\n"
        "/help — эта справка",
        parse_mode="HTML",
    )


# ── Main menu callbacks ────────────────────────────────────────

@router.callback_query(F.data == "back_main")
async def cb_back_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(None)
    await callback.message.edit_text(
        "🏠 <b>Главное меню</b>\n\nВыберите действие:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def cb_help(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "📖 <b>Как пользоваться ботом:</b>\n\n"
        "1️⃣ Нажмите <b>🔍 Поиск облигаций</b>\n"
        "2️⃣ Настройте фильтры\n"
        "3️⃣ Нажмите <b>✅ Применить фильтры</b>\n"
        "4️⃣ Листайте результаты ◀️ ▶️\n\n"
        "📊 <b>Обзор рынка</b> — общая статистика",
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery) -> None:
    await callback.answer()


# ── Market overview ─────────────────────────────────────────────

@router.callback_query(F.data == "market_overview")
async def cb_market_overview(callback: CallbackQuery) -> None:
    try:
        data = await api_client.fetch_market_overview()
    except Exception:
        logger.exception("market_overview_error")
        await callback.answer("❌ Ошибка загрузки", show_alert=True)
        return

    text = format_market_overview(data)
    await callback.message.edit_text(text, reply_markup=main_menu_kb(), parse_mode="HTML")
    await callback.answer()


# ── Filter menu ─────────────────────────────────────────────────

@router.callback_query(F.data == "search")
@router.callback_query(F.data == "back_filters")
async def cb_filter_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(None)
    data = await state.get_data()
    filters = _get_filters(data)
    text = format_current_filters(filters) + "\n\n🔧 Выберите параметр для настройки:"

    await callback.message.edit_text(text, reply_markup=filter_menu_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "my_filters")
async def cb_my_filters(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    filters = _get_filters(data)
    text = format_current_filters(filters)

    await callback.message.edit_text(text, reply_markup=filter_menu_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "reset_filters")
async def cb_reset_filters(callback: CallbackQuery, state: FSMContext) -> None:
    # Keep non-filter data, clear only filter keys
    data = await state.get_data()
    for key in list(data.keys()):
        if key not in ("current_page", "current_secids"):
            data.pop(key, None)
    await state.set_data(data)

    await callback.answer("🗑 Фильтры сброшены", show_alert=False)
    await cb_filter_menu(callback, state)


# ── Yield filter ────────────────────────────────────────────────

@router.callback_query(F.data == "f:yield")
async def cb_yield(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FilterInput.yield_min)
    await callback.message.edit_text(
        "📈 <b>Доходность к погашению</b>\n\n"
        "Введите <b>минимальную</b> доходность (%) или 0 чтобы пропустить:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(FilterInput.yield_min)
async def input_yield_min(message: Message, state: FSMContext) -> None:
    try:
        value = float(message.text.replace(",", "."))
        if value > 0:
            await state.update_data(yield_min=value)
    except ValueError:
        await message.answer("❌ Введите число. Например: 10")
        return

    await state.set_state(FilterInput.yield_max)
    await message.answer(
        "Введите <b>максимальную</b> доходность (%) или 0 чтобы пропустить:",
        parse_mode="HTML",
    )


@router.message(FilterInput.yield_max)
async def input_yield_max(message: Message, state: FSMContext) -> None:
    try:
        value = float(message.text.replace(",", "."))
        if value > 0:
            await state.update_data(yield_max=value)
    except ValueError:
        await message.answer("❌ Введите число. Например: 20")
        return

    await state.set_state(None)
    data = await state.get_data()
    text = format_current_filters(_get_filters(data)) + "\n\n🔧 Выберите параметр для настройки:"
    await message.answer(text, reply_markup=filter_menu_kb(), parse_mode="HTML")


# ── Price filter ────────────────────────────────────────────────

@router.callback_query(F.data == "f:price")
async def cb_price(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FilterInput.price_min)
    await callback.message.edit_text(
        "💵 <b>Цена (% от номинала)</b>\n\n"
        "Введите <b>минимальную</b> цену или 0 чтобы пропустить:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(FilterInput.price_min)
async def input_price_min(message: Message, state: FSMContext) -> None:
    try:
        value = float(message.text.replace(",", "."))
        if value > 0:
            await state.update_data(price_min=value)
    except ValueError:
        await message.answer("❌ Введите число. Например: 90")
        return

    await state.set_state(FilterInput.price_max)
    await message.answer(
        "Введите <b>максимальную</b> цену или 0 чтобы пропустить:",
        parse_mode="HTML",
    )


@router.message(FilterInput.price_max)
async def input_price_max(message: Message, state: FSMContext) -> None:
    try:
        value = float(message.text.replace(",", "."))
        if value > 0:
            await state.update_data(price_max=value)
    except ValueError:
        await message.answer("❌ Введите число. Например: 105")
        return

    await state.set_state(None)
    data = await state.get_data()
    text = format_current_filters(_get_filters(data)) + "\n\n🔧 Выберите параметр для настройки:"
    await message.answer(text, reply_markup=filter_menu_kb(), parse_mode="HTML")


# ── Coupon filter ───────────────────────────────────────────────

@router.callback_query(F.data == "f:coupon")
async def cb_coupon(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FilterInput.coupon_min)
    await callback.message.edit_text(
        "🎫 <b>Ставка купона (%)</b>\n\n"
        "Введите <b>минимальную</b> ставку или 0 чтобы пропустить:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(FilterInput.coupon_min)
async def input_coupon_min(message: Message, state: FSMContext) -> None:
    try:
        value = float(message.text.replace(",", "."))
        if value > 0:
            await state.update_data(coupon_min=value)
    except ValueError:
        await message.answer("❌ Введите число. Например: 8")
        return

    await state.set_state(FilterInput.coupon_max)
    await message.answer(
        "Введите <b>максимальную</b> ставку или 0 чтобы пропустить:",
        parse_mode="HTML",
    )


@router.message(FilterInput.coupon_max)
async def input_coupon_max(message: Message, state: FSMContext) -> None:
    try:
        value = float(message.text.replace(",", "."))
        if value > 0:
            await state.update_data(coupon_max=value)
    except ValueError:
        await message.answer("❌ Введите число. Например: 15")
        return

    await state.set_state(None)
    data = await state.get_data()
    text = format_current_filters(_get_filters(data)) + "\n\n🔧 Выберите параметр для настройки:"
    await message.answer(text, reply_markup=filter_menu_kb(), parse_mode="HTML")


# ── Maturity filter ─────────────────────────────────────────────

@router.callback_query(F.data == "f:maturity")
async def cb_maturity(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FilterInput.days_min)
    await callback.message.edit_text(
        "📅 <b>Дней до погашения</b>\n\n"
        "Введите <b>минимум</b> дней или 0 чтобы пропустить:",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(FilterInput.days_min)
async def input_days_min(message: Message, state: FSMContext) -> None:
    try:
        value = int(message.text)
        if value > 0:
            await state.update_data(days_min=value)
    except ValueError:
        await message.answer("❌ Введите целое число. Например: 30")
        return

    await state.set_state(FilterInput.days_max)
    await message.answer(
        "Введите <b>максимум</b> дней или 0 чтобы пропустить:",
        parse_mode="HTML",
    )


@router.message(FilterInput.days_max)
async def input_days_max(message: Message, state: FSMContext) -> None:
    try:
        value = int(message.text)
        if value > 0:
            await state.update_data(days_max=value)
    except ValueError:
        await message.answer("❌ Введите целое число. Например: 365")
        return

    await state.set_state(None)
    data = await state.get_data()
    text = format_current_filters(_get_filters(data)) + "\n\n🔧 Выберите параметр для настройки:"
    await message.answer(text, reply_markup=filter_menu_kb(), parse_mode="HTML")


# ── Bond type ───────────────────────────────────────────────────

@router.callback_query(F.data == "f:type")
async def cb_type(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "📋 <b>Тип облигации:</b>",
        reply_markup=bond_type_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("type:"))
async def cb_type_selected(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[1]
    if value == "all":
        await state.update_data(security_type=None)
    else:
        await state.update_data(security_type=value)

    emoji = {"ofz": "🏛 ОФЗ", "corp": "🏢 Корп.", "muni": "🏘 Муни."}.get(value, "Все")
    await callback.answer(f"Выбрано: {emoji}")

    data = await state.get_data()
    text = format_current_filters(_get_filters(data)) + "\n\n🔧 Выберите параметр для настройки:"
    await callback.message.edit_text(text, reply_markup=filter_menu_kb(), parse_mode="HTML")


# ── Listing level ───────────────────────────────────────────────

@router.callback_query(F.data == "f:listing")
async def cb_listing(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🏷 <b>Максимальный уровень листинга:</b>",
        reply_markup=listing_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("list:"))
async def cb_listing_selected(callback: CallbackQuery, state: FSMContext) -> None:
    value = int(callback.data.split(":")[1])
    await state.update_data(list_level_max=value)
    await callback.answer(f"Листинг: до {value} уровня")

    data = await state.get_data()
    text = format_current_filters(_get_filters(data)) + "\n\n🔧 Выберите параметр для настройки:"
    await callback.message.edit_text(text, reply_markup=filter_menu_kb(), parse_mode="HTML")


# ── Qualified investor ──────────────────────────────────────────

@router.callback_query(F.data == "f:qualified")
async def cb_qualified(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "👤 <b>Квалифицированный инвестор:</b>",
        reply_markup=qualified_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("qual:"))
async def cb_qualified_selected(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":")[1] == "yes"
    await state.update_data(qualified=value)
    await callback.answer("Квал.: Все" if value else "Квал.: Только неквал.")

    data = await state.get_data()
    text = format_current_filters(_get_filters(data)) + "\n\n🔧 Выберите параметр для настройки:"
    await callback.message.edit_text(text, reply_markup=filter_menu_kb(), parse_mode="HTML")


# ── Apply filters (search) ──────────────────────────────────────

@router.callback_query(F.data == "apply_filters")
async def cb_apply_filters(callback: CallbackQuery, state: FSMContext) -> None:
    await _show_bonds(callback, state, page=1)
    await callback.answer()


# ── Pagination ──────────────────────────────────────────────────

@router.callback_query(F.data.startswith("page:"))
async def cb_page(callback: CallbackQuery, state: FSMContext) -> None:
    page = int(callback.data.split(":")[1])
    await _show_bonds(callback, state, page=page)
    await callback.answer()


# ── Bond detail (by secid typed in chat) ────────────────────────

@router.message(F.text.regexp(r"^[A-Za-z0-9]{5,20}$"))
async def msg_bond_lookup(message: Message, state: FSMContext) -> None:
    """If user types a SECID-like string, try to look it up."""
    secid = message.text.upper()

    try:
        bond = await api_client.fetch_bond(secid)
    except Exception:
        logger.exception("bond_lookup_error", secid=secid)
        await message.answer("❌ Ошибка при поиске")
        return

    if not bond:
        await message.answer(
            f"🔍 Облигация <code>{secid}</code> не найдена.",
            parse_mode="HTML",
        )
        return

    data = await state.get_data()
    page = data.get("current_page", 1)
    text = format_bond_detail(bond)
    await message.answer(text, reply_markup=bond_detail_kb(page), parse_mode="HTML")
