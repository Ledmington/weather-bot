from geopy.geocoders import Nominatim
import telegram
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
            CommandHandler("weather", get_weather),
            CommandHandler("nexthour", get_next_hour),
            CommandHandler("tomorrow", get_tomorrow),
            CommandHandler("week", get_week),
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
    if len(update.message.text.split(" ")) == 1:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Error: you did not specify a location",
        )
        return

    location = " ".join(update.message.text.split(" ")[1:])
    logger.info(
        'Searching "' + location + '" for user id ' + str(update.effective_chat.id)
    )

    url = "https://forward-reverse-geocoding.p.rapidapi.com/v1/search"

    response = requests.get(
        url,
        headers={
            "X-RapidAPI-Host": "forward-reverse-geocoding.p.rapidapi.com",
            "X-RapidAPI-Key": geocoding_key,
        },
        params={"q": location, "accept-language": "en", "polygon_threshold": "0.0"},
    )

    if len(response.json()) == 0:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode=telegram.ParseMode.HTML,
            text=f'I\'m sorry but "<b>{location}</b>" does not exist. Try again.',
        )
        return

    data = response.json()[0]
    coordinates = (data["lat"], data["lon"])

    weather = requests.get(
        "https://api.openweathermap.org/data/2.5/onecall",
        params={
            "lat": coordinates[0],
            "lon": coordinates[1],
            "exclude": "minutely,hourly,daily,alerts",
            "appid": weather_key,
        },
    )

    # print(weather.json())
    current_weather = weather.json()["current"]
    temp = "{:.2f}".format(float(current_weather["temp"]) - 273.15)
    felt_temp = "{:.2f}".format(float(current_weather["feels_like"]) - 273.15)
    pressure = current_weather["pressure"]
    humidity = current_weather["humidity"]

    oneMetrePerSecondInKnots = float(1.94384)

    wind_speed_ms = current_weather["wind_speed"]
    wind_speed_knots = "{:.2f}".format(float(current_weather["wind_speed"]) * oneMetrePerSecondInKnots)
    wind_degrees = int(current_weather["wind_deg"])

    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]

    wind_direction = directions[int((wind_degrees % 360) / 22.5) + 1]

    description = current_weather["weather"][0]["description"]

    message = f"Current weather for <b>{location}</b>\nActual temperature: {temp}°C\nFelt temperature: {felt_temp}°C\nPressure: {pressure} hPa\nHumidity: {humidity}%\nWind: {wind_speed_ms} m/s ({wind_speed_knots} kn) {wind_direction}\nDescription: {description}\n"

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode=telegram.ParseMode.HTML,
        text=message,
    )


def get_next_hour(update, context):
    logger.info("Received /nexthour from user id " + str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Not implemented")


def get_tomorrow(update, context):
    logger.info("Received /tomorrow from user id " + str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Not implemented")


def get_week(update, context):
    logger.info("Received /week from user id " + str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Not implemented")


if __name__ == "__main__":
    main()
