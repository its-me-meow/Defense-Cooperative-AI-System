# streamlit_app.py
import streamlit as st
from src.chatbot import chat  # 예: final_test.py 안에 정의된 응답 함수

st.title("국방 기술 협력 챗봇")

user_input = st.text_input("질문을 입력하세요:")
if user_input:
    response = chat(user_input)  # 정의된 함수 사용
    st.write("응답:", response)
