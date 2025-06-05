import requests
import time
from config import OPENF1_BASE_URL


def make_api_request_with_retry(url, params=None, max_retries=3, delay=1):
    """Make API request with retry logic and rate limiting"""
    for attempt in range(max_retries):
        try:
            time.sleep(delay)  # Add delay between requests to avoid rate limiting
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 429:  # Rate limited
                wait_time = min(2**attempt, 10)  # Exponential backoff, max 10 seconds
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            print(
                f"Request failed (attempt {attempt + 1}), retrying in {delay * (attempt + 1)} seconds..."
            )
            time.sleep(delay * (attempt + 1))

    return None


def fetch_f1_data(endpoint, params=None):
    """Fetch data from OpenF1 API with proper error handling"""
    url = f"{OPENF1_BASE_URL}/{endpoint}"
    return make_api_request_with_retry(url, params)
