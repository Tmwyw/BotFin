import asyncio
import websockets
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
import random
import matplotlib.pyplot as plt
import io
from telegram import InputFile
import os
import requests
import numpy as np
from iqoptionapi.api import IQOptionAPI
from datetime import datetime
logging.disable(level=(logging.DEBUG))

# Подключение к IQ Option API
def connect_iq_option():
    API = IQOption("nik.2ch@gmail.com", "#U6dq$G!Ez65ad45F&gm")
    API.connect()
    API.changebalance("PRACTICE")  # или REAL

    if API.checkconnect():
        print("Успешное подключение к IQ Option")
        return API
    else:
        print("Ошибка подключения")
        return None

# Получение текущей цены валютной пары
def get_current_price(api, paridade="EURUSD", timeframe=1):
    status, candles = api.get_candles(paridade, 60, 1, time.time())
    if status:
        return candles[0]['close']
    else:
        print(f"Ошибка получения данных для {paridade}")
        return None

# Генерация сигнала LONG
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

# Генерация сигнала SHORT
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

# Отправка сигналов по валютным парам
async def send_signals(update: Update, context):
    chat_id = update.message.chat_id

    # Подключение к IQ Option
    api = connect_iq_option()
    if not api:
        await context.bot.send_message(chat_id=chat_id, text="Ошибка подключения к IQ Option")
        return
    
    base_currency, target_currency = "EUR", "USD"
    current_price = get_current_price(api, f"{base_currency}{target_currency}")

    if current_price:
        if random.choice([True, False]):
            # LONG
            take_profit1 = current_price * 1.05
            take_profit2 = current_price * 1.1
            stop_loss = current_price * 0.95
            signal = generate_long_signal(base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss)
        else:
            # SHORT
            take_profit1 = current_price * 0.95
            take_profit2 = current_price * 0.9
            stop_loss = current_price * 1.05
            signal = generate_short_signal(base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss)
        
        await context.bot.send_message(chat_id=chat_id, text=signal)
    else:
        await context.bot.send_message(chat_id=chat_id, text="Не удалось получить данные для валютной пары.")

# Обработчик команды /start
async def start(update: Update, context):
    await send_signals(update, context)

# Основная функция
def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == '__main__':
    main()
