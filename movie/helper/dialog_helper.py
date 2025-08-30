# helpers/dialog_helper.py
from botbuilder.core import StatePropertyAccessor, TurnContext
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus

class DialogHelper:
    @staticmethod
    async def run_dialog(
        dialog: Dialog, turn_context: TurnContext, accessor: StatePropertyAccessor
    ):
        # Create a DialogSet with the provided accessor to store the dialog state.
        dialog_set = DialogSet(accessor)
        # Add the dialog to the dialog set.
        '''A new DialogSet is instantiated with the provided accessor.
        # Significance:
        # This tells the dialog system where to save its state (i.e., the current progress in the dialog).
        # The state might be stored in memory, a database, or another storage mechanism.
        # Using an accessor ensures that the dialog's state is maintained across different turns of the conversation.'''
        dialog_set.add(dialog)

        # Create a dialog context for the current turn.
        dialog_context = await dialog_set.create_context(turn_context)
        # Continue any dialog that might already be active.
        '''continue_dialog() checks whether there is already an active dialog in progress.
            Significance:
            If a dialog is already active, this call will resume it and return its current status.
            The result (an object) has a property called status that tells you whether the dialog is waiting for input, has completed, or is empty.'''
        results = await dialog_context.continue_dialog()

        # If no dialog is active, start the provided dialog.
        if results.status == DialogTurnStatus.Empty:
            await dialog_context.begin_dialog(dialog.id)
