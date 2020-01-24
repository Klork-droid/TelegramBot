import telebot
from telebot.types import Message
from telebot import types
import requests

token = "1010570699:AAG8w1NHWTuEpgA0JZrRD_nO015pym37iXk"
appid = 'aa6bc48979bd3a747446e5727350ecd0'  # API for home.openweathermap.org
bot = telebot.TeleBot(token)

USERS = set()


@bot.message_handler(commands=["start", "help"])
def command_handler(message: Message):
    reply = """This bot can show the price of crypto and will can show the weather of your town. 
    You can use these commands: 
    /BTC 
    /ETH 
    /ETC 
    /Weather"""
    bot.send_message(message.chat.id, reply)


@bot.message_handler(commands=["geo"])
def geo(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Отправь мне свое местоположение!", reply_markup=keyboard)


@bot.message_handler(commands=["Weather"])
def get_weather(message: Message):
    pass


@bot.message_handler(commands=["BTC", "ETH", "ETC"])
def get_price(message: Message):
    crypto_symbol = message.text
    crypto_dict = {
        '/BTC': 'bitcoin',
        '/ETH': 'ethereum',
        '/ETC': 'ethereum-classic'
    }
    name_crypto = crypto_dict.get(crypto_symbol)
    url = f'https://api.coinmarketcap.com/v1/ticker/{name_crypto}/'
    r = requests.get(url).json()
    price = float(r[-1]['price_usd'])
    price = '{:.1f}'.format(price)
    smail_up = '📈'
    smail_down = '📉'
    temp = r[-1]['percent_change_1h']
    percent_change_1h = temp + smail_up if float(temp) > 0 else temp + smail_down
    temp = r[-1]['percent_change_24h']
    percent_change_24h = temp + smail_up if float(temp) > 0 else temp + smail_down
    temp = r[-1]['percent_change_7d']
    percent_change_7d = temp + smail_up if float(temp) > 0 else temp + smail_down
    reply = f"""Price of {name_crypto}: {price}$
Change of 1h: {percent_change_1h}
Change of 24h: {percent_change_24h}
Change of 7d: {percent_change_7d}
    """
    bot.send_message(message.chat.id, reply)


@bot.message_handler(content_types=["text"])
@bot.edited_message_handler(content_types=["text"])
def echo_i_see(message: Message):
    reply = str("I see you")
    if message.from_user.id in USERS:
        reply = f"Hello again, {message.from_user.username}. " + reply
    bot.reply_to(message, reply)
    USERS.add(message.from_user.id)


@bot.message_handler(content_types=['sticker'])
def sticker_handler(message: Message):
    reply = str("I can too")
    bot.reply_to(message, reply)
    bot.send_sticker(message.chat.id, message.sticker.file_id)


bot.polling(timeout=10)
