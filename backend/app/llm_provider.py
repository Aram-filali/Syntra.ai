import os
from langchain_openai import ChatOpenAI

def get_openrouter_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_base="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
