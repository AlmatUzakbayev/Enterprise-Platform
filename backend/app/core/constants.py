#--Parameters for document processing and retrieval
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
TOP_K_RETRIEVAL = 10
TOP_K_RERANK = 3

EMBEDDINGS_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
QDRANT_COLLECTION = "documents"

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

MAX_HISTORY_MESSAGES = 6
import os

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

OPENAI_MODEL = "gpt-3.5-turbo"

#--Prompts
SYSTEM_PROMPT = """You are an intelligent document assistant. 
Answer questions based ONLY on the provided context.

Rules:
- Answer in the same language as the question
- If the answer is not in the context, say so explicitly  
- Always cite the source (page number) for your claims
- Be concise but complete
- Do not make up information"""

SUMMARIZE_PROMPT = """Create a concise summary (3-5 sentences) of the following document.
Respond in the same language as the document.
Focus on: main topic, key points, document type.

Document:
{text}"""