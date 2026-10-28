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
- A Qdrant instance and a Supabase project

### Setup

1. Clone the repository:

```bash
git clone https://github.com/AlmatUzakbayev/Enterprise-Platform.git
cd Enterprise-Platform
```

2. Install dependencies:

```bash
pip install -r requirements.txt
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

- **Endpoint**: `/api/v1/documents/upload`
- **Method**: `POST`
- **Request**: Multipart form with `file` (PDF, DOCX or TXT) and `telegram_user_id`
- **Response**: Document id, language, summary and chunk count

Other document endpoints: `GET /api/v1/documents/` (list), `DELETE /api/v1/documents/{document_id}`.

### Question Answering

- **Endpoint**: `/api/v1/chat/`
- **Method**: `POST`
- **Request Body**:

```json
{
  "question": "Your question here",
  "document_id": 1,
  "telegram_user_id": 123456
}
```

- **Response**: `answer`, `sources`, `tokens_used`, `retrieval_score`

Chat history: `GET /api/v1/chat/history?telegram_user_id=...&document_id=...`.

## Development Notes

- To reset Qdrant collections: `python -m backend.app.reset_qdrant`
- For memory issues with embeddings, change model in `constants.py`
- Test endpoints using curl commands from project documentation

## Security

- Never commit API keys to version control
- Use secret managers for production deployments
- Regularly rotate API keys and tokens