import streamlit as st
import anthropic
import json
from datetime import datetime
 
# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Synaptrix – AI Email Intelligence",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
 
/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e6f0;
    min-width: 240px !important;
    max-width: 240px !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}
 
/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }
 
/* ── Sidebar nav items ── */
.sidebar-logo {
    display: flex; align-items: center; gap: 10px;
    padding: 18px 16px 14px;
    font-size: 15px; font-weight: 600;
    border-bottom: 1px solid #e2e6f0;
    color: #11141f;
}
.logo-mark {
    width: 30px; height: 30px; border-radius: 8px;
    background: #1a6ef5; color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
}
.sidebar-section-label {
    font-size: 10.5px; font-weight: 600; color: #9ca3af;
    text-transform: uppercase; letter-spacing: 0.8px;
    padding: 14px 18px 4px;
}
.nav-link {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 16px; border-radius: 8px; margin: 1px 8px;
    cursor: pointer; font-size: 13.5px; color: #6b7280;
    text-decoration: none; transition: all 0.15s;
}
.nav-link:hover { background: #f0f2f8; color: #11141f; }
.nav-link.active { background: #e8f0fe; color: #1a6ef5; font-weight: 500; }
.nav-badge {
    margin-left: auto; background: #1a6ef5; color: white;
    border-radius: 10px; font-size: 10px; font-weight: 600;
    padding: 1px 6px;
}
.nav-badge.gray { background: #f0f2f8; color: #6b7280; }
.sidebar-divider { height: 1px; background: #e2e6f0; margin: 10px 8px; }
 
/* ── Compose button ── */
.stButton > button {
    background: #1a6ef5 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13.5px !important; font-weight: 500 !important;
    padding: 9px 16px !important; width: 100% !important;
    cursor: pointer !important; transition: 0.15s !important;
}
.stButton > button:hover { background: #1251c0 !important; }
 
/* ── Top bar ── */
.topbar {
    background: #ffffff; border-bottom: 1px solid #e2e6f0;
    padding: 12px 24px; display: flex; align-items: center; gap: 16px;
    position: sticky; top: 0; z-index: 100;
}
.topbar-title { font-size: 17px; font-weight: 600; color: #11141f; flex: 1; }
.topbar-stats {
    display: flex; gap: 20px; font-size: 12px; color: #6b7280;
}
.topbar-stat strong { color: #11141f; font-size: 14px; font-weight: 600; }
 
/* ── Email cards ── */
.email-card {
    background: #fff; border: 1px solid #e2e6f0;
    border-radius: 10px; padding: 14px 16px;
    margin-bottom: 8px; cursor: pointer;
    transition: all 0.15s; position: relative;
}
.email-card:hover { border-color: #1a6ef5; box-shadow: 0 2px 8px rgba(26,110,245,0.08); }
.email-card.selected { border-color: #1a6ef5; background: #f0f5ff; }
.email-card.unread { border-left: 3px solid #1a6ef5; }
.email-header { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.email-avatar {
    width: 34px; height: 34px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600; flex-shrink: 0;
}
.email-from { font-size: 13px; color: #6b7280; flex: 1; }
.email-time { font-size: 11.5px; color: #9ca3af; }
.email-subject { font-size: 13.5px; font-weight: 500; color: #11141f; margin-bottom: 3px; }
.email-preview { font-size: 12px; color: #9ca3af; }
.email-tag {
    display: inline-block; font-size: 10.5px; padding: 2px 8px;
    border-radius: 6px; font-weight: 500; margin-top: 6px;
}
.tag-meeting { background: #dbeafe; color: #1d4ed8; }
.tag-urgent  { background: #fef2f2; color: #dc2626; }
.tag-follow  { background: #dcfce7; color: #16a34a; }
.tag-update  { background: #ede9fe; color: #6d28d9; }
.tag-info    { background: #fef3c7; color: #b45309; }
 
/* ── AI Analysis cards ── */
.analysis-panel {
    background: #fff; border: 1px solid #e2e6f0;
    border-radius: 12px; padding: 16px;
    margin-bottom: 12px;
}
.analysis-panel h4 {
    font-size: 11px; font-weight: 600; color: #9ca3af;
    text-transform: uppercase; letter-spacing: 0.6px;
    margin-bottom: 12px;
}
.intel-card {
    background: #f7f8fc; border-radius: 8px;
    padding: 10px 12px; margin-bottom: 8px;
}
.intel-row { display: flex; align-items: center; gap: 8px; }
.intel-icon {
    width: 24px; height: 24px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; flex-shrink: 0;
}
.intel-label { font-size: 12.5px; color: #11141f; font-weight: 500; }
.intel-sub { font-size: 11px; color: #6b7280; }
.conf-row { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
.conf-bar {
    flex: 1; height: 4px; border-radius: 2px;
    background: #e2e6f0; overflow: hidden;
}
.conf-fill { height: 100%; border-radius: 2px; background: #10b981; }
.conf-pct { font-size: 11px; color: #6b7280; }
 
/* ── Chat bubbles ── */
.chat-container {
    display: flex; flex-direction: column;
    gap: 10px; max-height: 380px;
    overflow-y: auto; padding: 4px 0;
}
.bubble-bot, .bubble-user {
    max-width: 88%; padding: 9px 13px;
    border-radius: 12px; font-size: 13px; line-height: 1.55;
}
.bubble-bot {
    background: #f0f2f8; color: #11141f;
    border-bottom-left-radius: 4px; align-self: flex-start;
}
.bubble-user {
    background: #1a6ef5; color: white;
    border-bottom-right-radius: 4px; align-self: flex-end;
}
.bubble-sender { font-size: 10.5px; color: #9ca3af; margin-bottom: 3px; }
 
/* ── Stat mini-cards ── */
.stat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 14px; }
.stat-mini {
    background: #f7f8fc; border-radius: 8px;
    padding: 10px 12px;
}
.stat-mini .val { font-size: 22px; font-weight: 600; color: #11141f; }
.stat-mini .lbl { font-size: 11px; color: #9ca3af; margin-top: 2px; }
.stat-mini .delta { font-size: 10.5px; color: #10b981; margin-top: 1px; }
 
/* ── Streamlit overrides ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 8px !important;
    border: 1px solid #e2e6f0 !important;
    font-size: 13px !important;
}
.stTextArea > div > div > textarea:focus,
.stTextInput > div > div > input:focus {
    border-color: #1a6ef5 !important;
    box-shadow: 0 0 0 2px rgba(26,110,245,0.15) !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #f0f2f8; border-radius: 8px; padding: 3px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important; font-size: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #6b7280 !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important; color: #11141f !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 12px 0 0 !important; }
div[data-testid="column"] { padding: 0 8px !important; }
</style>
""", unsafe_allow_html=True)
 
 
# ── Sample email data ──────────────────────────────────────────────────────────
EMAILS = [
    {
        "id": 0, "from": "boss@company.com", "subject": "Meeting Tomorrow at 10 AM",
        "preview": "Please attend the all-hands meeting tomorrow. Agenda includes Q2 review…",
        "body": "Please attend the all-hands meeting tomorrow at 10 AM. The agenda includes Q2 review, roadmap updates, and team announcements. Your presence is required.",
        "time": "4:28 PM", "tag": "Meeting", "tag_class": "tag-meeting",
        "avatar_bg": "#dbeafe", "avatar_color": "#1d4ed8", "unread": True,
        "intent": "Meeting Request", "priority": "High",
        "tone": "Professional, Directive", "conf": 94,
        "reply_time": "Within 2 hours",
    },
    {
        "id": 1, "from": "sarah@client.io", "subject": "🚨 Production issue — needs fix",
        "preview": "Our payment service is down affecting 2,000+ users. Please escalate…",
        "body": "Our payment service has been down since 3 PM, affecting 2,000+ users. This is a critical issue. Please escalate immediately and provide an ETA for resolution.",
        "time": "2:51 PM", "tag": "Urgent", "tag_class": "tag-urgent",
        "avatar_bg": "#fce7f3", "avatar_color": "#be185d", "unread": True,
        "intent": "Urgent Issue / Escalation", "priority": "Critical",
        "tone": "Alarmed, Urgent", "conf": 99,
        "reply_time": "Immediately",
    },
    {
        "id": 2, "from": "mike@team.co", "subject": "Re: Design review feedback",
        "preview": "Thanks for the notes! I've updated the mockups and added the animations…",
        "body": "Thanks for the detailed notes! I've updated the mockups based on your feedback, added the animations you requested, and improved the mobile layout significantly.",
        "time": "11:22 AM", "tag": "Follow-up", "tag_class": "tag-follow",
        "avatar_bg": "#dcfce7", "avatar_color": "#15803d", "unread": False,
        "intent": "Collaboration / Update", "priority": "Medium",
        "tone": "Friendly, Collaborative", "conf": 88,
        "reply_time": "Within 24 hours",
    },
    {
        "id": 3, "from": "github@github.com", "subject": "[Synaptrix] PR #42 merged",
        "preview": "Pull request 'Add AI analysis endpoint' was merged into main…",
        "body": "Pull request 'Add AI analysis endpoint' was successfully merged into main by krithu2006. All CI checks passed.",
        "time": "9:05 AM", "tag": "Update", "tag_class": "tag-update",
        "avatar_bg": "#ede9fe", "avatar_color": "#6d28d9", "unread": True,
        "intent": "Automated Notification", "priority": "Low",
        "tone": "Neutral, Automated", "conf": 99,
        "reply_time": "No reply needed",
    },
    {
        "id": 4, "from": "newsletter@techdigest.io", "subject": "This week in AI",
        "preview": "The AI landscape shifted again this week. Claude 4, GPT-5, and what's next…",
        "body": "The AI landscape shifted again this week. Major releases from Anthropic and OpenAI, plus open-source breakthroughs from Meta and Mistral.",
        "time": "Yesterday", "tag": "Newsletter", "tag_class": "tag-info",
        "avatar_bg": "#fef3c7", "avatar_color": "#b45309", "unread": False,
        "intent": "Newsletter", "priority": "Low",
        "tone": "Informational", "conf": 97,
        "reply_time": "No reply needed",
    },
]
 
 
# ── Session state ──────────────────────────────────────────────────────────────
if "selected_email" not in st.session_state:
    st.session_state.selected_email = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hi! I'm your Synaptrix AI assistant. I can help you draft replies, summarize threads, set up automation rules, and more. What can I do for you?"}
    ]
if "analysis_chat" not in st.session_state:
    st.session_state.analysis_chat = []
 
 
# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-mark">✉</div>
        Synaptrix
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown("<div style='padding: 12px 8px 4px;'>", unsafe_allow_html=True)
    if st.button("✏  Compose New Email"):
        st.session_state.chat_history.append({
            "role": "user", "content": "Help me compose a new professional email."
        })
 
    st.markdown("""
    <div class="sidebar-section-label">Mailbox</div>
    <a class="nav-link active">📥 Inbox <span class="nav-badge">12</span></a>
    <a class="nav-link">📤 Sent <span class="nav-badge gray">48</span></a>
    <a class="nav-link">📝 Drafts <span class="nav-badge gray">3</span></a>
    <a class="nav-link">⭐ Starred <span class="nav-badge gray">7</span></a>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section-label">AI Labels</div>
    <a class="nav-link">🔵 Meetings <span class="nav-badge gray">5</span></a>
    <a class="nav-link">🔴 Urgent <span class="nav-badge gray">2</span></a>
    <a class="nav-link">🟢 Follow-up <span class="nav-badge gray">8</span></a>
    <a class="nav-link">🟣 Updates <span class="nav-badge gray">14</span></a>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section-label">Automation</div>
    <a class="nav-link">⚡ Active Rules</a>
    <a class="nav-link">📊 Analytics</a>
    <a class="nav-link">⚙️ Settings</a>
    """, unsafe_allow_html=True)
 
 
# ── Main layout: email list | AI panel ────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-title">📥 Inbox</div>
    <div class="topbar-stats">
        <div><strong>247</strong><br>emails this week</div>
        <div><strong>94%</strong><br>AI accuracy</div>
        <div><strong>18m</strong><br>avg. reply time</div>
    </div>
</div>
""", unsafe_allow_html=True)
 
col_emails, col_ai = st.columns([1.1, 1], gap="small")
 
# ── Left: Email list ────────────────────────────────────────────────────────
with col_emails:
    st.markdown("<div style='padding: 16px 8px 8px;'>", unsafe_allow_html=True)
 
    # Filter chips (purely cosmetic here — extend with st.session_state filter)
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        st.markdown("<span style='font-size:12px;padding:5px 10px;border-radius:20px;background:#e8f0fe;color:#1a6ef5;font-weight:500;display:inline-block;'>All</span>", unsafe_allow_html=True)
    with fc2:
        st.markdown("<span style='font-size:12px;padding:5px 10px;border-radius:20px;border:1px solid #e2e6f0;color:#6b7280;display:inline-block;'>Unread</span>", unsafe_allow_html=True)
    with fc3:
        st.markdown("<span style='font-size:12px;padding:5px 10px;border-radius:20px;border:1px solid #e2e6f0;color:#6b7280;display:inline-block;'>Meetings</span>", unsafe_allow_html=True)
    with fc4:
        st.markdown("<span style='font-size:12px;padding:5px 10px;border-radius:20px;border:1px solid #e2e6f0;color:#6b7280;display:inline-block;'>Urgent</span>", unsafe_allow_html=True)
 
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
 
    for email in EMAILS:
        selected_class = "selected" if email["id"] == st.session_state.selected_email else ""
        unread_class = "unread" if email["unread"] else ""
        subject_weight = "600" if email["unread"] else "500"
 
        st.markdown(f"""
        <div class="email-card {selected_class} {unread_class}">
            <div class="email-header">
                <div class="email-avatar" style="background:{email['avatar_bg']};color:{email['avatar_color']};">
                    {email['from'][0].upper()}
                </div>
                <span class="email-from">{email['from']}</span>
                <span class="email-time">{email['time']}</span>
            </div>
            <div class="email-subject" style="font-weight:{subject_weight};">{email['subject']}</div>
            <div class="email-preview">{email['preview']}</div>
            <span class="email-tag {email['tag_class']}">{email['tag']}</span>
        </div>
        """, unsafe_allow_html=True)
 
        if st.button(f"Open", key=f"email_{email['id']}", help=email["subject"]):
            st.session_state.selected_email = email["id"]
            # Auto-add analysis message
            e = email
            st.session_state.analysis_chat = [
                {"role": "assistant", "content": f"**{e['subject']}**\n\nFrom: `{e['from']}`\n\n{e['body']}\n\n---\n✦ *Intent detected: {e['intent']} · Priority: {e['priority']}*"}
            ]
            st.rerun()
 
    st.markdown("</div>", unsafe_allow_html=True)
 
 
# ── Right: AI Panel ──────────────────────────────────────────────────────────
with col_ai:
    st.markdown("<div style='padding: 16px 8px 8px;'>", unsafe_allow_html=True)
 
    email = EMAILS[st.session_state.selected_email]
 
    # Header
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
        <div style="width:8px;height:8px;border-radius:50%;background:#10b981;box-shadow:0 0 0 2px #d1fae5;"></div>
        <span style="font-size:14px;font-weight:600;color:#11141f;">AI Assistant</span>
        <span style="margin-left:auto;font-size:11px;color:#9ca3af;">{email['from']}</span>
    </div>
    """, unsafe_allow_html=True)
 
    tab_analysis, tab_chat, tab_stats = st.tabs(["✦ Analysis", "💬 Chat", "📊 Stats"])
 
    # ── ANALYSIS TAB ──────────────────────────────────────────────────────
    with tab_analysis:
        st.markdown(f"""
        <div class="analysis-panel">
            <h4>Email Intelligence</h4>
            <div class="intel-card">
                <div class="intel-row">
                    <div class="intel-icon" style="background:#dbeafe;color:#1d4ed8;">🎯</div>
                    <div>
                        <div class="intel-label">{email['intent']}</div>
                        <div class="intel-sub">Priority: {email['priority']}</div>
                    </div>
                </div>
                <div class="conf-row">
                    <div class="conf-bar"><div class="conf-fill" style="width:{email['conf']}%;"></div></div>
                    <span class="conf-pct">{email['conf']}% confidence</span>
                </div>
            </div>
            <div class="intel-card">
                <div class="intel-row">
                    <div class="intel-icon" style="background:#dcfce7;color:#15803d;">💬</div>
                    <div>
                        <div class="intel-label">Tone: {email['tone']}</div>
                        <div class="intel-sub">Sender: {email['from'].split('@')[0].capitalize()}</div>
                    </div>
                </div>
            </div>
            <div class="intel-card">
                <div class="intel-row">
                    <div class="intel-icon" style="background:#fef9c3;color:#a16207;">⏱</div>
                    <div>
                        <div class="intel-label">Suggested reply time</div>
                        <div class="intel-sub">{email['reply_time']}</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
 
        # Quick action chips
        st.markdown("<div style='font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;'>Quick Actions</div>", unsafe_allow_html=True)
        qa1, qa2 = st.columns(2)
        with qa1:
            if st.button("✉ Draft Reply", key="qa_draft"):
                msg = f"Draft a professional reply to this email:\n\nSubject: {email['subject']}\nFrom: {email['from']}\nBody: {email['body']}"
                st.session_state.chat_history.append({"role": "user", "content": msg})
                st.session_state.selected_tab = "chat"
                st.rerun()
            if st.button("✨ Summarize", key="qa_sum"):
                msg = f"Summarize this email concisely: {email['body']}"
                st.session_state.chat_history.append({"role": "user", "content": msg})
                st.rerun()
        with qa2:
            if st.button("📅 Calendar", key="qa_cal"):
                msg = f"Help me add this to my calendar: {email['subject']} from {email['from']}"
                st.session_state.chat_history.append({"role": "user", "content": msg})
                st.rerun()
            if st.button("💡 Prep Tips", key="qa_prep"):
                msg = f"What should I prepare for or know about this email: {email['body']}"
                st.session_state.chat_history.append({"role": "user", "content": msg})
                st.rerun()
 
        # Mini analysis chat
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        if not st.session_state.analysis_chat:
            st.session_state.analysis_chat = [
                {"role": "assistant", "content": f"**{email['subject']}**\n\nThis email from `{email['from']}` is classified as **{email['intent']}** with **{email['priority']}** priority.\n\n*{email['body'][:120]}…*"}
            ]
        for msg in st.session_state.analysis_chat[-3:]:
            if msg["role"] == "assistant":
                st.markdown(f"<div class='bubble-sender'>✦ Synaptrix AI</div><div class='bubble-bot'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:right;'><div class='bubble-user' style='display:inline-block;'>{msg['content']}</div></div>", unsafe_allow_html=True)
 
        analysis_input = st.text_input("Ask about this email…", key="analysis_input", placeholder="e.g. What's the urgency level?", label_visibility="collapsed")
        if analysis_input:
            st.session_state.analysis_chat.append({"role": "user", "content": analysis_input})
            with st.spinner(""):
                try:
                    client = anthropic.Anthropic()
                    response = client.messages.create(
                        model="claude-opus-4-5",
                        max_tokens=500,
                        system=f"You are Synaptrix AI analyzing this email. Subject: {email['subject']}. From: {email['from']}. Body: {email['body']}. Be concise.",
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.analysis_chat]
                    )
                    reply = response.content[0].text
                except Exception:
                    reply = f"Analysis: This email is a **{email['intent']}** from {email['from']} with **{email['priority']}** priority. {email['tone']} tone detected."
                st.session_state.analysis_chat.append({"role": "assistant", "content": reply})
            st.rerun()
 
    # ── CHAT TAB ────────────────────────────────────────────────────────────
    with tab_chat:
        # Render chat history
        chat_html = "<div class='chat-container'>"
        for msg in st.session_state.chat_history:
            if msg["role"] == "assistant":
                chat_html += f"<div><div class='bubble-sender'>✦ Synaptrix AI</div><div class='bubble-bot'>{msg['content']}</div></div>"
            else:
                chat_html += f"<div style='text-align:right;'><div class='bubble-user' style='display:inline-block;'>{msg['content']}</div></div>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)
 
        # Suggested prompts
        if len(st.session_state.chat_history) <= 1:
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            sp1, sp2 = st.columns(2)
            with sp1:
                if st.button("Draft a reply to my boss", key="sp1"):
                    st.session_state.chat_history.append({"role": "user", "content": "Draft a professional reply to the meeting email from my boss."})
                    st.rerun()
            with sp2:
                if st.button("Set up auto-reply rules", key="sp2"):
                    st.session_state.chat_history.append({"role": "user", "content": "Help me set up automation rules for my inbox."})
                    st.rerun()
 
        # Chat input
        user_input = st.chat_input("Ask anything about your emails…")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner(""):
                try:
                    client = anthropic.Anthropic()
                    messages_to_send = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.chat_history
                    ]
                    response = client.messages.create(
                        model="claude-opus-4-5",
                        max_tokens=800,
                        system=(
                            "You are Synaptrix AI, an intelligent email assistant. "
                            "Help users manage their inbox, draft replies, summarize emails, "
                            "and set up automations. Be concise, friendly, and professional. "
                            f"Context: User is currently viewing an email with subject '{email['subject']}' from {email['from']}."
                        ),
                        messages=messages_to_send,
                    )
                    reply = response.content[0].text
                except Exception as ex:
                    reply = f"I'm ready to help with your emails! (Ensure your `ANTHROPIC_API_KEY` is set. Error: {str(ex)[:80]})"
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()
 
        if st.button("🗑 Clear chat", key="clear_chat"):
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Chat cleared. How can I help you?"}
            ]
            st.rerun()
 
    # ── STATS TAB ──────────────────────────────────────────────────────────
    with tab_stats:
        st.markdown("""
        <div class="stat-grid">
            <div class="stat-mini"><div class="val">247</div><div class="lbl">Emails this week</div><div class="delta">↑ 12%</div></div>
            <div class="stat-mini"><div class="val">94%</div><div class="lbl">AI accuracy</div><div class="delta">↑ 3%</div></div>
            <div class="stat-mini"><div class="val">18m</div><div class="lbl">Avg reply time</div><div class="delta">↓ 4m saved</div></div>
        </div>
        """, unsafe_allow_html=True)
 
        st.markdown("<div style='font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:10px;'>Category Breakdown</div>", unsafe_allow_html=True)
 
        import streamlit as st2
        categories = {"Meetings": 42, "Urgent": 23, "Updates": 68, "Newsletters": 89, "Other": 25}
        for cat, val in categories.items():
            pct = int(val / 89 * 100)
            colors = {"Meetings": "#1a6ef5", "Urgent": "#ef4444", "Updates": "#7c3aed", "Newsletters": "#f59e0b", "Other": "#6b7280"}
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <div style="width:80px;font-size:11.5px;color:#6b7280;text-align:right;">{cat}</div>
                <div style="flex:1;height:16px;background:#f0f2f8;border-radius:4px;overflow:hidden;">
                    <div style="width:{pct}%;height:100%;background:{colors[cat]};border-radius:4px;"></div>
                </div>
                <div style="width:24px;font-size:11px;font-weight:600;color:#11141f;">{val}</div>
            </div>
            """, unsafe_allow_html=True)
 
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:10px;'>Top Senders</div>", unsafe_allow_html=True)
 
        senders = [
            ("boss@company.com", 38, "#dbeafe", "#1d4ed8"),
            ("github@github.com", 54, "#ede9fe", "#6d28d9"),
            ("sarah@client.io", 21, "#fce7f3", "#be185d"),
            ("team@notion.so", 12, "#fef3c7", "#b45309"),
        ]
        for email_addr, count, bg, color in senders:
            initial = email_addr[0].upper()
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:0.5px solid #e2e6f0;">
                <div style="width:28px;height:28px;border-radius:50%;background:{bg};color:{color};display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;">{initial}</div>
                <div style="flex:1;font-size:12.5px;color:#11141f;">{email_addr}</div>
                <div style="font-size:12px;color:#6b7280;">{count} emails</div>
            </div>
            """, unsafe_allow_html=True)
 
    st.markdown("</div>", unsafe_allow_html=True)
