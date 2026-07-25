import os
import pandas as pd
import groq
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

# Groq rejects oversized requests with a 413 before it even looks at tokens/
# context window, so we cap what we send well below any reasonable limit -
# both by row count and by raw character count of the resulting CSV.
MAX_CONTEXT_ROWS = 300
MAX_CONTEXT_CHARS = 60_000


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set in .env")
        _client = Groq(api_key=api_key)
    return _client


def _bounded_csv(df: pd.DataFrame) -> tuple[str, bool]:
    """
    Convert a DataFrame to CSV text, capped in both row count and character
    length, so the resulting prompt can't grow unbounded as the underlying
    table grows. Returns (csv_text, was_truncated).
    """
    truncated = False
    original_rows = len(df)

    if original_rows > MAX_CONTEXT_ROWS:
        if "DetectedAt" in df.columns:
            df = df.sort_values("DetectedAt", ascending=False)
        df = df.head(MAX_CONTEXT_ROWS)
        truncated = True

    csv_text = df.to_csv(index=False)

    if len(csv_text) > MAX_CONTEXT_CHARS:
        csv_text = csv_text[:MAX_CONTEXT_CHARS]
        truncated = True

    return csv_text, truncated


def _call_groq(prompt: str) -> str:
    client = get_client()
    try:
        response = client.chat.completions.create(
            model="groq/compound",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=4000,  # compound's built-in tools consume extra tokens
        )
    except groq.APIStatusError as e:
        if e.status_code == 413:
            raise RuntimeError(
                "The request to Groq was too large (HTTP 413). Try asking about "
                "a narrower slice of the data, or reduce MAX_CONTEXT_ROWS/"
                "MAX_CONTEXT_CHARS in ai_helper.py."
            ) from e
        raise
    return response.choices[0].message.content


def summarize_incident(incident_row: dict) -> str:
    prompt = (
        "You are a security analyst assistant. Summarize this incident in 2-3 plain-English "
        "sentences for a non-technical stakeholder. Be factual, don't invent details. "
        "Do not search the web or use any tools - base your answer only on the data given.\n\n"
        f"Incident data: {incident_row}"
    )
    return _call_groq(prompt)


def ask_about_data(question: str, context_df: pd.DataFrame) -> str:
    context_text, truncated = _bounded_csv(context_df)
    truncation_note = (
        f"\n\n(Note: the full dataset has {len(context_df)} rows; only a subset "
        "is shown above due to request size limits. Mention this if it's "
        "relevant to your answer.)"
        if truncated
        else ""
    )
    prompt = (
        "You are a SOC data assistant. Answer the question using ONLY the CSV data below. "
        "Do not search the web or use any external tools. "
        "If the answer isn't in the data, say so explicitly instead of guessing.\n\n"
        f"CSV data:\n{context_text}{truncation_note}\n\nQuestion: {question}"
    )
    return _call_groq(prompt)
