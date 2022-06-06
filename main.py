from geopy.geocoders import Nominatim
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
)
import os
import logging
import requests
import json

logger = logging.getLogger(__name__)
geolocator = Nominatim(user_agent="weather-bot")


def get_key(filename: str) -> str:
    if not os.path.exists(filename):
        print(f'File "{filename}" not found.\nQuitting...')
        quit()
    with open(filename, "r") as token_file:
        mytoken = token_file.read()
    return mytoken


weather_key = get_key("weather_key.txt")
geocoding_key = get_key("geocoding_key.txt")


def main() -> None:
    FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=FORMAT, datefmt="%d/%m/%Y %H:%M:%S")
    logger.setLevel(logging.DEBUG)

    telegram_token = get_key("telegram_token.txt")

    logger.info("Creating updater")
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command),
            CommandHandler("help", help_command),
            CommandHandler("weatherfor", get_weather),
        ],
        states={},
        fallbacks=[],
    )

    dispatcher.add_handler(conv_handler)

    logger.info("Starting updater")
    updater.start_polling()
    updater.idle()


def start_command(update, context):
    logger.info("Received /start from user id " + str(update.effective_chat.id))
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to WeatherBot, a Telegram Bot to retrieve the latest weather data.",
    )


def help_command(update, context):
    logger.info("Received /help from user id " + str(update.effective_chat.id))
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Help not available at the moment"
    )


def get_weather(update, context):
    location = " ".join(update.message.text.split(" ")[1:])
    logger.info("Searching \"" + location + "\" for user id " + str(update.effective_chat.id))

    url = "https://forward-reverse-geocoding.p.rapidapi.com/v1/search"

    response = requests.get(url,
    headers={
        "X-RapidAPI-Host": "forward-reverse-geocoding.p.rapidapi.com",
        "X-RapidAPI-Key": geocoding_key
    },
    params={
        "q":location,
        "accept-language":"en",
        "polygon_threshold":"0.0"
    })

    coordinates = (response.json()[0]["lat"], response.json()[0]["lon"])

    weather = requests.get("https://api.openweathermap.org/data/2.5/onecall",
        params = {
            "lat": coordinates[0],
            "lon": coordinates[1],
            "exclude": "hourly,daily",
            "appid": weather_key
        }
    )

    print(weather.json())

    context.bot.send_message(
        chat_id=update.effective_chat.id, text="ghei"
    )


if __name__ == "__main__":
    main()
