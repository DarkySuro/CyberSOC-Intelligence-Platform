import os
import pandas as pd
from google import genai
from dotenv import load_dotenv
 
load_dotenv()
 
_client = None
 
def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in .env")
        _client = genai.Client(api_key=api_key)
    return _client
 
 
def summarize_incident(incident_row: dict) -> str:
    client = get_client()
    prompt = (
        "You are a security analyst assistant. Summarize this incident in 2-3 plain-English "
        "sentences for a non-technical stakeholder. Be factual, don't invent details.\n\n"
        f"Incident data: {incident_row}"
    )
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text
 
 
def ask_about_data(question: str, context_df: pd.DataFrame) -> str:
    client = get_client()
    context_text = context_df.to_csv(index=False)
    prompt = (
        "You are a SOC data assistant. Answer the question using ONLY the CSV data below. "
        "If the answer isn't in the data, say so explicitly instead of guessing.\n\n"
        f"CSV data:\n{context_text}\n\nQuestion: {question}"
    )
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text