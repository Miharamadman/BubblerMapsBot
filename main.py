import os
import logging
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from dotenv import load_dotenv
import requests
import aiohttp
from typing import Tuple, Optional, Dict
import re
import asyncio

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BUBBLER_TOKEN")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot with state storage
state_storage = StateMemoryStorage()
bot = AsyncTeleBot(BOT_TOKEN)

# Constants
BUBBLEMAPS_API_URL = "https://api-legacy.bubblemaps.io/map-data"
BUBBLEMAPS_UI_URL = "app.bubblemaps.io"
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex/tokens"

# Chain configurations with DexScreener mappings
SUPPORTED_CHAINS = {
    "eth": {
        "name": "Ethereum",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "address_length": 42,
        "prefix": "0x",
        "dexscreener": "ethereum"
    },
    "bsc": {
        "name": "Binance Smart Chain",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "address_length": 42,
        "prefix": "0x",
        "dexscreener": "bsc"
    },
    "ftm": {
        "name": "Fantom",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "address_length": 42,
        "prefix": "0x",
        "dexscreener": "fantom"
    },
    "avax": {
        "name": "Avalanche",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "address_length": 42,
        "prefix": "0x",
        "dexscreener": "avalanche"
    },
    "arbi": {
        "name": "Arbitrum",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "address_length": 42,
        "prefix": "0x",
        "dexscreener": "arbitrum"
    },
    "poly": {
        "name": "Polygon",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "address_length": 42,
        "prefix": "0x",
        "dexscreener": "polygon"
    },
    "base": {
        "name": "Base",
        "address_pattern": r"^0x[a-fA-F0-9]{40}$",
        "address_length": 42,
        "prefix": "0x",
        "dexscreener": "base"
    },
    "sol": {
        "name": "Solana",
        "address_pattern": r"^[1-9A-HJ-NP-Za-km-z]{32,44}$",
        "address_length": None,  # Variable length
        "prefix": None,
        "dexscreener": "solana"
    }
}

# Define states
class UserStates(StatesGroup):
    waiting_for_address = State()
    processing_request = State()

def validate_contract_address(chain: str, address: str) -> Tuple[bool, Optional[str]]:
    """Validate a contract address for a specific chain."""
    address = address.strip()
    chain_config = SUPPORTED_CHAINS.get(chain)
    
    if not chain_config:
        return False, f"Unsupported chain: {chain}"
    
    # Check prefix if required
    if chain_config["prefix"] and not address.startswith(chain_config["prefix"]):
        return False, f"Address must start with {chain_config['prefix']} for {chain_config['name']}"
    
    # Check length if specified
    if chain_config["address_length"] and len(address) != chain_config["address_length"]:
        return False, f"Invalid address length for {chain_config['name']}"
    
    # Check pattern
    if not re.match(chain_config["address_pattern"], address):
        return False, f"Invalid address format for {chain_config['name']}"
    
    return True, None

def extract_chain_and_address(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract chain and address from user input."""
    parts = text.strip().split()
    
    if len(parts) == 1:
        return "eth", parts[0], None
    
    if len(parts) == 2:
        chain = parts[0].lower()
        if chain not in SUPPORTED_CHAINS:
            return None, None, f"Unsupported chain. Supported chains are: {', '.join(SUPPORTED_CHAINS.keys())}"
        return chain, parts[1], None
    
    return None, None, "Invalid format. Use: /getinfo [chain] [address] or /getinfo [address]"

async def get_token_data(chain: str, address: str) -> dict:
    """Fetch token data from Bubblemaps API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            BUBBLEMAPS_API_URL,
            params={"token": address, "chain": chain}
        ) as response:
            if response.status == 401:
                raise ValueError("Token not found or maps hasn't been computed yet")
            if response.status != 200:
                raise ValueError(f"API error: {response.status}")
            
            return await response.json()

async def get_dexscreener_data(chain: str, address: str) -> Dict:
    """Fetch token data from DexScreener API."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{DEXSCREENER_API_URL}/{address}") as response:
                if response.status != 200:
                    logger.warning(f"DexScreener API error: {response.status}")
                    return {}

                data = await response.json()
                pairs = data.get('pairs', [])
                
                # Filter pairs for the specific chain
                chain_pairs = [
                    pair for pair in pairs 
                    if pair.get('chainId') == SUPPORTED_CHAINS[chain]['dexscreener']
                ]
                
                if not chain_pairs:
                    return {}

                # Get the pair with highest liquidity
                main_pair = max(chain_pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))
                
                return {
                    'price': float(main_pair.get('priceUsd', 0)),
                    'price_change': {
                        '5m': float(main_pair.get('priceChange', {}).get('m5', 0)),
                        '1h': float(main_pair.get('priceChange', {}).get('h1', 0)),
                        '6h': float(main_pair.get('priceChange', {}).get('h6', 0)),
                        '24h': float(main_pair.get('priceChange', {}).get('h24', 0))
                    },
                    'volume': {
                        '5m': float(main_pair.get('volume', {}).get('m5', 0)),
                        '1h': float(main_pair.get('volume', {}).get('h1', 0)),
                        '6h': float(main_pair.get('volume', {}).get('h6', 0)),
                        '24h': float(main_pair.get('volume', {}).get('h24', 0))
                    },
                    'liquidity': float(main_pair.get('liquidity', {}).get('usd', 0)),
                    'dex': main_pair.get('dexId', 'unknown'),
                    'pair_address': main_pair.get('pairAddress'),
                    'fdv': float(main_pair.get('fdv', 0)),
                    'market_cap': float(main_pair.get('marketCap', 0))
                }
    except Exception as e:
        logger.error(f"Error fetching DexScreener data: {str(e)}")
        return {}

def format_token_info(data: dict, chain: str, address: str, dex_data: dict) -> str:
    """Format token information into a readable message."""
    top_holders = data.get('nodes', [])
    
    # Calculate decentralization score
    top_20_concentration = sum(node['percentage'] for node in top_holders[:20])
    decentralization_score = max(0, 100 - (top_20_concentration / 2))
    
    # Format numbers
    def format_currency(value):
        if value >= 1_000_000_000:
            return f"${value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"${value/1_000:.2f}K"
        else:
            return f"${value:.2f}"

    def format_price(value):
        if value < 0.00000001:
            return f"${value:.12f}"
        elif value < 0.01:
            return f"${value:.8f}"
        elif value < 1:
            return f"${value:.4f}"
        else:
            return f"${value:.2f}"

    def format_price_change(value):
        emoji = "🟢" if value > 0 else "🔴" if value < 0 else "⚪"
        return f"{emoji}{value:+.1f}%"
    
    def format_percentage(value):
        return f"{value:.1f}%"

    message = (
        f"🔍 *{data.get('full_name', 'Unknown Token')} ({data.get('symbol', 'UNKNOWN')})*\n"
        f"`{address}`\n"
        f"{SUPPORTED_CHAINS[chain]['name']}\n"
    )

    if dex_data:
        message += (
            f"💰 P: {format_price(dex_data['price'])} "
            f"MC: {format_currency(dex_data['market_cap'])} "
            f"L: {format_currency(dex_data['liquidity'])}\n"
            f"📊 1H: {format_price_change(dex_data['price_change']['1h'])} "
            f"24H: {format_price_change(dex_data['price_change']['24h'])}\n"
        )

    # Add decentralization score with emoji indicator
    score_emoji = "🟢" if decentralization_score >= 70 else "🟡" if decentralization_score >= 40 else "🔴"
    message += (
        f"Decentralization Score: {score_emoji}{format_percentage(decentralization_score)} "
        f"Top20: {format_percentage(top_20_concentration)}\n"
        f"👥 Holders: {len(top_holders):,}\n\n"
        f"Top Holders:\n"
    )

    # Add top 15 holders with emojis for ranking
    for i, holder in enumerate(top_holders[:15], 1):
        rank_emoji = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "•"
        percentage = holder.get('percentage', 0)
        tx_count = holder.get('transaction_count', 0)
        is_contract = holder.get('is_contract', False)
        
        message += (
            f"{rank_emoji}{format_percentage(percentage)}"
        )
        
        if tx_count > 0:
            message += f" | 🔄 {tx_count:,} txns"
        if is_contract:
            message += " | 📜 Contract"
        
        message += "\n"

    # Add Bubblemaps URL
    message += f"\n🔍 View on Bubblemaps:\nhttps://{BUBBLEMAPS_UI_URL}/{chain}/token/{address}"

    return message

@bot.message_handler(commands=['start'])
async def start_command(message):
    """Handle /start command."""
    welcome_text = (
        "👋 Welcome to BubblerMaps Bot!\n\n"
        "I can help you analyze any token on Bubblemaps.\n\n"
        "Use /getinfo [chain] [address] to get started!\n"
        "Example: /getinfo eth 0x123...abc\n"
        "Example: /getinfo sol ABC123...\n\n"
        "Use /help for more information."
    )
    await bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
async def help_command(message):
    """Handle /help command."""
    help_text = (
        "🤖 *BubblerMaps Bot Help*\n\n"
        "*Available Commands:*\n"
        "• /start - Start the bot\n"
        "• /getinfo [chain] [address] - Get token information\n"
        "• /help - Show this help message\n\n"
        "*Supported Chains:*\n"
    )
    
    chains_list = "\n".join(f"• {chain} - {config['name']}" for chain, config in SUPPORTED_CHAINS.items())
    help_text += chains_list + "\n\n"
    help_text += "*Address Format Examples:*\n"
    help_text += "• ETH/BSC/etc: 0x... (42 characters)\n"
    help_text += "• Solana: Base58 format (32-44 characters)"
    
    await bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['getinfo'])
async def getinfo_command(message):
    """Handle /getinfo command."""
    try:
        command_text = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ''
        if not command_text:
            await bot.reply_to(
                message,
                "Please provide a contract address.\n"
                "Format: [chain] [address] or just [address] for Ethereum\n"
                "Example: eth 0x123...abc or 0x123...abc"
            )
            return

        await process_token_info(message, command_text)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        await bot.reply_to(message, "An unexpected error occurred. Please try again later.")

async def process_token_info(message, command_text):
    """Process token information request."""
    try:
        chain, address, error = extract_chain_and_address(command_text)
        if error:
            await bot.reply_to(message, error)
            return

        is_valid, error_msg = validate_contract_address(chain, address)
        if not is_valid:
            await bot.reply_to(message, error_msg)
            return

        # Send processing message
        processing_msg = await bot.reply_to(message, "🔄 Processing your request...")

        try:
            # Fetch data concurrently
            token_data, dex_data = await asyncio.gather(
                get_token_data(chain, address),
                get_dexscreener_data(chain, address)
            )
            
            # Get screenshot
            async with aiohttp.ClientSession() as session:
                screenshot_url = (
                    f"https://api.screenshotmachine.com"
                    f"?key={os.getenv('SCREENSHOT_API_TOKEN')}"
                    f"&url={BUBBLEMAPS_UI_URL}/{chain}/token/{address}"
                    "&dimension=1024x768"
                    "&device=desktop"
                    "&format=jpg"
                    "&cacheLimit=0"
                    "&delay=3000"
                )
                async with session.get(screenshot_url) as screenshot_response:
                    if screenshot_response.status != 200:
                        raise ValueError(f"Screenshot API error: {screenshot_response.status}")
                    screenshot_content = await screenshot_response.read()

            response_text = format_token_info(token_data, chain, address, dex_data)
            
            # Send response with screenshot
            await bot.send_photo(
                message.chat.id,
                photo=screenshot_content,
                caption=response_text,
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )

        except aiohttp.ClientError as e:
            logger.error(f"API error: {str(e)}")
            response_text = format_token_info(token_data, chain, address, dex_data)
            await bot.reply_to(message, response_text, parse_mode="Markdown")
        
        finally:
            # Clean up
            try:
                await bot.delete_message(message.chat.id, processing_msg.message_id)
            except Exception as e:
                logger.error(f"Error deleting processing message: {str(e)}")

    except ValueError as e:
        error_msg = f"Error: {str(e)}"
        await bot.reply_to(message, error_msg)
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        await bot.reply_to(message, "An unexpected error occurred. Please try again later.")

async def main():
    """Start the bot."""
    logger.info("Starting bot...")
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot connected successfully! Bot name: {bot_info.first_name}")
        await bot.infinity_polling()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
