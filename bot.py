import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
import requests
from datetime import datetime
import random
import os  # Импортируем os для работы с переменными окружения
import matplotlib.pyplot as plt
import io
from telegram import InputFile

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
    except requests.RequestException:
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

# Функция для построения графика валютной пары с сигналами
def plot_currency_chart(base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss, signal_type):
    plt.figure(figsize=(10, 5))
    
    # Примерные данные для графика движения цены
    prices = [current_price * (0.95 + 0.01 * i) for i in range(10)]
    time_points = range(len(prices))

    # Построение графика
    plt.plot(time_points, prices, label=f'{base_currency}/{target_currency}', color='blue')

    # Добавляем линии для Take Profit и Stop Loss
    plt.axhline(take_profit1, color='green', linestyle='--', label='Take Profit 1')
    plt.axhline(take_profit2, color='green', linestyle='--', label='Take Profit 2')
    plt.axhline(stop_loss, color='red', linestyle='--', label='Stop Loss')

    # Добавляем аннотации для точки входа
    if signal_type == 'LONG':
        plt.annotate('Entry (LONG)', xy=(5, current_price), xytext=(6, current_price * 1.02),
                     arrowprops=dict(facecolor='green', shrink=0.05))
    else:
        plt.annotate('Entry (SHORT)', xy=(5, current_price), xytext=(6, current_price * 0.98),
                     arrowprops=dict(facecolor='red', shrink=0.05))
        
         # Добавляем легенду и заголовок
    plt.legend()
    plt.title(f'График для {base_currency}/{target_currency}')
    plt.xlabel('Время')
    plt.ylabel('Цена')

    # Сохраняем график в буфер
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return buffer

# Функция для отправки графика через Telegram
async def send_chart(update, context, base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss, signal_type):
    chat_id = update.message.chat_id
    buffer = plot_currency_chart(base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss, signal_type)
    
    # Отправляем график в чат
    await context.bot.send_photo(chat_id=chat_id, photo=InputFile(buffer, filename='chart.png'))

# Асинхронная функция для отправки сигналов по валютным парам
async def send_signals(update: Update, context):
    chat_id = update.message.chat_id
    

    for base_currency, target_currency in CURRENCY_PAIRS[:3]:  # Берем первые 3 валютные пары
        current_price = get_currency_rate(base_currency, target_currency)
        if current_price:
            # Случайный выбор между LONG и SHORT
            if random.choice([True, False]):
                # LONG: Take Profit выше цены, Stop Loss ниже
                take_profit1 = current_price * 1.05  # Например, 5% выше текущей цены
                take_profit2 = current_price * 1.1   # Например, 10% выше текущей цены
                stop_loss = current_price * 0.95    # Например, 5% ниже текущей цены
                signal = generate_long_signal(base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss)
                signal_type = 'LONG'
            else:
                # SHORT: Take Profit ниже цены, Stop Loss выше
                take_profit1 = current_price * 0.95  # Например, 5% ниже текущей цены
                take_profit2 = current_price * 0.9   # Например, 10% ниже текущей цены
                stop_loss = current_price * 1.05    # Например, 5% выше текущей цены
                signal = generate_short_signal(base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss)
                signal_type = 'SHORT'
            
            await context.bot.send_message(chat_id=chat_id, text=signal)


            # Вызов функции отправки графика
            await send_chart(update, context, base_currency, target_currency, current_price, take_profit1, take_profit2, stop_loss, signal_type)
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
