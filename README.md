# EnterprisePlatform

Backend service and Telegram bot for enterprise data processing and analysis.

You can find the bot at @enterprise_platform_test_bot.

## Overview

This project provides a comprehensive platform for enterprise data analysis combining modern AI technologies with a convenient Telegram interface. Users can interact with the system through the Telegram bot to process documents, analyze content, and receive structured responses powered by LLMs.

Key features include:
- Document processing and embedding storage
- AI-powered question answering over uploaded documents
- Telegram bot interface for easy access
- Integration with Supabase and Qdrant for data persistence

## Architecture

The project consists of two main components:

- **Backend API** - FastAPI service handling document processing and AI interactions
- **Telegram Bot** - User interface for interacting with the backend

## Installation

### Prerequisites

- Python 3.12+
- Docker and docker-compose (for containerized deployment)

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd EnterprisePlatform
```

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Configure environment variables by creating a `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
TELEGRAM_BOT_TOKEN=your_telegram_token
BACKEND_URL=http://127.0.0.1:8080
```

## Usage

### Running with Docker

```bash
docker-compose up --build
```

### Running Locally

1. Start the backend API:

```bash
cd backend/app
uvicorn app:app --reload --port 8080
```

2. In a separate terminal, start the Telegram bot:

```bash
python -m bot.tg_app
```

3. Upload documents and interact with the bot through Telegram

## API Reference

### Document Upload

- **Endpoint**: `/api/v1/upload`
- **Method**: `POST`
- **Request**: Multipart form with `file` field
- **Response**: Processing status and document ID

### Question Answering

- **Endpoint**: `/api/v1/ask`
- **Method**: `POST`
- **Request Body**:

```json
{
  "document_id": "document_uuid",
  "question": "Your question here"
}
```

- **Response**: AI-generated answer based on document content

## Development Notes

- To reset Qdrant collections: `python -m backend.app.reset_qdrant`
- For memory issues with embeddings, change model in `constants.py`
- Test endpoints using curl commands from project documentation

## Security

- Never commit API keys to version control
- Use secret managers for production deployments
- Regularly rotate API keys and tokens