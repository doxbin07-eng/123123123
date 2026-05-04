import os
import asyncio
import subprocess
import psutil
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Проверка, запущен ли Telegram
def is_telegram_running() -> bool:
    try:
        return "Telegram.exe" in (p.name() for p in psutil.process_iter())
    except:
        return False

# Меню
def get_main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Управление ПК", callback_data="control_pc")
    builder.button(text="Программы", callback_data="programs")
    builder.adjust(2)
    return builder.as_markup()

def get_control_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Спящий режим", callback_data="sleep"),
        InlineKeyboardButton(text="Перезагрузка", callback_data="reboot"),
        InlineKeyboardButton(text="Выключение", callback_data="shutdown"),
        InlineKeyboardButton(text="Таймер выключения", callback_data="shutdown_timer"),
        InlineKeyboardButton(text="Назад", callback_data="back_main")
    )
    builder.adjust(2)
    return builder.as_markup()

def get_programs_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Динамическая кнопка Telegram
    telegram_running = is_telegram_running()
    telegram_button = InlineKeyboardButton(
        text="Закрыть Telegram" if telegram_running else "Telegram",
        callback_data="close_telegram" if telegram_running else "telegram"
    )
    
    builder.add(
        InlineKeyboardButton(text="Chrome", callback_data="chrome"),
        telegram_button,
        InlineKeyboardButton(text="Назад", callback_data="back_main")
    )
    builder.adjust(2)
    return builder.as_markup()

def get_timer_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="30 мин", callback_data="timer_30"),
        InlineKeyboardButton(text="1 час", callback_data="timer_60"),
        InlineKeyboardButton(text="2 часа", callback_data="timer_120"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel_timer"),
        InlineKeyboardButton(text="Назад", callback_data="back_control")
    )
    builder.adjust(3, 2)
    return builder.as_markup()

# Команды управления
async def handle_timer(callback: CallbackQuery, minutes: int) -> None:
    seconds = minutes * 60
    os.system(f"shutdown -s -t {seconds}")
    await callback.answer(f"Скрипт: выключение через {minutes} минут", show_alert=True)

async def cancel_timer(callback: CallbackQuery) -> None:
    os.system("shutdown -a")
    await callback.answer("Скрипт: отмена таймера", show_alert=True)

async def sleep_pc(callback: CallbackQuery) -> None:
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

async def reboot_pc(callback: CallbackQuery) -> None:
    os.system("shutdown -r -t 0")

async def shutdown_pc(callback: CallbackQuery) -> None:
    os.system("shutdown -s -t 0")

# Управление программами
async def open_chrome(callback: CallbackQuery) -> None:
    try:
        subprocess.Popen(["start", "chrome"], shell=True)
        await callback.answer("Chrome запускается...")
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)

async def open_telegram(callback: CallbackQuery) -> None:
    try:
        telegram_path = os.path.join(os.getenv('APPDATA'), 'Telegram Desktop', 'Telegram.exe')
        if not os.path.exists(telegram_path):
            await callback.answer("Telegram не найден", show_alert=True)
            return
        
        subprocess.Popen(telegram_path, shell=True)
        await asyncio.sleep(2)
        await callback.answer("Telegram запущен")
        
    except Exception as e:
        error_msg = str(e)[:100]
        await callback.answer(f"Ошибка: {error_msg}", show_alert=True)

async def close_telegram(callback: CallbackQuery) -> None:
    try:
        closed = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'Telegram.exe':
                proc.kill()
                closed = True
        
        if closed:
            await asyncio.sleep(1)
            await callback.answer("Telegram закрыт")
        else:
            await callback.answer("Telegram не запущен", show_alert=True)
            
    except Exception as e:
        error_msg = str(e)[:100]
        await callback.answer(f"Ошибка: {error_msg}", show_alert=True)