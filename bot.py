import websockets
import asyncio
import requests
import os

# Функция для подключения к WebSocket Pocket Option
async def connect_to_pocket_option():
    uri = "wss://api.pocketoption.com/socket"  # Убедись в правильности URL
    async with websockets.connect(uri) as websocket:
        # Используем SSID для авторизации через WebSocket
        auth_data = '{"action": "auth", "session":"ugceh9llu62egeenpnhalb629n", "isDemo":1, "uid":85002634, "platform":2}'
        await websocket.send(auth_data)  # Отправляем данные для авторизации
        response = await websocket.recv()  # Получаем ответ от сервера
        print(f"Ответ от сервера: {response}")
        return response

# Запрос на получение данных о валютных парах через REST API
def get_currency_pairs():
    url = "https://api.pocketoption.com/v1/market/currency-pairs"
    headers = {
        "Authorization": 'Bearer 42["auth",{"session":"ugceh9llu62egeenpnhalb629n","isDemo":1,"uid":85002634,"platform":2}]'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Возвращаем данные в формате JSON
    else:
        print(f"Ошибка получения валютных пар: {response.status_code}")
        return None

# Функция для получения курса валютной пары
def get_currency_rate(base_currency, target_currency):
    pairs = get_currency_pairs()  # Получаем список валютных пар через API
    if pairs:
        for pair in pairs['data']:
            if pair['symbol'] == f"{base_currency}/{target_currency}":
                return pair['price']  # Возвращаем текущую цену
    return None

# Асинхронная функция для генерации сигналов на основе валютных пар
async def send_signals():
    # Валютные пары, по которым будем генерировать сигналы
    CURRENCY_PAIRS = [
        ('EUR', 'USD'),
        ('GBP', 'USD'),
        ('AUD', 'USD'),
        ('USD', 'JPY'),
        ('USD', 'TRY')
    ]

    for base_currency, target_currency in CURRENCY_PAIRS:
        current_price = get_currency_rate(base_currency, target_currency)
        if current_price:
            print(f"Текущая цена {base_currency}/{target_currency}: {current_price}")
        else:
            print(f"Не удалось получить данные для {base_currency}/{target_currency}")

# Основная функция
def main():
    print("Запуск программы...")
    
    # Подключение к WebSocket Pocket Option для авторизации
    asyncio.get_event_loop().run_until_complete(connect_to_pocket_option())

    # Генерация сигналов
    asyncio.get_event_loop().run_until_complete(send_signals())

if __name__ == "__main__":
    main()
