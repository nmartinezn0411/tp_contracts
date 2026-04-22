import json
from typing import Optional
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from src.helpers.utils import clean_whitespace
from src.config.settings import settings

llm = ChatGoogleGenerativeAI(
    model=settings.GOOGLE_API_MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0,
)

# Draft text
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Eres un analista experto en auditoría de facturación y control financiero. 
            Tu tarea es analizar un registro individual y detectar discrepancias, explicarlas claramente y proponer acciones correctivas.

            ## Instrucciones:

            1. Explica cada discrepancia de forma clara y concisa.
            2. Evalúa el impacto potencial de cada error (financiero, contractual, operativo).
            3. Propón acciones correctivas específicas y prácticas.
            4. Si el estado es "OK", confirma que no hay problemas y justifica brevemente.
            5. Sé lo más resumido posible

            ## Formato de salida esperado:

            - Discrepancias detectadas (si aplica)
            - Impacto de los errores
            - Recomendaciones / acciones correctivas
            - Todo en formato Markdown

            ## Fila a analizar:
            """,
        ),
        ("human", "texto: {text}"),
    ]
)

extractor_chain: Runnable = prompt | llm

def generate_analysis(text: str = None) -> str:
    text = clean_whitespace(text) # Add clean whitespace to use less tokens
    response = extractor_chain.invoke({"text": text})

    try:
        response_data = response.content
    except Exception as e:
        return f"There was an error returning the result: {e}"

    return response_data

# Safe generation
import time
from google.genai.errors import ServerError

def safe_generate(text, retries=5):
    delay = 60

    for attempt in range(retries):
        try:
            return generate_analysis(text)
        except ServerError as e:
            print(f"Retry {attempt+1} - waiting {delay}s...")
            time.sleep(delay)

    return "ERROR: Failed after retries"