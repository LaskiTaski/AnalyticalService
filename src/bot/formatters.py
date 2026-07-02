"""Format bond data for Telegram messages — Markdown, single-window style."""

# Invisible image links for visual flair in messages
IMG_MENU = "https://goo.su/VKUr"
IMG_SETTINGS = "https://telegra.ph/Kak-nastroit-parametry-03-19"
IMG_INFO = "https://telegra.ph/Informaciya-o-bote-03-19"


def _img(url: str) -> str:
    """Invisible image link for Markdown — shows preview in message."""
    return f"[ ]({url})"


def format_menu() -> str:
    return f"Настройте стратегию для сортировки{_img(IMG_MENU)}"


def format_settings() -> str:
    return f"[Ознакомиться с параметрами для сортировки бумаг]({IMG_SETTINGS})"


def format_info() -> str:
    return f"[Информация о боте]({IMG_INFO})"


def format_after_setting(img_url: str = IMG_SETTINGS) -> str:
    return f'Вернитесь в меню или проверьте "Мои параметры 📋".{_img(img_url)}'


def format_params(filters: dict) -> str:
    """Format current user filters — Markdown style."""

    def _val(key, suffix="%"):
        v = filters.get(key)
        if v is None:
            return "—"
        return f"N > {v}{suffix}"

    def _val_eq(key, suffix=""):
        v = filters.get(key)
        if v is None:
            return "—"
        return f"N = {v}{suffix}"

    def _days_val():
        d_min = filters.get("days_min")
        d_max = filters.get("days_max")
        if d_min is not None and d_max is not None:
            return f"{d_min} — {d_max} дней"
        if d_max is not None:
            return f"N < {d_max} дней"
        if d_min is not None:
            return f"N >= {d_min} дней"
        return "—"

    def _qual_val():
        v = filters.get("qualified")
        if v is None:
            return "—"
        return "Да" if v else "Нет"

    def _type_val():
        v = filters.get("security_type")
        if v is None:
            return "—"
        return {"ofz": "🏛 ОФЗ", "corp": "🏢 Корпоративные", "muni": "🏘 Муниципальные"}.get(v, v)

    def _list_val():
        v = filters.get("list_level_max")
        if v is None:
            return "—"
        return f"До {v} уровня"

    lines = [
        f"*Котировка облигаций:*",
        f"🔸_{_val('price_min')}_",
        "",
        f"*Доходность к погашению:*",
        f"🔸_{_val('yield_min')}_",
        "",
        f"*Купонная доходность:*",
        f"🔸_{_val('coupon_min')}_",
        "",
        f"*Частота купона:*",
        f"🔸_{_val_eq('coupon_frequency', ' раз(а) в год')}_",
        "",
        f"*Дней до погашения:*",
        f"🔸_{_days_val()}_",
        "",
        f"*Тип бумаги:*",
        f"🔸_{_type_val()}_",
        "",
        f"*Уровень листинга:*",
        f"🔸_{_list_val()}_",
        "",
        f"*Статус квал. инвестора:*",
        f"🔸_{_qual_val()}_",
    ]

    return "\n".join(lines)


def format_bond_compact(bond: dict, idx: int) -> str:
    """Compact bond card for list view."""
    name = bond.get("short_name") or bond.get("secid", "—")
    secid = bond.get("secid", "—")
    price = bond.get("prev_price")
    ytm = bond.get("yield_at_prev_wa_price")
    coupon = bond.get("coupon_percent")
    days = bond.get("days_to_maturity")

    price_s = f"{price:.2f}%" if price else "—"
    ytm_s = f"{ytm:.2f}%" if ytm else "—"
    coupon_s = f"{coupon:.2f}%" if coupon else "—"
    days_s = f"{days} дн." if days is not None else "—"

    return (
        f"*{idx}. {name}* (`{secid}`)\n"
        f"   Цена: {price_s} | Дох: {ytm_s} | Купон: {coupon_s} | {days_s}"
    )


def format_bond_list(bonds: list[dict], total: int, page: int, pages: int) -> str:
    """Format a page of bonds — compact list."""
    if not bonds:
        return "🔍 По вашим фильтрам ничего не найдено.\nПопробуйте изменить параметры."

    header = f"📋 *Найдено: {total}* (стр. {page}/{pages})\n\n"
    cards = "\n\n".join(
        format_bond_compact(b, i + 1)
        for i, b in enumerate(bonds)
    )

    return header + cards


def format_bond_detail(bond: dict) -> str:
    """Detailed single bond view."""
    name = bond.get("full_name") or bond.get("short_name", "—")
    secid = bond.get("secid", "—")
    isin = bond.get("isin", "—")
    board = bond.get("board_id", "—")
    btype = bond.get("security_type", "—")

    price = bond.get("prev_price")
    face = bond.get("face_value")
    nkd = bond.get("accrued_int")
    lot = bond.get("lot_size")

    ytm = bond.get("yield_at_prev_wa_price")
    coupon_pct = bond.get("coupon_percent")
    coupon_val = bond.get("coupon_value")
    coupon_period = bond.get("coupon_period")
    coupon_freq = bond.get("coupon_frequency")

    mat_date = bond.get("mat_date", "—")
    offer_date = bond.get("offer_date")
    days = bond.get("days_to_maturity")
    duration = bond.get("duration")

    level = bond.get("list_level")
    qualified = bond.get("qualified_only")
    volume = bond.get("volume_today")
    updated = bond.get("updated_at", "—")

    def f(v, s=""):
        return f"{v:.2f}{s}" if v is not None else "—"

    def fi(v, s=""):
        return f"{v}{s}" if v is not None else "—"

    type_emoji = {"ofz": "🏛", "corp": "🏢", "muni": "🏘"}.get(btype, "📄")
    qual_s = "Да ⚠️" if qualified else "Нет ✅" if qualified is not None else "—"

    return "\n".join([
        f"{type_emoji} *{name}*\n",
        f"Тикер: `{secid}`",
        f"ISIN: `{isin}`",
        f"Борд: {board} | Тип: {btype}\n",
        f"*💰 Цена и стоимость*",
        f"Котировка: {f(price, '%')} от номинала",
        f"Номинал: {f(face, ' ₽')}",
        f"НКД: {f(nkd, ' ₽')}",
        f"Лот: {fi(lot, ' шт.')}\n",
        f"*📈 Доходность и купон*",
        f"Доходность к погашению: {f(ytm, '%')}",
        f"Ставка купона: {f(coupon_pct, '%')}",
        f"Купон: {f(coupon_val, ' ₽')}",
        f"Период: {fi(coupon_period, ' дн.')} ({fi(coupon_freq, ' раз/год')})\n",
        f"*📅 Сроки*",
        f"Дата погашения: {mat_date}",
        f"Дней до погашения: {fi(days, ' дней')}",
        f"Оферта: {offer_date or '—'}",
        f"Дюрация: {f(duration, ' дн.')}\n",
        f"*📋 Классификация*",
        f"Уровень листинга: {fi(level)}",
        f"Только для квал.: {qual_s}",
        f"Объём торгов: {f(volume, ' ₽')}\n",
        f"_Обновлено: {updated}_",
    ])


def format_market_overview(data: dict) -> str:
    """Market overview statistics — Markdown."""
    total = data.get("total_bonds", 0)
    by_type = data.get("by_type", {})
    avg_yield = data.get("avg_yield")
    avg_coupon = data.get("avg_coupon")
    avg_duration = data.get("avg_duration")
    updated = data.get("last_updated", "—")

    def f(v, s=""):
        return f"{v:.2f}{s}" if v else "—"

    type_lines = []
    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        emoji = {"ofz": "🏛", "corp": "🏢", "muni": "🏘"}.get(t, "📄")
        type_lines.append(f"  {emoji} {t}: *{count}*")

    return "\n".join([
        f"📊 *Обзор рынка облигаций*\n",
        f"Всего облигаций: *{total}*\n",
        "*По типам:*",
        *type_lines,
        "",
        f"📈 Средняя доходность: *{f(avg_yield, '%')}*",
        f"🎫 Средний купон: *{f(avg_coupon, '%')}*",
        f"⏱ Средняя дюрация: *{f(avg_duration, ' дн.')}*\n",
        f"🕐 _Обновлено: {updated}_",
    ])
