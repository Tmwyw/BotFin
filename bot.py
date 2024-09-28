import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
import random
import os
import time
from pocketoptionapi.stable_api import PocketOption  # Убедись, что у тебя есть такая библиотека

# Подключение к Pocket Option API
def connect_pocket_option():
    ssid = os.getenv('42["auth", {"session":"ugceh9llu62egeenpnhalb629n", "isDemo":1, "uid":85002634, "platform":2}]') # Используй правильный SSID сессии для авторизации
    api = PocketOption(ssid)
    check_connect, message = api.connect()

    if check_connect:
        print("Подключение к Pocket Option успешно!")
        return api
    else:
        print(f"Ошибка подключения к Pocket Option: {message}")
        return None

# Функция для получения курса валют с использованием Pocket Option API
def get_currency_rate(base_currency, target_currency, api):
    asset = f"{base_currency}_{target_currency}"  # Пример: EUR_USD
    candles = api.get_candles(asset, 60)  # Получаем последние 60 секунд свечи

    if candles:
        current_price = candles[-1]['close']  # Цена закрытия последней свечи
        return current_price
    else:
        print(f"Не удалось получить данные для {asset}")
        return None

# Функция для генерации LONG-сигнала
def generate_long_signal(base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss):
    signal = (
        f"🔥LONG🟢🔼\n\n"
        f"🔥#{base_currency}/{target_currency}☝️\n\n"
        f"💵Текущая цена:📈 {current_price}\n\n"
        f"🎯Take Profit 1: 📌{take_profit1}\n"
        f"🎯Take Profit 2: 📌{take_profit2}\n\n"
        f"⛔️STOP💥{stop_loss}\n\n"
    )
    return signal

# Функция для генерации SHORT-сигнала
def generate_short_signal(base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss):
    signal = (
        f"🔥SHORT🔴🔽\n\n"
        f"🔥#{base_currency}/{target_currency}☝️\n\n"
        f"💵Текущая цена:📉 {current_price}\n\n"
        f"🎯Take Profit 1: 📌{take_profit1}\n"
        f"🎯Take Profit 2: 📌{take_profit2}\n\n"
        f"🚫STOP💥{stop_loss}"
    )
    return signal

# Асинхронная функция для отправки сигналов по валютным парам
async def send_signals(update: Update, context):
    api = connect_pocket_option()  # Подключаемся к Pocket Option
    if api is None:
        await context.bot.send_message(chat_id=update.message.chat_id, text="Ошибка подключения к Pocket Option.")
        return

    chat_id = update.message.chat_id
    
    CURRENCY_PAIRS = [
        ('EUR', 'USD'),
        ('GBP', 'USD'),
        ('AUD', 'USD'),
        ('USD', 'JPY'),
        ('USD', 'TRY')
    ]

    for base_currency, target_currency in CURRENCY_PAIRS:  # Проходим по валютным парам
        current_price = get_currency_rate(base_currency, target_currency, api)
        if current_price:
            # Случайный выбор между LONG и SHORT
            if random.choice([True, False]):
                # LONG: Take Profit выше цены, Stop Loss ниже
                take_profit1 = current_price * 1.05  # Например, 5% выше текущей цены
                take_profit2 = current_price * 1.1   # Например, 10% выше текущей цены
                stop_loss = current_price * 0.95    # Например, 5% ниже текущей цены
                signal = generate_long_signal(base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss)
            else:
                # SHORT: Take Profit ниже цены, Stop Loss выше
                take_profit1 = current_price * 0.95  # Например, 5% ниже текущей цены
                take_profit2 = current_price * 0.9   # Например, 10% ниже текущей цены
                stop_loss = current_price * 1.05    # Например, 5% выше текущей цены
                signal = generate_short_signal(base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss)
            
            await context.bot.send_message(chat_id=chat_id, text=signal)
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"Не удалось получить данные для {base_currency}/{target_currency}")

# Обработчик команды /start
async def start(update: Update, context):
    await send_signals(update, context)

# Обработчик команды /stop для остановки сигналов
async def stop(update: Update, context):
    await update.message.reply_text("Генерация сигналов остановлена.")

# Основная функция
def main():
    print("Запуск бота")  # Отладочное сообщение
    
    # Получаем токен из переменной окружения
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Создание приложения с поддержкой JobQueue
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем команды /start и /stop
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))

    print("Начало выполнения run_polling()")  # Отладочное сообщение
    app.run_polling()
    print("После выполнения run_polling()")  # Отладочное сообщение

if __name__ == '__main__':
    main()
