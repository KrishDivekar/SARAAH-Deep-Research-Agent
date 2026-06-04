import os
import streamlit as st
from google import genai
from ddgs import DDGS
import time
import re

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="Saraah — Deep Research",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS injection ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400&display=swap');

/* ── Root palette ── */
:root {
    --bg:        #F0F9FF;
    --bg2:       #E0F2FE;
    --bg3:       #BAE6FD;
    --bg4:       #E6F9FF;
    --border:    rgba(147,197,253,0.18);
    --border2:   rgba(147,197,253,0.30);
    --text:      #0C2340;
    --text2:     #2b6b86;
    --text3:     #5b92a8;
    --accent:    #38BDF8;
    --accent2:   #7DD3FC;
    --accent-dim:rgba(56,189,248,0.12);
    --gold:      #c8b97a;
    --gold-dim:  rgba(200,185,122,0.10);
    --serif:     'Playfair Display', Georgia, serif;
    --sans:      'DM Sans', system-ui, sans-serif;
    --mono:      'DM Mono', monospace;
}

/* ── Global overrides ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background-color: var(--bg) !important;
    font-family: var(--sans) !important;
    color: var(--text) !important;
}

[data-testid="stSidebar"] {
    background-color: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stDecoration"] { display: none !important; }
.block-container { padding-top: 1.6rem !important; max-width: 960px !important; }

/* ── Sidebar inputs ── */
[data-testid="stTextInput"] input {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 13px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-dim) !important;
}
[data-testid="stTextInput"] label { color: var(--text2) !important; font-size: 12px !important; }

/* ── Buttons ── */
[data-testid="stButton"] > button {
    background: var(--accent) !important;
    color: var(--text) !important;
    border: 1px solid rgba(30, 90, 180, 0.95) !important;
    border-radius: 12px !important;
    font-family: var(--sans) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
[data-testid="stButton"] > button:hover {
    background: var(--accent2) !important;
    border-color: rgba(19, 78, 150, 1) !important;
    transform: translateY(-1px) !important;
}

/* ── Text inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: var(--bg2) !important;
    border: 1px solid rgba(30, 90, 180, 0.95) !important;
    border-radius: 14px !important;
    color: var(--text) !important;
    caret-color: var(--text) !important;
    font-family: var(--sans) !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
    resize: none !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: rgba(12, 35, 64, 0.45) !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: rgba(19, 78, 150, 1) !important;
    box-shadow: 0 0 0 4px rgba(56,189,248,0.15) !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label { color: var(--text2) !important; font-size: 13px !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--accent) !important; }
[data-testid="stSpinner"] * { color: var(--text2) !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────-
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:8px 0 20px;">
      <svg width="38" height="38" viewBox="0 0 38 38" fill="none">
        <circle cx="11" cy="22" r="8" stroke="#38BDF8" stroke-width="1.8" fill="none"/>
        <circle cx="27" cy="22" r="8" stroke="#38BDF8" stroke-width="1.8" fill="none"/>
        <path d="M19 22h2" stroke="#38BDF8" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M3 19Q1.5 15 3.5 13" stroke="#38BDF8" stroke-width="1.6" stroke-linecap="round" fill="none"/>
        <path d="M35 19Q36.5 15 34.5 13" stroke="#38BDF8" stroke-width="1.6" stroke-linecap="round" fill="none"/>
        <circle cx="11" cy="22" r="2.5" fill="rgba(56,189,248,0.18)"/>
        <circle cx="27" cy="22" r="2.5" fill="rgba(56,189,248,0.18)"/>
      </svg>
      <div>
        <div style="font-family:'Playfair Display',serif;font-size:20px;font-weight:500;color:#0C2340;line-height:1.1;">Saraah</div>
        <div style="font-size:10px;color:#2b6b86;letter-spacing:0.1em;text-transform:uppercase;">Deep Research</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="background:transparent;border:0;padding:12px 14px 8px;margin-bottom:12px;">
      <div style="font-size:11px;color:#0C2340;font-weight:700;margin-bottom:6px;letter-spacing:0.06em;text-transform:uppercase;">THE SARAAH ARCHITECTURE:</div>
      <div style="font-size:13px;color:#0C2340;line-height:1.6;">
        This deep research system is modeled after an incredibly high standard of intelligence and charm.<br>
        1. <strong>Maximum Brightness:</strong> Designed to match a mind that naturally lights up any room it enters.<br>
        2. <strong>Deep Focus Loop:</strong> Emulates an unmatched ability to listen intently, understand deeply, and care about the finer details.<br>
        3. <strong>Effortless Elegance:</strong> Processes complex, chaotic web data and transforms it into something structured, calm, and beautiful.
      </div>
    </div>
    """, unsafe_allow_html=True)

    api_key = os.environ.get("GEMINI_API_KEY", "")
    supported_models = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
    ]
    model = supported_models[0]

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:11px;color:#2b6b86;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Research depth</p>', unsafe_allow_html=True)
    depth = st.selectbox(
        "Depth",
        ["Standard (5 sources)", "Deep (10 sources)", "Exhaustive (15 sources)"],
        label_visibility="collapsed"
    )
    max_results = {"Standard (5 sources)": 5, "Deep (10 sources)": 10, "Exhaustive (15 sources)": 15}[depth]

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(56,189,248,0.07);border:1px solid rgba(56,189,248,0.15);
                border-radius:10px;padding:12px 14px;margin-top:8px;">
      <div style="font-size:11px;color:#38BDF8;font-weight:500;margin-bottom:6px;">HOW IT WORKS</div>
      <div style="font-size:12px;color:#2b6b86;line-height:1.7;">
        1. Enter your query<br>
        2. Saraah searches the web via DuckDuckGo<br>
        3. The AI engine synthesises a structured answer<br>
        4. Sources are listed below
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="position:fixed;bottom:20px;left:0;width:260px;text-align:center;">
      <span style="font-size:10px;color:#2b6b86;">made by Krish Divekar</span>
    </div>
    """, unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""
if "follow_up" not in st.session_state:
    st.session_state.follow_up = ""
if "query" not in st.session_state:
    st.session_state.query = ""
if "clear_follow_up" not in st.session_state:
    st.session_state.clear_follow_up = False

# ── Top branding row ─────────────────────────────────────────────────────────
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_left:
    st.write("")
with col_center:
    st.markdown("""
    <div style="text-align:center;padding:10px 0 4px;margin-bottom:4px;">
      <svg width="34" height="34" viewBox="0 0 38 38" fill="none" style="margin-bottom:8px;">
        <circle cx="11" cy="22" r="8" stroke="#38BDF8" stroke-width="1.8" fill="none"/>
        <circle cx="27" cy="22" r="8" stroke="#38BDF8" stroke-width="1.8" fill="none"/>
        <path d="M19 22h2" stroke="#38BDF8" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M3 19Q1.5 15 3.5 13" stroke="#38BDF8" stroke-width="1.6" stroke-linecap="round" fill="none"/>
        <path d="M35 19Q36.5 15 34.5 13" stroke="#38BDF8" stroke-width="1.6" stroke-linecap="round" fill="none"/>
      </svg>
      <div style="font-family:'Playfair Display',serif;font-size:18px;font-weight:600;color:#0C2340;line-height:1.1;">
        Saraah
      </div>
      <div style="font-size:11px;color:#2b6b86;letter-spacing:0.12em;text-transform:uppercase;margin-top:4px;">
        Deep Research
      </div>
    </div>
    """, unsafe_allow_html=True)
with col_right:
    if st.button("🗑 Clear history", use_container_width=True, key="clear_history_top"):
        st.session_state.history = []
        st.rerun()

st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("""
    <div style="text-align:left;padding:10px 0 12px;">
      <div style="font-family:'Playfair Display',serif;font-size:clamp(32px,5vw,52px);
                  font-weight:500;color:#0C2340;letter-spacing:-0.02em;line-height:1.1;margin-bottom:8px;">
        Research, deeply.
      </div>
      <div style="font-size:15px;color:#2b6b86;font-weight:300;">
        Ask anything. Saraah searches the web and synthesises verified, sourced answers.
      </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.write("")

st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

# ── Input area ─────────────────────────────────────────────────────────────

def _start_research():
    st.session_state.search_clicked = True

if st.session_state.clear_follow_up:
    st.session_state.follow_up = ""
    st.session_state.clear_follow_up = False

if st.session_state.current_topic:
    query = ""
    follow_up = st.text_input(
        "Ask a follow-up question",
        value=st.session_state.get("follow_up", ""),
        placeholder=f"Ask a follow-up about \"{st.session_state.current_topic}\"",
        label_visibility="collapsed",
        key="follow_up",
        on_change=_start_research,
    )
else:
    follow_up = ""
    query = st.text_input(
        "Your research question",
        value=st.session_state.get("query", ""),
        placeholder="e.g. How does the gut microbiome affect mental health?",
        label_visibility="collapsed",
        key="query",
        on_change=_start_research,
    )

query = str(query or "")
follow_up = str(follow_up or "")

col1, col2, col3 = st.columns([3, 2, 3])
with col2:
    search_clicked = st.button("🔍  Research", use_container_width=True)

search_clicked = search_clicked or st.session_state.search_clicked
if search_clicked:
    st.session_state.search_clicked = False

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# ── Agent functions ────────────────────────────────────────────────────────

def ddg_search(query: str, max_results: int) -> list[dict]:
    """Search DuckDuckGo and return a list of result dicts."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "href":  r.get("href", ""),
                    "body":  r.get("body", ""),
                })
    except Exception as e:
        st.warning(f"Search warning: {e}")
    return results


def build_prompt(base_topic: str, results: list[dict], follow_up: str = "") -> str:
    """Build the synthesis prompt from search results."""
    sources_block = ""
    for i, r in enumerate(results, 1):
        sources_block += f"\n[{i}] {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n"

    follow_up_text = follow_up.strip()
    original_topic = base_topic.strip() or follow_up_text
    current_query = follow_up_text if follow_up_text else original_topic
    follow_up_block = f"\nFOLLOW-UP QUESTION: {follow_up_text}\n" if follow_up_text else ""

    return f"""You are Saraah, an elite deep research intelligence. Using the web search results below, write a comprehensive and well-structured research report answering the user's current question. If this is a follow-up request, treat the follow-up as the current focus and provide fresh insights based only on the latest search results. Do not reuse or repeat the previous response.

ORIGINAL TOPIC: {original_topic}
{follow_up_block}
USER QUERY: {current_query}

WEB SEARCH RESULTS:
{sources_block}

INSTRUCTIONS:
- If a follow-up question is provided, focus only on that follow-up and provide fresh research from these results.
- Do not repeat the previous answer verbatim or reuse prior phrasing.
- Use a clear title (# Title), structured sections (##, ###), and concise, research-backed prose.
- Cite sources inline using the source title and URL.
- Include specific facts, statistics, dates, and named entities from the results.
- Be accurate — only state what is supported by the search results.
- End with a "## Key Takeaways" section containing 4-6 bullet points.
- Write for an intelligent adult reader. Be thorough but concise.
- Do not mention that this is a follow-up in the answer; just answer the question.
- Use the search results as the only factual basis for the response.
"""


def synthesise(client: genai.Client, prompt: str, model: str) -> str:
    """Call the AI service and return the text response."""
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text or ""


def extract_sources(results: list[dict]) -> list[dict]:
    """Return cleaned source list for display."""
    return [{"title": r["title"], "url": r["href"]} for r in results if r.get("href")]


# ── Main research flow ─────────────────────────────────────────────────────
if search_clicked:
    if not api_key:
        st.markdown("""
        <div style="background:rgba(200,100,100,0.08);border:1px solid rgba(200,100,100,0.2);
                    border-radius:12px;padding:16px 20px;color:#e08888;font-size:14px;">
          ⚠️ The AI service is not configured correctly. Please contact the administrator or try again later.
        </div>
        """, unsafe_allow_html=True)
    else:
        query_text = query.strip()
        follow_up_text = follow_up.strip()
        current_topic = st.session_state.get("current_topic", "")

        if query_text and not current_topic:
            current_topic = query_text
            st.session_state.current_topic = current_topic

        if not current_topic and st.session_state.history:
            current_topic = st.session_state.history[-1]["query"]
            st.session_state.current_topic = current_topic

        base_topic = current_topic or query_text

        if not current_topic and not query_text:
            st.markdown("""
            <div style="background:rgba(200,185,122,0.06);border:1px solid rgba(200,185,122,0.2);
                        border-radius:12px;padding:16px 20px;color:#c8b97a;font-size:14px;">
              💬 Please enter a research question or a follow-up question above.
            </div>
            """, unsafe_allow_html=True)
        elif current_topic and not follow_up_text and not query_text:
            st.markdown("""
            <div style="background:rgba(200,185,122,0.06);border:1px solid rgba(200,185,122,0.2);
                        border-radius:12px;padding:16px 20px;color:#c8b97a;font-size:14px;">
              💬 Ask a follow-up question about the current topic.
            </div>
            """, unsafe_allow_html=True)
        else:
            if follow_up_text:
                search_query = follow_up_text
            else:
                search_query = query_text

        with st.spinner("🔍 Searching the web…"):
            try:
                results = ddg_search(search_query, max_results)
            except NameError as e:
                st.error("Search engine function is unavailable. Please contact the administrator.")
                # Ensure `search_query` exists for later diagnostic messages
                try:
                    search_query = follow_up_text or query_text or ""
                except Exception:
                    search_query = ""
                results = []
            except Exception as e:
                st.warning(f"Search warning: {e}")
                # Ensure `search_query` exists in case of downstream formatting
                try:
                    search_query = follow_up_text or query_text or ""
                except Exception:
                    search_query = ""
                results = []

        if not results:
            st.error(f"No search results returned for \"{search_query}\". Try rephrasing your query.")
        else:
            with st.spinner("🧠 Saraah is synthesising your research…"):
                client = genai.Client(api_key=api_key)
                prompt = build_prompt(base_topic, results, follow_up.strip())
                answer = None
                error_message = ""
                for candidate in supported_models:
                    try:
                        answer = synthesise(client, prompt, candidate)
                        model = candidate
                        break
                    except Exception as e:
                        error_message = str(e)
                        if "RESOURCE_EXHAUSTED" in error_message or "429" in error_message or "NOT_FOUND" in error_message or "404" in error_message:
                            continue
                        else:
                            break

                if not answer:
                    if "RESOURCE_EXHAUSTED" in error_message or "429" in error_message:
                        st.markdown(f"""
                        <div style="background:rgba(200,100,100,0.08);border:1px solid rgba(200,100,100,0.2);
                                    border-radius:12px;padding:16px 20px;color:#e08888;font-size:14px;">
                          ❌ AI service quota error: {error_message}<br><br>
                          Please check that your service key has active quota and billing enabled, or retry after a short delay.
                        </div>
                        """, unsafe_allow_html=True)
                    elif "NOT_FOUND" in error_message or "404" in error_message:
                        st.markdown(f"""
                        <div style="background:rgba(200,100,100,0.08);border:1px solid rgba(200,100,100,0.2);
                                    border-radius:12px;padding:16px 20px;color:#e08888;font-size:14px;">
                          ❌ AI service model error: {error_message}<br><br>
                          The app will attempt another available model on the next request.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background:rgba(200,100,100,0.08);border:1px solid rgba(200,100,100,0.2);
                                    border-radius:12px;padding:16px 20px;color:#e08888;font-size:14px;">
                          ❌ AI service error: {error_message}
                        </div>
                        """, unsafe_allow_html=True)

            if answer:
                sources = extract_sources(results)

                # Save to history
                st.session_state.history.append({
                    "query": base_topic,
                    "follow_up": follow_up.strip(),
                    "answer": answer,
                    "sources": sources,
                    "ts": time.strftime("%H:%M"),
                })
                st.session_state.clear_follow_up = True

# ── Render history (newest first) ─────────────────────────────────────────
for item in reversed(st.session_state.history):

    # Query bubble
    st.markdown(f"""
    <div style="display:flex;align-items:flex-start;gap:12px;
                background:var(--bg3);border:1px solid var(--border);
                border-radius:14px;padding:14px 18px;margin-bottom:16px;">
      <div style="width:30px;height:30px;border-radius:50%;background:var(--gold-dim);
                  border:1px solid rgba(200,185,122,0.2);display:flex;align-items:center;
                  justify-content:center;font-size:13px;font-weight:500;color:#c8b97a;
                  flex-shrink:0;line-height:30px;text-align:center;">Q</div>
    <div style="font-size:15px;color:var(--text);padding-top:4px;line-height:1.5;">{item['query']}{' — ' + item['follow_up'] if item.get('follow_up') else ''}</div>
      <div style="margin-left:auto;font-size:11px;color:var(--text2);padding-top:6px;white-space:nowrap;">{item['ts']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Response card header
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid rgba(56,189,248,0.15);
                border-radius:14px 14px 0 0;padding:14px 20px;
                display:flex;align-items:center;justify-content:space-between;
                border-bottom:1px solid rgba(147,197,253,0.06);">
      <div style="display:flex;align-items:center;gap:10px;">
        <svg width="22" height="22" viewBox="0 0 28 28" fill="none">
          <circle cx="8" cy="16" r="6" stroke="#38BDF8" stroke-width="1.5" fill="none"/>
          <circle cx="20" cy="16" r="6" stroke="#38BDF8" stroke-width="1.5" fill="none"/>
          <path d="M14 16h1.5" stroke="#38BDF8" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M2 14Q1 11 2.5 9" stroke="#38BDF8" stroke-width="1.4" stroke-linecap="round" fill="none"/>
          <path d="M26 14Q27 11 25.5 9" stroke="#38BDF8" stroke-width="1.4" stroke-linecap="round" fill="none"/>
        </svg>
        <span style="font-family:'Playfair Display',serif;font-size:15px;color:#38BDF8;font-weight:500;">Saraah</span>
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <div style="width:6px;height:6px;border-radius:50%;background:#38BDF8;
                    animation:pulse 2s ease infinite;"></div>
        <span style="font-size:11px;color:var(--text2);">Research complete</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Response body — render as markdown inside a styled container
    st.markdown("""
    <div style="background:#FFFFFF;border-left:1px solid rgba(56,189,248,0.15);
                border-right:1px solid rgba(56,189,248,0.15);padding:4px 20px 4px;">
    </div>
    """, unsafe_allow_html=True)

    # Streamlit markdown for the actual answer (inside a custom wrapper)
    with st.container():
        st.markdown(f"""
        <div style="background:#FFFFFF;border-left:1px solid rgba(56,189,248,0.15);
                    border-right:1px solid rgba(56,189,248,0.15);
                    padding:20px 24px 8px;
                    font-family:'DM Sans',sans-serif;font-size:15px;line-height:1.8;color:#0C2340;">
        </div>
        """, unsafe_allow_html=True)
        st.markdown(item["answer"])

    # Sources footer
    if item["sources"]:
        source_chips = ""
        for i, s in enumerate(item["sources"][:12], 1):
            title = s["title"][:42] + "…" if len(s["title"]) > 42 else s["title"]
            source_chips += f"""
            <a href="{s['url']}" target="_blank" rel="noopener"
               style="display:inline-flex;align-items:center;gap:6px;
                      font-size:12px;color:#2b6b86;
                      background:rgba(255,255,255,0.04);
                      border:1px solid rgba(147,197,253,0.08);
                      padding:5px 10px;border-radius:6px;text-decoration:none;
                      transition:all 0.15s;">
              <span style="width:16px;height:16px;border-radius:4px;
                           background:rgba(56,189,248,0.12);color:#38BDF8;
                           font-size:10px;font-weight:500;display:inline-flex;
                           align-items:center;justify-content:center;flex-shrink:0;">{i}</span>
              <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:200px;">{title}</span>
            </a>"""

        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid rgba(56,189,248,0.15);
                    border-top:1px solid rgba(147,197,253,0.06);
                    border-radius:0 0 14px 14px;padding:14px 20px 16px;">
          <div style="font-size:11px;font-weight:500;text-transform:uppercase;
                      letter-spacing:0.08em;color:var(--text2);margin-bottom:10px;
                      display:flex;align-items:center;gap:6px;">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
            </svg>
            Sources
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;">{source_chips}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)


