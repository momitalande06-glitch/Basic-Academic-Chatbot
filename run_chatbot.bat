@echo off
title Academic AI Chatbot Launcher
echo Starting Academic AI Chatbot...
cd /d "C:\Users\momit\.gemini\antigravity\scratch\academic_chatbot"
start "" http://localhost:8501
python -m streamlit run app.py
