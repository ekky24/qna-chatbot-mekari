import streamlit as st
import requests
import json
import config

st.title("Q&A Chatbot Interface")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is on your mind?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # connecting to LLM
    payload = {
        "msg": prompt, 
    }
    response = requests.post(config.SERVICE_URL, json=payload)
    response = response.json()['response']

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
