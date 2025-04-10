from telegram import Update
from telegram.ext import ContextTypes
from typing import Dict, Any
import asyncio

from utils.validators import validate_contract_address, extract_chain_and_address
from utils.formatters import format_token_info, format_error_message
from services.bubblemaps import bubblemaps_api
from services.screenshot import screenshot_service

class RateLimiter:
    def __init__(self, max_requests: int, window: int):
        self.max_requests = max_requests
        self.window = window
        self.requests: Dict[int, list] = {}
    
    def is_allowed(self, user_id: int) -> bool:
        now = asyncio.get_event_loop().time()
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests
        self.requests[user_id] = [t for t in self.requests[user_id] if now - t < self.window]
        
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        self.requests[user_id].append(now)
        return True

# Initialize rate limiter
rate_limiter = RateLimiter(max_requests=10, window=60)

async def getinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /getinfo command.
    """
    user_id = update.effective_user.id
    
    # Check rate limit
    if not rate_limiter.is_allowed(user_id):
        await update.message.reply_text(
            format_error_message("rate_limit"),
            parse_mode="Markdown"
        )
        return
    
    # Extract and validate input
    if not context.args:
        await update.message.reply_text(
            "Please provide a contract address.\n"
            "Usage: /getinfo [chain] [address] or /getinfo [address]"
        )
        return
    
    chain, address, error = extract_chain_and_address(" ".join(context.args))
    if error:
        await update.message.reply_text(error)
        return
    
    is_valid, error_msg = validate_contract_address(address)
    if not is_valid:
        await update.message.reply_text(error_msg)
        return
    
    # Show "processing" message
    processing_msg = await update.message.reply_text("🔄 Processing your request...")
    
    try:
        # Fetch token data
        async with bubblemaps_api as api:
            token_data = await api.get_token_data(chain, address)
        
        # Generate screenshot
        async with screenshot_service as service:
            screenshot = await service.generate_screenshot(chain, address)
        
        # Format and send response
        message = format_token_info(token_data, chain, address)
        await update.message.reply_photo(
            photo=screenshot,
            caption=message,
            parse_mode="Markdown"
        )
        
        # Delete processing message
        await processing_msg.delete()
    
    except ValueError as e:
        await update.message.reply_text(
            format_error_message("api_error", str(e)),
            parse_mode="Markdown"
        )
        await processing_msg.delete()
    
    except Exception as e:
        await update.message.reply_text(
            format_error_message("api_error", "An unexpected error occurred."),
            parse_mode="Markdown"
        )
        await processing_msg.delete() 