"""
Autonomous AI Cyber Defense Platform – Main Application
"""
import streamlit as st
from datetime import datetime

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Autonomous AI Cyber Defense Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS (cyber dark theme) ─────────────────────────────
st.markdown(
    """
    <style>
    /* ── Global ─────────────────────────────────────────── */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] .stMarkdown { color: #c9d1d9; }
    .stMarkdown { color: #c9d1d9; }
    h1, h2, h3 { color: #58a6ff !important; }
    hr { border-color: #30363d !important; }

    /* ── Sidebar nav items ──────────────────────────────── */
    [data-testid="stSidebarNav"] a {
        color: #8b949e !important;
        text-decoration: none !important;
        padding: 6px 12px !important;
        border-radius: 8px !important;
        transition: all 0.2s !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: #21262d !important;
        color: #58a6ff !important;
    }

    /* ── Buttons ────────────────────────────────────────── */
    .stButton>button {
        background: linear-gradient(135deg, #238636, #2ea043) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px #2ea04366 !important;
        transform: translateY(-1px) !important;
    }

    /* ── Metric cards ───────────────────────────────────── */
    [data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 12px;
    }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }
    [data-testid="stMetricValue"] { color: #58a6ff !important; }

    /* ── DataFrame ──────────────────────────────────────── */
    .stDataFrame { border-radius: 8px; }

    /* ── Tabs ───────────────────────────────────────────── */
    .stTabs [data-baseweb="tab"] {
        color: #8b949e;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #58a6ff !important;
        border-bottom-color: #58a6ff !important;
    }

    /* ── Toast / alerts ─────────────────────────────────── */
    .stAlert { border-radius: 8px; }

    /* ── Glow animation ─────────────────────────────────── */
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px #58a6ff33; }
        50% { box-shadow: 0 0 20px #58a6ff66; }
    }
    .glow-box { animation: glow 3s infinite; }

    /* ── Scrollbar ──────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Initialise database + seed admin ──────────────────────────
from core.database import init_db
from auth.authentication import seed_default_admin

init_db()
seed_default_admin()

# ── Session defaults ──────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "active_sessions" not in st.session_state:
    st.session_state["active_sessions"] = 1

# ── Login gate ────────────────────────────────────────────────
if not st.session_state["authenticated"]:
    from ui.login import show_login
    show_login()
    st.stop()

# ── Authenticated UI ──────────────────────────────────────────
user = st.session_state["user"]

# Sidebar
with st.sidebar:
    # Logo / header
    st.markdown(
        """
        <div style="text-align:center; padding:1rem 0;">
            <div style="font-size:3rem">🛡️</div>
            <div style="color:#58a6ff; font-size:1.1rem; font-weight:700;">
                AI Cyber Defense
            </div>
            <div style="color:#8b949e; font-size:0.75rem;">Platform v1.0</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # User info
    st.markdown(f"**👤 {user['username']}** ({user['role']})")
    st.markdown(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📡 Live Monitoring",
            "🧠 Threat Detection",
            "📈 Analytics",
            "🗂️ Incident Center",
            "📑 Reports",
            "🤖 AI Assistant",
            "⚙️ Settings",
            "🔧 Admin Panel",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        from core.database import log_audit
        log_audit(user["username"], "logout", "")
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.rerun()

# ── Page router ───────────────────────────────────────────────
if page == "📊 Dashboard":
    from ui.dashboard import show_dashboard
    show_dashboard()
elif page == "📡 Live Monitoring":
    from ui.monitoring import show_monitoring
    show_monitoring()
elif page == "🧠 Threat Detection":
    from ui.detection import show_detection
    show_detection()
elif page == "📈 Analytics":
    from ui.analytics import show_analytics
    show_analytics()
elif page == "🗂️ Incident Center":
    from ui.incidents import show_incidents
    show_incidents()
elif page == "📑 Reports":
    from ui.reports import show_reports
    show_reports()
elif page == "🤖 AI Assistant":
    from ui.chatbot import show_chatbot
    show_chatbot()
elif page == "⚙️ Settings":
    from ui.settings import show_settings
    show_settings()
elif page == "🔧 Admin Panel":
    from ui.admin import show_admin
    show_admin()
