import asyncio
import os
import logging
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

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-app.up.railway.app")
PORT = int(os.getenv("PORT", 8080))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


BANNER_FILE = Path(__file__).parent / "banner.png"

WELCOME_TEXT = (
    "🎯 <b>Демо-накрутка до 10 000 лайков/просмотров — за 1 ₽</b>\n\n"
    "Наш сервис только запустился, и чтобы завоевать доверие — "
    "мы дарим каждому новому пользователю пробную накрутку "
    "<b>до 10 000 единиц всего за 1 рубль.</b>\n\n"
    "💡 Хочешь больше? Продвижение в ленту, охваты, подписчики — "
    "всё это доступно в <b>PRO-режиме</b> внутри приложения.\n\n"
    "👇 <b>Нажми кнопку, пройди за 30 секунд и получай ХАЛЯВУ прямо сейчас!</b>"
)


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть сервис",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )
    # Отправляем баннер + текст вместе
    if BANNER_FILE.exists():
        await message.answer_photo(
            photo=FSInputFile(BANNER_FILE),
            caption=WELCOME_TEXT,
            parse_mode="HTML",
            reply_markup=kb,
        )
    else:
        await message.answer(
            WELCOME_TEXT,
            parse_mode="HTML",
            reply_markup=kb,
        )
    # Кнопка «НАКРУТИТЬ» слева от поля ввода
    try:
        await bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=MenuButtonWebApp(
                text="НАКРУТИТЬ",
                web_app=WebAppInfo(url=WEBAPP_URL),
            ),
        )
    except Exception as e:
        log.warning("Could not set menu button: %s", e)


# ── Web server (раздаём index.html) ──────────────────────────────────────────

HTML_FILE = Path(__file__).parent / "index.html"


async def handle_index(request: web.Request) -> web.Response:
    return web.FileResponse(HTML_FILE)


async def handle_health(request: web.Request) -> web.Response:
    return web.Response(text="ok")


async def build_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/health", handle_health)
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
