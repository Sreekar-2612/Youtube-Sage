# using two models one is using GROQ_API and another one is huggingface model api

from langchain_groq import ChatGroq
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


from src.config import GROQ_API_KEY , HF_TOKEN

def get_groq_llm(model_name : str, temperature: float = 0.5):
    if not GROQ_API_KEY:
        raise ValueError("Groq api key is not set , add it to your .env file")
    return ChatGroq(
        model = model_name,
        api_key = GROQ_API_KEY,
        temperature = temperature,
        streaming = True
    )


def get_hf_llm(model_name: str, temperature: float = 0.5):
    if not HF_TOKEN:
        raise ValueError("Hugging face api key is not set , add it to your .env file")
    return ChatHuggingFace(
        model = model_name,
        huggingfacehub_api_token= HF_TOKEN,
        temperature = temperature,
        max_new_tokens = 512
    )


def get_llm(provider : str, model_name:str, temperature: float = 0.5):
    if provider == "groq":
        return get_groq_llm(model_name,temperature)
    elif provider == "hugggingface":
        return get_hf_llm(model_name,temperature)
    raise ValueError(f"Unknown provider: {provider}")
