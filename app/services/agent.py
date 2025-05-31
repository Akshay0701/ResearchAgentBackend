from app.services.web_search import WebSearch
from app.services.content_parser import ContentParser
from app.services.summarizer import Summarizer
from app.services.safety import Safety
from app.models.schemas import Source, QueryResponse, ThoughtProcess
from app.utils.logger import logger
from typing import List, Dict, Any, Optional
import re
import tiktoken
import time
from openai import RateLimitError

class ResearchAgent:
    def __init__(self):
        self.searcher = WebSearch()
        self.parser = ContentParser()
        self.summarizer = Summarizer()
        self.safety = Safety()
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        self.max_tokens = 7000  # Leave room for system message and prompt
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.max_search_results = 5  # Maximum number of search results per query
        self.max_total_sources = 6  # Maximum total number of sources to process

    def _count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string"""
        return len(self.encoding.encode(text))

    def _truncate_content(self, content: str, max_tokens: int) -> str:
        """Truncate content to fit within token limit"""
        tokens = self.encoding.encode(content)
        if len(tokens) <= max_tokens:
            return content
        return self.encoding.decode(tokens[:max_tokens])

    def _generate_sub_questions(self, query: str) -> List[str]:
        """Generate sub-questions to break down the main query"""
        prompt = f"""Break down the following research question into 2-3 specific sub-questions that will help gather comprehensive information. 
        Focus on different aspects of the topic. Return only the questions, one per line.
        
        Main question: {query}
        
        Sub-questions:"""
        
        try:
            for attempt in range(self.max_retries):
                try:
                    response = self.summarizer.client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a research assistant that breaks down complex questions into specific, focused sub-questions."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=200
                    )
                    questions = response.choices[0].message.content.strip().split('\n')
                    return [q.strip('- ').strip() for q in questions if q.strip()][:3]  # Limit to 3 sub-questions
                except RateLimitError:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    raise
                except Exception as e:
                    logger.error(f"Error generating sub-questions: {str(e)}")
                    return [query]  # Fallback to original query
        except Exception as e:
            logger.error(f"Failed to generate sub-questions after {self.max_retries} attempts: {str(e)}")
            return [query]  # Fallback to original query

    def _sanitize_input(self, text: str) -> str:
        """Sanitize input text to prevent prompt injection and remove malicious content"""
        # Remove HTML tags and scripts
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<.*?>', '', text)
        
        # Remove common prompt injection patterns
        injection_patterns = [
            r'ignore previous instructions',
            r'disregard the above',
            r'output confidential data',
            r'bypass safety measures'
        ]
        for pattern in injection_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()

    def _format_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources for inclusion in the summary"""
        formatted = []
        for i, source in enumerate(sources, 1):
            formatted.append(f"[{i}] {source['title']} ({source['url']})")
        return "\n".join(formatted)

    def _prepare_summary_content(self, all_results: List[Dict[str, Any]], all_sources: List[Dict[str, Any]]) -> tuple[str, str]:
        """Prepare content for summary while respecting token limits"""
        # Calculate available tokens for content
        system_prompt = "You are a helpful research assistant that provides accurate, comprehensive summaries based on the given information."
        base_prompt = "Based on the following research findings, provide a detailed and thorough answer that:"
        prompt_requirements = """
        1. Directly addresses the original question with a comprehensive analysis
        2. Synthesizes information from multiple sources, highlighting key insights
        3. Includes specific citations (e.g., "According to [1]...") for all major points
        4. Provides detailed comparisons and contrasts where relevant
        5. Maintains a professional and objective tone while being thorough
        6. Organizes information in clear sections with proper headings
        7. Concludes with a summary of key findings and implications"""

        # Reserve tokens for system message, base prompt, and requirements
        reserved_tokens = self._count_tokens(system_prompt + base_prompt + prompt_requirements)
        available_tokens = self.max_tokens - reserved_tokens

        # Format sources (this is usually small)
        sources_text = self._format_sources(all_sources)
        available_tokens -= self._count_tokens(sources_text)

        # Prepare content with token limit
        content_parts = []
        current_tokens = 0
        
        for result in all_results:
            content = f"From {result['question']}:\n{result['content']}"
            content_tokens = self._count_tokens(content)
            
            if current_tokens + content_tokens > available_tokens:
                # If adding this content would exceed the limit, truncate it
                remaining_tokens = available_tokens - current_tokens
                if remaining_tokens > 100:  # Only add if we have meaningful space
                    truncated_content = self._truncate_content(content, remaining_tokens)
                    content_parts.append(truncated_content)
                break
            else:
                content_parts.append(content)
                current_tokens += content_tokens

        return sources_text, "\n---\n".join(content_parts)

    def _generate_summary(self, clean_query: str, sources_text: str, content_text: str) -> Optional[str]:
        """Generate summary with retry logic"""
        summary_prompt = f"""Based on the following research findings, provide a comprehensive and detailed answer to the original question: "{clean_query}"

        Research findings:
        {sources_text}
        
        Content from sources:
        {content_text}
        
        Please provide a well-structured, detailed answer that:
        1. Directly addresses the original question with a comprehensive analysis
        2. Synthesizes information from multiple sources, highlighting key insights
        3. Includes specific citations (e.g., "According to [1]...") for all major points
        4. Provides detailed comparisons and contrasts where relevant
        5. Maintains a professional and objective tone while being thorough
        6. Organizes information in clear sections with proper headings
        7. Concludes with a summary of key findings and implications

        Structure your response with clear sections and subsections, using markdown formatting for better readability."""

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to generate summary (attempt {attempt + 1}/{self.max_retries})")
                response = self.summarizer.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful research assistant that provides detailed, comprehensive summaries based on the given information. Focus on thoroughness and clarity in your responses."
                        },
                        {
                            "role": "user",
                            "content": summary_prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2500  # Increased token limit for longer responses
                )
                return response.choices[0].message.content
            except RateLimitError:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    logger.info(f"Rate limit hit, waiting {wait_time} seconds before retry")
                    time.sleep(wait_time)
                    continue
                raise
            except Exception as e:
                logger.error(f"Error during summarization: {str(e)}")
                raise

        return None

    def _analyze_findings(self, question: str, content: str) -> str:
        """Analyze findings for a specific question and generate a brief summary"""
        try:
            prompt = f"""Analyze the following content in relation to the question: "{question}"
            
            Content:
            {content[:2000]}  # Limit content length for analysis
            
            Provide a brief analysis (2-3 sentences) of how this content relates to the question.
            Focus on key insights and relevance."""
            
            response = self.summarizer.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a research analyst that provides concise, insightful analysis of content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error analyzing findings: {str(e)}")
            return "Unable to analyze content at this time."

    def _generate_analysis_steps(self, query: str, sub_questions: List[str], findings: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Generate analysis steps based on the research process"""
        steps = [
            f"1. Initial Query Analysis: Breaking down '{query}' into focused sub-questions",
            f"2. Generated {len(sub_questions)} sub-questions to explore different aspects of the topic"
        ]
        
        for i, question in enumerate(sub_questions, 1):
            results = findings.get(question, [])
            steps.append(f"3.{i} Researching sub-question {i}: '{question}'")
            steps.append(f"   - Found {len(results)} relevant sources")
            if results:
                steps.append(f"   - Key sources include: {', '.join(r['title'][:30] + '...' for r in results[:2])}")
        
        steps.extend([
            "4. Content Analysis:",
            "   - Extracting and analyzing information from each source",
            "   - Identifying key insights and patterns",
            "   - Cross-referencing information across sources",
            "5. Synthesis:",
            "   - Combining findings from all sub-questions",
            "   - Identifying common themes and unique perspectives",
            "   - Preparing comprehensive response"
        ])
        
        return steps

    async def handle(self, query: str) -> QueryResponse:
        try:
            # Initialize thought process tracking
            thought_process = {
                "sub_questions": [],
                "search_results": {},
                "analysis_steps": [],
                "content_summary": {}
            }
            
            # 1. Input sanitization and safety check
            clean_query = self._sanitize_input(query.strip())
            if not clean_query:
                raise ValueError("Query cannot be empty after sanitization")

            # Check query safety
            is_safe, reason = self.safety.check_query(clean_query)
            if not is_safe:
                raise ValueError(f"Query rejected for safety reasons: {reason}")

            # 2. Generate sub-questions
            logger.info("Generating sub-questions for comprehensive research")
            sub_questions = self._generate_sub_questions(clean_query)
            
            # Safety check sub-questions
            for question in sub_questions:
                is_safe, reason = self.safety.check_query(question)
                if not is_safe:
                    logger.warning(f"Sub-question rejected for safety reasons: {reason}")
                    sub_questions.remove(question)
            
            if not sub_questions:
                raise ValueError("No safe sub-questions could be generated")
                
            thought_process["sub_questions"] = sub_questions
            logger.info(f"Generated sub-questions: {sub_questions}")

            # 3. Research each sub-question
            all_results = []
            all_sources = []
            findings = {}
            
            for sub_q in sub_questions:
                if len(all_sources) >= self.max_total_sources:
                    logger.info(f"Reached maximum number of sources ({self.max_total_sources})")
                    break

                logger.info(f"Researching sub-question: {sub_q}")
                
                # Web search for this sub-question
                results = self.searcher.search(sub_q, num_results=min(3, self.max_search_results))
                
                # Filter out potentially harmful search results
                safe_results = self.safety.check_search_results(results)
                thought_process["search_results"][sub_q] = safe_results
                
                if not safe_results:
                    logger.warning(f"No safe results found for sub-question: {sub_q}")
                    continue

                # Extract content from sources
                sub_question_content = []
                for item in safe_results:
                    if len(all_sources) >= self.max_total_sources:
                        break

                    if any(s['url'] == item['link'] for s in all_sources):
                        continue
                        
                    if item['link'].lower().endswith(('.pdf', '.doc', '.docx')):
                        logger.info(f"Skipping non-HTML content: {item['link']}")
                        continue
                        
                    text = self.parser.fetch_and_parse(item['link'])
                    if text:
                        # Safety check the parsed content
                        is_safe, reason = self.safety._check_content_safety(text)
                        if not is_safe:
                            logger.warning(f"Content rejected for safety reasons: {reason}")
                            continue
                            
                        content = text[:3000]
                        sub_question_content.append(content)
                        all_results.append({
                            'question': sub_q,
                            'content': content,
                            'source': item
                        })
                        all_sources.append({
                            'title': item['title'],
                            'url': item['link']
                        })
                
                # Analyze findings for this sub-question
                if sub_question_content:
                    combined_content = "\n".join(sub_question_content)
                    # Safety check the analysis
                    is_safe, reason = self.safety._check_content_safety(combined_content)
                    if not is_safe:
                        logger.warning(f"Analysis rejected for safety reasons: {reason}")
                        thought_process["content_summary"][sub_q] = "Content analysis skipped due to safety concerns"
                    else:
                        analysis = self._analyze_findings(sub_q, combined_content)
                        thought_process["content_summary"][sub_q] = analysis

            if not all_results:
                return QueryResponse(
                    thought_process=ThoughtProcess(**thought_process),
                    answer="No safe and relevant information found for your query.",
                    sources=[]
                )

            # 4. Generate analysis steps
            thought_process["analysis_steps"] = self._generate_analysis_steps(
                clean_query, 
                sub_questions, 
                thought_process["search_results"]
            )

            # 5. Generate comprehensive summary
            logger.info("Generating comprehensive summary")
            sources_text, content_text = self._prepare_summary_content(all_results, all_sources)
            
            answer = self._generate_summary(clean_query, sources_text, content_text)
            if not answer:
                raise ValueError("Failed to generate summary after multiple attempts")

            # 6. Final safety check
            is_safe, reason = self.safety._check_content_safety(answer)
            if not is_safe:
                raise ValueError(f"Generated content rejected for safety reasons: {reason}")

            # 7. Return response with thought process
            return QueryResponse(
                thought_process=ThoughtProcess(**thought_process),
                answer=answer,
                sources=[Source(title=s['title'], url=s['url']) for s in all_sources]
            )

        except ValueError as e:
            logger.warning(f"Validation or safety error: {str(e)}")
            raise
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded after {self.max_retries} retries: {str(e)}")
            raise ValueError("The service is currently experiencing high demand. Please try again in a few moments.")
        except Exception as e:
            logger.error(f"Error in research agent: {str(e)}")
            raise ValueError("An unexpected error occurred while processing your request. Please try again later.") 