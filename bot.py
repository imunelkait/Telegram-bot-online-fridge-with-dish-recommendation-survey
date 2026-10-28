# -*- coding: utf-8 -*-
"""Телеграм-бот «Онлайн-холодильник» (aiogram 3).

Функционал:
  /start          — приветствие и меню;
  Холодильник     — пользователь списком указывает продукты, бот запоминает
                    (SQLite, переживает перезапуск);
  Что приготовить — пошаговый опрос:
      1. Какую еду предпочитаем? (мясо / рыба / крупы / овощи / суп / сладкое / любая)
      2. Нужна ли диета? Если да — какая и на какой период (в днях);
      3. Сложность приготовления (по умению и времени);
      4. Чего конкретно хочется сейчас?
    После этого бот предлагает случайное блюдо из подходящих под холодильник.
  /fridge         — посмотреть список продуктов;
  /clear          — очистить холодильник;
  /diet           — показать/сбросить активную диету и её срок.

Запуск:
    export BOT_TOKEN="токен от @BotFather"
    python bot.py
"""

import asyncio
import logging
import os
import sqlite3
from datetime import date, timedelta

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from dishes import CATEGORIES, DIETS, DIFFICULTIES
from fridge_logic import filter_dishes, parse_products, pick_random

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("Не задан BOT_TOKEN. Экспортируйте токен от @BotFather.")

DB_PATH = os.getenv("DB_PATH", "fridge.db")

router = Router()

# ---------------------------------------------------------------- БД ---------


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS fridge ("
        " user_id INTEGER, product TEXT, PRIMARY KEY (user_id, product))"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS diets ("
        " user_id INTEGER PRIMARY KEY, diet TEXT, until TEXT)"
    )
    conn.commit()
    return conn


def get_fridge(user_id: int) -> list[str]:
    with db() as conn:
        rows = conn.execute(
            "SELECT product FROM fridge WHERE user_id=? ORDER BY product", (user_id,)
        ).fetchall()
    return [r[0] for r in rows]


def set_fridge(user_id: int, products: list[str]) -> None:
    with db() as conn:
        conn.execute("DELETE FROM fridge WHERE user_id=?", (user_id,))
        conn.executemany(
            "INSERT OR IGNORE INTO fridge VALUES (?, ?)",
            [(user_id, p) for p in products],
        )
        conn.commit()


def clear_fridge(user_id: int) -> None:
    with db() as conn:
        conn.execute("DELETE FROM fridge WHERE user_id=?", (user_id,))
        conn.commit()


def get_diet(user_id: int) -> tuple[str | None, str | None]:
    """Возвращает (диета, до_какой_даты) или (None, None), если диеты нет/истекла."""
    with db() as conn:
        row = conn.execute(
            "SELECT diet, until FROM diets WHERE user_id=?", (user_id,)
        ).fetchone()
    if not row:
        return None, None
    if row[1] and row[1] < date.today().isoformat():  # срок вышел
        conn = db()
        conn.execute("DELETE FROM diets WHERE user_id=?", (user_id,))
        conn.commit()
        return None, None
    return row[0], row[1]


def set_diet(user_id: int, diet: str, days: int) -> None:
    until = (date.today() + timedelta(days=days)).isoformat()
    with db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO diets VALUES (?, ?, ?)", (user_id, diet, until)
        )
        conn.commit()


# ------------------------------------------------------------- КЛАВИАТУРЫ ----

kb_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧊 Мой холодильник"), KeyboardButton(text="➕ Обновить продукты")],
        [KeyboardButton(text="🍳 Что приготовить?"), KeyboardButton(text="🗑 Очистить холодильник")],
    ],
    resize_keyboard=True,
)

kb_yesno = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")],
        [KeyboardButton(text="⬅ Отмена")],
    ],
    resize_keyboard=True,
)


def kb_options(mapping: dict, cols: int = 2, cancel: bool = True) -> ReplyKeyboardMarkup:
    buttons, row = [], []
    for key, label in mapping.items():
        row.append(KeyboardButton(text=f"{key}::{label}"))
        if len(row) == cols:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    if cancel:
        buttons.append([KeyboardButton(text="⬅ Отмена")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def parse_choice(text: str) -> str:
    """Из кнопки вида 'meat::🥩 Мясо' возвращает 'meat'."""
    return text.split("::", 1)[0]


# --------------------------------------------------------------- ХЭНДЛЕРЫ ----

STATE_WAIT_PRODUCTS = "wait_products"          # ждём список продуктов
STATE_ASK_PREFERENCE = "ask_preference"        # шаг 1: какую еду предпочитаем
STATE_ASK_DIET = "ask_diet"                    # шаг 2: нужна ли диета
STATE_ASK_DIET_TYPE = "ask_diet_type"          # шаг 2a: какая диета
STATE_ASK_DIET_PERIOD = "ask_diet_period"      # шаг 2b: на какой период
STATE_ASK_DIFFICULTY = "ask_difficulty"        # шаг 3: сложность
STATE_ASK_CRAVING = "ask_craving"              # шаг 4: чего хочется конкретно
STATE_AGAIN = "again"                          # блюдо показано, можно «Ещё»

# Промежуточные ответы пользователя в рамках одного диалога
session: dict[int, dict] = {}


def is_survey_state(state: str | None) -> bool:
    return state in (
        STATE_ASK_PREFERENCE, STATE_ASK_DIET, STATE_ASK_DIET_TYPE,
        STATE_ASK_DIET_PERIOD, STATE_ASK_DIFFICULTY, STATE_ASK_CRAVING,
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    fridge = get_fridge(message.from_user.id)
    hint = (
        f"\n🧊 В холодильнике: {', '.join(fridge)}"
        if fridge
        else "\nПока холодильник пуст — нажмите «➕ Обновить продукты»."
    )
    await message.answer(
        "🤖 Привет! Я бот «Онлайн-холодильник».\n\n"
        "1️⃣ Нажмите «➕ Обновить продукты» и перечислите через запятую, "
        "что есть у вас в холодильнике. Я всё запомню.\n"
        "2️⃣ Нажмите «🍳 Что приготовить?» — я задам 4 вопроса "
        "(предпочтения, диета, сложность, чего хочется) и предложу случайное "
        "блюдо, которое реально приготовить из ваших продуктов.\n"
        f"{hint}",
        reply_markup=kb_main,
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Команды:\n"
        "/start — меню\n"
        "/add — обновить список продуктов\n"
        "/fridge — посмотреть продукты\n"
        "/clear — очистить холодильник\n"
        "/cook — подобрать блюдо\n"
        "/diet — информация об активной диете",
        reply_markup=kb_main,
    )


@router.message(Command("fridge"))
async def cmd_fridge(message: Message):
    fridge = get_fridge(message.from_user.id)
    text = "🧊 В холодильнике: " + (", ".join(fridge) if fridge else "пусто 😔")
    await message.answer(text, reply_markup=kb_main)


@router.message(Command("clear"))
async def cmd_clear(message: Message):
    clear_fridge(message.from_user.id)
    await message.answer("🧊 Холодильник очищен.", reply_markup=kb_main)


@router.message(Command("diet"))
async def cmd_diet(message: Message):
    diet, until = get_diet(message.from_user.id)
    if diet:
        await message.answer(
            f"🥗 Активная диета: {DIETS.get(diet, diet)} до {until}.",
            reply_markup=kb_main,
        )
    else:
        await message.answer(
            "🥗 Диета не активна. Назначить можно во время опроса «🍳 Что приготовить?».",
            reply_markup=kb_main,
        )


# —— Функция «Холодильник»: ввод продуктов ————————————————

@router.message(F.text == "➕ Обновить продукты")
@router.message(Command("add"))
async def ask_products(message: Message):
    session.setdefault(message.from_user.id, {})["state"] = STATE_WAIT_PRODUCTS
    await message.answer(
        "🧾 Перечислите продукты через запятую (или каждый с новой строки):\n"
        "Например: <i>картошка, морковь, курица, яйца, молоко, гречка</i>\n\n"
        "Бот запомнит их — можно будет возвращаться к подбору блюд в любой момент.\n"
        "(Новые продукты добавляются к уже сохранённым; «🗑 Очистить холодильник» — начать с чистого листа.)",
    )


@router.message(F.text == "🧊 Мой холодильник")
async def btn_fridge(message: Message):
    await cmd_fridge(message)


@router.message(F.text == "🗑 Очистить холодильник")
async def btn_clear(message: Message):
    await cmd_clear(message)


@router.message(F.text.in_({"🍳 Что приготовить?", "/cook"}))
async def btn_cook(message: Message):
    await start_cook_flow(message)


@router.message(F.text.in_({"Ещё", "ещё", "🎲 Ещё вариант"}))
async def another_dish(message: Message):
    uid = message.from_user.id
    s = session.get(uid, {})
    if s.get("state") != STATE_AGAIN:
        await start_cook_flow(message)
        return
    await suggest_dish(message, dict(s["params"]), uid)


@router.message(F.text == "⬅ Отмена")
async def btn_cancel(message: Message):
    session.pop(message.from_user.id, None)
    await message.answer("Ок, отменил. Возвращаемся в меню.", reply_markup=kb_main)


# —— Подбор блюда: пошаговый опрос —————————————————————————

async def start_cook_flow(message: Message):
    uid = message.from_user.id
    if not get_fridge(uid):
        await message.answer(
            "Сначала расскажите, что лежит в холодильнике 😊\nНажмите «➕ Обновить продукты».",
            reply_markup=kb_main,
        )
        return
    session[uid] = {"state": STATE_ASK_PREFERENCE}
    await message.answer(
        "1️⃣ Какую еду предпочитаем?",
        reply_markup=kb_options(CATEGORIES),
    )


async def ask_difficulty(message: Message, s: dict):
    s["state"] = STATE_ASK_DIFFICULTY
    await message.answer(
        "3️⃣ Насколько сложное блюдо готовы готовить? (умение + время)",
        reply_markup=kb_options(DIFFICULTIES, cols=1, cancel=False),
    )


async def suggest_dish(message: Message, s: dict, uid: int):
    fridge = get_fridge(uid)
    diet_active, _ = get_diet(uid)
    diet = s.get("diet") or diet_active or "none"
    difficulty = s["difficulty"]
    category = s["category"]
    craving = s.get("craving", "any")

    candidates = filter_dishes(fridge, category, diet, difficulty)
    used_fallback = False

    # Если по сочетанию «предпочтение + хотелка» пусто — пробуем по «хотелке»,
    # затем постепенно снижаем требования.
    if not candidates and craving not in ("any", "surprise"):
        candidates = filter_dishes(fridge, craving, diet, difficulty)
    if not candidates:
        used_fallback = True
        candidates = filter_dishes(fridge, "any", "none", difficulty, min_coverage=40)
    if not candidates:
        candidates = filter_dishes(fridge, "any", "none", "hard", min_coverage=30)
    if not candidates:
        session.pop(uid, None)
        await message.answer(
            "😔 Из таких продуктов с такими пожеланиями ничего не подбирается.\n"
            "Добавьте продукты («➕ Обновить продукты») и попробуйте снова.",
            reply_markup=kb_main,
        )
        return

    # Не повторяем то же блюдо подряд: если вариантов больше одного — исключаем прошлое
    last = s.get("last")
    if len(candidates) > 1 and last is not None:
        filtered = [c for c in candidates if c[0]["name"] != last]
        if filtered:
            candidates = filtered

    pick = pick_random(candidates)
    dish, cov, have, miss = pick["dish"], pick["coverage"], pick["have"], pick["miss"]
    s["last"] = dish["name"]

    lines = [
        f"🍽 <b>{dish['name']}</b>",
        "",
        f"⏱ Время: ~{dish['time']} мин | Сложность: {DIFFICULTIES[dish['difficulty']]}",
        f"📊 Подходит вашим продуктам на {cov:.0f}%",
    ]
    if have:
        lines.append(f"✅ Есть в холодильнике: {', '.join(have)}")
    if miss:
        lines.append(f"➕ Не хватает: {', '.join(miss)}")
    if used_fallback:
        lines.append("\nℹ️ Точных совпадений не нашлось — предложил самое близкое.")
    lines.append("\nХотите ещё вариант? Напишите «Ещё» 🎲")

    session[uid] = {"state": STATE_AGAIN, "params": s}
    await message.answer("\n".join(lines), reply_markup=kb_main)


@router.message(F.text)
async def on_survey(message: Message):
    """Обрабатывает ответы опроса (и ввод списка продуктов)."""
    uid = message.from_user.id
    s = session.get(uid)
    text = (message.text or "").strip()

    # Ввод списка продуктов
    if s and s.get("state") == STATE_WAIT_PRODUCTS:
        products = parse_products(text)
        if not products:
            await message.answer(
                "Не получилось распознать продукты 🤔 Попробуйте ещё раз, "
                "например: картошка, яйца, курица"
            )
            return
        merged = get_fridge(uid)
        for p in products:
            if p not in merged:
                merged.append(p)
        set_fridge(uid, merged)
        session.pop(uid, None)
        await message.answer(
            f"✅ Запомнил! Теперь в холодильнике: {', '.join(merged)}\n\n"
            "Нажмите «🍳 Что приготовить?», чтобы подобрать блюдо.",
            reply_markup=kb_main,
        )
        return

    # Ответы на вопросы опроса
    if s and is_survey_state(s.get("state")):
        state = s["state"]

        if state == STATE_ASK_PREFERENCE:
            if "::" not in text:
                await message.answer("Выберите вариант кнопкой 🙂")
                return
            s["category"] = parse_choice(text)
            s["state"] = STATE_ASK_DIET
            diet, until = get_diet(uid)
            extra = f"\n(У вас уже активна диета: {DIETS[diet]} до {until})" if diet else ""
            await message.answer(
                f"2️⃣ Нужна ли диета?{extra}\n"
                "Если да — спрошу, какую и на какой период.",
                reply_markup=kb_yesno,
            )
            return

        if state == STATE_ASK_DIET:
            if text == "✅ Да":
                s["state"] = STATE_ASK_DIET_TYPE
                await message.answer(
                    "Какая диета?",
                    reply_markup=kb_options(DIETS, cols=1, cancel=False),
                )
            elif text == "❌ Нет":
                s["diet"] = None
                await ask_difficulty(message, s)
            else:
                await message.answer("Нажмите «Да» или «Нет» 🙂", reply_markup=kb_yesno)
            return

        if state == STATE_ASK_DIET_TYPE:
            if "::" not in text:
                await message.answer("Выберите диету кнопкой 🙂")
                return
            s["diet"] = parse_choice(text)
            s["state"] = STATE_ASK_DIET_PERIOD
            await message.answer(
                "На какой период соблюдаем диету?\n"
                "Введите количество дней, например: <b>14</b>"
            )
            return

        if state == STATE_ASK_DIET_PERIOD:
            digits = "".join(ch for ch in text if ch.isdigit())
            if not digits or not (1 <= int(digits) <= 365):
                await message.answer("Введите число от 1 до 365 🙂")
                return
            days = int(digits)
            set_diet(uid, s["diet"], days)
            until = (date.today() + timedelta(days=days)).isoformat()
            await message.answer(f"🥗 Записал: диета «{DIETS[s['diet']]}» до {until}.")
            await ask_difficulty(message, s)
            return

        if state == STATE_ASK_DIFFICULTY:
            if "::" not in text:
                await message.answer("Выберите сложность кнопкой 🙂")
                return
            s["difficulty"] = parse_choice(text)
            s["state"] = STATE_ASK_CRAVING
            craving_map = {**CATEGORIES, "surprise": "🎲 На твой вкус!"}
            await message.answer(
                "4️⃣ Чего хочется конкретно сейчас? "
                "(мясо, крупа, овощи… — учту как дополнительное пожелание)",
                reply_markup=kb_options(craving_map),
            )
            return

        if state == STATE_ASK_CRAVING:
            if "::" not in text:
                await message.answer("Выберите вариант кнопкой 🙂")
                return
            s["craving"] = parse_choice(text)
            await suggest_dish(message, s, uid)
            return

    # Ничего не подошло
    await message.answer(
        "Я не понял 🤷 Выберите действие на клавиатуре ниже или /help",
        reply_markup=kb_main,
    )


def _make_session():
    """Сессия aiogram с поддержкой прокси.

    Если в окружении задан PROXY_URL (например
    socks5://user:pass@host:1080 или http://host:port), бот пойдёт через прокси.
    Для http/https-прокси дополнительно подставляется aiohttp TrustEnv,
    чтобы учитывались стандартные переменные HTTPS_PROXY.
    """
    proxy_url = os.getenv("PROXY_URL")
    kwargs = {}
    if proxy_url:
        kwargs["proxy"] = proxy_url
        if proxy_url.startswith(("http://", "https://")):
            import aiohttp
            kwargs["trust_env"] = True
    return AiohttpSession(**kwargs)


async def main():
    # get_me() с понятной подсказкой, если Telegram недоступен
    bot = Bot(token=BOT_TOKEN, session=_make_session())
    try:
        me = await bot.get_me()
    except Exception as e:
        await bot.session.close()  # чтобы не осталось "Unclosed client session"
        print(f"Не удалось подключиться к Telegram API: {e}")
        print(
            "\nЧастые причины:\n"
            "  1) api.telegram.org заблокирован провайдером (в РФ бывает)\n"
            "     -> поставьте прокси для Telegram и запустите так:\n"
            "        export PROXY_URL=\"socks5://хост:порт\"   (Linux/macOS)\n"
            "        set PROXY_URL=socks5://хост:порт        (Windows cmd)\n"
            "  2) нет интернета / режет антивирус или файрвол\n"
            "  3) неверный токен (обычно даёт 401 Unauthorized)\n"
        )
        raise SystemExit(1)
    print(f"Бот @{me.username} запущен и работает... (Ctrl+C — остановить)")

    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")
