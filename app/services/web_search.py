import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.utils.logger import logger
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class WebSearch:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.engine_id = os.getenv("GOOGLE_CSE_ID")
        
        if not self.api_key or not self.engine_id:
            raise ValueError("GOOGLE_API_KEY and GOOGLE_CSE_ID must be set in environment variables or hardcoded.")
        
        try:
            self.client = build("customsearch", "v1", developerKey=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Google Search client: {str(e)}")
            raise

    def search(self, query: str, num_results: int = 5):
        logger.info(f"[WebSearch] Querying: {query}")
        try:
            res = self.client.cse().list(
                q=query,
                cx=self.engine_id,
                num=num_results
            ).execute()

            items = res.get("items", [])
            results = []
            for item in items:
                result = {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet", ""),
                    "displayLink": item.get("displayLink", "")
                }
                results.append(result)
            
            logger.info(f"[WebSearch] Retrieved {len(results)} results for: {query}")
            return results

        except HttpError as http_err:
            logger.error(f"[WebSearch] HTTP Error: {http_err}")
            return []
        except Exception as e:
            logger.error(f"[WebSearch] General Error: {str(e)}")
            return []
