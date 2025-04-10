import re
from typing import Tuple, Optional

def validate_contract_address(address: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a contract address.
    Returns (is_valid, error_message)
    """
    # Remove any whitespace
    address = address.strip()
    
    # Check if address starts with 0x
    if not address.startswith('0x'):
        return False, "Address must start with '0x'"
    
    # Check length (40 characters + 0x prefix)
    if len(address) != 42:
        return False, "Address must be 42 characters long (including 0x prefix)"
    
    # Check if it's a valid hexadecimal string
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False, "Address must be a valid hexadecimal string"
    
    return True, None

def extract_chain_and_address(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract chain and address from user input.
    Returns (chain, address, error_message)
    """
    parts = text.strip().split()
    
    if len(parts) == 1:
        # Default to Ethereum if no chain specified
        return "eth", parts[0], None
    
    if len(parts) == 2:
        chain = parts[0].lower()
        address = parts[1]
        return chain, address, None
    
    return None, None, "Invalid format. Use: /getinfo [chain] [address] or /getinfo [address]" 