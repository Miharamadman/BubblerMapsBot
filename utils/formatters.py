from typing import Dict, Any
from config import BUBBLEMAPS_UI_URL, SUPPORTED_CHAINS

def format_token_info(data: Dict[str, Any], chain: str, address: str) -> str:
    """
    Format token information into a readable message.
    """
    # Calculate top 10% holdings
    top_holders = data.get('nodes', [])
    top_10_percent = sum(node['percentage'] for node in top_holders[:15])  # Assuming top 15 holders represent top 10%
    
    # Format the message
    message = (
        f"🔍 *{data.get('full_name', 'Unknown Token')} ({data.get('symbol', 'UNKNOWN')})*\n\n"
        f"*Contract:* `{address}`\n"
        f"*Chain:* {SUPPORTED_CHAINS.get(chain, chain.upper())}\n\n"
        f"*Token Metrics:*\n"
        f"• Top 10% Holdings: {top_10_percent:.2f}%\n"
        f"• Total Holders: {len(top_holders)}\n\n"
        f"*View on Bubblemaps:*\n"
        f"{BUBBLEMAPS_UI_URL}/{chain}/{address}"
    )
    
    return message

def format_error_message(error_type: str, additional_info: str = "") -> str:
    """
    Format error messages with additional information if provided.
    """
    from config import ERROR_MESSAGES
    
    message = ERROR_MESSAGES.get(error_type, "An unknown error occurred.")
    if additional_info:
        message += f"\n\n{additional_info}"
    
    return message 