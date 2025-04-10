import aiohttp
from typing import Optional
from config import BUBBLEMAPS_UI_URL, SCREENSHOT_API_KEY

class ScreenshotService:
    def __init__(self):
        self.session = None
        self.api_key = SCREENSHOT_API_KEY
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate_screenshot(self, chain: str, address: str) -> Optional[bytes]:
        """
        Generate a screenshot of the token's bubble map.
        """
        if not self.api_key:
            raise ValueError("Screenshot API key not configured")
        
        url = f"{BUBBLEMAPS_UI_URL}/{chain}/{address}"
        screenshot_url = (
            f"https://api.screenshotmachine.com"
            f"?key={self.api_key}"
            f"&url={url}"
            "&dimension=1024x768"
            "&device=desktop"
            "&format=jpg"
            "&cacheLimit=0"
            "&delay=2000"
        )
        
        try:
            async with self.session.get(screenshot_url) as response:
                if response.status != 200:
                    raise ValueError(f"Screenshot API error: {response.status}")
                return await response.read()
        
        except aiohttp.ClientError as e:
            raise ValueError(f"Network error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")

# Create a singleton instance
screenshot_service = ScreenshotService() 