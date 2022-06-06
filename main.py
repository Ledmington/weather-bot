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

logger = logging.getLogger(__name__)


def get_key(filename: str) -> str:
    if not os.path.exists(filename):
        print(f'File "{filename}" not found.\nQuitting...')
        quit()
    with open(filename, "r") as token_file:
        mytoken = token_file.read()
    return mytoken


def main() -> None:
    FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=FORMAT, datefmt="%d/%m/%Y %H:%M:%S")
    logger.setLevel(logging.DEBUG)

    """
    geolocator = Nominatim(user_agent="weather-bot")
    location = geolocator.geocode("Riccione")
    print(location.address)
    print((location.latitude, location.longitude))
    print(location.raw)
    """

    weather_key = get_key("weather_key.txt")
    telegram_token = get_key("telegram_token.txt")
    print(weather_key)
    print(telegram_token)

    logger.info("Creating updater")
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command),
            CommandHandler("help", help_command),
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


if __name__ == "__main__":
    main()
