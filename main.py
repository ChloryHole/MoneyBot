import telebot
from telebot import types
import requests
import time 
import yaml
import threading

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
        "id_message": message.message_id + 2
    }
    response = requests.post(f"{url}/users/add", json=data)
    if response.status_code == 200:
        bot.send_message(message.chat.id, "Here will be the quotes you selected, pin this message - important! ")
    else:
        bot.send_message(message.chat.id, "error, return later plz")

@bot.message_handler(commands=['add_headline'])
def add_headline(message):
    msg = bot.send_message(message.chat.id, "Напиши FIGI идентификатор акции")
    bot.register_next_step_handler(msg, read_new_headline)

def read_new_headline(message):
    msg = message.text.strip()
    if len(msg) == 12:
        data = {
            "id": msg,
            "id_user": message.chat.id
        }
        response = requests.post(f"{url}/headline/add", json=data)
        if response.status_code == 200:
            bot.send_message(message.chat.id, "круто")
        else:
            bot.send_message(message.chat.id, f"error, return later plz: {response.json()}" )
    else:
        bot.send_message(message.chat.id, "неправильный FIGI идентификатор") 


@bot.message_handler(commands=['change_head'])
def change_head(message):
    data = {
        "id": message.chat.id
    }
    response = requests.get(f"{url}/users/quotes", json=data)
    if response.status_code == 200:
        data = response.json()
        new_text = ""
        for quote in data["quotes"]:
            new_text += f"{quote["name"]}: {quote["cost"]}\n"
        bot.edit_message_text(
            chat_id=data["id"],
            message_id=data["id_message"],
            text=new_text
        )
        bot.send_message(message.chat.id, "обновили")
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


@bot.message_handler(commands=['help'])
def handler(message):
    bot.send_message(message.chat.id, 
                    "/add_headline -- добавить отслеживаемую акцию в закрепленное сообщение" \
                    "")
    
def scheduled_messages():
    memory = dict()
    while True:
        time.sleep(10) 
        response = requests.get(f"{url}/headlines")
        if response.status_code == 200:
            data_all = response.json()
            for data in data_all:
                new_text = ""
                for quote in data["quotes"]:
                    new_text += f"{quote["name"]}: {quote["cost"]}\n"
                if data["id"] in memory and memory[data["id"]] == new_text:
                    continue
                memory[data["id"]] = new_text
                bot.edit_message_text(
                    chat_id=data["id"],
                    message_id=data["id_message"],
                    text=new_text
                )
        else:
            bot.send_message(config["tg-bot:"]["admin_id"], "владыка, сервер не отвечает")


        # bot.send_message(858080623, "Автоматическое сообщение")

threading.Thread(target=scheduled_messages, daemon=True).start()

bot.infinity_polling()



