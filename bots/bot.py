from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount




class EcoBot(ActivityHandler):
    
    async def on_members_added_activity(self, members_added :[ChannelAccount], turn_context:TurnContext):
       
       for mem in members_added:
           if mem.id != turn_context.activity.recipient.id:
               await turn_context.send_activity("Hello and Welcome")


    async def on_message_activity(self, turn_context:TurnContext):
        response = turn_context.activity.text
        print(turn_context.activity)
        print(response)
        result = f"You entered {response}"
        await turn_context.send_activity(MessageFactory.text(f"Echo {result}"))

