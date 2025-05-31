import os
from openai import OpenAI
from app.utils.logger import logger
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple
import re

load_dotenv()

class Safety:
    def __init__(self):
        self.client = OpenAI()
        self.disallowed_categories = [
            "hate", "hate/threatening", "harassment", "harassment/threatening",
            "self-harm", "self-harm/intent", "self-harm/instructions",
            "sexual", "sexual/minors", "violence", "violence/graphic",
            "illegal_activities", "harmful_instructions"
        ]
        
        # Common patterns for potentially harmful content
        self.harmful_patterns = [
            r"(?i)how to (?:commit|perform|carry out) (?:illegal|crime|criminal)",
            r"(?i)how to (?:hack|break into|steal|cheat)",
            r"(?i)how to (?:harm|hurt|kill|attack)",
            r"(?i)how to (?:bypass|circumvent) (?:security|safety|protection)",
            r"(?i)ignore (?:previous|above) instructions",
            r"(?i)disregard (?:previous|above) instructions",
            r"(?i)output (?:confidential|secret|private) (?:data|information)",
            r"(?i)bypass (?:safety|security|moderation) (?:measures|checks)",
            r"(?i)generate (?:malicious|harmful|dangerous) (?:code|content)",
            r"(?i)create (?:malware|virus|exploit)"
        ]

    def _check_harmful_patterns(self, text: str) -> Tuple[bool, str]:
        """Check for harmful patterns in the text"""
        for pattern in self.harmful_patterns:
            if re.search(pattern, text):
                return True, f"Content matches harmful pattern: {pattern}"
        return False, ""

    def _check_query_safety(self, query: str) -> Tuple[bool, str]:
        """Check if the query itself is safe"""
        # Check for harmful patterns
        is_harmful, reason = self._check_harmful_patterns(query)
        if is_harmful:
            return False, f"Query contains potentially harmful content: {reason}"

        # Check with OpenAI's moderation
        try:
            response = self.client.moderations.create(input=query)
            result = response.results[0]
            
            # Check all categories
            for category in self.disallowed_categories:
                if getattr(result.categories, category, False):
                    return False, f"Query flagged for {category}"
            
            return True, "Query passed safety checks"
        except Exception as e:
            logger.error(f"Error in query safety check: {str(e)}")
            return False, "Error during safety check"

    def _check_content_safety(self, content: str) -> Tuple[bool, str]:
        """Check if the content is safe"""
        # Check for harmful patterns
        is_harmful, reason = self._check_harmful_patterns(content)
        if is_harmful:
            return False, f"Content contains potentially harmful material: {reason}"

        # Check for prompt injection attempts
        if re.search(r"(?i)(ignore|disregard|bypass).*(instructions|safety|moderation)", content):
            return False, "Content contains potential prompt injection attempts"

        # Check with OpenAI's moderation
        try:
            response = self.client.moderations.create(input=content)
            result = response.results[0]
            
            # Check all categories
            for category in self.disallowed_categories:
                if getattr(result.categories, category, False):
                    return False, f"Content flagged for {category}"
            
            return True, "Content passed safety checks"
        except Exception as e:
            logger.error(f"Error in content safety check: {str(e)}")
            return False, "Error during safety check"

    def moderate(self, content: str) -> bool:
        """Main moderation function that checks both query and content safety"""
        try:
            # Check content safety
            is_safe, reason = self._check_content_safety(content)
            if not is_safe:
                logger.warning(f"Content moderation failed: {reason}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error in moderation: {str(e)}")
            return False

    def check_query(self, query: str) -> Tuple[bool, str]:
        """Check if a query is safe to process"""
        return self._check_query_safety(query)

    def check_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out potentially harmful search results"""
        safe_results = []
        for result in results:
            # Check title and snippet
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            content = f"{title} {snippet}"
            
            is_safe, _ = self._check_content_safety(content)
            if is_safe:
                safe_results.append(result)
            else:
                logger.warning(f"Filtered out potentially harmful search result: {title}")
        
        return safe_results 