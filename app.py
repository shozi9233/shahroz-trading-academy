import os
import time

import streamlit as st
from google import genai
from google.genai import types

# =====================================================================
#  SETTINGS  (sirf yahan tabdeeli karein)
# =====================================================================

# Option 1 (sab se aasan): apni API key neeche quotes ke andar paste karein.
# Option 2 (behtar/safe): Streamlit Secrets ya Environment Variable mein
#           GEMINI_API_KEY naam se rakhein, phir yahan kuch likhne ki zaroorat nahi.
HARDCODED_API_KEY = "PASTE_YOUR_GEMINI_API_KEY_HERE"

MAIN_MODEL = "gemini-3.5-flash"       # sirf yahi model use hoga
MAX_MESSAGES_PER_SESSION = 40         # ek student ke liye limit (quota bachane ke liye)
HISTORY_LIMIT = 10                    # AI ko pichhle kitne messages bhejne hain

# =====================================================================
#  PAGE CONFIG
# =====================================================================
st.set_page_config(
    page_title="SHAHROZ AI TRADING ACADEMY",
    page_icon="📈",
    layout="wide",
)


# =====================================================================
#  API KEY + CLIENT
# =====================================================================
def get_api_key() -> str:
    """Key ko is tarteeb se dhoondta hai: Streamlit Secrets -> Environment -> Code."""
    try:
        key = st.secrets["GEMINI_API_KEY"]
        if key:
            return str(key).strip()
    except Exception:
        pass

    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key.strip()

    if HARDCODED_API_KEY and "PASTE_YOUR" not in HARDCODED_API_KEY:
        return HARDCODED_API_KEY.strip()

    return ""


API_KEY = get_api_key()


@st.cache_resource
def get_client(api_key: str):
    # Client sirf ek dafa banta hai, har message par dobara nahi.
    return genai.Client(api_key=api_key)


# =====================================================================
#  SIDEBAR
# =====================================================================
st.sidebar.markdown("## ⚙️ Academy Settings")

language = st.sidebar.selectbox(
    "🗣️ Teaching Language",
    ["Roman Urdu", "English", "Urdu"],
)

personality = st.sidebar.selectbox(
    "🎭 Teacher Personality",
    ["Funny + Friendly", "Strict Professor", "Professional Mentor"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Quick Lessons")

LESSONS = {
    "1️⃣ Trading kya hai? (Basics)": "Mujhe bilkul shuru se samjhao ke trading kya hoti hai aur forex market kaise kaam karti hai.",
    "2️⃣ Gold (XAUUSD) kya hai?": "XAUUSD kya hai? Gold ki trading kaise hoti hai, pip, lot size aur spread samjhao.",
    "3️⃣ Doo Prime par account kholna": "Doo Prime ki official website par account kholne ke steps ek ek kar ke samjhao.",
    "4️⃣ Demo account": "Demo account kya hota hai, kaise banate hain, aur is par practice kaise karni chahiye? Poori detail se batao.",
    "5️⃣ MT5 sikhao": "MetaTrader 5 (MT5) ka use sikhao: chart, buy/sell order, stop loss aur take profit kaise lagate hain.",
    "6️⃣ Risk Management": "Risk management samjhao: stop loss, lot size, risk per trade aur nuksan se kaise bachna hai.",
    "7️⃣ Live account kab?": "Demo ke baad live account par kab aur kaise jana chahiye? Kin baton ka khayal rakhna chahiye?",
}

for title, question in LESSONS.items():
    if st.sidebar.button(title, use_container_width=True):
        st.session_state["pending_prompt"] = question

st.sidebar.markdown("---")
st.sidebar.warning(
    "⚠️ **Risk Warning:** Trading mein paisa lagane se nuksan ho sakta hai. "
    "Ye academy sirf taleem ke liye hai, kamai ki koi guarantee nahi. "
    "Sirf wo paisa lagayein jiske doob jane ka aap bardasht kar sakein."
)
st.sidebar.markdown("### 👨‍💻 Developed By")
st.sidebar.markdown("**Shahroz Asghar**")

# =====================================================================
#  MAIN HEADER
# =====================================================================
st.markdown(
    "<h1 style='text-align:center;'>📈 SHAHROZ AI TRADING ACADEMY 🚀</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center;'><b>Your Personal AI Trading Teacher & Mentor</b></p>",
    unsafe_allow_html=True,
)
st.markdown("---")

if not API_KEY:
    st.error(
        "⚠️ API key set nahi hai. Code ke upar `HARDCODED_API_KEY` mein key paste karein "
        "ya Streamlit Secrets mein `GEMINI_API_KEY` add karein."
    )
    st.stop()

# =====================================================================
#  SESSION STATE
# =====================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Assalam-o-Alaikum, future trader! 😎📈\n\n"
                "SHAHROZ AI TRADING ACADEMY mein khush aamdeed! ❤️\n\n"
                "Left sidebar se koi lesson chunein ya neeche apna sawal likhein. "
                "Hum step by step seekhenge: Basics → Gold (XAUUSD) → Demo account → MT5 → Risk management.\n\n"
                "Batao, aaj kya seekhna hai?"
            ),
        }
    ]

if "user_msg_count" not in st.session_state:
    st.session_state.user_msg_count = 0


# =====================================================================
#  HELPERS
# =====================================================================
def build_system_instruction() -> str:
    return f"""
You are a world-class trading teacher and mentor at "SHAHROZ AI TRADING ACADEMY".
Your personality: {personality}.
You MUST reply in {language}. (If the language is Roman Urdu, write Urdu using English letters.)
Keep answers clear, engaging, beginner-friendly and well organised (short paragraphs, simple steps, small examples).

TEACHING PLAN (follow this order for beginners and guide students step by step):
1. Trading and forex basics.
2. Gold (XAUUSD): pip, lot, spread, leverage, why gold moves.
3. Opening an account with the broker Doo Prime (a Singapore-based broker): explain the general steps
   (registration, verification, choosing account type). Tell students to open the broker's OFFICIAL website
   themselves, to double-check the broker's regulation and terms before depositing money, and never to
   share passwords or send money to strangers.
4. Demo account: explain fully what it is, how to open it, and how to practise on it.
5. MetaTrader 5 (MT5): charts, placing buy/sell orders, stop loss, take profit.
6. Risk management: risk per trade, stop loss, lot size, avoiding over-leverage.
7. Going live only after consistent practice on demo, starting with a very small amount.

STRICT RULES:
- Always remember: trading carries a high risk of losing money. Never promise or imply guaranteed profit.
- Never give buy/sell signals, "sure shot" trades or tell the student to invest a specific amount of money.
  Teach concepts and method instead.
- Encourage students to use only money they can afford to lose, and to practise on a demo account first.
- Warn against scams: signal sellers, "double your money" schemes, fake brokers, and anyone asking for passwords.
- If asked about something unrelated to trading or finance education, politely steer back to trading.
- If you are not sure about a fact (for example a broker's exact current rules), say so honestly and
  tell the student to verify it on the official website.
""".strip()


def build_contents(messages):
    """Pichhle messages ko Gemini ke format mein badalta hai.
    Pehla message hamesha 'user' hona chahiye, warna API error deti hai."""
    recent = messages[-HISTORY_LIMIT:]
    while recent and recent[0]["role"] != "user":
        recent = recent[1:]
    contents = []
    for m in recent:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    return contents


def is_key_error(text: str) -> bool:
    t = text.lower()
    return any(
        s in t
        for s in (
            "api key",
            "api_key",
            "permission_denied",
            "unauthenticated",
            "leaked",
        )
    )


def stream_reply(contents, system_instruction):
    """Jawab ko tukron mein deta hai (streaming). Busy hone par dobara koshish karta hai."""
    client = get_client(API_KEY)
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
    )

    last_error = None
    for model in (MAIN_MODEL,):
        for attempt in range(3):
            started = False
            try:
                stream = client.models.generate_content_stream(
                    model=model,
                    contents=contents,
                    config=config,
                )
                for chunk in stream:
                    if chunk.text:
                        started = True
                        yield chunk.text
                if started:
                    return
                last_error = RuntimeError("Empty response")
            except Exception as e:  # noqa: BLE001
                last_error = e
                if started:
                    raise  # jawab aadha aa chuka ho to dobara na bhejein
                # Key ka masla ho to dobara koshish ka faida nahi
                if is_key_error(str(e)):
                    raise
                time.sleep(1.5)
    raise last_error if last_error else RuntimeError("Unknown error")


def friendly_error(e: Exception) -> str:
    t = str(e).lower()
    if "429" in t or "resource_exhausted" in t or "quota" in t:
        return (
            "⏳ Is waqt bohat zyada students ek saath use kar rahe hain ya daily limit poori ho gayi hai. "
            "Thori der baad dobara koshish karein."
        )
    if "503" in t or "unavailable" in t or "overloaded" in t:
        return "🔧 AI server abhi busy hai. Kuch der baad dobara koshish karein."
    if "leaked" in t:
        return (
            "🔑 Academy ki API key leak ho chuki hai aur Google ne use band kar diya hai. "
            "Admin (Shahroz) ko batayein ke nayi key banaye."
        )
    if is_key_error(t):
        return (
            "🔑 Academy ki API key mein masla hai. Admin (Shahroz) ko batayein ke key check kare."
        )
    if "404" in t or "not_found" in t:
        return "🔧 AI model abhi available nahi hai. Admin ko batayein ke model ka naam check kare."
    return "❌ Kuch masla aa gaya. Thori der baad dobara koshish karein."


# =====================================================================
#  CHAT HISTORY DISPLAY
# =====================================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =====================================================================
#  CHAT INPUT
# =====================================================================
typed_prompt = st.chat_input("Apna trading sawal yahan likho...")
prompt = typed_prompt or st.session_state.pop("pending_prompt", None)

if prompt:
    if st.session_state.user_msg_count >= MAX_MESSAGES_PER_SESSION:
        st.warning(
            "📌 Is session ki limit poori ho gayi hai. Page refresh karke naya session shuru karein."
        )
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.user_msg_count += 1
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            contents = build_contents(st.session_state.messages)
            reply = st.write_stream(stream_reply(contents, build_system_instruction()))
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:  # noqa: BLE001
            st.error(friendly_error(e))
            with st.expander("🔧 Technical details (admin ke liye)"):
                st.code(str(e))
            # Error wale sawal ko history se hata dein taake agla jawab kharab na ho
            st.session_state.messages.pop()
            st.session_state.user_msg_count -= 1
