import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from env.environment import EmailTriageEnv
from agent.agent import simple_agent

st.set_page_config(page_title="AI Email Intelligence", layout="wide")

# 🔥 BACKGROUND + STYLE
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

.big-title {
    font-size: 40px;
    font-weight: bold;
    color: #22c55e;
}

.card {
    padding: 20px;
    border-radius: 15px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    margin-bottom: 10px;
}

.button {
    background-color: #22c55e;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">📧 AI Email Intelligence Dashboard</p>', unsafe_allow_html=True)

# Session state
if "env" not in st.session_state:
    st.session_state.env = EmailTriageEnv()
    st.session_state.obs = st.session_state.env.reset()

env = st.session_state.env
obs = st.session_state.obs

col1, col2 = st.columns(2)

# LEFT SIDE
with col1:
    st.markdown("### 📩 Incoming Email")

    st.markdown(f"""
    <div class="card">
    <b>Subject:</b> {obs.subject} <br><br>
    <b>Body:</b> {obs.body} <br><br>
    <b>Sender:</b> {obs.sender}
    </div>
    """, unsafe_allow_html=True)

# RIGHT SIDE
with col2:
    st.markdown("### 🤖 AI Analysis")

    if st.button("🚀 Analyze Email"):
        action = simple_agent(obs)
        result = env.step(action)

        summary = obs.body[:60] + "..."
        reply = "Thank you for your email. I will respond shortly."

        st.markdown(f"""
        <div class="card">
        <b>Category:</b> {action.category} <br>
        <b>Priority:</b> {action.priority} <br>
        <b>Tone:</b> {action.tone} <br><br>
        <b>Summary:</b> {summary} <br><br>
        <b>Suggested Reply:</b> {reply}
        </div>
        """, unsafe_allow_html=True)

        st.success(f"🏆 Score: {result.reward}")

        st.session_state.obs = env.reset()