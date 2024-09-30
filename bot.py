import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio

# Список валютных пар для анализа
CURRENCY_PAIRS = [
    ('AUD', 'CAD'),
    ('CHF', 'JPY'),
    ('GBP', 'CAD'),
    ('AUD', 'USD'),
    ('CAD', 'USD'),
    ('NZD', 'USD'),
    ('CHF', 'USD'),
    ('JPY', 'USD'),
    ('USD', 'CNY'),
    ('USD', 'TRY')
]

# Функция для получения данных валютных курсов (примерные данные, заменить на реальный API)
def get_currency_data(base_currency, target_currency):
    # Пример временных меток и цен, замени на реальные данные от API
    data = {
        'timestamp': ['2024-09-30 07:00', '2024-09-30 09:00', '2024-09-30 11:00', 
                      '2024-09-30 13:00', '2024-09-30 15:00', '2024-09-30 17:00'],
        'price': [random.uniform(1.0, 1.5) for _ in range(6)]
    }
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Стратегия на основе пересечения скользящих средних (SMA)
def check_for_signal(df):
    signal = None
    # Проверка пересечения скользящих средних
    if df['SMA_5'].iloc[-1] > df['SMA_10'].iloc[-1] and df['SMA_5'].iloc[-2] <= df['SMA_10'].iloc[-2]:
        signal = 'BUY'
    elif df['SMA_5'].iloc[-1] < df['SMA_10'].iloc[-1] and df['SMA_5'].iloc[-2] >= df['SMA_10'].iloc[-2]:
        signal = 'SELL'
    return signal

# Функция для создания графика
def create_chart(df, signal, currency_pair):
    # Разбираем валютную пару
    base_currency, target_currency = currency_pair
    time_stamps = df['timestamp']
    exchange_rates = df['price']
    
    # Создание графика
    plt.figure(figsize=(10, 6))
    plt.plot(time_stamps, exchange_rates, label=f'{base_currency}/{target_currency} Rate', color='white', linewidth=2)
    
    # Визуальные настройки
    plt.title(f'Analysis for {base_currency}/{target_currency} with {signal} Signal', fontsize=16)
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Rate', fontsize=12)
    plt.grid(True, which='both', linestyle='--', color='gray', alpha=0.7)

    # Настройка фона
    plt.gca().set_facecolor('#1a1a1a')
    plt.gcf().set_facecolor('#1a1a1a')
    plt.gca().spines['bottom'].set_color('white')
    plt.gca().spines['left'].set_color('white')
    plt.gca().tick_params(axis='x', colors='white')
    plt.gca().tick_params(axis='y', colors='white')

    # Сохранение графика
    chart_filename = f'{base_currency}_{target_currency}_signal_chart.png'
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight', transparent=True)
    plt.close()

    return chart_filename

# Функция для проверки валютных пар и отправки сигналов
async def analyze_currency_pairs(context):
    chat_id = context.job.chat_id
    for currency_pair in CURRENCY_PAIRS:
        base_currency, target_currency = currency_pair
        
        # Получаем данные по валютной паре
        df = get_currency_data(base_currency, target_currency)
        
        # Вычисляем скользящие средние
        df['SMA_5'] = df['price'].rolling(window=5).mean()
        df['SMA_10'] = df['price'].rolling(window=10).mean()

        # Проверяем сигнал по стратегии
        signal = check_for_signal(df)
        
        if signal:
            # Генерация графика
            chart_filename = create_chart(df, signal, currency_pair)
            
            # Отправка сигнала с графиком
            await context.bot.send_message(chat_id=chat_id, 
                                           text=f"{signal} сигнал на {base_currency}/{target_currency}")
            await context.bot.send_photo(chat_id=chat_id, photo=open(chart_filename, 'rb'))

# Команда для начала автоматической проверки сигналов
async def start_signals(update: Update, context):
    await update.message.reply_text("Автоматическая проверка сигналов запущена.")
    context.job_queue.run_repeating(analyze_currency_pairs, interval=60, first=0, chat_id=update.message.chat_id)

# Команда для остановки автоматической проверки сигналов
async def stop_signals(update: Update, context):
    context.job_queue.stop()
    await update.message.reply_text("Автоматическая проверка сигналов остановлена.")

# Настройка бота
application = ApplicationBuilder().token("ТВОЙ_ТОКЕН").build()
application.add_handler(CommandHandler("start_signals", start_signals))
application.add_handler(CommandHandler("stop_signals", stop_signals))

# Запуск бота
application.run_polling()
