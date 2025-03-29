# Movie Booking Bot

A conversational chatbot built with the Microsoft Bot Framework and Python that allows users to book movies, manage profiles, order food, and book parking—all integrated with real movie data from TMDB. This project leverages adaptive cards for a rich UI experience and uses state management to track user data across turns.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Running the Bot](#running-the-bot)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Movie Booking Bot is a multi-functional chatbot designed for movie enthusiasts. It is built using the Microsoft Bot Framework with Python and supports Microsoft Teams as one of its channels. The bot allows users to:
- **Manage their profile** (including uploading a profile picture)
- **Book movies** with details pulled from TMDB (The Movie Database)
- **Book parking** near theaters
- **Order food** related to the movie experience
- **Retrieve booking details** across these services

The bot uses Adaptive Cards to present rich, interactive content and state management (UserState and ConversationState) to persist user data.

## Features

- **Multi-turn Dialogs:**  
  Uses Waterfall Dialogs for structured conversation flows.
- **Profile Management:**  
  Users can create and update their profiles, including validating email, phone, and age, and uploading a profile picture.
- **Movie Booking:**  
  Integrates with TMDB (dummy data provided in this version) to display movie options based on selected city and language.
- **Parking Booking & Food Ordering:**  
  Additional dialogs allow booking parking and ordering food, with confirmation tickets generated as Adaptive Cards.
- **Adaptive Cards:**  
  Rich card UI for an interactive user experience.
- **Middleware Support:**  
  The bot uses middleware to handle authentication, logging, and error handling.

## Architecture

The system is composed of the following main components:
- **Bot Adapter (CloudAdapter):**  
  Handles incoming HTTP requests, performs authentication, and passes the activity to the bot.
- **TurnContext:**  
  Wraps each incoming activity and provides methods to send, update, or delete activities.
- **Dialogs:**  
  Modular dialog components manage different conversation flows:
  - **MainDialog:** Routes the conversation based on user choices.
  - **UserProfileDialog:** Manages user profile creation and updates.
  - **BookMovieDialog:** Allows users to book movies (integrated with TMDB data).
  - **BookParkingDialog & OrderFoodDialog:** Handle booking parking and ordering food.
  - **GetBookingDetailsDialog:** Retrieves booking history.
- **State Management:**  
  Uses MemoryStorage during development with UserState and ConversationState to persist user and conversation data.
- **TMDB Integration:**  
  Uses either dummy movie data or can be extended to call TMDB APIs for real-time movie details.
- **Authentication:**  
  Uses BotFrameworkAuthentication and middleware to securely authenticate incoming requests, especially from channels like Microsoft Teams.

## Setup and Installation

### Prerequisites

- Python 3.8 or later
- An [Azure Bot Service](https://azure.microsoft.com/en-us/services/bot-services/) (or use the Bot Framework Emulator for local testing)
- [Ngrok](https://ngrok.com/) for exposing your local server
- TMDB API key (optional for real movie data)
- Microsoft App ID and App Password (for production deployments)

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/movie-booking-bot.git
   cd movie-booking-bot
