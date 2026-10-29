import streamlit as st
from google import genai
from google.genai import types

# =========================================
# 1. PAGE SETTINGS
# =========================================

st.set_page_config(
    page_title="SHAHROZ AI TRADING ACADEMY", page_icon="📈", layout="centered"
)

st.markdown(
    """
<style>
.main-title {
    text-align: center;
    color: #00C878;
    font-size: 30px;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: #888888;
    font-size: 16px;
}
[data-testid="stSidebar"] {
    min-width: 300px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">'
    "📈 SHAHROZ AI TRADING ACADEMY 🚀"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Your Personal AI Trading Teacher & Mentor"
    "</div>",
    unsafe_allow_html=True,
)

st.divider()


# =========================================
# 2. AI TEACHER INSTRUCTIONS
# =========================================

SYSTEM_PROMPT = """
You are the friendly AI teacher of SHAHROZ AI TRADING ACADEMY.
The academy offers free trading education, especially for people
who cannot afford paid courses. Your job is to teach, not to sell.

PERSONALITY:
- Be friendly, patient, respectful and encouraging.
- Use light Pakistani humour when appropriate.
- Explain difficult concepts with simple examples.
- Never insult students or make fun of their mistakes.
- Use emojis occasionally.

TEACHING:
- Teach trading from beginner to advanced level.
- Main focus: gold trading (XAUUSD) in forex using MetaTrader 5 (MT5).
- Also explain stocks, cryptocurrency, candlesticks, trends,
 support, resistance and risk management when asked.
- Gold basics to cover: what XAUUSD is, pip/point, lot size
 (0.01 is the smallest normal lot), spread, margin, leverage,
 stop-loss, take-profit, and what moves gold (US dollar,
 interest rates, inflation, geopolitical news).
- Give practical educational examples and practice questions.
- Explain technical terms in simple language.
- Never invent live market prices or breaking news.
- Never claim to have live market data unless it is provided.

LEARNING PATH (always guide students in this order):
1. Basics: money, risk, reward, how the market works.
2. Open a DEMO account and practice on MT5 with virtual money.
3. Keep a trading journal and practice on demo for several weeks.
4. Only after steady, disciplined demo results, talk about a live account.

DEMO ACCOUNT AND MT5 HELP:
- You can explain step by step how to open a demo account on a broker's
 official website, install MT5 (or use its web terminal), log in with
 the login, password and server name from the broker's email, find
 XAUUSD in Market Watch, and place a practice order with a small
 volume (such as 0.01) with stop-loss and take-profit.
- You cannot see the student's screen. Button and menu names can differ
 between brokers and app versions, so say so and give general steps.
- Doo Prime (a broker that offers MT5) may be used as an EXAMPLE, but
 the academy does not endorse or guarantee any broker. Teach students
 how to choose a broker: check the regulator's official website for
 the license number, type the broker's website address manually (do not
 use links from social media or chat groups), and read withdrawal terms.
- Remind students to check the laws and rules of their own country
 (for example SECP and SBP guidance in Pakistan) before opening an
 account with an offshore broker.
- Never ask for or accept passwords, account numbers or card details.
 Tell students never to share their passwords with anyone.

LIVE ACCOUNT RULES:
- Only talk about going live after demo practice.
- Only use money the student can afford to lose. Never borrow money,
 never use rent, food, school fees or other household money.
- Recommend a small start, low leverage and risking only about 1-2%
 of the account on a single trade.

FINANCIAL SAFETY:
- Trading involves risk; most retail traders lose money.
- Profits are never guaranteed. Explain potential losses as well as gains.
- Do not promise guaranteed profits or risk-free strategies.
- Do not give buy/sell signals, "buy gold now" calls or personal
 investment advice. Educational examples are not signals.
- Teach scam awareness: "guaranteed profit", paid signal groups,
 fake brokers, fake "account managers", pressure to deposit quickly,
 and people asking for passwords or remote access.
- If a student says they are in financial trouble or want to borrow
 money to trade, gently discourage it and suggest safer options.

TOPIC & UNRELATED QUESTIONS RULE:
- Focus strictly on trading and related financial education.
- If a user asks any question outside of trading, finance, or markets (such as coding, general knowledge, movies, personal questions, etc.), you must reply with this exact sentiment/phrase in Roman Urdu: "SIR SHAHROZ ny muje bs trading sekhany ky hawaly sy design kiya ha" and politely guide them back to trading.

Your goal is to help students understand trading safely
and enjoy learning.
"""


# =========================================
# 3. SIDEBAR SETTINGS
# =========================================

with st.sidebar:
  st.header("⚙️ Academy Settings")

  api_key_input = st.text_input(
      "Google Gemini API Key",
      type="password",
      help="Enter your Gemini API key. Never share it publicly.",
  )

  # Only Gemini 3.5 models available
  model_name = st.selectbox(
      "Choose Gemini Model",
      ["gemini-3.5-flash", "gemini-3.5-pro"],
      index=0,
  )

  language = st.selectbox(
      "Teaching Language", ["Roman Urdu", "Urdu", "English"]
  )

  style = st.selectbox(
      "Teacher Personality",
      ["Funny + Friendly", "Friendly + Professional", "Simple + Serious"],
  )

  st.divider()

  st.subheader("👨‍💻 Developed By")
  st.write("**Shahroz Asghar**")
  st.caption("© 2026 SHAHROZ AI TRADING ACADEMY")

  st.warning(
      "Trading involves financial risk. This assistant provides educational"
      " information only."
  )


# =========================================
# 4. HELPER FUNCTIONS
# =========================================

LANGUAGE_RULES = {
    "Roman Urdu": "Always reply in Roman Urdu using Latin letters.",
    "Urdu": "Reply in Urdu script.",
    "English": "Reply in English.",
}

STYLE_RULES = {
    "Funny + Friendly": "Be funny, friendly and use light Pakistani humour.",
    "Friendly + Professional": "Be friendly, clear and professional.",
    "Simple + Serious": "Be simple, direct and serious.",
}


def get_api_key(user_key):
  """Use the key typed in the sidebar, or one saved in st.secrets."""
  user_key = (user_key or "").strip()
  if user_key:
    return user_key
  try:
    return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
  except Exception:
    return ""


def build_contents(messages):
  """Turn recent chat history into Gemini's format."""
  recent = messages[1:][-12:]

  while recent and recent[0]["role"] != "user":
    recent = recent[1:]

  contents = []
  for item in recent:
    role = "model" if item["role"] == "assistant" else "user"
    contents.append(
        types.Content(
            role=role, parts=[types.Part.from_text(text=item["content"])]
        )
    )
  return contents


def ask_gemini(key, model, instructions, contents):
  """Create a fresh client for every request and get the answer."""
  client = genai.Client(api_key=key)
  response = client.models.generate_content(
      model=model,
      contents=contents,
      config=types.GenerateContentConfig(
          system_instruction=instructions, temperature=0.7
      ),
  )
  return (response.text or "").strip()


def friendly_error(error):
  """Short, helpful message for common problems."""
  text = str(error)
  upper = text.upper()
  if "API_KEY_INVALID" in upper or "API KEY" in upper:
    return (
        "API key galat lag rahi hai. Sidebar mein sahi Gemini API key dobara"
        " enter karein."
    )
  if "NOT_FOUND" in upper or "404" in upper:
    return (
        "Yeh model nahi mila. Sidebar se koi doosra model chunein, ya Google"
        " AI Studio mein model ka naam check karein."
    )
  if "RESOURCE_EXHAUSTED" in upper or "429" in upper:
    return "Limit poori ho gayi hai. Thori dair ruk kar dobara try karein."
  return "Kuch masla aa gaya. Dobara try karein."


# =========================================
# 5. INITIALIZE CHAT HISTORY
# =========================================

WELCOME_MESSAGE = (
    "Assalam-o-Alaikum, future trader! 😎📈\n\n"
    "Welcome to SHAHROZ AI TRADING ACADEMY! ❤️\n\n"
    "Main tumhara friendly trading teacher hoon. Hum trading seekhenge,"
    " examples solve karenge aur thora hansenge bhi! 😂\n\n"
    "Batao, aaj kya seekhna hai?"
)

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "assistant",
      "content": WELCOME_MESSAGE,
  }]


# =========================================
# 6. DISPLAY CHAT HISTORY
# =========================================

st.subheader("💬 Ask Your Trading Teacher")

for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])


# =========================================
# 7. NEW CHAT BUTTON
# =========================================

if st.sidebar.button("🗑️ Start New Chat", use_container_width=True):
  st.session_state.messages = [{
      "role": "assistant",
      "content": (
          "Nayi chat, nayi learning! 😎📚\n\nBatao student sahab, aaj kya seekhna"
          " hai?"
      ),
  }]
  st.rerun()


# =========================================
# 8. CHAT INPUT
# =========================================

prompt = st.chat_input("Apna trading sawal yahan likho...")

if prompt:
  api_key = get_api_key(api_key_input)

  if not api_key:
    with st.chat_message("assistant"):
      st.warning("Pehle sidebar mein apni Gemini API key enter karein.")
    st.stop()

  st.session_state.messages.append({"role": "user", "content": prompt})

  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    try:
      instructions = (
          SYSTEM_PROMPT
          + "\n\nLANGUAGE RULE:\n"
          + LANGUAGE_RULES[language]
          + "\n\nPERSONALITY RULE:\n"
          + STYLE_RULES[style]
      )

      contents = build_contents(st.session_state.messages)

      with st.spinner("Teacher sahab soch rahe hain... 🤔"):
        answer = ask_gemini(api_key, model_name, instructions, contents)

      if not answer:
        answer = (
            "Mujhe is sawal ka jawab nahi mil saka. Sawal thora alag tareeqe"
            " se likh kar dekhein."
        )

      st.markdown(answer)

      st.session_state.messages.append(
          {"role": "assistant", "content": answer}
      )

    except Exception as error:
      if (
          st.session_state.messages
          and st.session_state.messages[-1]["role"] == "user"
      ):
        st.session_state.messages.pop()

      st.error(friendly_error(error))
      with st.expander("Technical details"):
        st.code(str(error))