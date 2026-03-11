from core.config import LLM_PROVIDER, OPENAI_API_KEY, GEMINI_API_KEY


def get_llm(temperature: float = 0.1):
    if LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=temperature,
            google_api_key=GEMINI_API_KEY,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature,
            api_key=OPENAI_API_KEY,
        )

