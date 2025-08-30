# dialogs/main_dialog.py
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    ChoicePrompt,
    PromptOptions,
    TextPrompt,
)
from botbuilder.dialogs.choices import Choice, ListStyle
from botbuilder.core import MessageFactory
from .book_movie_dialog import BookMovieDialog
from .book_parking_dialog import BookParkingDialog
from .order_food_dialog import OrderFoodDialog
from .get_booking_details_dialog import GetBookingDetailsDialog
from botbuilder.core import UserState
from botbuilder.dialogs import Choice
from .user_profile_dialog import UserProfileDialog
from data_models.user_profile import UserProfile


class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(MainDialog, self).__init__(MainDialog.__name__)
        # Add sub-dialogs
        self.user_profile_accessor = user_state.create_property("UserProfile")

        self.add_dialog(UserProfileDialog(self.user_profile_accessor))
        self.add_dialog(BookMovieDialog(self.user_profile_accessor))
        self.add_dialog(BookParkingDialog(self.user_profile_accessor))
        self.add_dialog(OrderFoodDialog(self.user_profile_accessor))
        self.add_dialog(GetBookingDetailsDialog(self.user_profile_accessor))
        self.add_dialog(
            WaterfallDialog(
                "MainWaterfall",
                [self.welcome_step, self.profile_step, self.menu_step, self.route_step],
            )
        )
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.initial_dialog_id = "MainWaterfall"

    async def welcome_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        await step_context.context.send_activity("Welcome to the Movie Booking Bot!")
        return await step_context.next(None)

    async def profile_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        #
        user_profile = await self.user_profile_accessor.get(
            step_context.context, UserProfile
        )

        if user_profile is None or user_profile.name == "":
            return await step_context.begin_dialog(UserProfileDialog.__name__)
        else:

            return await step_context.next(None)

    async def menu_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        options = [
            Choice("Manage Profile"),
            Choice("Book Movie"),
            Choice("Book Parking"),
            Choice("Order Food"),
            Choice("Get Booking Details"),
        ]
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("What would you like to do?"),
                choices=options,
                style=ListStyle(2),
            ),
        )

    async def route_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        choice = (
            step_context.result.value
            if step_context.result and hasattr(step_context.result, "value")
            else None
        )

        raw_input = step_context.context.activity.text

        if not choice and raw_input:
            await step_context.context.send_activity(
                f"You typed: {raw_input}. That is not a valid option."
            )
            return await step_context.replace_dialog(MainDialog.__name__)

        if choice == "Book Movie":
            return await step_context.begin_dialog(BookMovieDialog.__name__)

        elif choice == "Book Parking":
            return await step_context.begin_dialog(BookParkingDialog.__name__)
        elif choice == "Order Food":
            return await step_context.begin_dialog(OrderFoodDialog.__name__)
        elif choice == "Get Booking Details":
            return await step_context.begin_dialog(GetBookingDetailsDialog.__name__)
        elif choice == "Manage Profile":
            return await step_context.begin_dialog(UserProfileDialog.__name__)
        else:
            await step_context.context.send_activity(
                "Invalid choice. Please try again."
            )
            return await step_context.replace_dialog(MainDialog.__name__)
