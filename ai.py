import streamlit as st
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set page config
st.set_page_config(
    page_title="⚡ AI-Based Home Energy Saver",
    page_icon="💡",
    layout="centered"
)

# Custom CSS for better background visibility
background_image_url = "https://c1.wallpaperflare.com/preview/660/739/814/light-bulb-idea-self-employed-incidence.jpg"
st.markdown(
    f"""
    <style>
        body {{
            background-image: url("{background_image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp {{
            background: rgba(0, 0, 0, 0.6);
            border-radius: 10px;
            padding: 20px;
            color: white;
        }}
        .stChatMessage {{
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            color: white;
        }}
        .stChatInput {{
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 5px;
            color: white;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: white;
        }}
        .stSidebar {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! 😊 I am your AI-Based Home Energy Saver. Ask me for tips on reducing electricity bills!"
    }]

# Sidebar settings
with st.sidebar:
    st.markdown("""
        <div style='text-align: left; font-size: 16px; font-weight: bold;'>
            Reg. No: 12312632<br>
            Reg. No: 12306669<br>
            Reg. No: 12306903
        </div>
    """, unsafe_allow_html=True)

    st.title("⚙️ Settings")
    api_key = st.text_input("OpenRouter API Key", type="password")
    st.markdown("[Get API Key](https://openrouter.ai/keys)")

    # Model selection
    model_name = st.selectbox(
        "Choose AI Model",
        ("deepseek/deepseek-r1-zero:free", "google/palm-2-chat-bison"),
        index=0
    )

    # Advanced settings
    with st.expander("Advanced Settings"):
        temperature = st.slider("Response Creativity", 0.0, 1.0, 0.7)
        max_retries = st.number_input("Max Retries", 1, 5, 2)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Chat cleared! Ask me for energy-saving tips!"
        }]

# Main interface
st.title("💡 AI-Based Home Energy Saver")
st.caption("Smart recommendations to help you cut down your electricity bills")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"<div class='stChatMessage'>{message['content']}</div>", unsafe_allow_html=True)

# Handle user input
if prompt := st.chat_input("Ask me about saving energy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(f"<div class='stChatMessage'>{prompt}</div>", unsafe_allow_html=True)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("🔑 API key required! Check sidebar settings")
        st.stop()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        attempts = 0

        while attempts < max_retries:
            try:
                # API request
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://energy-saver.streamlit.app",
                        "X-Title": "AI-Based Home Energy Saver"
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {
                                "role": "system",
                                "content": f"""You are an expert in home energy conservation. Follow these STRICT rules:
1. RESPOND ONLY IN PLAIN TEXT
2. NEVER USE JSON, MARKDOWN, OR CODE BLOCKS
3. Format lists with hyphens (-) only
4. Provide practical energy-saving tips
5. Structure responses clearly with line breaks
6. If unsure about information, say "I need to verify that"
7. Maintain a friendly and informative tone
8. Current date: {time.strftime("%B %d, %Y")}
"""
                            },
                            *st.session_state.messages
                        ],
                        "temperature": temperature
                    },
                    timeout=15
                )

                response.raise_for_status()
                raw_response = response.json()['choices'][0]['message']['content']

                # Stream response
                for chunk in raw_response.split():
                    full_response += chunk + " "
                    response_placeholder.markdown(f"<div class='stChatMessage'>{full_response}▌</div>", unsafe_allow_html=True)
                    time.sleep(0.03)

                response_placeholder.markdown(f"<div class='stChatMessage'>{full_response}</div>", unsafe_allow_html=True)
                break

            except requests.exceptions.RequestException as e:
                logging.error(f"Network Error: {str(e)}")
                response_placeholder.error(f"🌐 Network Error: {str(e)}")
                full_response = "Error: Connection issue - try again later"
                break

            except Exception as e:
                logging.error(f"Unexpected Error: {str(e)}")
                response_placeholder.error(f"❌ Unexpected error: {str(e)}")
                full_response = "Error: Please check your input and try again"
                break

    st.session_state.messages.append({"role": "assistant", "content": full_response})

