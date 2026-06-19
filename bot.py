import asyncio
import json
import os
import logging
import urllib.parse
from pathlib import Path

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    MenuButtonWebApp,
    FSInputFile,
)
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BOT_TOKEN      = os.getenv("BOT_TOKEN")
WEBAPP_URL     = os.getenv("WEBAPP_URL", "https://your-app.up.railway.app")
PORT           = int(os.getenv("PORT", 8080))
PAYMENT_URL    = os.getenv("PAYMENT_URL", "https://onelinkgo.ru/stream/nakrutka")
ADMIN_CHAT_ID  = int(os.getenv("ADMIN_CHAT_ID", 0))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment")

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()

BANNER_FILE = Path(__file__).parent / "banner.png"

WELCOME_TEXT = (
    "🎯 <b>Демо-накрутка до 10 000 лайков/просмотров — за 1 ₽</b>\n\n"
    "Наш сервис только запустился, и чтобы завоевать доверие — "
    "мы дарим каждому новому пользователю пробную накрутку "
    "<b>до 10 000 единиц всего за 1 рубль.</b>\n\n"
    "💡 Хочешь больше? Продвижение в ленту, охваты, подписчики — "
    "всё это доступно в <b>PRO-режиме</b> внутри приложения.\n\n"
    "👇 <b>Нажми кнопку, пройди за 30 секунд и получай ХАЛЯВУ прямо сейчас!</b>\n\n"
    "⚠️ Если накрутка не началась в течение 24 часов после оплаты — пишите в поддержку @nagievChina"
)

PAYMENT_TEXT = (
    "🎁 <b>Получай подарок и доступ к аналитике за 1 рубль!</b>\n\n"
    "Твоя заявка на накрутку готова — осталось оплатить всего <b>1 ₽</b>\n\n"
    "После оплаты:\n"
    "✅ Накрутка запустится автоматически\n"
    "✅ Доступ к аналитике на 5 дней\n"
    "✅ Шанс выиграть подарок от партнёра\n\n"
    "🔥 Только что оплатили: @shpeeeeh, @nagievChina\n\n"
    "👇 Нажми кнопку и оплати 1 ₽\n\n"
    "‼️ <b>ОБЯЗАТЕЛЬНО НАЖМИ ВСЕ ГАЛОЧКИ И ОПЛАТИ</b> ‼️"
)

FOLLOWUP_TEXT = (
    "👋 Эй! Твоя заявка на накрутку всё ещё ждёт оплаты.\n\n"
    "Не потеряй своё место — заявки хранятся 24 часа, потом сгорают 🔥\n\n"
    "Напомнить когда будешь готов оплатить?"
)


@dp.message(Command("myid"))
async def cmd_myid(message: types.Message) -> None:
    await message.answer(f"Твой chat_id: <code>{message.chat.id}</code>", parse_mode="HTML")


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    if ADMIN_CHAT_ID:
        u = message.from_user
        name = f"{u.first_name or ''} {u.last_name or ''}".strip()
        username = f"@{u.username}" if u.username else "—"
        from datetime import datetime, timezone, timedelta
        msk = datetime.now(timezone(timedelta(hours=3))).strftime("%d.%m.%Y в %H:%M")
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=(
                    f"👤 <b>Новый пользователь!</b>\n"
                    f"Имя: {name}\n"
                    f"Ник: {username}\n"
                    f"ID: <code>{u.id}</code>\n"
                    f"🕐 {msk}"
                ),
                parse_mode="HTML",
            )
        except Exception as e:
            log.warning("Admin notify failed: %s", e)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🚀 Открыть сервис", web_app=WebAppInfo(url=WEBAPP_URL))
        ]]
    )
    if BANNER_FILE.exists():
        await message.answer_photo(
            photo=FSInputFile(BANNER_FILE),
            caption=WELCOME_TEXT,
            parse_mode="HTML",
            reply_markup=kb,
        )
    else:
        await message.answer(WELCOME_TEXT, parse_mode="HTML", reply_markup=kb)

    try:
        await bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=MenuButtonWebApp(text="НАКРУТИТЬ", web_app=WebAppInfo(url=WEBAPP_URL)),
        )
    except Exception as e:
        log.warning("Could not set menu button: %s", e)


# ── Delayed messages ─────────────────────────────────────────────────────────

async def send_delayed_payment(chat_id: int) -> None:
    await asyncio.sleep(120)  # 2 minutes
    try:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="💳 Оплатить 1 ₽", url=PAYMENT_URL)
            ]]
        )
        if BANNER_FILE.exists():
            await bot.send_photo(
                chat_id=chat_id,
                photo=FSInputFile(BANNER_FILE),
                caption=PAYMENT_TEXT,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=PAYMENT_TEXT,
                parse_mode="HTML",
                reply_markup=kb,
            )
        log.info("Payment message sent to %d", chat_id)
    except Exception as e:
        log.error("Failed to send payment message to %d: %s", chat_id, e)


async def send_followup(chat_id: int) -> None:
    await asyncio.sleep(6 * 3600)  # 6 hours
    try:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Да, напомни!", callback_data="remind"),
            InlineKeyboardButton(text="❌ Не надо",     callback_data="cancel"),
        ]])
        await bot.send_message(chat_id=chat_id, text=FOLLOWUP_TEXT, reply_markup=kb)
        log.info("Follow-up sent to %d", chat_id)
    except Exception as e:
        log.error("Failed to send followup to %d: %s", chat_id, e)


@dp.callback_query(lambda c: c.data == "remind")
async def cb_remind(callback: types.CallbackQuery) -> None:
    await callback.answer()
    await callback.message.delete()
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="💳 Оплатить 1 ₽", url=PAYMENT_URL)
    ]])
    if BANNER_FILE.exists():
        await callback.message.answer_photo(
            photo=FSInputFile(BANNER_FILE),
            caption=PAYMENT_TEXT,
            parse_mode="HTML",
            reply_markup=kb,
        )
    else:
        await callback.message.answer(PAYMENT_TEXT, parse_mode="HTML", reply_markup=kb)


@dp.callback_query(lambda c: c.data == "cancel")
async def cb_cancel(callback: types.CallbackQuery) -> None:
    await callback.answer("Понял! Если передумаешь — мы тут 😊")
    await callback.message.delete()


# ── Web server ────────────────────────────────────────────────────────────────

HTML_FILE = Path(__file__).parent / "index.html"


async def handle_index(request: web.Request) -> web.Response:
    return web.FileResponse(HTML_FILE)


async def handle_health(request: web.Request) -> web.Response:
    return web.Response(text="ok")


async def handle_order(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        init_data = data.get("initData", "")
        parsed    = urllib.parse.parse_qs(init_data)
        user_str  = parsed.get("user", ["{}"])[0]
        user      = json.loads(user_str)
        chat_id   = user.get("id")

        if chat_id:
            log.info("Order received from %d — scheduling payment + followup", chat_id)
            asyncio.create_task(send_delayed_payment(int(chat_id)))
            asyncio.create_task(send_followup(int(chat_id)))
        else:
            log.warning("Order received but could not parse chat_id from initData")
    except Exception as e:
        log.error("handle_order error: %s", e)

    return web.Response(text="ok")


async def build_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/",        handle_index)
    app.router.add_get("/health",  handle_health)
    app.router.add_post("/order",  handle_order)
    return app


async def main() -> None:
    app = await build_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info("Web server started on port %d  →  %s", PORT, WEBAPP_URL)

    log.info("Bot polling started")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
