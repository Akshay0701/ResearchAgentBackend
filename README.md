# Research Agent 🤖

A powerful AI-powered research assistant that helps users gather, analyze, and summarize information from various sources. This agent combines web search capabilities with advanced natural language processing to provide accurate, well-sourced answers to research queries.

## Overview

This project implements a research assistant that can:
- Process user queries and break them down into searchable components
- Search the web for relevant information using Google Search API
- Extract and clean content from web pages
- Analyze and summarize information using OpenAI's GPT-4
- Present well-structured, source-attributed responses

The agent is designed to be a helpful tool for researchers, students, and anyone needing to gather and synthesize information quickly and accurately.

## Technical Approach

### Core Components

1. **Query Processing & Search Pipeline**
   - Uses Google Custom Search API for web search
   - Implements content extraction using `newspaper3k` and `trafilatura`
   - Processes and cleans web content to remove irrelevant information

2. **Summarization Engine**
   - Leverages OpenAI's GPT-4 for intelligent summarization
   - Implements context-aware summarization with source attribution
   - Uses temperature control (0.7) for balanced creativity and accuracy

3. **Backend Architecture**
   - Built with FastAPI for high-performance async operations
   - Modular design with separate services for search, summarization, and content processing
   - Implements proper error handling and logging

### Key Technologies
- **Backend Framework**: FastAPI
- **Search**: Google Custom Search API
- **Content Processing**: newspaper3k, trafilatura
- **AI/ML**: OpenAI GPT-4
- **Environment Management**: python-dotenv
- **HTTP Client**: httpx, requests

## Security Measures

1. **API Key Protection**
   - Environment variables for sensitive credentials
   - No hardcoded API keys in the codebase
   - Secure handling of OpenAI and Google API keys

2. **Content Safety**
   - Input validation using Pydantic models
   - Content sanitization during web scraping
   - Rate limiting on API endpoints

3. **Potential Improvements**
   - Implement user authentication
   - Add request rate limiting
   - Implement content filtering for sensitive topics
   - Add input validation for malicious prompts

## Setup & Running Instructions

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Google Custom Search API key and Search Engine ID

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akshay0701/ResearchAgent.git
   cd ResearchAgent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
   ```

### Running the Application

1. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. The API will be available at `http://localhost:8000`

## Usage Guide

1. **Making Queries**
   - Send POST requests to `/api/research` endpoint
   - Include your query in the request body
   - Example query format:
     ```json
     {
       "query": "What are the latest developments in quantum computing?"
     }
     ```

2. **Response Format**
   - The agent returns a JSON response with:
     - Summary of findings
     - Source URLs
     - Confidence scores
     - Relevant quotes

## Example Scenarios

### Example 1: Research Query
**Input:**
```json
{
  "query": "What are the environmental impacts of electric vehicles?"
}
```

**Output:**
```json
{
  "summary": "Electric vehicles (EVs) have several environmental impacts...",
  "sources": [
    "https://example.com/ev-impact-2023",
    "https://example.com/green-transport"
  ],
  "key_points": [
    "Reduced direct emissions",
    "Battery production impact",
    "Grid dependency"
  ]
}
```

### Example 2: Technical Research
**Input:**
```json
{
  "query": "Compare React vs Vue.js for large-scale applications"
}
```

**Output:**
```json
{
  "summary": "Both React and Vue.js are powerful frameworks...",
  "sources": [
    "https://example.com/framework-comparison",
    "https://example.com/react-vs-vue"
  ],
  "key_points": [
    "Performance metrics",
    "Learning curve",
    "Ecosystem size"
  ]
}
```

## Time Spent & Reflections

The project was developed over 48 hours with the following time allocation:
- 30%: Core architecture and API integration
- 25%: Search and content processing implementation
- 25%: Summarization engine and response formatting
- 20%: Testing, documentation, and refinement

### Challenges & Learnings
- Balancing response quality with API rate limits
- Optimizing content extraction for various website formats
- Implementing effective error handling for API failures

### Future Improvements
- Add support for more search engines
- Implement caching for frequent queries
- Add support for file uploads and PDF processing
- Develop a web interface for easier interaction

## License

MIT License - feel free to use this project for your own purposes.
