import nltk
from core.constants import CHUNK_SIZE, CHUNK_OVERLAP

def chunk_text(text: str, page_map: list) -> list[dict]:
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    char_pos = 0

    for sentence in sentences:
        if len(current_chunk) + len(sentence) > CHUNK_SIZE and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_index": len(chunks),
                "char_start": char_pos,
                "page_num": _get_page(char_pos, page_map),
            })
            current_chunk = current_chunk[-CHUNK_OVERLAP:] + " " + sentence
        else:
            current_chunk += " " + sentence

        char_pos += len(sentence) + 1

    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "chunk_index": len(chunks),
            "char_start": char_pos,
            "page_num": _get_page(char_pos, page_map),
        })

    return chunks


def _get_page(char_pos: int, page_map: list) -> int:
    for start, end, page_num in page_map:
        if start <= char_pos < end:
            return page_num
    return 1