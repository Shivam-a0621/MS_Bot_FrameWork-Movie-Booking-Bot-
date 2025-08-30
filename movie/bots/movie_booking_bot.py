# bots/movie_booking_bot.py
from botbuilder.core import ActivityHandler, TurnContext, ConversationState, UserState, MessageFactory
from botbuilder.schema import ActivityTypes
from helper.dialog_helper import DialogHelper

class MovieBookingBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState, user_state: UserState, dialog):
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog

    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.message:
            print(turn_context.activity.text)
            # Run the dialog system
            await DialogHelper.run_dialog(
                self.dialog, 
                turn_context, 
                self.conversation_state.create_property("DialogState")    # Doubt - So each time when user will send message it will create a new property for storing each turn data.?
            )
        elif turn_context.activity.type == ActivityTypes.conversation_update:
            # Welcome new members
            for member in turn_context.activity.members_added:
                    if member.id != turn_context.activity.recipient.id:
                        await turn_context.send_activity(MessageFactory.text("Hello! Welcome to Movie Booking Bot!"))
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)
