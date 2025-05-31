from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., example="Compare the latest electric vehicle models and their safety features.")

class Source(BaseModel):
    title: str
    url: str

class ThoughtProcess(BaseModel):
    sub_questions: List[str]
    search_results: Dict[str, List[Dict[str, Any]]]  # question -> list of search results
    analysis_steps: List[str]
    content_summary: Dict[str, str]  # question -> brief summary of findings

class QueryResponse(BaseModel):
    thought_process: ThoughtProcess
    answer: str
    sources: List[Source] 