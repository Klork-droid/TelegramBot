import telebot
from telebot.types import Message
from telebot import types
import requests
from db import init_db
from db import add_message
from db import last_location
from db import all_users
from datetime import datetime
import time
from bs4 import BeautifulSoup as bs

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': user_agent}

token = "1010570699:AAG8w1NHWTuEpgA0JZrRD_nO015pym37iXk"
appid = 'aa6bc48979bd3a747446e5727350ecd0'  # API for home.openweathermap.org
bot = telebot.TeleBot(token)

init_db()

user_id_location_dict = {}

reply_for_start = "This bot can show the price of crypto, show the weather of your town" \
                  "and parsing photo from instagram.\n" \
                  "You can use these commands:"
reply_for_crypto = "This bot can show the price of crypto.\n" \
                   "Please, choose a crypto:"
reply_for_weather = "Send me your location please!"

reply_for_choice_location = "Choose your location:"


def location_message(chat_id):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_geo = types.KeyboardButton(text="Send location", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(chat_id, text=reply_for_weather, reply_markup=keyboard)


def keyboard_first():
    keyboard = types.InlineKeyboardMarkup()
    crypto_button = types.InlineKeyboardButton(text="Crypto", callback_data="crypto_button")
    weather_button = types.InlineKeyboardButton(text="Weather", callback_data="weather_button")
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


def location_keyboard(city_dict):
    keyboard = types.InlineKeyboardMarkup()
    for ikey in city_dict.keys():
        keyboard.add(types.InlineKeyboardButton(text=ikey, callback_data=ikey))
    keyboard.add(types.InlineKeyboardButton(text="Current location", callback_data="current_location"))
    keyboard.add(types.InlineKeyboardButton(text="Back ⬅", callback_data="back_button"))
    return keyboard


@bot.message_handler(commands=["start"])
def key(message: Message):
    bot.send_message(message.chat.id,
                     text=reply_for_start,
                     reply_markup=keyboard_first())
    add_message(user_id=message.chat.id, text="/start", user_name=message.chat.username)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    city_dict = None
    if user_id_location_dict.get(chat_id):
        city_dict = user_id_location_dict.get(chat_id)
    elif last_location(user_id=chat_id):
        city_dict = last_location(user_id=chat_id)
        city_dict = unique_location(city_dict)
        user_id_location_dict.update({chat_id: city_dict})
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
    elif call.data == "weather_button":
        if city_dict:
            bot.edit_message_text(chat_id=chat_id,
                                  text=reply_for_choice_location,
                                  message_id=message_id,
                                  reply_markup=location_keyboard(city_dict))
        else:
            bot.delete_message(chat_id, message_id)
            location_message(chat_id)
    elif call.data == "current_location":
        bot.delete_message(chat_id, message_id)
        location_message(chat_id)
    elif call.data in city_dict.keys():
        ivalues = city_dict.get(call.data)
        reply = get_weather(ivalues[0], ivalues[1])
        bot.edit_message_text(chat_id=chat_id,
                              text=reply,
                              message_id=message_id)
        bot.send_message(chat_id=chat_id,
                         text=reply_for_start,
                         reply_markup=keyboard_first())


@bot.message_handler(content_types=["location"])
def get_location(message: Message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    add_message(user_id=message.chat.id,
                user_name=message.chat.username,
                text="/location",
                latitude=latitude,
                longitude=longitude)
    reply = get_weather(lat=latitude, lon=longitude)
    bot.send_message(chat_id=message.chat.id, text=reply)
    bot.send_message(chat_id=message.chat.id,
                     text=reply_for_start,
                     reply_markup=keyboard_first())


def unique_location(loc: tuple):
    lat = loc[0][0]
    lon = loc[0][1]
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={appid}"
    r = requests.get(url).json()
    unique_city_dict = {r['name']: [lat, lon]}
    i = 1
    while i < len(loc) - 1:
        lat = loc[i][0]
        lon = loc[i][1]
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={appid}"
        r = requests.get(url).json()
        if r['name'] not in unique_city_dict:
            unique_city_dict[r['name']] = [lat, lon]
    return unique_city_dict


def get_weather(lat, lon):
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
    return reply


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
        'btc': 'BTC',
        'eth': 'ETH',
        'etc': 'ETC'
    }
    name_crypto = crypto_dict.get(crypto_symbol)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': f'{name_crypto}'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '6a7ebccc-a26a-41d3-85ca-7590d84214be',
    }

    session = requests.session()

    try:
        response = session.get(url, params=parameters, headers=headers)
        data = response.json()
        r = data['data'][f'{name_crypto}']['quote']['USD']
        price = float(r['price'])
        price = '{:.1f}'.format(price)
        smail_up = '📈'
        smail_down = '📉'
        temp = str(r['percent_change_1h'])
        percent_change_1h = temp + smail_up if float(temp) > 0 else temp + smail_down
        temp = str(r['percent_change_24h'])
        percent_change_24h = temp + smail_up if float(temp) > 0 else temp + smail_down
        temp = str(r['percent_change_7d'])
        percent_change_7d = temp + smail_up if float(temp) > 0 else temp + smail_down
        reply = f"""Price of {name_crypto}: {price}$
        Change of 1h:   {percent_change_1h}
        Change of 24h:  {percent_change_24h}
        Change of 7d:   {percent_change_7d}
        """
    except Exception as e:
        print(e)

    return reply


def get_image_from_url(url):
    img = None
    session = requests.session()
    request = session.get(url=url, headers=headers)
    if request.status_code == 200:
        soup = bs(request.content, 'lxml')
        try:
            soup = str(soup)
            index = soup.find("accessibility_caption")
            soup = soup[index - 1000:index]
            end = soup.rfind('\",\"')
            start = soup.rfind('{') + 8
            link = soup[start:end]
            link = link.replace('\\u0026', '&')
            print(link)
            img = requests.get(link)
            print('img')
        except Exception as e:
            print(e)
    else:
        print(request.status_code)
        print('ERROR')

    return img.content


@bot.message_handler(content_types=["text"])
@bot.edited_message_handler(content_types=["text"])
def echo_i_see(message: Message):
    if message.text.startswith('https://www.instagram.com/'):
        url = message.text
        image = get_image_from_url(url)
        if image:
            bot.send_photo(chat_id=message.chat.id, photo=image)
        else:
            bot.send_message(chat_id=message.chat.id, text='Photo not found')
    else:
        reply = str("Use '/start' please")
        add_message(user_id=message.from_user.id, user_name=message.from_user.username, text=message.text)
        bot.reply_to(message, reply)


@bot.message_handler(content_types=['sticker'])
def sticker_handler(message: Message):
    reply = str("I can too")
    bot.reply_to(message, reply)
    bot.send_sticker(message.chat.id, message.sticker.file_id)


def check_time_message():
    try:
        with open("Time_last_price_etc.txt", "r+") as file:
            flag = file.read()
            time_now = str(datetime.now())
            do_send_message = False
            for x in [5, 8]:  # 5 is month, 8 is day, 11 is hour
                if time_now[x:x + 2] > flag[x:x + 2]:
                    do_send_message = True
                    file.seek(0)
                    file.write(time_now)
                    break
                elif int(time_now[11:13]) - int(flag[11:13]) >= 12:
                    do_send_message = True
                    file.seek(0)
                    file.write(time_now)
                    break
            if do_send_message:
                for user_id in all_users():
                    bot.send_message(chat_id=user_id[0], text=get_price("etc"))
    except IOError:
        print("An IOError has occurred!")
        open("Time_last_price_etc.txt", "w+")


check_time_message()

while True:
    try:
        bot.polling(30)
    except Exception as e:
        print(e)
        time.sleep(60)
