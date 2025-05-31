# AI Research Assistant Backend

A FastAPI-based backend service that provides an AI-powered research assistant capable of searching the web, extracting content, and generating summaries using OpenAI's GPT models.

## Features

- Web search using Google Custom Search API
- Content extraction from web pages using newspaper3k
- AI-powered summarization using OpenAI GPT-4
- Content moderation and safety checks
- RESTful API with FastAPI
- Comprehensive logging
- Error handling and validation

## Prerequisites

- Python 3.8+
- Google Custom Search API credentials
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-research-assistant-backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
OPENAI_API_KEY=your_openai_api_key
```

## Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

### Endpoints

- `GET /health` - Health check endpoint
- `POST /api/ask` - Submit a research query
  - Request body:
    ```json
    {
        "query": "Your research question here"
    }
    ```
  - Response:
    ```json
    {
        "answer": "Generated summary and answer",
        "sources": [
            {
                "title": "Source title",
                "url": "Source URL"
            }
        ]
    }
    ```

## Error Handling

The API includes comprehensive error handling:
- 400 Bad Request: Invalid input or validation errors
- 500 Internal Server Error: Server-side processing errors

All errors are logged with appropriate context.

## Development

The project follows a modular structure:
- `app/main.py`: FastAPI application entry point
- `app/routers/`: API route definitions
- `app/services/`: Core business logic
- `app/models/`: Pydantic models and schemas
- `app/utils/`: Utility functions and logging

## License

MIT License 