import streamlit as st
import requests
import json
import config

st.title("Q&A Chatbot Interface")

if "messages" not in st.session_state:
    _ = requests.get(f'{config.SERVICE_URL}/init')
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("thinking"):
            with st.expander("Thinking...", expanded=False):
                st.markdown(message["thinking"])
        st.markdown(message["content"])

# Phase 1: capture the new user message, store it, and rerun so it renders
# through the history loop above (avoids a trailing transient user bubble).
if prompt := st.chat_input("What is on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Phase 2: if the last turn is an unanswered user message, stream the reply.
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        tool_status = st.empty()
        thinking_box = st.empty()
        response_box = st.empty()

        full_response = ""
        thinking_text = ""

        with requests.post(
            f"{config.SERVICE_URL}/chat/stream",
            json={"msg": prompt},
            stream=True,
        ) as r:
            for line in r.iter_lines():
                if not line:
                    continue
                data_str = line.decode("utf-8")
                if not data_str.startswith("data: "):
                    continue
                data = data_str[6:]
                if data == "[DONE]":
                    break
                try:
                    event = json.loads(data)
                    if event["type"] == "status":
                        tool_status.caption(f"⚙️ {event['content']}")
                    elif event["type"] == "thinking":
                        tool_status.empty()
                        thinking_text += event["content"]
                        thinking_box.markdown(
                            f"<details open><summary>Thinking...</summary>"
                            f"<small>{thinking_text}</small></details>",
                            unsafe_allow_html=True,
                        )
                    elif event["type"] == "token":
                        tool_status.empty()
                        if thinking_text:
                            thinking_box.markdown(
                                f"<details><summary>Thinking...</summary>"
                                f"<small>{thinking_text}</small></details>",
                                unsafe_allow_html=True,
                            )
                        full_response += event["content"]
                        response_box.markdown(full_response + "▌")
                except (json.JSONDecodeError, KeyError):
                    pass

        response_box.markdown(full_response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "thinking": thinking_text,
    })
    # Rerun so the finished reply is re-rendered through the stable history
    # loop and the transient streaming block is discarded (no ghost/duplicate).
    st.rerun()
