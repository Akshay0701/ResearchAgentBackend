import os
from openai import OpenAI
from app.utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

class Summarizer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        self.client = OpenAI(api_key=self.api_key)

    def summarize(self, texts: list[str], query: str) -> str:
        if not texts:
            return "No relevant content found to summarize."

        prompt = (
            f"Combine the following information to answer: {query}\n\n"
            + "\n---\n".join(texts)
        )

        logger.info("Calling OpenAI for summarization")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant that provides accurate, concise summaries based on the given information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error during summarization: {str(e)}")
            raise
