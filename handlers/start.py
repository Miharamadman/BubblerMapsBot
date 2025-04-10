from telegram import Update
from telegram.ext import ContextTypes
from config import SUCCESS_MESSAGES

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    """
    await update.message.reply_text(
        SUCCESS_MESSAGES["welcome"],
        parse_mode="Markdown"
    ) 