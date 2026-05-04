import asyncio
from colorama import Style, init as colorama_init

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage

from settings import BOT_TOKEN, PASSWORD
from commands import (
    get_main_menu, get_control_menu, get_programs_menu, get_timer_menu,
    handle_timer, cancel_timer, sleep_pc, reboot_pc, shutdown_pc,
    open_chrome, open_telegram, close_telegram
)

# ====== INIT ======
PINK = '\033[95m'
authorized_users = set()


def animated_loading():
    colorama_init()
    print(PINK + "GEEK_BOT v1.0" + Style.RESET_ALL)
    print(PINK + "Запуск..." + Style.RESET_ALL)


# ====== BOT ======
bot = Bot(token=8550356522:AAEvWF2zclndI1pWvl4zG9S1oz8L_LJY1yk)
dp = Dispatcher(storage=MemoryStorage())


# ====== START ======
@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        "💖 Привет!\n"
        "Я бот для управления ПК.\n\n"
        "🔐 Введите пароль:"
    )


# ====== PASSWORD ======
@dp.message(F.text)
async def password_handler(message: Message):
    user_id = message.from_user.id
    text = message.text

    if not text:
        return

    # уже авторизован
    if user_id in authorized_users:
        return

    # проверка пароля
    if text == PASSWORD:
        authorized_users.add(user_id)

        await message.answer(
            "🔓 Доступ разрешён!",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer("❌ Неверный пароль")


# ====== CHECK AUTH ======
async def check_auth(callback: CallbackQuery) -> bool:
    if callback.from_user.id not in authorized_users:
        await callback.answer("Нет доступа", show_alert=True)
        return False
    return True


# ====== NAVIGATION ======
@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    if not await check_auth(callback):
        return

    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "control_pc")
async def control_pc(callback: CallbackQuery):
    if not await check_auth(callback):
        return

    await callback.message.edit_text(
        "Управление ПК:",
        reply_markup=get_control_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "programs")
async def programs(callback: CallbackQuery):
    if not await check_auth(callback):
        return

    await callback.message.edit_text(
        "Программы:",
        reply_markup=get_programs_menu()
    )
    await callback.answer()


# ====== POWER ======
@dp.callback_query(F.data == "sleep")
async def sleep_handler(callback: CallbackQuery):
    if not await check_auth(callback):
        return
    await sleep_pc(callback)
    await callback.answer()


@dp.callback_query(F.data == "reboot")
async def reboot_handler(callback: CallbackQuery):
    if not await check_auth(callback):
        return
    await reboot_pc(callback)
    await callback.answer()


@dp.callback_query(F.data == "shutdown")
async def shutdown_handler(callback: CallbackQuery):
    if not await check_auth(callback):
        return
    await shutdown_pc(callback)
    await callback.answer()


# ====== PROGRAMS ======
@dp.callback_query(F.data == "chrome")
async def chrome_handler(callback: CallbackQuery):
    if not await check_auth(callback):
        return
    await open_chrome(callback)
    await callback.answer()


@dp.callback_query(F.data == "telegram")
async def telegram_handler(callback: CallbackQuery):
    if not await check_auth(callback):
        return
    await open_telegram(callback)
    await callback.answer()


@dp.callback_query(F.data == "close_telegram")
async def close_telegram_handler(callback: CallbackQuery):
    if not await check_auth(callback):
        return
    await close_telegram(callback)
    await callback.answer()


# ====== TIMER ======
@dp.callback_query(F.data.startswith("timer_"))
async def timer_handler(callback: CallbackQuery):
    if not await check_auth(callback):
        return

    try:
        minutes = int(callback.data.split("_")[1])
        await handle_timer(callback, minutes)
    except Exception as e:
        await callback.message.answer(f"Ошибка таймера: {e}")

    await callback.answer()


@dp.callback_query(F.data == "cancel_timer")
async def cancel_timer_handler(callback: CallbackQuery):
    if not await check_auth(callback):
        return

    await cancel_timer(callback)
    await callback.answer()


# ====== MAIN ======
async def main():
    animated_loading()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
