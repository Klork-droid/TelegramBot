import telebot
from telebot.types import Message
from telebot import types
import requests

token = "1010570699:AAG8w1NHWTuEpgA0JZrRD_nO015pym37iXk"
appid = 'aa6bc48979bd3a747446e5727350ecd0'  # API for home.openweathermap.org
bot = telebot.TeleBot(token)

USERS = set()

reply_for_start = "This bot can show the price of crypto and will can show the weather of your town.\n" \
                  "You can use these commands:"
reply_for_crypto = "This bot can show the price of crypto.\n" \
                   "Please, choose a crypto:"
reply_for_weather = "Send me your location please!"


def location_message(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_geo = types.KeyboardButton(text="Send location", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(chat_id, text=reply_for_weather, reply_markup=keyboard)


def keyboard_first():
    keyboard = types.InlineKeyboardMarkup()
    crypto_button = types.InlineKeyboardButton(text="Crypto", callback_data="crypto_button")
    weather_button = types.InlineKeyboardButton(text="Weather", callback_data="location_button")
    keyboard.add(crypto_button, weather_button)
    return keyboard


def crypto_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btc_button = types.InlineKeyboardButton(text="BTC 💰", callback_data="btc_button")
    etc_button = types.InlineKeyboardButton(text="ETC 💰", callback_data="etc_button")
    eth_button = types.InlineKeyboardButton(text="ETH 💰", callback_data="eth_button")
    back_button = types.InlineKeyboardButton(text="Back ⬅", callback_data="back_button")
    keyboard.add(btc_button, etc_button, eth_button)
    keyboard.add(back_button)
    return keyboard


def weather_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    pass


@bot.message_handler(commands=["start"])
def key(message: Message):
    bot.send_message(message.chat.id,
                     text=reply_for_start,
                     reply_markup=keyboard_first())


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data == "crypto_button":
        bot.edit_message_text(chat_id=chat_id,
                              text=reply_for_crypto,
                              message_id=message_id,
                              reply_markup=crypto_keyboard())
    elif call.data in ("btc_button", "etc_button", "eth_button"):
        bot.edit_message_text(chat_id=chat_id,
                              text=get_price(call.data),
                              message_id=message_id,
                              reply_markup=crypto_keyboard())
    elif call.data == "back_button":
        bot.edit_message_text(chat_id=chat_id,
                              text=reply_for_start,
                              message_id=message_id,
                              reply_markup=keyboard_first())
    elif call.data == "location_button":
        bot.delete_message(chat_id, message_id)
        location_message(chat_id)


@bot.message_handler(content_types=["location"])
def get_location(message: Message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    get_weather(latitude, longitude, message.chat.id)


def get_weather(lat, lon, chat_id):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={appid}"
    r = requests.get(url).json()
    temp = float(r['main']['temp']) - 273
    temp = "{0:.2f}".format(temp)
    feels_like = float(r['main']['feels_like']) - 273
    feels_like = "{0:.2f}".format(feels_like)
    deg = float(r['wind']['deg']) + 22.5
    direct = get_direction(deg)
    reply = f"The weather in {r['name']}:\n" \
            f"main: {r['weather'][-1]['main']}\n" \
            f"description: {r['weather'][-1]['description']}\n" \
            f"temp: {temp}\n" \
            f"feels like: {feels_like}\n" \
            f"speed: {r['wind']['speed']} m/s\n" \
            f"deg: {direct}\n" \
            f"clouds: {r['clouds']['all']}%"
    bot.send_message(chat_id=chat_id, text=reply)


def get_direction(deg):
    deg %= 360
    deg /= 45
    direction = 'Error'
    if deg == 0:
        direction = 'WN'
    if deg <= 1:
        direction = 'N'
    elif deg <= 2:
        direction = 'NE'
    elif deg <= 3:
        direction = 'E'
    elif deg <= 4:
        direction = 'SE'
    elif deg <= 5:
        direction = 'S'
    elif deg <= 6:
        direction = 'SW'
    elif deg <= 7:
        direction = 'W'
    elif deg <= 8:
        direction = 'WN'
    return direction


def get_price(name):
    crypto_symbol = name[0:3]
    crypto_dict = {
        'btc': 'bitcoin',
        'eth': 'ethereum',
        'etc': 'ethereum-classic'
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
    Change of 1h:   {percent_change_1h}
    Change of 24h:  {percent_change_24h}
    Change of 7d:   {percent_change_7d}
    """
    return reply


@bot.message_handler(content_types=["text"])
@bot.edited_message_handler(content_types=["text"])
def echo_i_see(message: Message):
    reply = str("Use '/start' please")
    if message.from_user.id in USERS:
        reply = f"Hello again, {message.from_user.username}. " + reply
    bot.reply_to(message, reply)
    USERS.add(message.from_user.id)


@bot.message_handler(content_types=['sticker'])
def sticker_handler(message: Message):
    reply = str("I can too")
    bot.reply_to(message, reply)
    bot.send_sticker(message.chat.id, message.sticker.file_id)


bot.polling(timeout=60)
