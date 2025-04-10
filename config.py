import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BUBBLER_TOKEN")
SCREENSHOT_API_KEY = os.getenv("SCREENSHOT_API_TOKEN")

# API Endpoints
BUBBLEMAPS_API_URL = "https://api-legacy.bubblemaps.io/map-data"
BUBBLEMAPS_UI_URL = "https://bubblemaps.io/token"

# Supported Chains
SUPPORTED_CHAINS = {
    "eth": "Ethereum",
    "bsc": "Binance Smart Chain",
    "ftm": "Fantom",
    "avax": "Avalanche",
    "cro": "Cronos",
    "arbi": "Arbitrum",
    "poly": "Polygon",
    "base": "Base",
    "sol": "Solana",
    "sonic": "Sonic"
}

# Rate Limiting
RATE_LIMIT_PER_USER = 10  # requests per minute
RATE_LIMIT_WINDOW = 60    # seconds

# Error Messages
ERROR_MESSAGES = {
    "invalid_address": "❌ Invalid contract address. Please provide a valid address and try again.",
    "rate_limit": "⚠️ Too many requests. Please wait a moment before trying again.",
    "api_error": "❌ Error fetching data. Please try again later.",
    "screenshot_error": "❌ Error generating screenshot. Please try again later.",
    "invalid_chain": "❌ Invalid chain. Supported chains are: " + ", ".join(SUPPORTED_CHAINS.keys())
}

# Success Messages
SUCCESS_MESSAGES = {
    "welcome": "👋 Welcome to BubblerMaps Bot!\n\n"
               "I can help you analyze any token on Bubblemaps.\n\n"
               "Use /getinfo [contract_address] to get started!\n"
               "Example: /getinfo 0x123...abc\n\n"
               "Use /help for more information."
} 