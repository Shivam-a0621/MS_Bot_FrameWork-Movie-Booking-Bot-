import re
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    PromptOptions,
    AttachmentPrompt
)
from botbuilder.dialogs.prompts import TextPrompt, NumberPrompt, ConfirmPrompt, PromptValidatorContext
from botbuilder.schema import Attachment
from botbuilder.core import MessageFactory
from data_models.user_profile import UserProfile

class UserProfileDialog(ComponentDialog):
    def __init__(self, user_profile_accessor, dialog_id: str = "UserProfileDialog"):
        super(UserProfileDialog, self).__init__(dialog_id)

        self.user_profile_access = user_profile_accessor

        # Add prompts with custom validators where needed.
        self.add_dialog(TextPrompt("NamePrompt"))
        self.add_dialog(TextPrompt("EmailPrompt", self.email_validator))
        self.add_dialog(NumberPrompt("NumberPrompt", self.age_validator))
        self.add_dialog(TextPrompt("PhonePrompt", self.phone_validator))
     
        self.add_dialog(ConfirmPrompt("ConfirmPrompt"))

        # Define the waterfall dialog and its steps.
        self.add_dialog(
            WaterfallDialog(
                "UserProfileWaterfall",
                [
                    self.ask_name_step,
                    self.ask_email_step,
                    self.ask_age_step,
                    self.ask_phone_step,
                
                    self.summary_step,
                    self.confirm_step,
                ],
            )
        )

        self.initial_dialog_id = "UserProfileWaterfall"

    async def ask_name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "NamePrompt",
            PromptOptions(prompt=MessageFactory.text("Please enter your name.")),
        )

    async def ask_email_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Save name and ask for email.
        step_context.values["name"] = step_context.result
        return await step_context.prompt(
            "EmailPrompt",
            PromptOptions(prompt=MessageFactory.text("Please enter your email address.")),
        )

    async def ask_age_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Save email and ask for age.
        step_context.values["email"] = step_context.result
        return await step_context.prompt(
            "NumberPrompt",
            PromptOptions(prompt=MessageFactory.text("Please enter your age.")),
        )

    async def ask_phone_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Save age and ask for phone number.
        step_context.values["age"] = step_context.result
        return await step_context.prompt(
            "PhonePrompt",
            PromptOptions(prompt=MessageFactory.text("Please enter your phone number.")),
        )

    async def summary_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # Save phone number.
        step_context.values["phone"] = step_context.result

        # Build a summary string.
        summary = (
            f"Your details are:\n"
            f"Name: {step_context.values['name']}\n"
            f"Email: {step_context.values['email']}\n"
            f"Age: {step_context.values['age']}\n"
            f"Phone: {step_context.values['phone']}\n\n"
            "Is this information correct?"
        )
        return await step_context.prompt(
            "ConfirmPrompt", PromptOptions(prompt=MessageFactory.text(summary))
        )

    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            # Create and store the user profile if the user confirms.
            user_profile = UserProfile(
                name=step_context.values["name"],
                email=step_context.values["email"],
                age=step_context.values["age"],
                phone=step_context.values["phone"],
            )
            # Save user_profile to state.
            await self.user_profile_access.set(step_context.context, user_profile)
            await step_context.context.send_activity(
                MessageFactory.text(f"Thank you! Your profile has been saved:\n{user_profile}")
            )
        else:
            await step_context.context.send_activity(
                MessageFactory.text("Okay, let's try again.")
            )
        return await step_context.end_dialog()

    # --- Validators ---

    async def age_validator(self, prompt_context: PromptValidatorContext) -> bool:
        if prompt_context.recognized.succeeded:
            value = prompt_context.recognized.value
            if 0 < value < 150:
                return True
        await prompt_context.context.send_activity("Please enter a valid age between 1 and 149.")
        return False

    async def email_validator(self, prompt_context: PromptValidatorContext) -> bool:
        if prompt_context.recognized.succeeded:
            value = prompt_context.recognized.value
            pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if re.match(pattern, value):
                return True
        await prompt_context.context.send_activity("Please enter a valid email address.")
        return False

    async def phone_validator(self, prompt_context: PromptValidatorContext) -> bool:
        if prompt_context.recognized.succeeded:
            value = prompt_context.recognized.value
            # Allow an optional + and 7-15 digits.
            pattern = r'^\+?\d{7,15}$'
            if re.match(pattern, value):
                return True
        await prompt_context.context.send_activity("Please enter a valid phone number (digits only, with optional +).")
        return False
    

     
