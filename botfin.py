import openai
import os
import random
import time
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка OpenAI API и Telegram API
openai.api_key = os.getenv("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")
TELEGRAM_BOT_TOKEN = os.getenv("8068789170:AAHmKXcP9g_qTVuP_KNBAFGU56__-0nDseQ")

# Список каналов с топиками
channels = [
    {'chat_id': '-1002243376132', 'thread_id': 4},  # Первый канал
    {'chat_id': '-1002290780268', 'thread_id': 6}   # Второй канал
]

# Хештеги для разделения по темам
hash_tags = {
    "crypto": "#криптовалюта",
    "politics": "#политика",
    "finance": "#финансы",
    "important": "#ВАЖНЫЕ_НОВОСТИ"
}

# Функция генерации краткого описания новости
def get_news_summary(news_text: str, category: str) -> str:
    # Формируем запрос для GPT
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Сделай краткое описание следующих финансовых новостей на русском языке: {news_text}",
        max_tokens=150
    )
    
    summary = response.choices[0].text.strip()

    # Форматируем текст для Telegram
    formatted_summary = f"**{category.upper()}**\n\n*{summary}*\n\n[Подробнее по ссылке](https://example.com)"
    
    # Добавляем хештеги по категориям
    if "важные" in category.lower():
        formatted_summary += f"\n{hash_tags['important']}"
    else:
        formatted_summary += f"\n{hash_tags.get(category.lower(), '')}"
    
    return formatted_summary

# Функция генерации изображения через DALL·E
def generate_image(news_text: str) -> str:
    # Запрашиваем у OpenAI DALL·E генерацию изображения
    response = openai.Image.create(
        prompt=news_text,  # Используем новость как описание для изображения
        n=1,
        size="1024x1024"  # Устанавливаем размер изображения
    )
    
    image_url = response['data'][0]['url']  # Получаем ссылку на сгенерированное изображение
    return image_url

# Функция для отправки новостей и изображений в каналы
def send_news_to_channels(news_text: str, category: str):
    # Генерируем текст и изображение
    summary = get_news_summary(news_text, category)
    image_url = generate_image(news_text)
    
    for channel in channels:
        chat_id = channel['chat_id']
        thread_id = channel['thread_id']
        
        # Отправляем текст с форматированием
        updater.bot.send_message(chat_id=chat_id, text=summary, parse_mode=ParseMode.MARKDOWN, message_thread_id=thread_id)
        
        # Отправляем изображение
        updater.bot.send_photo(chat_id=chat_id, photo=image_url, message_thread_id=thread_id)

# Основные команды бота
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Этот бот отправляет финансовые новости с изображениями.")

def handle_message(update: Update, context: CallbackContext):
    news_text = update.message.text
    category = "финансы"  # Пример: категорию можно улучшить в будущем
    send_news_to_channels(news_text, category)

# Функция для генерации случайного времени ожидания
def get_random_interval():
    # Генерируем случайное время от 30 до 180 минут (в секундах)
    return random.randint(30, 180) * 60

# Основной цикл для автоматической отправки новостей
def run_news_bot():
    while True:
        # Пример текста новости для теста
        news_text = "Новости о криптовалютах и финансах"
        category = "финансы"
        
        # Отправляем новости
        send_news_to_channels(news_text, category)
        
        # Ждём случайное время перед следующей отправкой
        random_interval = get_random_interval()
        print(f"Ждём {random_interval // 60} минут до следующей новости.")
        time.sleep(random_interval)

if __name__ == "__main__":
    # Настраиваем бота
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    
    # Регистрируем обработчики
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Запускаем бота в отдельном потоке
    updater.start_polling()
    
    # Запускаем основной цикл для автоматической отправки новостей
    run_news_bot()

    updater.idle()
