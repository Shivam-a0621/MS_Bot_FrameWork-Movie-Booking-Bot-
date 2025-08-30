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

# # from datetime import datetime
# from tmdbv3api import TMDb,Movie
# tmdb = TMDb()
# tmdb.api_key = "33bccb67ad3e9bd9ae9655388424aded"
# movie = Movie()

# Dummy movie data JSON
DUMMY_MOVIES = [
    {
        "title": "Avengers: Endgame",
        "theatre": "AMC Empire 25",
        "timing": "7:00 PM",
        "price": "$12",
        "banner": "https://preview.redd.it/1sdabp4nt2m21.jpg?width=1080&crop=smart&auto=webp&s=a6e02510dff2863b0563437915d6a214055ceba8",
    },
    {
        "title": "Spider-Man: No Way Home",
        "theatre": "Regal Cinemas",
        "timing": "8:30 PM",
        "price": "$15",
        "banner": "https://m.media-amazon.com/images/I/71RToZIDORL.jpg",
    },
    {
        "title": "Inception",
        "theatre": "Cineplex 10",
        "timing": "6:00 PM",
        "price": "$10",
        "banner": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_FMjpg_UX1000_.jpg",
        # "trailer":"https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4"
    },
    {
        "title": "The Matrix",
        "theatre": "Downtown Theatre",
        "timing": "9:00 PM",
        "price": "$11",
        "banner": "https://popcult.blog/wp-content/uploads/2021/12/matrix-banner.png",
    },
    {
        "title": "Ek Bihari Sau Pr Bhari",
        "theatre": "SonaGaachi",
        "timing": "12:00 PM",
        "price": "$10000",
        "banner": "https://i.ytimg.com/vi/OFiqCQB0WnE/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLD70gehl0mJxlR9dvLNAz13vS2QNQ",
    },
]


regions = {"US": "United States", "IN": "India", "GB": "United Kingdom", "FR": "France"}

regions_reverse = {
    "United States": "US",
    "India": "IN",
    "United Kingdom": "GB",
    "France": "FR",
}


class BookMovieDialog(ComponentDialog):
    def __init__(self, user_profile_accessor, dialog_id: str = "BookMovieDialog"):
        super(BookMovieDialog, self).__init__(dialog_id)
        # Save the user profile accessor for later use
        self.user_profile_access = user_profile_accessor

        self.add_dialog(
            WaterfallDialog(
                "BookMovieWaterfall",
                [
                    self.choose_city_step,
                    self.fetch_movies_step,
                    self.show_movie_options_step,
                    self.movie_selection_step,
                    self.booking_ticket_step,
                    self.end_step,
                ],
            )
        )
        self.add_dialog(ChoicePrompt("ChoicePrompt"))
        self.initial_dialog_id = "BookMovieWaterfall"

    async def choose_city_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # Prompt the user to select a city
        cities = [
            Choice("Mumbai"),
            Choice("Pune"),
            Choice("Banglore"),
            Choice("Chennai"),
        ]
        return await step_context.prompt(
            "ChoicePrompt",
            PromptOptions(
                prompt=MessageFactory.text("Please select your city:"),
                choices=cities,
            ),
        )

    async def fetch_movies_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # Based on the selected city, assign movies.
        selected_region = step_context.result.value
        step_context.values["city"] = selected_region
        print(step_context.values["city"])

        # movies_popular =movie.popular(page=1, region=selected_region_code)

        movies = DUMMY_MOVIES
        step_context.values["movies"] = movies
        return await step_context.next(movies)

    async def show_movie_options_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # Build Adaptive Cards for each movie and display them as a carousel.
        movies = step_context.values["movies"]
        attachments = []
        for movie in movies:
            movie_card = {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": movie["title"],
                        "weight": "Bolder",
                        "size": "Large",
                        "horizontalAlignment": "Center",
                    },
                    {
                        "type": "Image",
                        "url": movie["banner"],
                        "size": "large",
                        "horizontalAlignment": "Center",
                    },
                    {
                        "type": "TextBlock",
                        "text": f"Theatre: {movie['theatre']}",
                        "wrap": True,
                    },
                    {
                        "type": "TextBlock",
                        "text": f"Timing: {movie['timing']}",
                        "wrap": True,
                    },
                    {
                        "type": "TextBlock",
                        "text": f"Price: {movie['price']}",
                        "wrap": True,
                    },
                ],
                "actions": [
                    {
                        "type": "Action.Submit",
                        "title": "Book This Movie",
                        "data": {"selected_movie": movie},
                    },
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.2",
            }

            attachment = CardFactory.adaptive_card(movie_card)
            attachments.append(attachment)
        message = MessageFactory.carousel(attachments)
        await step_context.context.send_activity(message)
        # Wait for the user's click on the button
        return DialogTurnResult(status=DialogTurnStatus.Waiting)

    async def movie_selection_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # Capture the submitted data from the Adaptive Card button click
        submitted_data = step_context.context.activity.value
        selected_movie = submitted_data.get("selected_movie", {})
        step_context.values["selected_movie"] = selected_movie
        # await step_context.context.send_activity(f"You have selected: {selected_movie.get('title', 'N/A')}.")
        return await step_context.next(None)

    async def booking_ticket_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # Retrieve the user's profile details from the user state
        user_profile = await self.user_profile_access.get(
            step_context.context, UserProfile
        )
        # if not user_profile or not user_profile.name:
        #     await step_context.context.send_activity("User profile not found or incomplete!")
        # else:
        #     await step_context.context.send_activity(f"User profile: {user_profile}")
        selected_movie = step_context.values["selected_movie"]

        if user_profile.movies_booked is None:
            user_profile.movies_booked = []
        # Append the new parking booking details.
        user_profile.movies_booked.append(selected_movie)

        booking_ticket_card = {
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
                                    "url": selected_movie.get("banner", ""),
                                    "size": "medium",
                                }
                            ],
                        },
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": "🎉 Booking Confirmation 🎉",
                                    "weight": "Bolder",
                                    "size": "ExtraLarge",
                                    "horizontalAlignment": "Center",
                                }
                            ],
                        },
                    ],
                },
                {
                    "type": "TextBlock",
                    "text": f"Name: {user_profile.name}",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": f"Email: {user_profile.email}",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": f"Phone: {user_profile.phone}",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": "Movie Details:",
                    "weight": "Bolder",
                    "spacing": "Medium",
                },
                {
                    "type": "TextBlock",
                    "text": f"Title: {selected_movie.get('title', 'N/A')}",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": f"Theatre: {selected_movie.get('theatre', 'N/A')}",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": f"Timing: {selected_movie.get('timing', 'N/A')}",
                    "wrap": True,
                },
                {
                    "type": "TextBlock",
                    "text": f"Price: {selected_movie.get('price', 'N/A')}",
                    "wrap": True,
                },
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.3",
        }

        ticket_attachment = CardFactory.adaptive_card(booking_ticket_card)

        await step_context.context.send_activity(
            MessageFactory.attachment(ticket_attachment)
        )
        # await step_context.context.send_activity(MessageFactory.text(f"profile with movies details: {user_profile}"))
        return await step_context.next(None)

    async def end_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity(
            "Thank you for booking your movie! Your ticket has been generated."
        )
        return await step_context.end_dialog()
