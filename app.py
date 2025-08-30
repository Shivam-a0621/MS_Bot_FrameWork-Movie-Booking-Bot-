import os
import asyncio
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity


from bots.bot import EcoBot

APP_ID = ""
APP_PASSWORD = ""


adapter_setting = BotFrameworkAdapterSettings(app_id=APP_ID, app_password=APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_setting)

bot = EcoBot()


async def message_handler(request: web.Request) -> web.Response:
    body = await request.json()
    # print(body)
    activity = Activity.deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def aux_function(turn_context):
        await bot.on_turn(turn_context)

    await adapter.process_activity(activity, auth_header, aux_function)

    return web.Response(status=200)


app = web.Application()

app.router.add_post("/api/messages", message_handler)

if __name__ == "__main__":
    web.run_app(app, host="localhost", port=3978)
