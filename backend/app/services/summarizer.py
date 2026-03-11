from langchain_core.messages import HumanMessage
from core.constants import SUMMARIZE_PROMPT
from services.llm import get_llm

async def summarize_document(text: str, language: str) -> str:
    llm = get_llm(temperature=0.1)
    prompt = SUMMARIZE_PROMPT.format(text=text[:3000])
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content