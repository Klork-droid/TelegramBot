import telebot
from telebot.types import Message

token = "1010570699:AAG8w1NHWTuEpgA0JZrRD_nO015pym37iXk"

bot = telebot.TeleBot(token)

USERS = set()


@bot.message_handler(commands=["start", "help"])
def command_handler(message: Message):
    bot.reply_to(message, "There is no answer:(")


@bot.message_handler(content_types=["text"])
@bot.edited_message_handler(content_types=["text"])
def echo_i_see(message: Message):
    reply = str("I see you")
    if message.from_user.id in USERS:
        reply += f"Hello again, {message.from_user.username}"
    bot.reply_to(message, reply)
    USERS.add(message.from_user.id)


@bot.message_handler(content_types=['sticker'])
def sticker_handler(message: Message):
    #   bot.send_sticker(message.chat.id, message.sticker.file_id)
    bot.send_message(message.chat.id, message.sticker.file_id)
    bot.send_message(message.chat.id, message.sticker.set_name)


bot.polling(timeout=10)
