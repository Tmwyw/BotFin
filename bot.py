import random
import requests
import matplotlib.pyplot as plt
import numpy as np
from telegram import Bot
from telegram.ext import CommandHandler, Updater
import datetime

API_KEY_ALPHA_VANTAGE = '74O1PFK2C59IB5ND'
TG_BOT_TOKEN = '7449818362:AAHrejKv90PyRkrgMTdZvHzT9p44ePlZYcg'

# Список валютных пар
CURRENCY_PAIRS = [
    ('EUR', 'GBP'),
    ('AUD', 'CAD'),
    ('GBP', 'CHF'),
    ('NZD', 'CAD'),
    ('EUR', 'AUD'),
    ('AUD', 'NZD'),
    ('EUR', 'CHF'),
    ('GBP', 'AUD'),
    ('CAD', 'CHF'),
    ('NZD', 'CHF')
]

bot = Bot(token=TG_BOT_TOKEN)

# Функция для получения данных валютной пары
def get_currency_data(from_currency, to_currency):
    url = f'https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={from_currency}&to_symbol={to_currency}&interval=1min&apikey={API_KEY_ALPHA_VANTAGE}'
    response = requests.get(url)
    data = response.json()
    # Возвращаем последние значения
    return list(data['Time Series FX (1min)'].values())[0]['1. open']

# Функция для создания и отправки графика
def send_chart(pair, signal):
    from_currency, to_currency = pair
    current_price = get_currency_data(from_currency, to_currency)
    prices = np.random.normal(float(current_price), 0.005, 100)  # Симуляция данных для графика
    times = np.linspace(0, 10, 100)

    plt.figure(figsize=(10, 5))
    plt.plot(times, prices, label=f'{from_currency}/{to_currency} Price')
    plt.title(f'{from_currency}/{to_currency} Chart with {signal}')
    plt.axhline(y=min(prices), color='r', linestyle='--', label="Support Level")
    plt.axhline(y=max(prices), color='g', linestyle='--', label="Resistance Level")
    plt.legend()

    file_path = '/mnt/data/chart.png'
    plt.savefig(file_path)
    plt.close()

    bot.send_photo(chat_id='YOUR_CHAT_ID', photo=open(file_path, 'rb'))

# Функция для отправки сигнала
def send_signal(update, context):
    # Рандомный выбор валютной пары
    pair = random.choice(CURRENCY_PAIRS)
    from_currency, to_currency = pair
    signal_type = random.choice(['LONG 🟢🔼', 'SHORT 🔴🔽'])
    time_options = ['1M', '2M', '3M', '5M']
    deal_time = random.choice(time_options)

    current_price = get_currency_data(from_currency, to_currency)
    template = f"""
    🔥{signal_type}
    🔥{from_currency}/{to_currency} OTC📌
    ⌛️ Время сделки: {deal_time}
    💵Текущая цена:📉 {current_price}
    """

    send_chart(pair, signal_type)  # Отправляем график
    update.message.reply_text(template)  # Отправляем текст

# Основная функция для запуска бота
def main():
    updater = Updater(TG_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('signal', send_signal))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
