# app/services/documents.py
from fastapi import UploadFile
import io
from PyPDF2 import PdfReader
import docx
from app.services.ai_service import ask_ai

async def summarize_document(file: UploadFile) -> str:
    """
    Extracts text from uploaded PDF/TXT/DOCX file and summarizes using Gemini AI.
    """
    try:
        contents = await file.read()
        text = ""

        # ---- PDF ----
        if file.content_type == "application/pdf":
            reader = PdfReader(io.BytesIO(contents))
            for page in reader.pages:
                text += page.extract_text() or ""

        # ---- Plain Text ----
        elif file.content_type == "text/plain":
            text = contents.decode("utf-8", errors="ignore")

        # ---- Word Document ----
        elif file.content_type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]:
            doc = docx.Document(io.BytesIO(contents))
            text = "\n".join([p.text for p in doc.paragraphs])

        else:
            return "Unsupported file type."

        if not text.strip():
            return "No text could be extracted from the file."

        # ---- Summarization ----
        prompt = f"Summarize this maritime document concisely:\n{text}"
        summary = await ask_ai(prompt, max_tokens=256)  # ✅ Await async function
        return summary

    except Exception as e:
        return f"Error in summarize_document: {e}"
