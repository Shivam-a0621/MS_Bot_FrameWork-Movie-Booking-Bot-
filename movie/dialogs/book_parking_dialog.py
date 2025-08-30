from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    DialogTurnStatus,
)
from botbuilder.core import MessageFactory, CardFactory
from data_models.user_profile import UserProfile

class BookParkingDialog(ComponentDialog):
    def __init__(self, user_profile_accessor, dialog_id: str = "BookParkingDialog"):
        super(BookParkingDialog, self).__init__(dialog_id)
        # Save the user profile accessor for later use.
        self.user_profile_accessor = user_profile_accessor
        
        self.add_dialog(
            WaterfallDialog("BookParkingWaterfall", [
                self.show_parking_card_step,
                self.update_parking_profile_step,
                self.send_ticket_step,       # New step to send the ticket
                self.end_step,
            ])
        )
        self.initial_dialog_id = "BookParkingWaterfall"

    async def show_parking_card_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        parking_card = {
            "type": "AdaptiveCard",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "🚗 Book Your Parking Spot 🚗",
                    "weight": "Bolder",
                    "size": "ExtraLarge",
                    "horizontalAlignment": "Center"
                },
                {
                    "type": "TextBlock",
                    "text": "Parking Lot: ABC Parking",
                    "wrap": True,
                    "horizontalAlignment": "Center"
                },
                {
                    "type": "TextBlock",
                    "text": "Slot Number: 42",
                    "wrap": True,
                    "horizontalAlignment": "Center"
                },
                {
                    "type": "TextBlock",
                    "text": "Price: $5",
                    "wrap": True,
                    "horizontalAlignment": "Center"
                },
                {
                    "type": "TextBlock",
                    "text": "Location: Near the main theatre entrance",
                    "wrap": True,
                    "horizontalAlignment": "Center"
                },
                {
                    "type": "Input.Text",
                    "id": "duration",
                    "placeholder": "Enter duration of parking (in hours)"
                },
                {
                    "type": "Input.Text",
                    "id": "car_number",
                    "placeholder": "Enter your car number"
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Book Parking",
                    "data": {"action": "book_parking"}
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.3"
        }
        card = CardFactory.adaptive_card(parking_card)
        await step_context.context.send_activity(MessageFactory.attachment(card))
        # Wait for the user's submission that contains the input values.
        return DialogTurnResult(status=DialogTurnStatus.Waiting)

    async def update_parking_profile_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Retrieve the submitted input values from the Adaptive Card.
        submitted_data = step_context.context.activity.value
        duration = submitted_data.get("duration", "Not specified")
        car_number = submitted_data.get("car_number", "Not provided")
        
        # Define static parking details from the card.
        parking_details = {
            "parking_lot": "ABC Parking",
            "slot_number": "42",
            "price": "$5",
            "location": "Near the main theatre entrance",
            "duration": duration,
            "car_number": car_number
        }
        
        # Retrieve the current user profile from user state.
        user_profile = await self.user_profile_accessor.get(step_context.context, UserProfile)
        if user_profile is None:
            user_profile = UserProfile()
        # Initialize the parking_done list if not present.
        if user_profile.parking_done is None:
            user_profile.parking_done = []
        # Append the new parking booking details.
        user_profile.parking_done.append(parking_details)
        # Save the updated profile back to state.
        await self.user_profile_accessor.set(step_context.context, user_profile)
        await step_context.context.send_activity("Your parking booking has been saved in your profile!")
        return await step_context.next(None)

    async def send_ticket_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Retrieve the updated user profile.
        user_profile = await self.user_profile_accessor.get(step_context.context, UserProfile)
        if user_profile is None or not user_profile.parking_done:
            await step_context.context.send_activity("No parking booking found.")
            return await step_context.next(None)
        
        # Get the most recent parking booking.
        recent_booking = user_profile.parking_done[-1]
        # Ensure a spot number is assigned.
        if "spot_number" not in recent_booking:
            recent_booking["spot_number"] = "42"  # You can generate or assign dynamically
        
        # Build a ticket card with all parking details.
        ticket_card = {
            "type": "AdaptiveCard",
            "body": [
                {"type": "TextBlock", "text": "Parking Ticket", "weight": "Bolder", "size": "ExtraLarge", "horizontalAlignment": "Center"},
                {"type": "TextBlock", "text": f"Parking Lot: {recent_booking.get('parking_lot', 'N/A')}", "wrap": True},
                {"type": "TextBlock", "text": f"Slot Number: {recent_booking.get('slot_number', 'N/A')}", "wrap": True},
                {"type": "TextBlock", "text": f"Spot Number: {recent_booking.get('spot_number', 'N/A')}", "wrap": True},
                {"type": "TextBlock", "text": f"Price: {recent_booking.get('price', 'N/A')}", "wrap": True},
                {"type": "TextBlock", "text": f"Duration: {recent_booking.get('duration', 'N/A')}", "wrap": True},
                {"type": "TextBlock", "text": f"Car Number: {recent_booking.get('car_number', 'N/A')}", "wrap": True},
                {"type": "TextBlock", "text": f"Location: {recent_booking.get('location', 'N/A')}", "wrap": True}
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.3"
        }
        ticket_attachment = CardFactory.adaptive_card(ticket_card)
        await step_context.context.send_activity(MessageFactory.attachment(ticket_attachment))
        # await step_context.context.send_activity(MessageFactory.text(f"Aftr booking parking profile is : {user_profile}"))
        return await step_context.next(None)

    async def end_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Your parking slot has been booked!")
        return await step_context.end_dialog()
