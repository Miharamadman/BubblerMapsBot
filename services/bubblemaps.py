import aiohttp
import asyncio
from typing import Dict, Any, Optional
from config import BUBBLEMAPS_API_URL, SUPPORTED_CHAINS

class BubblemapsAPI:
    def __init__(self):
        self.session = None
        self._lock = asyncio.Lock()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_token_data(self, chain: str, address: str) -> Dict[str, Any]:
        """
        Fetch token data from Bubblemaps API.
        """
        if chain not in SUPPORTED_CHAINS:
            raise ValueError(f"Unsupported chain: {chain}")
        
        async with self._lock:  # Ensure thread safety
            try:
                async with self.session.get(
                    BUBBLEMAPS_API_URL,
                    params={"token": address, "chain": chain}
                ) as response:
                    if response.status == 401:
                        raise ValueError("Token not found")
                    if response.status != 200:
                        raise ValueError(f"API error: {response.status}")
                    
                    return await response.json()
            
            except aiohttp.ClientError as e:
                raise ValueError(f"Network error: {str(e)}")
            except ValueError as e:
                raise e
            except Exception as e:
                raise ValueError(f"Unexpected error: {str(e)}")

bubblemaps_api = BubblemapsAPI() 