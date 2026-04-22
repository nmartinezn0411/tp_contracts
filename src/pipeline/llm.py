import json
from typing import Optional
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from src.config.settings import settings

llm = ChatGoogleGenerativeAI(
    model=settings.GOOGLE_API_MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0,
    verbose=True,
)

# Draft text
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Eres un analista experto en auditoría de facturación y control financiero. Tu tarea es analizar un registro individual (una fila de datos) y detectar discrepancias, explicarlas claramente y proponer acciones correctivas.

            A continuación se te proporcionará una fila con información consolidada de horas trabajadas, facturación y condiciones contractuales.

            ## Significado de las columnas:

            - Employee_ID: Identificador único del empleado.
            - Employee_Name: Nombre del empleado.
            - Project: Proyecto al que está asignado el empleado.
            - Hours_Worked: Cantidad de horas que el empleado reportó haber trabajado (timesheet).
            - Hours_Billed: Cantidad de horas que fueron facturadas al cliente.
            - Rate_per_Hour: Tarifa por hora establecida en el contrato para ese proyecto.
            - Rate_Charged: Tarifa por hora que realmente se cobró al cliente.
            - Expected_Billing: Monto esperado a facturar según contrato (Hours_Worked × Rate_per_Hour).
            - Actual_Billing: Monto realmente facturado (Hours_Billed × Rate_Charged).
            - Rate_Mismatch: Indica si hay diferencia entre la tarifa contractual y la tarifa cobrada (True/False).
            - Hours_Mismatch: Indica si hay diferencia entre horas trabajadas y horas facturadas (True/False).
            - Exceeds_Max_Hours: Indica si las horas trabajadas superan el máximo permitido por contrato (True/False).
            - Overbilling: Indica si el monto facturado supera el monto esperado (True/False).
            - Status: Estado general del registro (OK / ERROR).

            ## Instrucciones:

            1. Analiza cuidadosamente la fila proporcionada.
            2. Identifica todas las discrepancias presentes (si las hay).
            3. Explica cada discrepancia de forma clara y concisa.
            4. Evalúa el impacto potencial de cada error (financiero, contractual, operativo).
            5. Propón acciones correctivas específicas y prácticas.
            6. Si el estado es "OK", confirma que no hay problemas y justifica brevemente.

            ## Formato de salida esperado:

            - Resumen general del caso
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
    response = extractor_chain.invoke({"text": text})

    try:
        response_data = response.content
    except Exception as e:
        return f"There was an error returning the result: {e}"

    return response_data