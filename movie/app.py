# app.py
import os
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    BotFrameworkAdapter,
    ConversationState,
    UserState,
    MemoryStorage,
)
from bots.movie_booking_bot import MovieBookingBot
from dialogs.main_dialog import MainDialog
from botbuilder.integration.aiohttp import (
    CloudAdapter,
    ConfigurationBotFrameworkAuthentication,
)

from aiohttp.web import Request, Response, json_response
from config import DefaultConfig


APP_ID = os.getenv("MICROSOFT_APP_ID", "")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD", "")


# Set up the adapter
settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
CONFIG = DefaultConfig()

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
ADAPTER = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))

# Create in-memory storage and state management
memory = MemoryStorage()
conversation_state = ConversationState(memory)
user_state = UserState(memory)

# Create main dialog and bot instance
main_dialog = MainDialog(user_state)
bot = MovieBookingBot(conversation_state, user_state, main_dialog)


async def messages(req: Request) -> Response:
    return await ADAPTER.process(req, bot)


app = web.Application()
app.router.add_post("/api/messages", messages)


if __name__ == "__main__":
    try:
        web.run_app(app, host="localhost", port=3978)
    except Exception as error:
        raise error
