from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    ChoicePrompt,
    PromptOptions,
    DialogTurnStatus,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, CardFactory
from data_models.user_profile import UserProfile  # Ensure this model exists

DUMMY_FOOD = [
    {
        "restaurant": "The Food Hub",
        "food_name": "Veggie Pizza",
        "price": "$8",
        "type": "Veg",
        "banner": "https://t3.ftcdn.net/jpg/00/27/57/96/240_F_27579652_tM7V4fZBBw8RLmZo0Bi8WhtO2EosTRFD.jpg"
    },
    {
        "restaurant": "Burger Bonanza",
        "food_name": "Burger",
        "price": "$10",
        "type": "Non-Veg",
        "banner": "https://img.freepik.com/free-photo/delicious-burger-with-many-ingredients-isolated-white-background-tasty-cheeseburger-splash-sauce_90220-1266.jpg?semt=ais_hybrid"
    },
    {
        "restaurant": "Sushi Central",
        "food_name": "Salmon Sushi",
        "price": "$15",
        "type": "Non-Veg",
        "banner": "https://img.freepik.com/free-photo/japanese-sushi-with-salmon-caviar_114579-1106.jpg?ga=GA1.1.358372964.1739445085&semt=ais_hybrid"
    },
    {
        "restaurant": "Green Delight",
        "food_name": "Quinoa Salad",
        "price": "$7",
        "type": "Veg",
        "banner": "https://img.freepik.com/free-photo/top-view-salad-seeds-sesame-seeds-flax-sunflower-seeds-with-tomatoes-basil_141793-4114.jpg?ga=GA1.1.358372964.1739445085&semt=ais_hybrid"
    }
]

class OrderFoodDialog(ComponentDialog):
    def __init__(self, user_profile_accessor, dialog_id: str = "OrderFoodDialog"):
        super(OrderFoodDialog, self).__init__(dialog_id)
        self.user_profile_access = user_profile_accessor
        
        self.add_dialog(
            WaterfallDialog("OrderFoodWaterfall", [
                self.choose_food_type_step,
                self.fetch_food_items_step,
                self.show_food_options_step,
                self.food_selection_step,
                self.order_confirmation_step,
                self.end_step,
            ])
        )
        self.add_dialog(ChoicePrompt("ChoicePrompt"))
        self.initial_dialog_id = "OrderFoodWaterfall"

    async def choose_food_type_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Prompt user to select food type
        food_types = [Choice("Veg"), Choice("Non-Veg")]
        return await step_context.prompt(
            "ChoicePrompt",
            PromptOptions(
                prompt=MessageFactory.text("Please select your food preference:"),
                choices=food_types,
            ),
        )

    async def fetch_food_items_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Filter food items based on selection
        selected_type = step_context.result.value
        step_context.values["food_type"] = selected_type
        filtered_food = [item for item in DUMMY_FOOD if item["type"] == selected_type]
        step_context.values["food_items"] = filtered_food
        return await step_context.next(filtered_food)

    async def show_food_options_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Create carousel of food cards
        food_items = step_context.values["food_items"]
        attachments = []
        
        for item in food_items:
            food_card = {
                "type": "AdaptiveCard",
                "body": [
                    {"type": "TextBlock", "text": item["food_name"], "weight": "Bolder", "size": "Large", "horizontalAlignment": "Center"},
                    {"type": "Image", "url": item["banner"], "size": "large", "horizontalAlignment": "Center"},
                    {"type": "TextBlock", "text": f"Restaurant: {item['restaurant']}", "wrap": True},
                    {"type": "TextBlock", "text": f"Price: {item['price']}", "wrap": True},
                    {"type": "TextBlock", "text": f"Type: {item['type']}", "wrap": True}
                ],
                "actions": [
                    {
                        "type": "Action.Submit",
                        "title": "Order This",
                        "data": {"selected_food": item}
                    }
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.2"
            }
            attachments.append(CardFactory.adaptive_card(food_card))
        
        await step_context.context.send_activity(MessageFactory.carousel(attachments))
        return DialogTurnResult(status=DialogTurnStatus.Waiting)

    async def food_selection_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Capture food selection
        selected_food = step_context.context.activity.value.get("selected_food", {})
        step_context.values["selected_food"] = selected_food
        return await step_context.next(None)

    async def order_confirmation_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Show confirmation with user details
        user_profile = await self.user_profile_access.get(step_context.context, UserProfile)
        selected_food = step_context.values["selected_food"]
        if user_profile.food_ordered is None:
            user_profile.food_ordered = []
        # Append the new parking booking details.
        user_profile.food_ordered.append(selected_food)
        
        confirmation_card = {
            "type": "AdaptiveCard",
            "body": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                                {
                                    "type": "Image",
                                    "url": selected_food.get("banner", ""),
                                    "size": "Medium"
                                }
                            ]
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "🎉 Order Confirmation 🎉",
                                    "weight": "Bolder",
                                    "size": "ExtraLarge",
                                    "horizontalAlignment": "Center"
                                }
                            ]
                        }
                    ]
                },
                {"type": "TextBlock", "text": f"Name: {user_profile.name}", "wrap": True},
                {"type": "TextBlock", "text": f"Email: {user_profile.email}", "wrap": True},
                {"type": "TextBlock", "text": f"Phone: {user_profile.phone}", "wrap": True},
                {"type": "TextBlock", "text": "Order Details:", "weight": "Bolder", "spacing": "Medium"},
                {"type": "TextBlock", "text": f"Item: {selected_food.get('food_name', 'N/A')}", "wrap": True},
                {"type": "TextBlock", "text": f"Restaurant: {selected_food.get('restaurant', 'N/A')}", "wrap": True},
                {"type": "TextBlock", "text": f"Price: {selected_food.get('price', 'N/A')}", "wrap": True},
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.3"
        }
        
        await step_context.context.send_activity(
            MessageFactory.attachment(CardFactory.adaptive_card(confirmation_card)))
        # await step_context.context.send_activity(MessageFactory.text(f"Profile after ordereing food: {user_profile}"))
        return await step_context.next(None)

    async def end_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Your food order is being prepared! Bon appétit! 🍴")
        return await step_context.end_dialog()