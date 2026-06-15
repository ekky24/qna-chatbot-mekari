import streamlit as st
import requests
import json
import config

USER_AVATAR = "🧑‍💻"
ASSISTANT_AVATAR = "🤖"

st.set_page_config(
    page_title="Fraud Q&A Assistant",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- Styling -----------------------------------------------------------------
# Colors use rgba/neutral tones so the UI reads well in both light & dark mode.
st.markdown(
    """
    <style>
      .block-container { padding-top: 2.5rem; padding-bottom: 6rem; max-width: 820px; }

      /* Reasoning / thinking panel */
      details.think {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-left: 3px solid rgba(99, 102, 241, 0.7);
        border-radius: 8px;
        padding: 0.5rem 0.85rem;
        margin: 0.1rem 0 0.7rem 0;
      }
      details.think summary {
        cursor: pointer;
        font-size: 0.8rem;
        font-weight: 600;
        opacity: 0.75;
        list-style: none;
        user-select: none;
      }
      details.think summary::-webkit-details-marker { display: none; }
      details.think .think-body {
        font-size: 0.82rem;
        line-height: 1.55;
        opacity: 0.7;
        margin-top: 0.5rem;
        white-space: pre-wrap;
      }

      /* Animated tool-status badge */
      .tool-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        background: rgba(99, 102, 241, 0.14);
        border: 1px solid rgba(99, 102, 241, 0.30);
        padding: 0.28rem 0.7rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 500;
      }
      .tool-badge .spin { display: inline-block; animation: spin 1.6s linear infinite; }
      @keyframes spin { from { transform: rotate(0); } to { transform: rotate(360deg); } }
    </style>
    """,
    unsafe_allow_html=True,
)


def thinking_html(text: str, is_open: bool = False) -> str:
    open_attr = " open" if is_open else ""
    label = "Reasoning…" if is_open else "Reasoning"
    return (
        f'<details class="think"{open_attr}>'
        f"<summary>🧠 {label}</summary>"
        f'<div class="think-body">{text}</div>'
        f"</details>"
    )


def tool_badge_html(text: str) -> str:
    return f'<span class="tool-badge"><span class="spin">⚙️</span>{text}</span>'


# --- Sidebar -----------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛡️ Fraud Q&A Assistant")
    st.caption(
        "Ask questions about credit card fraud, query transaction data, "
        "and search the fraud manuals."
    )
    st.divider()
    st.markdown("**Model**")
    st.code(config.MODEL_NAME, language=None)
    st.divider()
    if st.button("🗑️  Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Header ------------------------------------------------------------------
st.title("💬 Q&A Chatbot")
st.caption("Retrieval-augmented assistant for fraud detection & analysis.")
st.divider()

# --- Session bootstrap -------------------------------------------------------
if "messages" not in st.session_state:
    _ = requests.get(f"{config.SERVICE_URL}/init")
    st.session_state.messages = []

# --- Render chat history -----------------------------------------------------
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else ASSISTANT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        if message.get("thinking"):
            st.markdown(thinking_html(message["thinking"]), unsafe_allow_html=True)
        st.markdown(message["content"])

# Phase 1: capture the new user message, store it, and rerun so it renders
# through the history loop above (avoids a trailing transient user bubble).
if prompt := st.chat_input("Ask about fraud, transactions, or the manuals…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Phase 2: if the last turn is an unanswered user message, stream the reply.
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    prompt = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
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
                        tool_status.markdown(
                            tool_badge_html(event["content"]), unsafe_allow_html=True
                        )
                    elif event["type"] == "thinking":
                        tool_status.empty()
                        thinking_text += event["content"]
                        thinking_box.markdown(
                            thinking_html(thinking_text, is_open=True),
                            unsafe_allow_html=True,
                        )
                    elif event["type"] == "token":
                        tool_status.empty()
                        if thinking_text:
                            thinking_box.markdown(
                                thinking_html(thinking_text, is_open=False),
                                unsafe_allow_html=True,
                            )
                        full_response += event["content"]
                        response_box.markdown(full_response + " ▌")
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
