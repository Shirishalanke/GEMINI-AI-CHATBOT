import streamlit as st
from dotenv import load_dotenv
import os
import json
import uuid
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

st.set_page_config(
    page_title="Gemini AI Chatbot",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------- Saved history file ----------
HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chat_history.json"
)


def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(
                st.session_state.history,
                f,
                ensure_ascii=False,
                indent=2
            )
    except Exception:
        pass


# ---------- Custom CSS ----------
st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@800&family=Figtree:wght@400;500;600;700&display=swap');

    :root {
        --ink: #1b1b3a;
        --line: rgba(27, 27, 58, 0.25);
        --sun: #ffc94d;
    }

    /* ===== Background ===== */
    .stApp {
        background: linear-gradient(
            120deg,
            #ffd3de 0%,
            #ffe2c2 17%,
            #fff6c4 34%,
            #d3f5d1 51%,
            #c8e6ff 68%,
            #ddd2ff 85%,
            #ffd3de 100%
        );
        color: var(--ink);
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    /* ===== Layout ===== */
    .block-container {
        max-width: 780px;
        padding-top: 4rem;
        padding-bottom: 7rem;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 1.8rem;
    }

    div[data-testid="stChatMessage"] div[data-testid="stVerticalBlock"] {
        gap: 1rem;
    }

    /* ===== Font ===== */
    .stMarkdown,
    .stMarkdown p,
    .stMarkdown li,
    textarea,
    .stButton button,
    .stButton button p,
    div[data-testid="stAlert"],
    div[data-testid="stAlert"] p,
    div[data-testid="stSpinner"],
    div[data-testid="stWidgetLabel"] p {
        font-family: 'Figtree', sans-serif !important;
    }

    /* ===== Title ===== */
    div[data-testid="stHeading"] {
        margin-bottom: 0.6rem;
    }

    h1 {
        font-family: 'Bricolage Grotesque', sans-serif !important;
        font-weight: 800 !important;
        font-size: 3.2rem !important;
        letter-spacing: -0.02em;
        line-height: 1.1 !important;
        color: var(--ink) !important;
        display: block;
        width: fit-content;
        max-width: 100%;
        padding: 0.5rem 1.4rem 0.7rem !important;
        background: var(--sun);
        border: 4px solid var(--ink);
        border-radius: 16px;
        box-shadow: 8px 8px 0 var(--ink);
        margin: 0 0 1rem 0 !important;
    }

    /* ===== Subtitle ===== */
    .stMarkdown p {
        font-size: 1.3rem;
        font-weight: 500;
        line-height: 1.6;
        color: var(--ink);
    }

    /* ===== Old textarea CSS kept for edit message ===== */
    .stTextArea,
    .stTextArea * {
        color-scheme: light;
    }

    .stTextArea [data-testid="stTextAreaRootElement"] {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    .stTextArea div[data-baseweb="textarea"],
    .stTextArea div[data-baseweb="textarea"]:hover,
    .stTextArea div[data-baseweb="textarea"]:focus-within {
        background: #ffffff !important;
        border: 2px solid rgba(27, 27, 58, 0.25) !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        outline: none !important;
        overflow: hidden;
    }

    .stTextArea div[data-baseweb="textarea"]:focus-within {
        border-color: #1b1b3a !important;
    }

    .stTextArea div[data-baseweb="base-input"],
    .stTextArea div[data-baseweb="base-input"]:focus-within {
        background: #ffffff !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    .stTextArea textarea,
    .stTextArea textarea:focus {
        background: #ffffff !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink);
        font-size: 1.2rem !important;
        line-height: 1.6;
        font-weight: 500;
        min-height: 150px;
        padding: 1.1rem 1.3rem !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        resize: none !important;
    }

    /* ===== Buttons ===== */
    .stButton > button {
        background: #ffffff;
        color: var(--ink);
        border: 2px solid var(--ink);
        border-radius: 12px;
        padding: 0.6rem 1.6rem;
        min-height: 3rem;
        box-shadow: none;
        transform: none;
        transition: none;
    }

    .stButton > button p {
        font-weight: 600;
        font-size: 1.1rem !important;
        color: var(--ink);
    }

    .stButton > button:hover {
        background: #f1f2f9;
        color: var(--ink);
        border-color: var(--ink);
        transform: none;
        box-shadow: none;
    }

    .stButton > button:active {
        transform: none;
        box-shadow: none;
    }

    .stButton > button:focus-visible {
        outline: 3px solid rgba(27, 27, 58, 0.35);
        outline-offset: 2px;
    }

    /* ===== Hide old Generate Response button ===== */
    .st-key-send_btn {
        display: none !important;
    }

    /* ===== Small chat buttons ===== */
    [class*="st-key-edit_btn_"] button,
    [class*="st-key-save_btn_"] button,
    [class*="st-key-cancel_btn_"] button {
        padding: 0.3rem 1.1rem;
        min-height: 2.4rem;
    }

    [class*="st-key-edit_btn_"] button p,
    [class*="st-key-save_btn_"] button p,
    [class*="st-key-cancel_btn_"] button p {
        font-size: 1rem !important;
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.35) !important;
        border-right: 1px solid var(--line);
    }

    section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {
        background: transparent !important;
        padding: 1.5rem 1.2rem 2rem;
    }

    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 1rem;
    }

    section[data-testid="stSidebar"] h3 {
        font-family: 'Figtree', sans-serif !important;
        font-weight: 700;
        font-size: 1.3rem;
        color: var(--ink);
        padding: 0;
        margin: 0.3rem 0 0;
    }

    section[data-testid="stSidebar"] .stButton > button {
        width: auto;
        padding: 0.2rem 1rem;
        min-height: 2.3rem;
        border-width: 2px;
    }

    section[data-testid="stSidebar"] .stButton > button p {
        font-size: 1rem !important;
    }

    .hist-empty {
        font-family: 'Figtree', sans-serif;
        font-size: 1rem;
        font-weight: 500;
        color: #4a4e75;
    }

    /* ===== Saved chats ===== */
    section[data-testid="stSidebar"] [class*="st-key-hist_"] {
        width: 100%;
    }

    section[data-testid="stSidebar"] [class*="st-key-hist_"] button {
        width: 100%;
        justify-content: flex-start;
        text-align: left;
        min-height: 2.5rem;
        padding: 0.3rem 0.9rem;
        border-width: 1.5px;
        border-color: var(--line);
    }

    section[data-testid="stSidebar"] [class*="st-key-hist_"] button p {
        font-size: 0.98rem !important;
        font-weight: 500;
        text-align: left;
    }

    section[data-testid="stSidebar"] [class*="st-key-hist_active_"] button {
        border-color: var(--ink);
        background: #eef0fb;
    }

    section[data-testid="stSidebar"] [class*="st-key-hist_active_"] button p {
        font-weight: 700;
    }

    /* ===== Chat bubbles ===== */
    div[data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 2px solid var(--line);
        border-radius: 16px;
        box-shadow: none;
        padding: 1.2rem 1.4rem;
    }

    div[data-testid="stChatMessage"]:has(
        [data-testid="stChatMessageAvatarUser"]
    ) {
        background: #f4f5fc !important;
    }

    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li {
        font-size: 1.15rem;
        font-weight: 500;
        line-height: 1.7;
        color: var(--ink);
    }

    /* ===== Alerts ===== */
    div[data-testid="stAlert"] {
        border: 2px solid var(--line);
        border-radius: 14px;
        box-shadow: none;
        padding: 0.6rem 0.8rem;
    }

    div[data-testid="stAlert"] p {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--ink);
    }

    div[data-testid="stAlert"]:has(
        [data-testid="stAlertContentSuccess"]
    ) {
        background: #e6f7ee;
    }

    div[data-testid="stAlert"]:has(
        [data-testid="stAlertContentWarning"]
    ) {
        background: #fff5db;
    }

    div[data-testid="stAlert"]:has(
        [data-testid="stAlertContentError"]
    ) {
        background: #fde8e8;
    }

    div[data-testid="stAlert"]:has(
        [data-testid="stAlertContentInfo"]
    ) {
        background: #eaf0ff;
    }

    /* ===== Spinner ===== */
    div[data-testid="stSpinner"] p {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--ink);
    }

    /* ===== Response text ===== */
    .stMarkdown h2,
    .stMarkdown h3 {
        font-family: 'Figtree', sans-serif !important;
        font-weight: 700;
        color: var(--ink);
    }

    .stMarkdown code {
        background: #eceef8;
        color: var(--ink);
        border-radius: 6px;
        padding: 0.1rem 0.4rem;
    }

    .stMarkdown pre {
        border: 2px solid var(--line);
        border-radius: 12px;
        box-shadow: none;
    }

    /* =====================================================
       CHATGPT STYLE INPUT BAR
       ===================================================== */

    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 1.5rem;
        left: 50%;
        transform: translateX(-50%);
        width: min(780px, calc(100% - 2rem));
        z-index: 999;
    }

    div[data-testid="stChatInput"] > div {
        background: #ffffff !important;
        border: 2px solid rgba(27, 27, 58, 0.25) !important;
        border-radius: 24px !important;
        box-shadow: 0 4px 18px rgba(27, 27, 58, 0.12) !important;
    }

    div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #1b1b3a !important;
        -webkit-text-fill-color: #1b1b3a !important;
        font-family: 'Figtree', sans-serif !important;
        font-size: 1.1rem !important;
        min-height: 24px !important;
        max-height: 180px !important;
        padding: 0.8rem 3.5rem 0.8rem 1.2rem !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #7b7fa8 !important;
        opacity: 1 !important;
    }

    div[data-testid="stChatInput"] > div:focus-within {
        border-color: #1b1b3a !important;
        box-shadow: 0 4px 20px rgba(27, 27, 58, 0.16) !important;
    }

    @media (max-width: 600px) {

        h1 {
            font-size: 2.2rem !important;
        }

        div[data-testid="stChatInput"] {
            width: calc(100% - 1rem);
            bottom: 0.5rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Session state ----------
defaults = {
    "messages": [],
    "editing": None,
    "pending": False,
    "warn": False,
    "done": False,
    "error": None,
    "prompt": "",
    "chat_id": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "history" not in st.session_state:
    st.session_state.history = load_history()


# ---------- Callbacks ----------
def send_prompt():
    text = st.session_state.prompt.strip()

    if not text:
        st.session_state.warn = True
        return

    st.session_state.warn = False
    st.session_state.editing = None

    st.session_state.messages.append({
        "role": "user",
        "content": text
    })

    st.session_state.prompt = ""
    st.session_state.pending = True


def start_edit(i):
    st.session_state.editing = i
    st.session_state[f"edit_{i}"] = (
        st.session_state.messages[i]["content"]
    )


def cancel_edit():
    st.session_state.editing = None


def save_edit(i):
    text = st.session_state[f"edit_{i}"].strip()

    if not text:
        return

    st.session_state.messages = (
        st.session_state.messages[:i]
        + [
            {
                "role": "user",
                "content": text
            }
        ]
    )

    st.session_state.editing = None
    st.session_state.pending = True


def archive_current():
    """Save current conversation into History."""

    msgs = st.session_state.messages

    if not msgs:
        return

    title = next(
        (
            m["content"]
            for m in msgs
            if m["role"] == "user"
        ),
        "Chat"
    )

    cid = st.session_state.chat_id

    for entry in st.session_state.history:

        if cid is not None and entry["id"] == cid:

            entry["title"] = title
            entry["messages"] = [
                dict(m)
                for m in msgs
            ]

            save_history()
            return

    st.session_state.history.append(
        {
            "id": uuid.uuid4().hex,
            "title": title,
            "messages": [
                dict(m)
                for m in msgs
            ]
        }
    )

    save_history()


def clear_chat():
    """Save conversation then clear screen."""

    archive_current()

    st.session_state.messages = []
    st.session_state.chat_id = None
    st.session_state.editing = None
    st.session_state.pending = False


def load_chat(idx):
    """Open saved chat."""

    archive_current()

    entry = st.session_state.history[idx]

    st.session_state.messages = [
        dict(m)
        for m in entry["messages"]
    ]

    st.session_state.chat_id = entry["id"]
    st.session_state.editing = None
    st.session_state.pending = False


def reset_chat():
    """Start a completely fresh chat."""

    st.session_state.messages = []
    st.session_state.chat_id = None
    st.session_state.editing = None
    st.session_state.pending = False
    st.session_state.prompt = ""
    st.session_state.warn = False
    st.session_state.done = False
    st.session_state.error = None


def delete_history():
    st.session_state.history = []
    st.session_state.chat_id = None
    save_history()


# ---------- Sidebar ----------
with st.sidebar:

    st.markdown("### Chat Tools")

    st.button(
        "Clear chat",
        key="clear_btn",
        on_click=clear_chat
    )

    st.button(
        "Reset chat",
        key="reset_btn",
        on_click=reset_chat
    )

    st.markdown("### History")

    if not st.session_state.history:

        st.markdown(
            '<div class="hist-empty">'
            'No history yet. Cleared chats are saved here.'
            '</div>',
            unsafe_allow_html=True,
        )

    for idx in reversed(
        range(len(st.session_state.history))
    ):

        entry = st.session_state.history[idx]

        title = entry["title"]

        short = (
            title
            if len(title) <= 32
            else title[:32].rstrip() + "…"
        )

        is_open = (
            entry["id"]
            == st.session_state.chat_id
        )

        st.button(
            short,
            key=(
                f"hist_active_{idx}"
                if is_open
                else f"hist_{idx}"
            ),
            on_click=load_chat,
            args=(idx,),
        )

    if st.session_state.history:

        st.button(
            "Delete history",
            key="delete_hist_btn",
            on_click=delete_history
        )


# ---------- Main page ----------
st.title("Gemini AI Chatbot 🤖")

st.write("Ask Gemini anything!")


# ==========================================================
# CHATGPT-STYLE TYPE BAR
# ==========================================================

st.chat_input(
    "Message Gemini...",
    key="prompt",
    on_submit=send_prompt,
)


# ---------- Warning ----------
if st.session_state.warn:

    st.warning(
        "Please enter a prompt to generate a response."
    )


# ---------- Status ----------
status_area = st.container()

with status_area:

    if st.session_state.done:

        st.success(
            "Response generated!"
        )

        st.session_state.done = False

    if st.session_state.error:

        st.error(
            f"Something went wrong: "
            f"{st.session_state.error}"
        )

        st.session_state.error = None


# ---------- Conversation ----------
def render_message(i):

    msg = st.session_state.messages[i]

    with st.chat_message(msg["role"]):

        if (
            msg["role"] == "user"
            and st.session_state.editing == i
        ):

            st.text_area(
                "Edit your message",
                key=f"edit_{i}",
                label_visibility="collapsed",
            )

            b_save, b_cancel, _ = st.columns(
                [2, 1, 1]
            )

            b_save.button(
                "Save & regenerate",
                key=f"save_btn_{i}",
                on_click=save_edit,
                args=(i,),
            )

            b_cancel.button(
                "Cancel",
                key=f"cancel_btn_{i}",
                on_click=cancel_edit
            )

        else:

            st.write(
                msg["content"]
            )

            if msg["role"] == "user":

                st.button(
                    "Edit",
                    key=f"edit_btn_{i}",
                    on_click=start_edit,
                    args=(i,),
                )


# ---------- Create turns ----------
turns = []

for i, m in enumerate(
    st.session_state.messages
):

    if (
        m["role"] == "user"
        or not turns
    ):

        turns.append([i])

    else:

        turns[-1].append(i)


# ---------- Display newest first ----------
for turn in reversed(turns):

    for i in turn:

        render_message(i)


# ==========================================================
# GENERATE GEMINI RESPONSE
# ==========================================================

if st.session_state.pending:

    contents = [

        {
            "role": (
                "user"
                if m["role"] == "user"
                else "model"
            ),

            "parts": [
                {
                    "text": m["content"]
                }
            ],
        }

        for m in st.session_state.messages
    ]

    with status_area:

        with st.spinner(
            "Generate is thinking..."
        ):

            try:

                response = (
                    client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=contents
                    )
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response.text
                    }
                )

                st.session_state.done = True

            except Exception as e:

                st.session_state.error = str(e)

    st.session_state.pending = False

    st.rerun()