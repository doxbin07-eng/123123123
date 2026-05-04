import os
import asyncio
from colorama import Fore, Style, init as colorama_init
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from settings import BOT_TOKEN, PASSWORD
from commands import (
    get_main_menu, get_control_menu, get_programs_menu, get_timer_menu,
    handle_timer, cancel_timer, sleep_pc, reboot_pc, shutdown_pc,
    open_chrome, open_telegram, close_telegram, is_telegram_running
)

# Инициализация цветного вывода
PINK = '\033[95m'

def animated_loading():
    colorama_init()
    print(PINK + " GEEK_BOT  Version 1.0 " + Style.RESET_ALL)
    print(PINK + " Создатели: GEEK" + Style.RESET_ALL)
    print(PINK + " Моя миссия — помогать тебе управлять ПК" + Style.RESET_ALL)

# Инициализация бота
bot = Bot(token="8550356522:AAE2y0LvFHKq-XjuZAAOG3ZXXoprnYc6XF4")
dp = Dispatcher(storage=MemoryStorage())
authorized_users = set()

@dp.message(F.text == "/start")  
async def start_handler(message: Message) -> None:  
    await message.answer_sticker("CAACAgIAAxkBAAEP1-xoTJKwEkI_hZHm6Q4gGd31ctjCtgACLBkAAh7RQElE4DTtGCLf-TYE")
    await message.answer(  
        "💖 Привет-привет! 💖\n"  
        "Я — Ася, твоя цифровая помощница! 🧸\n\n"  
        "Моя миссия — помогать тебе управлять ПК, даже если ты в пижаме 🛌\n\n"  
        "🔑 Введи пароль, и я открою тебе доступ! ✨"  
    )

@dp.message()
async def password_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in authorized_users:
        return
    
    if message.text == PASSWORD:
        await message.answer_sticker("CAACAgIAAxkBAAEP1-RoTJJ38ZEisz70JJb-jG3noNrcHQACvEMAAgjWWUv_LfJD81F1fDYE")
        await message.answer(
            "🔓 Доступ разрешен! 🔓\n\n"
            "✨ Добро пожаловать в систему управления ПК!\n"
            "🖥️ Теперь вы можете управлять компьютером удаленно.\n\n"
            "📝 Выберите действие в меню:",
            reply_markup=get_main_menu()
        )
        authorized_users.add(user_id)
    else:
        await message.answer_sticker("CAACAgIAAxkBAAEP1-hoTJKToXWiAAEmfwZya_YzpK5nyx8AAjY4AAKO87FLCdowuSW13BU2BA")
        await message.answer(
            "🚫 Ошибка доступа! 🚫\n\n"
            "❌ Введен неверный пароль.\n"
            "🔐 Пожалуйста, попробуйте еще раз.\n\n"
            "👨‍💻 Если забыли пароль, обратитесь к администратору.")

async def check_auth(callback: CallbackQuery) -> bool:
    if callback.from_user.id not in authorized_users:
        await callback.message.answer("Требуется авторизация. Введите пароль:")
        await callback.answer()
        return False
    return True

# Навигация
@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await callback.message.edit_text("📝 Выберите действие в меню:", reply_markup=get_main_menu())
    await callback.answer()

@dp.callback_query(F.data == "control_pc")
async def control_pc(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await callback.message.edit_text("👨‍💻 Меню управления ПК", reply_markup=get_control_menu())
    await callback.answer()

@dp.callback_query(F.data == "programs")
async def programs(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await callback.message.edit_text("👨‍💻 Загрузка списка программ...", reply_markup=get_programs_menu())
    await callback.answer()

@dp.callback_query(F.data == "back_control")
async def back_control(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await callback.message.edit_text("Меню управления ПК:", reply_markup=get_control_menu())
    await callback.answer()

# Команды управления
@dp.callback_query(F.data == "shutdown_timer")
async def shutdown_timer(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await callback.message.edit_text("Настройка таймера выключения:", reply_markup=get_timer_menu())
    await callback.answer()

@dp.callback_query(F.data.startswith("timer_"))
async def timer_handler(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    minutes = int(callback.data.split("_")[1])
    await handle_timer(callback, minutes)
    await back_control(callback)

@dp.callback_query(F.data == "cancel_timer")
async def cancel_timer_handler(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await cancel_timer(callback)
    await back_control(callback)

@dp.callback_query(F.data == "sleep")
async def sleep_handler(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await sleep_pc(callback)

@dp.callback_query(F.data == "reboot")
async def reboot_handler(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await reboot_pc(callback)

@dp.callback_query(F.data == "shutdown")
async def shutdown_handler(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await shutdown_pc(callback)

# Управление программами
@dp.callback_query(F.data == "chrome")
async def chrome_handler(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await open_chrome(callback)

@dp.callback_query(F.data == "telegram")
async def telegram_handler(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await open_telegram(callback)
    # Обновляем меню после изменения состояния
    try:
        await callback.message.edit_reply_markup(reply_markup=get_programs_menu())
    except Exception as e:
        print(f"Ошибка при обновлении меню: {e}")

@dp.callback_query(F.data == "close_telegram")
async def close_telegram_handler(callback: CallbackQuery) -> None:
    if not await check_auth(callback):
        return
    await close_telegram(callback)
    # Обновляем меню после изменения состояния
    try:
        await callback.message.edit_reply_markup(reply_markup=get_programs_menu())
    except Exception as e:
        print(f"Ошибка при обновлении меню: {e}")

# Запуск бота
async def main() -> None:
    animated_loading()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
