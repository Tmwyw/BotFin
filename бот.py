import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
import requests
from telegram.ext import JobQueue
from datetime import datetime
import random
import os  # Импортируем os для работы с переменными окружения

# Твой API ключ для обменных курсов
API_KEY = "e9313eae0113f4c915d2946b3a633c1e"

# Список валютных пар для мониторинга
CURRENCY_PAIRS = [
    ('USD', 'RUB'),
    ('EUR', 'USD'),
    ('GBP', 'USD'),
    ('AUD', 'USD'),
    ('CAD', 'USD'),
    ('NZD', 'USD'),
    ('CHF', 'USD'),
    ('JPY', 'USD'),
    ('USD', 'CNY'),
    ('USD', 'TRY')
]

# Переменная для отслеживания количества сигналов в день
signals_sent_today = 0
current_day = datetime.now().day

# Функция для получения курса валют
def get_currency_rate(base_currency, target_currency):
    try:
        url = f'https://api.exchangeratesapi.io/v1/latest?access_key={API_KEY}&symbols={target_currency}'
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки
        data = response.json()
        
        if 'rates' in data:
            return data['rates'][target_currency]
        else:
            return None
    except requests.RequestException as e:
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
async def send_signals(context):
    global signals_sent_today, current_day

    # Проверка, нужно ли сбросить счетчик сигналов в начале нового дня
    today = datetime.now().day
    if today != current_day:
        current_day = today
        signals_sent_today = 0

    # Если уже отправлено 3 сигнала за день, не отправляем больше
    if signals_sent_today >= 3:
        return

    chat_id = context.job.chat_id
    for base_currency, target_currency in CURRENCY_PAIRS:
        current_price = get_currency_rate(base_currency, target_currency)
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
            signals_sent_today += 1
            if signals_sent_today >= 3:
                return
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"Не удалось получить данные для {base_currency}/{target_currency}")

# Обработчик команды /start
async def start(update: Update, context):
    # Запуск задачи для генерации сигналов каждые 60 секунд без сообщения
    context.job_queue.run_repeating(send_signals, interval=60, first=60, chat_id=update.message.chat_id)

# Обработчик команды /stop для остановки сигналов
async def stop(update: Update, context):
    context.job_queue.stop()
    await update.message.reply_text("Генерация сигналов остановлена.")

# Основная функция
def main():
    print("Запуск бота")  # Отладочное сообщение
    
    # Получаем токен из переменной окружения
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Создание приложения с поддержкой JobQueue
    app = ApplicationBuilder().token(TOKEN).post_init(lambda app: app.job_queue.start()).build()

    # Добавляем команды /start и /stop
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))

    print("Начало выполнения run_polling()")  # Отладочное сообщение
    app.run_polling()
    print("После выполнения run_polling()")  # Отладочное сообщение

if __name__ == '__main__':
    main()
