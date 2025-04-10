from telegram import Update
from telegram.ext import ContextTypes
from config import SUPPORTED_CHAINS

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    """
    help_text = (
        "🤖 *BubblerMaps Bot Help*\n\n"
        "*Available Commands:*\n"
        "• /start - Start the bot\n"
        "• /getinfo [chain] [address] - Get token information\n"
        "• /help - Show this help message\n\n"
        "*Supported Chains:*\n"
    )
    
    # Add supported chains
    chains_list = "\n".join(f"• {chain} - {name}" for chain, name in SUPPORTED_CHAINS.items())
    help_text += chains_list
    
    await update.message.reply_text(
        help_text,
        parse_mode="Markdown"
    ) 