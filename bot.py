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
from iqoptionapi.stable_api import IQ_Option

# Подключение к IQ Option
async def connect_to_iq_option():
    iq = IQ_Option("nik.2ch@gmail.com", "#U6dq$G!Ez65ad45F&gm")
    iq.connect()
    
    if iq.check_connect() == False:
        print("Ошибка подключения")
        return None
    else:
        print("Подключено")
    
    return iq

# Получение текущей цены на IQ Option
async def get_current_price():
    iq = await connect_to_iq_option()
    if iq:
        goal = "EURUSD"
        current_price = iq.get_candles(goal, 60, 1, time.time())[-1]['close']
        return current_price
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
    
    base_currency, target_currency = "EUR", "USD"
    current_price = await get_current_price()

    if current_price is None:
        await context.bot.send_message(chat_id=chat_id, text="Ошибка подключения к IQ Option.")
        return

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
