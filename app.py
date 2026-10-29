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

# Student API Key Input Field
user_api_key = st.sidebar.text_input(
    "🔑 Enter Your Gemini API Key",
    type="password",
    help="Apni Google AI Studio se mili hui API key yahan paste karein."
)

# Model Selection - Using gemini-3.5-flash as requested
selected_model = st.sidebar.selectbox(
    "Choose Gemini Model",
    ["gemini-3.5-flash", "gemini-2.5-pro"]
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
            "content": "Assalam-o-Alaikum, future trader! 😎 📈\n\nWelcome to SHAHROZ AI TRADING ACADEMY! ❤️\n\nSidebar mein apni API key enter karein aur sawal poochein. Hum trading seekhenge aur maza bhi aayega! 😂\n\nBatao, aaj kya seekhna hai?"
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Apna trading sawal yahan likho..."):
    # Check if student has entered the API key
    if not user_api_key:
        st.error("⚠️ Pehle sidebar mein apni Gemini API Key enter karein!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                # Initialize Gemini Client with user's provided API Key
                client = genai.Client(api_key=user_api_key.strip())
                
                system_instruction = f"""
                You are a world-class trading mentor at SHAHROZ AI TRADING ACADEMY.
                Your personality is {personality}.
                You teach forex (XAUUSD/Gold), MT5, stocks, and crypto.
                You must reply in {language}. Keep the tone engaging, helpful, and educational.
                """
                
                # Limit conversation history to last 6 messages
                recent_messages = st.session_state.messages[-6:]
                contents = []
                for m in recent_messages:
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
