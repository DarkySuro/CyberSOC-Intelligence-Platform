import os
import pandas as pd
from google import genai
from groq import Groq
from dotenv import load_dotenv
 
load_dotenv()
 
_client = None
 
def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in .env")
        _client = Groq(api_key=api_key)
    return _client
 
 
def summarize_incident(incident_row: dict) -> str:
    client = get_client()
    prompt = [
        {"role":"system", "content":"You are a security analyst assistant."},
        {"role":"user" ,
         "content":f"""
            Summarize this incident in 2-3 plain-English sentences for a non-technical stakeholder. 
            Be factual, don't invent details.
            Replace the heading 'Plain‑English summary (2‑3 sentences):' with Summary only in the output.\n\n"
            Incident data: {incident_row}
            """
        }
    ]
    response = client.chat.completions.create(model="groq/compound", messages=prompt)
    return response.choices[0].message.content
 
 
def ask_about_data(question: str, context_df: pd.DataFrame) -> str:
    client = get_client()
    context_text = context_df.to_csv(index=False)
    prompt = [
        {"role":"system", "content":"You are a SOC data assistant."},
        {"role":"user",
         "content":f"""
         Answer the question using ONLY the CSV data below.
         If the answer isn't in the data, say so explicitly instead of guessing.
         Replace the heading 'Plain‑English summary (2‑3 sentences):' with Summary only in the output.\n\n"
         CSV data:\n{context_text}\n\nQuestion: {question}"""
        }
    ]
    response = client.chat.completions.create(model="groq/compound", messages=prompt)
    return response.choices[0].message.content
