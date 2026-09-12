import io
import os
import time
from typing import List, Dict, Optional, Tuple, Any
from dotenv import load_dotenv
import pypdf

# Optional import for DOCX files
try:
    import docx
except ImportError:
    docx = None

# Optional import for PPTX files (PowerPoint)
try:
    import pptx
except ImportError:
    pptx = None

# Load environment variables from .env file if available
load_dotenv()

# System Instruction Personas tailored for academic study & research
PERSONAS: Dict[str, str] = {
    "🎓 Academic Tutor": (
        "You are an encouraging and patient Academic Tutor. Your goal is to help students learn.\n"
        "- Explain complex academic concepts in simple, step-by-step terms.\n"
        "- Use analogies, bullet points, and clear examples.\n"
        "- Ask a short follow-up question at the end to check the student's understanding."
    ),
    "🔬 Research Assistant": (
        "You are a rigorous Academic Research Assistant.\n"
        "- Provide well-structured, analytical summaries and literature breakdowns.\n"
        "- Highlight key arguments, methodologies, findings, and research gaps.\n"
        "- Maintain a formal, academic tone suitable for paper writing."
    ),
    "💻 Code & STEM Mentor": (
        "You are a Computer Science and STEM Coding Mentor.\n"
        "- Help students debug code, understand data structures, and learn algorithms.\n"
        "- Provide clean, commented code examples (Python/C++/Java/JS) and explain time/space complexity (Big O notation).\n"
        "- Encourage best practices and modular programming."
    ),
    "🤖 General Assistant": (
        "You are a helpful, versatile AI study assistant.\n"
        "- Provide quick, clear, and accurate answers to any general or academic questions."
    ),
}

def process_file(uploaded_file) -> Dict[str, Any]:
    """
    Processes uploaded file (PDF, PPTX, DOCX, TXT, MD, CSV, PNG, JPG, JPEG, WEBP).
    Returns dict with keys:
    - 'type': 'text' or 'image'
    - 'content': extracted text string if type=='text'
    - 'image_bytes': raw bytes if type=='image'
    - 'mime_type': mime type string
    - 'filename': file name
    """
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()
    
    # Image files (PNG, JPG, JPEG, WEBP)
    if filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
        mime_type = "image/png" if filename.endswith(".png") else "image/jpeg"
        if filename.endswith(".webp"):
            mime_type = "image/webp"
            
        return {
            "type": "image",
            "content": None,
            "image_bytes": file_bytes,
            "mime_type": mime_type,
            "filename": uploaded_file.name
        }

    # Document / Text files (PDF, PPTX, DOCX, TXT, MD, CSV)
    text = ""
    if filename.endswith((".txt", ".md", ".csv")):
        text = file_bytes.decode("utf-8", errors="ignore")
    elif filename.endswith(".pdf"):
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for idx, page in enumerate(pdf_reader.pages, start=1):
                extracted = page.extract_text()
                if extracted:
                    text += f"\n--- Page {idx} ---\n" + extracted + "\n"
        except Exception as e:
            text = f"Error reading PDF pages: {e}"
    elif filename.endswith((".pptx", ".ppt")):
        if pptx is None:
            text = "Notice: python-pptx package is missing. Install with 'pip install python-pptx'."
        else:
            try:
                prs = pptx.Presentation(io.BytesIO(file_bytes))
                slide_texts = []
                for idx, slide in enumerate(prs.slides, start=1):
                    slide_content = []
                    for shape in slide.shapes:
                        if hasattr(shape, "text") and shape.text:
                            slide_content.append(shape.text)
                    if slide_content:
                        slide_texts.append(f"\n--- Slide {idx} ---\n" + "\n".join(slide_content))
                text = "\n".join(slide_texts)
            except Exception as e:
                text = f"Error reading PowerPoint presentation: {e}"
    elif filename.endswith(".docx"):
        if docx is None:
            text = "Notice: python-docx package is missing. Install with 'pip install python-docx'."
        else:
            try:
                doc = docx.Document(io.BytesIO(file_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text]
                text = "\n".join(paragraphs)
            except Exception as e:
                text = f"Error reading Word document: {e}"
    else:
        # Fallback text decoding for any other text-based extension
        text = file_bytes.decode("utf-8", errors="ignore")

    return {
        "type": "text",
        "content": text.strip(),
        "image_bytes": None,
        "mime_type": "text/plain",
        "filename": uploaded_file.name
    }

class GeminiChatEngine:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Gemini client using google-genai or google-generativeai."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.legacy_mode = False
        
        if not self.api_key:
            return
            
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.legacy_mode = False
        except ImportError:
            try:
                import google.generativeai as genai_legacy
                genai_legacy.configure(api_key=self.api_key)
                self.client = genai_legacy
                self.legacy_mode = True
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Gemini SDK: {e}")

    def is_configured(self) -> bool:
        return self.client is not None

    def generate_response(
        self,
        prompt: str,
        chat_history: List[Dict[str, Any]],
        persona_name: str = "🎓 Academic Tutor",
        doc_info: Optional[Dict[str, Any]] = None,
        model_name: str = "gemini-3.6-flash",
        temperature: float = 0.7
    ) -> str:
        """Generate response from Gemini API supporting chat history, personas, and text/image file reference."""
        if not self.is_configured():
            return "⚠️ **API Key Missing**: Please enter a valid Gemini API key in the sidebar or set it in your `.env` file."

        system_instruction = PERSONAS.get(persona_name, PERSONAS["🎓 Academic Tutor"])
        
        # Format text document context if present
        full_system_instruction = system_instruction
        if doc_info and doc_info.get("type") == "text" and doc_info.get("content"):
            # Keep the complete extracted document so later PDF pages remain available for questions.
            doc_text = doc_info["content"]
            full_system_instruction += (
                "\n\n--- UPLOADED STUDY DOCUMENT CONTEXT ---\n"
                f"Filename: {doc_info['filename']}\n"
                f"{doc_text}\n"
                "--- END DOCUMENT CONTEXT ---\n"
                "CRITICAL INSTRUCTION: The user has attached a study document above. "
                "Use the complete document when answering questions, including content from later pages. "
                "If the answer is not present in the document, say so clearly instead of guessing. "
                "Whenever possible, cite page numbers/slides (e.g. [Page X] or [Slide X]) or quote relevant excerpts from the document."
            )

        # Models to try with automatic fallback for 503 / 404 / rate limits
        models_to_try = [model_name]
        for fallback in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_error = None
        for current_model in models_to_try:
            try:
                if not self.legacy_mode:
                    from google.genai import types
                    
                    contents = []
                    for msg in chat_history:
                        role = "user" if msg["role"] == "user" else "model"
                        parts = [types.Part.from_text(text=msg["content"])]
                        contents.append(types.Content(role=role, parts=parts))
                    
                    # Current user message parts
                    prompt_parts = []
                    
                    # Attach image part if an image document is uploaded
                    if doc_info and doc_info.get("type") == "image" and doc_info.get("image_bytes"):
                        img_part = types.Part.from_bytes(
                            data=doc_info["image_bytes"],
                            mime_type=doc_info["mime_type"]
                        )
                        prompt_parts.append(img_part)
                        prompt_text = f"[Attached Image: {doc_info['filename']}]\n{prompt}"
                        prompt_parts.append(types.Part.from_text(text=prompt_text))
                    else:
                        prompt_parts.append(types.Part.from_text(text=prompt))

                    contents.append(types.Content(
                        role="user",
                        parts=prompt_parts
                    ))

                    config = types.GenerateContentConfig(
                        system_instruction=full_system_instruction,
                        temperature=temperature,
                    )

                    response = self.client.models.generate_content(
                        model=current_model,
                        contents=contents,
                        config=config,
                    )
                    return response.text
                else:
                    # Legacy SDK fallback
                    model = self.client.GenerativeModel(
                        model_name=current_model,
                        system_instruction=full_system_instruction
                    )
                    
                    history = []
                    for msg in chat_history:
                        role = "user" if msg["role"] == "user" else "model"
                        history.append({"role": role, "parts": [msg["content"]]})

                    chat = model.start_chat(history=history)
                    
                    if doc_info and doc_info.get("type") == "image" and doc_info.get("image_bytes"):
                        import PIL.Image
                        img = PIL.Image.open(io.BytesIO(doc_info["image_bytes"]))
                        response = chat.send_message([prompt, img], generation_config={"temperature": temperature})
                    else:
                        response = chat.send_message(prompt, generation_config={"temperature": temperature})
                        
                    return response.text

            except Exception as e:
                err_str = str(e)
                last_error = err_str
                if any(k in err_str.lower() for k in ["503", "unavailable", "high demand", "404", "not_found", "quota", "429"]):
                    time.sleep(1.5)
                    continue
                else:
                    return f"❌ **Error generating response**: {err_str}"

        return f"⚠️ **Server Busy (503)**: Google Gemini servers are currently experiencing peak traffic.\n\n*Suggestion*: Please wait 5-10 seconds and resubmit your question. (Details: {last_error})"
