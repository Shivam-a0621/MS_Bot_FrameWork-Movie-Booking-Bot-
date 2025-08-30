from botbuilder.dialogs import(
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    
)

from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    
    PromptOptions,
    PromptValidatorContext,
)


from botbuilder.schema import (
    ChannelAccount,
    HeroCard,
    CardImage,
    CardAction,
    ActionTypes,
    
)

from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory,UserState,CardFactory
from data.shivamstate import UserProfile



class UserProfileDialog(ComponentDialog):
    def __init__(self,user_sate:UserState):
        super(UserProfileDialog,self).__init__(UserProfileDialog.__name__)

        self.user_profile_accessor = user_sate.create_property("UserProfile")
        # print(self.user_profile_accessor)
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
            self.sex_step,
            self.name_step,
            self.name_confirm,
            self.age_step,
            self.summary_step,
            self.show_card,
            self.confirm_step,
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            NumberPrompt(NumberPrompt.__name__, UserProfileDialog.age_prompt_validator)
        )
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        

       
        # print(self.add_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__


    async def sex_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
       
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please enter your sex."),
                choices=[Choice("Male"), Choice("Female"), Choice("Gay")],
            ),
        )
    
    async def name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
            
            step_context.values["sex"] = step_context.result.value
            # print(step_context.result.value)

            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Please enter your name.")),
            )
    
    async def name_confirm(self,step_context:WaterfallStepContext)->DialogTurnResult:
         step_context.values["name"] = step_context.result

         await step_context.context.send_activity(
              f"Thanks {step_context.result} this is your name"
         )

         return await step_context.prompt(
              ConfirmPrompt.__name__,
              PromptOptions(
                   prompt=MessageFactory.text("Would you like to enter your age type Yes or No")
                
              )
         )
    
    async def age_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
            
            
            
            if step_context.result:
              
                return await step_context.prompt(
                    NumberPrompt.__name__,
                    PromptOptions(
                        prompt=MessageFactory.text("Please enter your age."),
                        retry_prompt=MessageFactory.text(
                            "The value entered must be greater than 0 and less than 150."
                        ),
                    ),
                )
            

           
            return await step_context.next(-1)
    

    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
            msg = f"Thanks."
            if step_context.result:
                msg += f" Your profile saved successfully."
            else:
                msg += f" Your profile will not be kept."

            await step_context.context.send_activity(MessageFactory.text(msg))

            
            return await step_context.end_dialog()
    
    async def summary_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["age"]=step_context.result
        
        user_profile = await self.user_profile_accessor.get(
            step_context.context, UserProfile
        )

        user_profile.sex = step_context.values["sex"]
        user_profile.name = step_context.values["name"]
        user_profile.age = step_context.values["age"]

        # await step_context.context.send_activity(f"This is user profile {user_profile}")
        

        msg = f"I have your sex as {user_profile.sex} and your name as {user_profile.name}."
        if user_profile.age != -1:
            msg += f" And age as {user_profile.age}."

        await step_context.context.send_activity(MessageFactory.text(msg))

      
       

        
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Is this ok?")),
        )
    

    

    async def show_card(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        user_profile = await self.user_profile_accessor.get(
             step_context.context, UserProfile
             )
        user_profile.sex = step_context.values["sex"]
        user_profile.name = step_context.values["name"]
        user_profile.age = step_context.values["age"]

  

        # Define the Adaptive Card JSON payload with summary details
        adaptive_card_content = {
    "type": "AdaptiveCard",
    "body": [
        {
            
            "type": "Container",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "🎉 User Profile Summary 🎉",
                    "weight": "Bolder",
                    "size": "ExtraLarge",
                    "color": "Accent",
                    "horizontalAlignment": "Center"
                }
            ]
        },
        {
            # Name Container
            "type": "Container",
            "separator": True,
            "spacing": "Medium",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "👤 Name",
                    "weight": "Bolder",
                    "size": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": f"{user_profile.name}",
                    "wrap": True,
                    "spacing": "Small"
                }
            ]
        },
        {
            # Sex Container
            "type": "Container",
            "separator": True,
            "spacing": "Medium",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "🚻 Sex",
                    "weight": "Bolder",
                    "size": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": f"{user_profile.sex}",
                    "wrap": True,
                    "spacing": "Small"
                }
            ]
        },
        {
            # Age Container
            "type": "Container",
            "separator": True,
            "spacing": "Medium",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "🎂 Age",
                    "weight": "Bolder",
                    "size": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": f"{user_profile.age}",
                    "wrap": True,
                    "spacing": "Small"
                }
            ]
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}

        # Create the Adaptive Card attachment
        card_attachment = CardFactory.adaptive_card(adaptive_card_content)
        
        # Send the Adaptive Card as an attachment in the message
        await step_context.context.send_activity(MessageFactory.attachment(card_attachment))

    # Prompt the user for confirmation
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Is this ok?")),
        )
     









    @staticmethod
    async def age_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        # This condition is our validation rule. You can also change the value at this point.
        
        return (
            prompt_context.recognized.succeeded
            and 0 < prompt_context.recognized.value < 150
        )


