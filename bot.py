import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio

# Твой API-ключ от Alpha Vantage
API_KEY = '74O1PFK2C59IB5ND'

# Список валютных пар для анализа
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

# Функция для получения данных валютных курсов через Alpha Vantage API
def get_currency_data(base_currency, target_currency):
    try:
        # Формируем URL для запроса
        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={base_currency}&to_currency={target_currency}&apikey={API_KEY}'
        
        # Отправляем запрос к API
        response = requests.get(url)
        response.raise_for_status()  # Проверяем, нет ли ошибок в запросе

        # Преобразуем данные в JSON
        data = response.json()

        # Проверяем наличие данных
        if 'Realtime Currency Exchange Rate' in data:
            exchange_rate = float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
            timestamp = datetime.now()  # Получаем текущее время как метку времени

            # Формируем DataFrame для возвращаемых данных
            df = pd.DataFrame({
                'timestamp': [timestamp],
                'price': [exchange_rate]
            })
            return df
        else:
            # Если данных нет, возвращаем None
            return None

    except requests.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
        return None

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
        
        # Получаем данные по валютной паре через Alpha Vantage API
        df = get_currency_data(base_currency, target_currency)
        
        if df is not None:
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
        else:
            await context.bot.send_message(chat_id=chat_id, 
                                           text=f"Не удалось получить данные по {base_currency}/{target_currency}")

# Команда для начала автоматической проверки сигналов каждые 30 минут
async def start_signals(update: Update, context):
    await update.message.reply_text("Автоматическая проверка сигналов запущена.")
    context.job_queue.run_repeating(analyze_currency_pairs, interval=1800, first=0, chat_id=update.message.chat_id)

# Команда для остановки автоматической проверки сигналов
async def stop_signals(update: Update, context):
    context.job_queue.stop()
    await update.message.reply_text("Автоматическая проверка сигналов остановлена.")

# Настройка бота
application = ApplicationBuilder().token("7449818362:AAHrejKv90PyRkrgMTdZvHzT9p44ePlZYcg").build()
application.add_handler(CommandHandler("start_signals", start_signals))
application.add_handler(CommandHandler("stop_signals", stop_signals))

# Запуск бота
application.run_polling()
