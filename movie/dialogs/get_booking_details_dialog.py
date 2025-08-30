from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.core import MessageFactory, CardFactory
from data_models.user_profile import UserProfile

class GetBookingDetailsDialog(ComponentDialog):
    def __init__(self, user_profile_accessor, dialog_id: str = "GetBookingDetailsDialog"):
        super(GetBookingDetailsDialog, self).__init__(dialog_id)
        self.user_profile_accessor = user_profile_accessor

        self.add_dialog(
            WaterfallDialog(
                "GetBookingDetailsWaterfall",
                [
                    self.show_details_step,
                    self.end_step,
                ],
            )
        )
        self.initial_dialog_id = "GetBookingDetailsWaterfall"

    async def show_details_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Retrieve the user profile from state.
        user_profile = await self.user_profile_accessor.get(step_context.context, UserProfile)
        
        # Create a list to hold Adaptive Card attachments.
        attachments = []

        # Profile Card (always display)
        profile_card = {
            "type": "AdaptiveCard",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "👤 User Profile",
                    "weight": "Bolder",
                    "size": "ExtraLarge",
                    "horizontalAlignment": "Center"
                },
                {"type": "TextBlock", "text": f"Name: {user_profile.name}", "wrap": True},
                {"type": "TextBlock", "text": f"Email: {user_profile.email}", "wrap": True},
                {"type": "TextBlock", "text": f"Age: {user_profile.age}", "wrap": True},
                {"type": "TextBlock", "text": f"Phone: {user_profile.phone}", "wrap": True},
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.2"
        }
        attachments.append(CardFactory.adaptive_card(profile_card))

        # Movie Booking Card (if movies booked exists)
        if user_profile.movies_booked and len(user_profile.movies_booked) > 0:
            movie_items = []
            for movie in user_profile.movies_booked:
                movie_items.append({
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                                {
                                    "type": "Image",
                                    "url": movie.get("banner", ""),
                                    "size": "Small"
                                }
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {"type": "TextBlock", "text": f"Title: {movie.get('title', 'N/A')}", "wrap": True},
                                {"type": "TextBlock", "text": f"Theatre: {movie.get('theatre', 'N/A')}", "wrap": True},
                                {"type": "TextBlock", "text": f"Timing: {movie.get('timing', 'N/A')}", "wrap": True},
                                {"type": "TextBlock", "text": f"Price: {movie.get('price', 'N/A')}", "wrap": True}
                            ]
                        }
                    ]
                })
            movie_card = {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "🎬 Movies Booked",
                        "weight": "Bolder",
                        "size": "Large",
                        "horizontalAlignment": "Center"
                    }
                ] + movie_items,
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.2"
            }

            attachments.append(CardFactory.adaptive_card(movie_card))

        # Food Order Card (if food ordered exists)
        if user_profile.food_ordered and len(user_profile.food_ordered) > 0:
            food_text = ""
            for food in user_profile.food_ordered:
                food_text += (
                    f"Restaurant: {food.get('restaurant', 'N/A')}\n"
                    f"Food: {food.get('food_name', 'N/A')}\n"
                    f"Price: {food.get('price', 'N/A')}\n"
                    f"Type: {food.get('type', 'N/A')}\n\n"
                )
            food_card = {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "🍔 Food Orders",
                        "weight": "Bolder",
                        "size": "Large",
                        "horizontalAlignment": "Center"
                    },
                    {"type": "TextBlock", "text": food_text, "wrap": True},
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.2"
            }
            attachments.append(CardFactory.adaptive_card(food_card))

        # Parking Details Card (if parking done exists)
        if user_profile.parking_done and len(user_profile.parking_done) > 0:
            parking_text = ""
            for parking in user_profile.parking_done:
                parking_text += (
                    f"Parking Lot: {parking.get('parking_lot', 'N/A')}\n"
                    f"Slot: {parking.get('slot_number', 'N/A')}\n"
                    f"Spot: {parking.get('spot_number', 'N/A')}\n"
                    f"Price: {parking.get('price', 'N/A')}\n"
                    f"Duration: {parking.get('duration', 'N/A')}\n"
                    f"Car Number: {parking.get('car_number', 'N/A')}\n"
                    f"Location: {parking.get('location', 'N/A')}\n\n"
                )
            parking_card = {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "🚗 Parking Details",
                        "weight": "Bolder",
                        "size": "Large",
                        "horizontalAlignment": "Center"
                    },
                    {"type": "TextBlock", "text": parking_text, "wrap": True},
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.2"
            }
            attachments.append(CardFactory.adaptive_card(parking_card))

        if attachments:
            # Send the cards as a carousel.
            await step_context.context.send_activity(MessageFactory.carousel(attachments))
        else:
            await step_context.context.send_activity("No booking details found.")

        return await step_context.next(None)

    async def end_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("These are your current booking details.")
        return await step_context.end_dialog()
