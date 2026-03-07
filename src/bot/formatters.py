"""Format bond data for Telegram messages."""


def format_bond_card(bond: dict) -> str:
    """Format a single bond as a compact card for list view."""
    name = bond.get("short_name") or bond.get("secid", "—")
    secid = bond.get("secid", "—")
    price = bond.get("prev_price")
    ytm = bond.get("yield_at_prev_wa_price")
    coupon = bond.get("coupon_percent")
    days = bond.get("days_to_maturity")
    level = bond.get("list_level")

    price_str = f"{price:.2f}%" if price else "—"
    ytm_str = f"{ytm:.2f}%" if ytm else "—"
    coupon_str = f"{coupon:.2f}%" if coupon else "—"
    days_str = f"{days} дн." if days is not None else "—"
    level_str = f"ур.{level}" if level else "—"

    return (
        f"<b>{name}</b> ({secid})\n"
        f"  💰 Цена: {price_str} | 📈 Дох: {ytm_str}\n"
        f"  🎫 Купон: {coupon_str} | 📅 {days_str} | {level_str}"
    )


def format_bond_list(bonds: list[dict], total: int, page: int, pages: int) -> str:
    """Format a page of bonds for display."""
    if not bonds:
        return "🔍 По вашим фильтрам ничего не найдено.\nПопробуйте изменить параметры."

    header = f"📋 <b>Найдено: {total}</b> (стр. {page}/{pages})\n\n"
    cards = "\n\n".join(format_bond_card(b) for b in bonds)
    footer = "\n\n💡 <i>Нажмите на ▶️ для следующей страницы</i>"

    return header + cards + footer


def format_bond_detail(bond: dict) -> str:
    """Format detailed bond view."""
    name = bond.get("full_name") or bond.get("short_name", "—")
    secid = bond.get("secid", "—")
    isin = bond.get("isin", "—")
    board = bond.get("board_id", "—")
    bond_type = bond.get("security_type", "—")

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

    def f_float(v, suffix=""):
        return f"{v:.2f}{suffix}" if v is not None else "—"

    def f_int(v, suffix=""):
        return f"{v}{suffix}" if v is not None else "—"

    type_emoji = {"ofz": "🏛", "corp": "🏢", "muni": "🏘"}.get(bond_type, "📄")
    qual_str = "Да ⚠️" if qualified else "Нет ✅"

    lines = [
        f"{type_emoji} <b>{name}</b>",
        f"Тикер: <code>{secid}</code> | ISIN: <code>{isin}</code>",
        f"Борд: {board} | Тип: {bond_type}",
        "",
        "💰 <b>Цена и стоимость</b>",
        f"  Цена: {f_float(price, '%')} от номинала",
        f"  Номинал: {f_float(face, ' ₽')}",
        f"  НКД: {f_float(nkd, ' ₽')}",
        f"  Лот: {f_int(lot, ' шт.')}",
        "",
        "📈 <b>Доходность и купон</b>",
        f"  Доходность к погашению: {f_float(ytm, '%')}",
        f"  Ставка купона: {f_float(coupon_pct, '%')}",
        f"  Купон: {f_float(coupon_val, ' ₽')}",
        f"  Период: {f_int(coupon_period, ' дн.')} ({f_int(coupon_freq, ' раз/год')})",
        "",
        "📅 <b>Сроки</b>",
        f"  Погашение: {mat_date}",
        f"  До погашения: {f_int(days, ' дн.')}",
        f"  Оферта: {offer_date or '—'}",
        f"  Дюрация: {f_float(duration, ' дн.')}",
        "",
        "📋 <b>Классификация</b>",
        f"  Уровень листинга: {f_int(level)}",
        f"  Только квал.: {qual_str}",
        f"  Объём торгов: {f_float(volume, ' ₽')}",
    ]

    return "\n".join(lines)


def format_market_overview(data: dict) -> str:
    """Format market overview statistics."""
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
        type_lines.append(f"  {emoji} {t}: {count}")

    return "\n".join([
        "📊 <b>Обзор рынка облигаций</b>",
        "",
        f"Всего облигаций: <b>{total}</b>",
        "",
        "<b>По типам:</b>",
        *type_lines,
        "",
        f"📈 Средняя доходность: <b>{f(avg_yield, '%')}</b>",
        f"🎫 Средний купон: <b>{f(avg_coupon, '%')}</b>",
        f"⏱ Средняя дюрация: <b>{f(avg_duration, ' дн.')}</b>",
        "",
        f"🕐 Обновлено: {updated}",
    ])


def format_current_filters(filters: dict) -> str:
    """Format current filter settings for display."""
    lines = ["⚙️ <b>Текущие фильтры:</b>\n"]

    def add_range(label, key_min, key_max, suffix=""):
        v_min = filters.get(key_min)
        v_max = filters.get(key_max)
        if v_min is not None or v_max is not None:
            min_s = f"{v_min}{suffix}" if v_min is not None else "—"
            max_s = f"{v_max}{suffix}" if v_max is not None else "—"
            lines.append(f"  {label}: {min_s} — {max_s}")

    add_range("💰 Доходность", "yield_min", "yield_max", "%")
    add_range("💵 Цена", "price_min", "price_max", "%")
    add_range("🎫 Купон", "coupon_min", "coupon_max", "%")
    add_range("📅 Дней до погашения", "days_min", "days_max")

    if filters.get("security_type"):
        emoji = {"ofz": "🏛", "corp": "🏢", "muni": "🏘"}.get(filters["security_type"], "")
        lines.append(f"  📋 Тип: {emoji} {filters['security_type']}")

    if filters.get("list_level_max"):
        lines.append(f"  🏷 Макс. листинг: {filters['list_level_max']}")

    if filters.get("qualified") is not None:
        lines.append(f"  👤 Квал.: {'Все' if filters['qualified'] else 'Только неквал.'}")

    if len(lines) == 1:
        lines.append("  <i>Фильтры не заданы — покажутся все облигации</i>")

    return "\n".join(lines)
