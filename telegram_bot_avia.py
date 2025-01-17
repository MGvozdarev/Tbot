import telebot
import requests
from datetime import datetime
import os

API_TOKEN = '7631978521:AAHoPI-PE2_X9WimOzfLEE5XarqDj-owUKk'
AVIASALES_API_TOKEN = '6d85204831b4af582145a29a6a771e47'

bot = telebot.TeleBot(API_TOKEN)

# URL API 
AVIASALES_API_URL = 'https://api.travelpayouts.com/aviasales/v3/prices_for_dates'

# обработчик команды start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для отслеживания стоимости авиабилетов. Используйте команду /search, чтобы найти дешевые билеты.")

# обработчик команды search
@bot.message_handler(commands=['search'])
def search_flights(message):
    msg = bot.send_message(message.chat.id, "Введите пункт вылета (IATA код, например MOW - (Москва):")
    bot.register_next_step_handler(msg, get_departure)

def get_departure(message): 
    departure = message.text.strip().upper()
    # проверка на допустимость иата кода 2-3 символа
    if len(departure) < 2 or len(departure) > 3:
        bot.send_message(message.chat.id, "Некорректный IATA код. Пожалуйста, введите правильный код.")
        return
    msg = bot.send_message(message.chat.id, "Введите пункт назначения (IATA код, например KZN - (Казань):")
    bot.register_next_step_handler(msg, get_destination, departure)

def get_destination(message, departure):
    destination = message.text.strip().upper()
    if len(destination) < 2 or len(destination) > 3: # то же самое по проверке иата
        bot.send_message(message.chat.id, "Некорректный IATA код. Пожалуйста, введите правильный код.")
        return
    msg = bot.send_message(message.chat.id, "Введите дату вылета (в формате ГГГГ-ММ-ДД, например 2025-01-01):")
    bot.register_next_step_handler(msg, get_date, departure, destination)

def get_date(message, departure, destination):
    date = message.text.strip()
    try:
        # проверка формата даты
        datetime.strptime(date, '%Y-%m-%d')
        payload = {
            'origin': departure,
            'destination': destination,
            'departure_at': date,
            'currency': 'rub',
            'token': AVIASALES_API_TOKEN,
            'limit': 5,  
            'sorting': 'price',
            'one_way': 'true',  # билеты в одну сторону
        }
        response = requests.get(AVIASALES_API_URL, params=payload)

        if response.status_code == 200:
            data = response.json()
            if data['data']:
                for flight in data['data']:
                    min_price = flight['price']
                    departure_time = flight['departure_at']
                    bot.send_message(message.chat.id, f"Цена на билеты из {departure} в {destination} на {departure_time}:\nМинимальная цена: {min_price} RUB")
            else:
                bot.send_message(message.chat.id, "Не удалось найти билеты по указанным данным.")
        else:
            bot.send_message(message.chat.id, f"Ошибка при получении данных: {response.status_code}. Попробуйте позже.")
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный формат даты. Используйте формат ГГГГ-ММ-ДД.")

bot.polling()