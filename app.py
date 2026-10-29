import streamlit as st
from google import genai

# Page Configuration
st.set_page_config(
    page_title="SHAHROZ AI TRADING ACADEMY",
    page_icon="📈",
    layout="wide",
)

# Sidebar Settings
st.sidebar.markdown("## ⚙️ Academy Settings")

# ========================================================
# LINE 17 PAR APNI API KEY LIKHNI HAI:
# Yahan neeche "YAHAN_APNI_ASLI_GEMINI_API_KEY_LIKH_DEIN" 
# ki jagah apni asli Gemini API key quotes ("") ke andar paste kar dein.
# ========================================================
API_KEY = "AQ.Ab8RN6IigfrTg2uE-9Jra_i2zbntXysDJ86iFZ_YiON216AXYw"

# Model Selection
selected_model = st.sidebar.selectbox(
    "Choose Gemini Model",
    ["gemini-2.5-flash", "gemini-2.5-pro"]
)

# Teaching Language
language = st.sidebar.selectbox(
    "Teaching Language",
    ["Roman Urdu", "English", "Urdu"]
)

# Teacher Personality
personality = st.sidebar.selectbox(
    "Teacher Personality",
    ["Funny + Friendly", "Strict Professor", "Professional Mentor"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Developed By")
st.sidebar.markdown("**Shahroz Asghar**")

# Main Interface
st.markdown("<h1 align='center'>📈 SHAHROZ AI TRADING ACADEMY 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p align='center'><b>Your Personal AI Trading Teacher & Mentor</b></p>", unsafe_allow_html=True)
st.markdown("---")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Assalam-o-Alaikum, future trader! 😎 📈\n\nWelcome to SHAHROZ AI TRADING ACADEMY! ❤️\n\nMain tumhara friendly trading teacher hoon. Hum trading seekhenge, examples solve karenge aur thora hansenge bhi! 😂\n\nBatao, aaj kya seekhna hai?"
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Apna trading sawal yahan likho..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if not API_KEY or API_KEY == "YAHAN_APNI_ASLI_GEMINI_API_KEY_LIKH_DEIN":
            response_text = "⚠️ Error: Developer ne code mein API key configure nahi ki!"
            message_placeholder.markdown(response_text)
        else:
            try:
                # Initialize Gemini Client with hardcoded key
                client = genai.Client(api_key=API_KEY)
                
                # System instructions based on settings
                system_instruction = f"""
                You are a world-class trading mentor at SHAHROZ AI TRADING ACADEMY.
                Your personality is {personality}.
                You teach forex (XAUUSD/Gold), MT5, stocks, and crypto.
                You must reply in {language}. Keep the tone engaging, helpful, and educational.
                """
                
                # Format conversation history for Gemini
                contents = []
                for m in st.session_state.messages:
                    role_name = "user" if m["role"] == "user" else "model"
                    contents.append({"role": role_name, "parts": [{"text": m["content"]}]})
                
                response = client.models.generate_content(
                    model=selected_model,
                    contents=contents,
                    config={
                        'system_instruction': system_instruction,
                    }
                )
                response_text = response.text
                message_placeholder.markdown(response_text)
            except Exception as e:
                response_text = f"❌ Error: {str(e)}"
                message_placeholder.markdown(response_text)

        st.session_state.messages.append({"role": "assistant", "content": response_text})
