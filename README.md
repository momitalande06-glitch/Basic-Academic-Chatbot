# 🎓 Interactive Academic AI Chatbot

An interactive, multi-modal conversational AI chatbot designed for academic learning, tutoring, research assistance, document analysis, and image Q&A. Built with **Python**, **Streamlit**, and powered by **Google Gemini AI**.

---

## 📌 Project Overview

This project demonstrates an interactive Educational Conversational AI. Students and researchers can ask general academic questions, upload study documents (PDFs, Word DOCX, TXT, Markdown, CSV) or images (textbook diagrams, handwritten notes, math equations), and utilize quick action buttons (Summarize, Key Takeaways, Quiz Generator).

---

## ✨ Key Features

- **💬 Interactive Chat & Preset Quick Actions**:
  - **📄 Summarize Content**: One-click comprehensive document summary.
  - **💡 Key Takeaways**: Extract core concepts & bullet points.
  - **📝 5 Quiz Questions**: Auto-generate multiple-choice practice questions.
  - **🔍 Term Explanations**: Breakdown of technical terms and formulas.
- **🖼️ Multimodal Uploads (Images + Documents)**:
  - **Images**: PNG, JPG, JPEG, WEBP (analyzes diagrams, math equations, charts, handwritten notes).
  - **Documents**: PDF, Word (.docx), TXT, Markdown (.md), CSV.
- **🎓 Multi-Persona Assistance**:
  - **Academic Tutor**: Explains complex concepts step-by-step with comprehension checks.
  - **Research Assistant**: Formats analytical summaries and literature breakdowns.
  - **Code & STEM Mentor**: Helps debug code, explains algorithms, and calculates Big O complexity ($O(N)$).
  - **General Assistant**: Handles general academic queries.
- **🛡️ Fault-Tolerant Engine**: Built-in 503 high demand retry & multi-model fallback cascade.

---

## 🛠️ Setup & Running Instructions

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Run the Interactive Web UI
```bash
python -m streamlit run app.py
```
Access the application in your browser at `http://localhost:8501`.
