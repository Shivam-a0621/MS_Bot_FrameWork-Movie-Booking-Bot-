from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    ConversationState,
    UserState
)

from botbuilder.dialogs import Dialog
from helpers.shivam_dialog_helper import DialogHelper



class   DialogBot(ActivityHandler):

    def __init__(self,conv_state:ConversationState,user_state:UserState,dialog:Dialog):


        if conv_state is None:
            raise TypeError(
                "Conversation state is none"
            )
        if user_state is None:
            raise TypeError(
                "User state is none "
            )
        
        if dialog is None:
            raise TypeError(
                "Dialog is None"
            )
        

        self.conv_state= conv_state
        self.user_state= user_state
        self.dialog= dialog


    async def on_turn(self, turn_context:TurnContext):
        
        await super().on_turn(turn_context)   

        await self.conv_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)


    async def on_message_activity(self, turn_context:TurnContext):
        # print("line number 47 shivambot",turn_context.activity.text)

        # if (turn_context.activity.text == "hi"):
            await DialogHelper.run_dialog(
                self.dialog,
                turn_context,
                self.conv_state.create_property("DialogState")
            )




