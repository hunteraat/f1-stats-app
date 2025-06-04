import os
import sys
import aiohttp
import asyncio
import logging
from config import OPENF1_BASE_URL

async def fetch_f1_data(session: aiohttp.ClientSession, endpoint: str, params: dict = None, max_retries: int = 3, initial_delay: float = 1.0):
    """
    Fetch data from OpenF1 API with retry logic and error handling.
    
    Args:
        session (aiohttp.ClientSession): The aiohttp session to use
        endpoint (str): The API endpoint to call
        params (dict, optional): Query parameters to include
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
        initial_delay (float, optional): Initial delay between retries in seconds. Defaults to 1.0.
        
    Returns:
        dict: The JSON response from the API
        
    Raises:
        Exception: If the request fails after all retries
    """
    url = f"{OPENF1_BASE_URL}/{endpoint}"
    retry_count = 0
    delay = initial_delay
    logger = logging.getLogger(__name__)
    
    while retry_count <= max_retries:
        try:
            logger.debug(f"Making request to: {url} with params: {params}")
            
            async with session.get(url, params=params) as response:
                status = response.status
                logger.debug(f"Response status: {status}")
                
                if status == 200:
                    data = await response.json()
                    logger.debug(f"Received {len(data) if data else 0} records")
                    return data
                    
                elif status == 429:  # Rate limited
                    if retry_count < max_retries:
                        logger.warning(f"Rate limited. Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                        delay *= 2  # Exponential backoff
                        retry_count += 1
                        continue
                    else:
                        raise Exception(f"Max retries reached after rate limit")
                        
                else:
                    error_text = await response.text()
                    raise Exception(f"API error: Status {status}, {error_text}")
                    
        except Exception as e:
            if retry_count < max_retries:
                logger.warning(f"Request failed: {str(e)}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2
                retry_count += 1
                continue
            raise Exception(f"Failed to fetch data after {max_retries} retries: {str(e)}")
    
    raise Exception("Unexpected error in fetch_f1_data") 