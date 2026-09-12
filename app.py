import os
import streamlit as st
from dotenv import load_dotenv
from ai_engine import GeminiChatEngine, PERSONAS, process_file

# Auto-load environment variables from .env file
load_dotenv()

# Configure Page
st.set_page_config(
    page_title="Interactive Academic AI Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 0.5rem 1rem;
        margin-bottom: 0.8rem;
    }
    .doc-badge {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 0.88rem;
        font-weight: 600;
        display: inline-block;
    }
    .quick-btn-container {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I am your Interactive Academic AI Assistant 🎓.\n\nAsk me any question, or upload study notes, slides, papers, or images (PDF, PPTX, DOCX, TXT, PNG, JPG) to get started!"}
    ]

if "doc_info" not in st.session_state:
    st.session_state["doc_info"] = None

if "doc_filename" not in st.session_state:
    st.session_state["doc_filename"] = None

if "preset_prompt" not in st.session_state:
    st.session_state["preset_prompt"] = None

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🎓 Chatbot Settings")
    st.markdown("---")

    # API Key Input
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.text_input(
        "Google Gemini API Key",
        value=env_api_key,
        type="password",
        help="Get a free key from https://aistudio.google.com/"
    )

    if not user_api_key:
        st.warning("🔑 Please enter a Gemini API Key to activate the bot.")
    else:
        st.success("✅ API Key Connected")

    st.markdown("---")

    # Persona Selection
    st.subheader("🎭 Persona / Role")
    selected_persona = st.selectbox(
        "Select Academic Mode",
        options=list(PERSONAS.keys()),
        index=0,
        help="Controls the tone and pedagogical style of responses."
    )

    st.caption(f"**Persona Style:** {PERSONAS[selected_persona][:80]}...")

    st.markdown("---")

    # Multimodal File Uploader (PDF, PPTX, PPT, DOCX, TXT, MD, CSV, PNG, JPG, JPEG, WEBP)
    st.subheader("📚 File / Image Assistant")
    uploaded_file = st.file_uploader(
        "Upload Notes, Slides, Paper, or Image",
        type=["pdf", "pptx", "ppt", "docx", "txt", "md", "csv", "png", "jpg", "jpeg", "webp"],
        help="Upload PDF documents, PowerPoint slides (.pptx), Word notes (.docx), or images."
    )

    if uploaded_file is not None:
        if st.session_state["doc_filename"] != uploaded_file.name:
            with st.spinner(f"Processing '{uploaded_file.name}'..."):
                try:
                    processed_data = process_file(uploaded_file)
                    st.session_state["doc_info"] = processed_data
                    st.session_state["doc_filename"] = uploaded_file.name
                    
                    if processed_data["type"] == "image":
                        st.success(f"🖼️ Loaded Image: {uploaded_file.name}")
                        st.image(processed_data["image_bytes"], caption="Uploaded Image Preview", use_container_width=True)
                    else:
                        st.success(f"📄 Loaded Document: {uploaded_file.name} ({len(processed_data['content'])} chars)")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
    else:
        if st.session_state["doc_filename"] is not None:
            st.session_state["doc_info"] = None
            st.session_state["doc_filename"] = None

    st.markdown("---")

    # Advanced Model Settings
    with st.expander("⚙️ Advanced Parameters"):
        selected_model = st.selectbox(
            "Model Version",
            options=["gemini-3.6-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            index=0
        )
        temperature = st.slider(
            "Creativity (Temperature)",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Lower values make output more deterministic; higher values make output more creative."
        )

    # Clear Chat Button
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Chat history cleared. How can I help you today?"}
        ]
        st.rerun()

# --- MAIN CHAT AREA ---
col_title, col_status = st.columns([3, 1])

with col_title:
    st.markdown('<div class="main-header">🎓 Interactive Academic AI Chatbot</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Active Persona: <b>{selected_persona}</b></div>', unsafe_allow_html=True)

with col_status:
    if st.session_state["doc_filename"]:
        badge_icon = "🖼️" if st.session_state["doc_info"] and st.session_state["doc_info"]["type"] == "image" else "📄"
        st.markdown(f'<div style="text-align: right; padding-top: 10px;"><span class="doc-badge">{badge_icon} Attached: {st.session_state["doc_filename"]}</span></div>', unsafe_allow_html=True)

st.markdown("---")

# Render Existing Chat History
for message in st.session_state["messages"]:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Quick Interactive Action Buttons if a file is uploaded
if st.session_state["doc_filename"]:
    st.markdown("**⚡ Quick Actions for Attached File:**")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    
    with q_col1:
        if st.button("📄 Summarize Content", use_container_width=True):
            st.session_state["preset_prompt"] = "Please provide a comprehensive summary of the attached file."
    with q_col2:
        if st.button("💡 Key Takeaways", use_container_width=True):
            st.session_state["preset_prompt"] = "What are the key takeaways and main concepts in the attached file?"
    with q_col3:
        if st.button("📝 5 Quiz Questions", use_container_width=True):
            st.session_state["preset_prompt"] = "Generate 5 multiple-choice practice quiz questions based on the attached file."
    with q_col4:
        if st.button("🔍 Explain Key Terms", use_container_width=True):
            st.session_state["preset_prompt"] = "Explain all key technical terms or formulas mentioned in the attached file."

# Handle Preset Prompts or Chat Input
user_input = st.chat_input("Ask any question or query about your study topic or uploaded file...")

# Determine effective prompt
effective_prompt = None
if st.session_state.get("preset_prompt"):
    effective_prompt = st.session_state["preset_prompt"]
    st.session_state["preset_prompt"] = None  # Reset preset
elif user_input:
    effective_prompt = user_input

if effective_prompt:
    # Display user prompt in UI
    st.session_state["messages"].append({"role": "user", "content": effective_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(effective_prompt)

    # Generate Bot Response
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Analyzing & generating response... 🧠")

        engine = GeminiChatEngine(api_key=user_api_key)
        
        response_text = engine.generate_response(
            prompt=effective_prompt,
            chat_history=st.session_state["messages"][:-1],
            persona_name=selected_persona,
            doc_info=st.session_state["doc_info"],
            model_name=selected_model,
            temperature=temperature
        )

        message_placeholder.markdown(response_text)

    # Save Assistant Response
    st.session_state["messages"].append({"role": "assistant", "content": response_text})
    st.rerun()
