import telebot
from telebot import types
import requests

import yaml

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
      
bot = telebot.TeleBot(config["tg-bot"]["token"])
url = f"{config["api"]["url"]}:{config["api"]["port"]}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hello!')    
    data = {
        "id": message.chat.id,
        "name": message.from_user.first_name,
        "id_message": message.id + 2
    }
    response = requests.post(f"{url}/users/add", json=data)
    if response.status_code == 200:
        bot.send_message(message.chat.id, "Here will be the quotes you selected, pin this message - important! ")
    else:
        bot.send_message(message.chat.id, "error, return later plz")

@bot.message_handler(commands=['show_users'])
def show_users(message):
    response= requests.get(f"{url}/users/show")
    if response.status_code == 200:
        data = response.json()
        message_text = "Список пользователей:\n\n"
        for user in data:
            message_text += f"🆔 ID: {user['id']}\n👤 Имя: {user['name']}\n✉️ ID сообщения: {user['id_message']}\n\n"
        bot.send_message(message.chat.id, message_text)
    else:
        bot.send_message(message.chat.id, f"error, return later plz\n{response.json()}")

bot.infinity_polling()


