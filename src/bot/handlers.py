"""Telegram bot handlers — single-window UX, old-style design."""

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import structlog

from src.bot import api_client
from src.bot.formatters import (
    format_after_setting,
    format_bond_detail,
    format_bond_list,
    format_info,
    format_market_overview,
    format_menu,
    format_params,
    format_settings,
)
from src.bot.keyboards import (
    kb_after_setting,
    kb_bond_detail,
    kb_bond_list,
    kb_coupon,
    kb_days,
    kb_frequency,
    kb_listing,
    kb_menu,
    kb_price,
    kb_qualified,
    kb_settings,
    kb_type,
    kb_yield,
)

logger = structlog.get_logger()
router = Router()


# ── FSM States (for manual input) ──────────────────────────────

class ManualInput(StatesGroup):
    yield_val = State()
    coupon_val = State()
    price_val = State()
    frequency_val = State()
    days_val = State()


# ── Helpers ─────────────────────────────────────────────────────

FILTER_KEYS = [
    "yield_min", "yield_max", "price_min", "price_max",
    "coupon_min", "coupon_max", "days_min", "days_max",
    "security_type", "list_level_max", "qualified",
    "coupon_frequency", "board_id",
]


def _get_filters(data: dict) -> dict:
    return {k: data.get(k) for k in FILTER_KEYS}


async def _safe_delete(message: Message) -> None:
    """Try to delete a message, ignore errors."""
    try:
        await message.delete()
    except Exception:
        pass


# ── /start ──────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    # Store the bot's main message ID for single-window editing
    sent = await message.answer(format_menu(), reply_markup=kb_menu(), parse_mode="Markdown")
    await state.update_data(main_msg_id=sent.message_id)
    await _safe_delete(message)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "*Как пользоваться ботом:*\n\n"
        "1️⃣ Нажмите *Настройки ⚙️*\n"
        "2️⃣ Настройте фильтры (кнопки или ввод вручную)\n"
        "3️⃣ Вернитесь в меню и нажмите *Получить бумаги 🗃️*\n"
        "4️⃣ Листайте результаты ◀️ ▶️\n"
        "5️⃣ Нажмите *📄 Подробнее* для деталей\n\n"
        "/start — главное меню",
        parse_mode="Markdown",
    )
    await _safe_delete(message)


# ── Main menu ───────────────────────────────────────────────────

@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(None)
    await callback.message.edit_text(format_menu(), reply_markup=kb_menu(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery) -> None:
    await callback.answer()


# ── Info ────────────────────────────────────────────────────────

@router.callback_query(F.data == "info")
async def cb_info(callback: CallbackQuery) -> None:
    from src.bot.keyboards import _btn, BTN_MENU
    from aiogram.types import InlineKeyboardMarkup
    kb = InlineKeyboardMarkup(inline_keyboard=[[BTN_MENU]])
    await callback.message.edit_text(format_info(), reply_markup=kb, parse_mode="Markdown")
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

    from src.bot.keyboards import BTN_MENU
    from aiogram.types import InlineKeyboardMarkup
    kb = InlineKeyboardMarkup(inline_keyboard=[[BTN_MENU]])
    text = format_market_overview(data)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


# ── Settings menu ───────────────────────────────────────────────

@router.callback_query(F.data == "settings")
@router.callback_query(F.data == "back_settings")
async def cb_settings(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(None)
    await callback.message.edit_text(
        format_settings(), reply_markup=kb_settings(), parse_mode="Markdown"
    )
    await callback.answer()


# ── My params ───────────────────────────────────────────────────

@router.callback_query(F.data == "my_params")
async def cb_my_params(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    filters = _get_filters(data)
    text = format_params(filters)

    from src.bot.keyboards import _btn, BTN_BACK, BTN_MENU
    from aiogram.types import InlineKeyboardMarkup
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [BTN_BACK],
        [_btn("Сбросить настройки ♻️", "reset")],
        [BTN_MENU],
    ])

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


# ── Reset filters ───────────────────────────────────────────────

@router.callback_query(F.data == "reset")
async def cb_reset(callback: CallbackQuery, state: FSMContext) -> None:
    # Keep only non-filter data
    data = await state.get_data()
    keep = {k: v for k, v in data.items() if k not in FILTER_KEYS}
    await state.set_data(keep)

    await callback.answer("Ваши настройки сброшены!", show_alert=True)

    # Show updated params
    await cb_my_params(callback, state)


# ══════════════════════════════════════════════════════════════════
# SETTING SCREENS — Presets + manual input
# ══════════════════════════════════════════════════════════════════

# ── Yield ───────────────────────────────────────────────────────

@router.callback_query(F.data == "set:yield")
async def cb_set_yield(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ManualInput.yield_val)
    await callback.message.edit_text(
        "Какой размер доходности к погашению вас интересует?\n\n"
        "_Выберите кнопку или введите число вручную._",
        reply_markup=kb_yield(), parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("v:yield:"))
async def cb_val_yield(callback: CallbackQuery, state: FSMContext) -> None:
    val = callback.data.split(":")[2]
    if val == "clear":
        await state.update_data(yield_min=None, yield_max=None)
    else:
        await state.update_data(yield_min=float(val))
    await state.set_state(None)
    await callback.message.edit_text(
        format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ManualInput.yield_val)
async def input_yield(message: Message, state: FSMContext) -> None:
    await _safe_delete(message)
    try:
        value = float(message.text.replace(",", "."))
        await state.update_data(yield_min=value)
    except ValueError:
        return  # silently ignore bad input

    await state.set_state(None)
    data = await state.get_data()
    msg_id = data.get("main_msg_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id, message_id=msg_id,
                text=format_after_setting(), reply_markup=kb_after_setting(),
                parse_mode="Markdown",
            )
        except Exception:
            await message.answer(
                format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
            )


# ── Coupon ──────────────────────────────────────────────────────

@router.callback_query(F.data == "set:coupon")
async def cb_set_coupon(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ManualInput.coupon_val)
    await callback.message.edit_text(
        "Какой размер купонной доходности вас интересует?\n\n"
        "_Выберите кнопку или введите число вручную._",
        reply_markup=kb_coupon(), parse_mode="Markdown",
    )
    await state.update_data(main_msg_id=callback.message.message_id)
    await callback.answer()


@router.callback_query(F.data.startswith("v:coupon:"))
async def cb_val_coupon(callback: CallbackQuery, state: FSMContext) -> None:
    val = callback.data.split(":")[2]
    if val == "clear":
        await state.update_data(coupon_min=None, coupon_max=None)
    else:
        await state.update_data(coupon_min=float(val))
    await state.set_state(None)
    await callback.message.edit_text(
        format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ManualInput.coupon_val)
async def input_coupon(message: Message, state: FSMContext) -> None:
    await _safe_delete(message)
    try:
        value = float(message.text.replace(",", "."))
        await state.update_data(coupon_min=value)
    except ValueError:
        return

    await state.set_state(None)
    data = await state.get_data()
    msg_id = data.get("main_msg_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id, message_id=msg_id,
                text=format_after_setting(), reply_markup=kb_after_setting(),
                parse_mode="Markdown",
            )
        except Exception:
            await message.answer(
                format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
            )


# ── Price ───────────────────────────────────────────────────────

@router.callback_query(F.data == "set:price")
async def cb_set_price(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ManualInput.price_val)
    await callback.message.edit_text(
        "Выберите минимальную котировку облигации.\n\n"
        "_Выберите кнопку или введите число вручную._",
        reply_markup=kb_price(), parse_mode="Markdown",
    )
    await state.update_data(main_msg_id=callback.message.message_id)
    await callback.answer()


@router.callback_query(F.data.startswith("v:price:"))
async def cb_val_price(callback: CallbackQuery, state: FSMContext) -> None:
    val = callback.data.split(":")[2]
    if val == "clear":
        await state.update_data(price_min=None, price_max=None)
    else:
        await state.update_data(price_min=float(val))
    await state.set_state(None)
    await callback.message.edit_text(
        format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ManualInput.price_val)
async def input_price(message: Message, state: FSMContext) -> None:
    await _safe_delete(message)
    try:
        value = float(message.text.replace(",", "."))
        await state.update_data(price_min=value)
    except ValueError:
        return

    await state.set_state(None)
    data = await state.get_data()
    msg_id = data.get("main_msg_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id, message_id=msg_id,
                text=format_after_setting(), reply_markup=kb_after_setting(),
                parse_mode="Markdown",
            )
        except Exception:
            await message.answer(
                format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
            )


# ── Frequency ───────────────────────────────────────────────────

@router.callback_query(F.data == "set:frequency")
async def cb_set_frequency(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ManualInput.frequency_val)
    await callback.message.edit_text(
        "Выберите предпочтительную частоту выплаты купона.\n\n"
        "_Или введите число вручную._",
        reply_markup=kb_frequency(), parse_mode="Markdown",
    )
    await state.update_data(main_msg_id=callback.message.message_id)
    await callback.answer()


@router.callback_query(F.data.startswith("v:freq:"))
async def cb_val_freq(callback: CallbackQuery, state: FSMContext) -> None:
    val = callback.data.split(":")[2]
    if val == "clear":
        await state.update_data(coupon_frequency=None)
    else:
        await state.update_data(coupon_frequency=int(val))
    await state.set_state(None)
    await callback.message.edit_text(
        format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ManualInput.frequency_val)
async def input_frequency(message: Message, state: FSMContext) -> None:
    await _safe_delete(message)
    try:
        value = int(message.text)
        await state.update_data(coupon_frequency=value)
    except ValueError:
        return

    await state.set_state(None)
    data = await state.get_data()
    msg_id = data.get("main_msg_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id, message_id=msg_id,
                text=format_after_setting(), reply_markup=kb_after_setting(),
                parse_mode="Markdown",
            )
        except Exception:
            await message.answer(
                format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
            )


# ── Days ────────────────────────────────────────────────────────

@router.callback_query(F.data == "set:days")
async def cb_set_days(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ManualInput.days_val)
    await callback.message.edit_text(
        "Выберите количество дней до погашения облигации.\n\n"
        "_Или введите число вручную._",
        reply_markup=kb_days(), parse_mode="Markdown",
    )
    await state.update_data(main_msg_id=callback.message.message_id)
    await callback.answer()


@router.callback_query(F.data.startswith("v:days:"))
async def cb_val_days(callback: CallbackQuery, state: FSMContext) -> None:
    val = callback.data.split(":")[2]
    if val == "clear":
        await state.update_data(days_min=None, days_max=None)
    elif val == "365+":
        await state.update_data(days_min=365, days_max=None)
    else:
        await state.update_data(days_min=None, days_max=int(val))
    await state.set_state(None)
    await callback.message.edit_text(
        format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
    )
    await callback.answer()


@router.message(ManualInput.days_val)
async def input_days(message: Message, state: FSMContext) -> None:
    await _safe_delete(message)
    try:
        value = int(message.text)
        await state.update_data(days_max=value)
    except ValueError:
        return

    await state.set_state(None)
    data = await state.get_data()
    msg_id = data.get("main_msg_id")
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id, message_id=msg_id,
                text=format_after_setting(), reply_markup=kb_after_setting(),
                parse_mode="Markdown",
            )
        except Exception:
            await message.answer(
                format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
            )


# ── Qualified ───────────────────────────────────────────────────

@router.callback_query(F.data == "set:qualified")
async def cb_set_qualified(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "У вас есть статус квалифицированного инвестора?",
        reply_markup=kb_qualified(), parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("v:qual:"))
async def cb_val_qual(callback: CallbackQuery, state: FSMContext) -> None:
    val = callback.data.split(":")[2]
    if val == "clear":
        await state.update_data(qualified=None)
    else:
        await state.update_data(qualified=(val == "yes"))
    await callback.message.edit_text(
        format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
    )
    await callback.answer()


# ── Bond type ───────────────────────────────────────────────────

@router.callback_query(F.data == "set:type")
async def cb_set_type(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Выберите тип облигации:",
        reply_markup=kb_type(), parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("v:type:"))
async def cb_val_type(callback: CallbackQuery, state: FSMContext) -> None:
    val = callback.data.split(":")[2]
    if val == "clear":
        await state.update_data(security_type=None)
    else:
        await state.update_data(security_type=val)
    await callback.message.edit_text(
        format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
    )
    await callback.answer()


# ── Listing level ───────────────────────────────────────────────

@router.callback_query(F.data == "set:listing")
async def cb_set_listing(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "Выберите максимальный уровень листинга:",
        reply_markup=kb_listing(), parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("v:list:"))
async def cb_val_listing(callback: CallbackQuery, state: FSMContext) -> None:
    val = callback.data.split(":")[2]
    if val == "clear":
        await state.update_data(list_level_max=None)
    else:
        await state.update_data(list_level_max=int(val))
    await callback.message.edit_text(
        format_after_setting(), reply_markup=kb_after_setting(), parse_mode="Markdown"
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════════
# BOND RESULTS — List + Detail
# ══════════════════════════════════════════════════════════════════

@router.callback_query(F.data == "get_bonds")
async def cb_get_bonds(callback: CallbackQuery, state: FSMContext) -> None:
    """Fetch bonds and show compact list."""
    await callback.answer("Пожалуйста подождите, ищем подходящие бумаги", show_alert=True)
    await _show_bonds_page(callback, state, page=1)


async def _show_bonds_page(callback: CallbackQuery, state: FSMContext, page: int) -> None:
    data = await state.get_data()
    filters = _get_filters(data)
    filters["page"] = page
    filters["per_page"] = 5
    filters["sort_by"] = "yield_at_prev_wa_price"
    filters["sort_order"] = "desc"

    try:
        result = await api_client.fetch_bonds(filters)
    except Exception:
        logger.exception("api_fetch_error")
        await callback.answer("❌ Ошибка при загрузке данных", show_alert=True)
        return

    items = result.get("items", [])
    total = result.get("total", 0)
    pages = result.get("pages", 0)

    if not items:
        await callback.answer(
            "К сожалению бумаг с данными параметрами сейчас нет.\nИзмените параметры!",
            show_alert=True,
        )
        return

    secids = [b["secid"] for b in items]
    secid_names = {b["secid"]: b.get("short_name") or b["secid"] for b in items}
    await state.update_data(current_page=page, current_secids=secids, secid_names=secid_names)

    text = format_bond_list(items, total, page, pages)
    kb = kb_bond_list(page, pages, secids, secid_names)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")


# ── Pagination ──────────────────────────────────────────────────

@router.callback_query(F.data.startswith("page:"))
async def cb_page(callback: CallbackQuery, state: FSMContext) -> None:
    page = int(callback.data.split(":")[1])
    await _show_bonds_page(callback, state, page=page)
    await callback.answer()


# ── Bond detail ─────────────────────────────────────────────────

@router.callback_query(F.data.startswith("detail:"))
async def cb_detail(callback: CallbackQuery, state: FSMContext) -> None:
    secid = callback.data.split(":")[1]

    try:
        bond = await api_client.fetch_bond(secid)
    except Exception:
        logger.exception("bond_detail_error", secid=secid)
        await callback.answer("❌ Ошибка загрузки", show_alert=True)
        return

    if not bond:
        await callback.answer("Облигация не найдена", show_alert=True)
        return

    data = await state.get_data()
    secids = data.get("current_secids", [])
    list_page = data.get("current_page", 1)

    current_idx = secids.index(secid) if secid in secids else 0
    kb = kb_bond_detail(secids, current_idx, list_page)

    text = format_bond_detail(bond)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    
    await callback.answer()


# ── Payment placeholder ─────────────────────────────────────────

@router.callback_query(F.data == "payment")
async def cb_payment(callback: CallbackQuery) -> None:
    await callback.answer("💳 Оплата будет добавлена позже", show_alert=True)
