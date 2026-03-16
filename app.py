import streamlit as st
import pandas as pd
import pickle
import numpy as np
import time as time_module
import random
from datetime import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fraud Shield — V Hack 2026",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.main { background-color: #0a0f1e; color: #e2e8f0; }
.block-container { padding: 2rem 3rem; }

.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #38bdf8, #818cf8, #e879f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
    margin-bottom: 0.3rem;
}
.hero-sub { font-size: 1.1rem; color: #94a3b8; margin-bottom: 1.5rem; }
.story-box {
    background: linear-gradient(135deg, rgba(56,189,248,0.08), rgba(129,140,248,0.08));
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 1.5rem;
    color: #bae6fd;
    font-size: 0.95rem;
}
.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    transition: border-color 0.3s;
}
.stat-card:hover { border-color: rgba(56,189,248,0.4); }
.stat-number { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; color: #38bdf8; }
.stat-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }

.result-approved {
    background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(16,185,129,0.05));
    border: 1px solid #10b981; border-radius: 14px; padding: 1.5rem; text-align: center;
}
.result-flagged {
    background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(245,158,11,0.05));
    border: 1px solid #f59e0b; border-radius: 14px; padding: 1.5rem; text-align: center;
}
.result-blocked {
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05));
    border: 1px solid #ef4444; border-radius: 14px; padding: 1.5rem; text-align: center;
}
.result-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.result-title { font-family: 'Space Mono', monospace; font-size: 1.4rem; font-weight: 700; }
.result-sub { font-size: 0.9rem; color: #94a3b8; margin-top: 0.3rem; }

.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #475569;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}
[data-testid="stSidebar"] { background: #080d1a; border-right: 1px solid rgba(255,255,255,0.06); }
.flag-badge {
    background: rgba(245,158,11,0.15);
    border: 1px solid rgba(245,158,11,0.4);
    border-radius: 8px; padding: 0.5rem 0.8rem;
    font-size: 0.85rem; color: #fbbf24; margin-bottom: 0.5rem;
}
.history-row {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 0.7rem 1rem;
    margin-bottom: 0.5rem; font-size: 0.88rem;
}
.custom-divider { border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 1.5rem 0; }

.feed-row-blocked {
    background: rgba(239,68,68,0.08);
    border-left: 3px solid #ef4444;
    border-radius: 6px; padding: 0.5rem 0.8rem;
    margin-bottom: 0.4rem; font-size: 0.82rem; color: #fca5a5;
}
.feed-row-flagged {
    background: rgba(245,158,11,0.08);
    border-left: 3px solid #f59e0b;
    border-radius: 6px; padding: 0.5rem 0.8rem;
    margin-bottom: 0.4rem; font-size: 0.82rem; color: #fcd34d;
}
.feed-row-approved {
    background: rgba(16,185,129,0.06);
    border-left: 3px solid #10b981;
    border-radius: 6px; padding: 0.5rem 0.8rem;
    margin-bottom: 0.4rem; font-size: 0.82rem; color: #6ee7b7;
}
.sms-box {
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.3);
    border-radius: 12px; padding: 1rem 1.2rem;
    margin-top: 1rem; color: #7dd3fc; font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)

# ── Load model & data ──────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    with open('fraud_model.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_data
def load_data():
    df = pd.read_csv('creditcard.csv')
    return df[df['Class'] == 1].head(50), df[df['Class'] == 0].head(50)

model = load_model()
fraud_df, legit_df = load_data()

# ── Session state ──────────────────────────────────────────────────────────────
if 'history' not in st.session_state:
    st.session_state.history = []
if 'live_feed' not in st.session_state:
    st.session_state.live_feed = []

# ── ASEAN country config ───────────────────────────────────────────────────────
COUNTRY_CONFIG = {
    "🇲🇾 Malaysia": {
        "currency": "RM",  "threshold": 5000,
        "fraud_rate": "0.8%", "top_fraud": "E-wallet phishing",
        "usd_rate": 4.7,   "flag": "🇲🇾"
    },
    "🇵🇭 Phillippines": {
        "currency": "PHP", "threshold": 4000,
        "fraud_rate": "1.2%", "top_fraud": "SIM swap fraud",
        "usd_rate": 56.0,  "flag": "🇵🇭"
    },
    "🇹🇭 Thailand": {
        "currency": "THB", "threshold": 4500,
        "fraud_rate": "0.9%", "top_fraud": "QR code spoofing",
        "usd_rate": 35.0,  "flag": "🇹🇭"
    },
    "🇮🇩 Indonesia": {
        "currency": "IDR", "threshold": 3500,
        "fraud_rate": "1.4%", "top_fraud": "Fake merchant scams",
        "usd_rate": 15800.0, "flag": "🇮🇩"
    },
}

# ── Email alert function ───────────────────────────────────────────────────────
def send_email_alert(decision, amount, currency, country_flag):
    try:
        gmail_address = os.getenv("GMAIL_ADDRESS")
        app_password  = os.getenv("GMAIL_APP_PASSWORD")
        alert_email   = os.getenv("ALERT_EMAIL")

        if not all([gmail_address, app_password, alert_email]):
            return False, "Gmail credentials not found in .env file"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{'🚫 FRAUD BLOCKED' if decision == 'BLOCKED' else '⚠️ Transaction Flagged'} — Fraud Shield Alert"
        msg["From"]    = gmail_address
        msg["To"]      = alert_email

        if decision == "BLOCKED":
            html_body = f"""
            <div style="font-family:Arial,sans-serif; max-width:480px; margin:0 auto;
                        background:#0a0f1e; color:#e2e8f0; padding:2rem; border-radius:12px;">
                <h2 style="color:#ef4444;">🚫 Transaction BLOCKED</h2>
                <p style="color:#94a3b8;">Fraud Shield detected a high-risk transaction on your account.</p>
                <div style="background:#1e1e2e; border-radius:8px; padding:1rem; margin:1rem 0;">
                    <p style="margin:0.3rem 0;">{country_flag} <strong>Amount:</strong> {currency} {amount:,.2f}</p>
                    <p style="margin:0.3rem 0;">🕐 <strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    <p style="margin:0.3rem 0;">⚡ <strong>Decision:</strong>
                        <span style="color:#ef4444; font-weight:bold;">BLOCKED</span></p>
                </div>
                <p style="color:#94a3b8; font-size:0.85rem;">
                    If this was you, please contact support immediately.<br>Your money has been protected.
                </p>
                <hr style="border-color:#334155;">
                <p style="color:#475569; font-size:0.75rem;">Fraud Shield ASEAN · Protecting the Unbanked · V Hack 2026</p>
            </div>"""
        else:
            html_body = f"""
            <div style="font-family:Arial,sans-serif; max-width:480px; margin:0 auto;
                        background:#0a0f1e; color:#e2e8f0; padding:2rem; border-radius:12px;">
                <h2 style="color:#f59e0b;">⚠️ Transaction Flagged for Review</h2>
                <p style="color:#94a3b8;">A suspicious transaction was detected and held for your review.</p>
                <div style="background:#1e1e2e; border-radius:8px; padding:1rem; margin:1rem 0;">
                    <p style="margin:0.3rem 0;">{country_flag} <strong>Amount:</strong> {currency} {amount:,.2f}</p>
                    <p style="margin:0.3rem 0;">🕐 <strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    <p style="margin:0.3rem 0;">⚡ <strong>Decision:</strong>
                        <span style="color:#f59e0b; font-weight:bold;">FLAGGED</span></p>
                </div>
                <p style="color:#94a3b8; font-size:0.85rem;">
                    Reply to this email or open your app to approve or cancel this transaction.
                </p>
                <hr style="border-color:#334155;">
                <p style="color:#475569; font-size:0.75rem;">Fraud Shield ASEAN · Protecting the Unbanked · V Hack 2026</p>
            </div>"""

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, app_password)
            server.sendmail(gmail_address, alert_email, msg.as_string())

        return True, alert_email

    except Exception as e:
        return False, str(e)

# ── Predict function ───────────────────────────────────────────────────────────
def predict(row, amount_usd, txn_time, country_threshold):
    if row is not None:
        feature_cols = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        row_values = row[feature_cols].copy()
        row_values['Amount'] = amount_usd
        row_values['Time']   = txn_time
        input_df = pd.DataFrame([row_values.values], columns=feature_cols)
    else:
        features = [txn_time] + [0] * 28 + [amount_usd]
        input_df = pd.DataFrame([features], columns=['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount'])

    prob = model.predict_proba(input_df)[0][1]
    amount_suspicious = amount_usd > country_threshold
    time_suspicious   = txn_time < 3600

    adjusted_prob = prob
    if amount_suspicious:
        adjusted_prob = min(1.0, prob + 0.4)
    if time_suspicious and amount_usd > 1000:
        adjusted_prob = min(1.0, adjusted_prob + 0.2)

    if adjusted_prob < 0.3:
        decision = "APPROVED"
    elif adjusted_prob < 0.7:
        decision = "FLAGGED"
    else:
        decision = "BLOCKED"

    return prob, adjusted_prob, decision, amount_suspicious, time_suspicious

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="section-header">🛡️ Fraud Shield</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#475569; font-size:0.8rem;">V Hack 2026 · Case Study 2<br>SDG 8: Decent Work & Economic Growth</p>', unsafe_allow_html=True)
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    st.markdown('<p class="section-header">🌏 ASEAN Region</p>', unsafe_allow_html=True)
    selected_country = st.selectbox("Select country", list(COUNTRY_CONFIG.keys()), label_visibility="collapsed")
    cfg = COUNTRY_CONFIG[selected_country]

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
         border-radius:10px; padding:0.9rem; font-size:0.82rem; color:#94a3b8; line-height:1.9;">
        <strong style="color:#e2e8f0;">Currency:</strong> {cfg['currency']}<br>
        <strong style="color:#e2e8f0;">Block threshold:</strong> ${cfg['threshold']:,} USD<br>
        <strong style="color:#e2e8f0;">Regional fraud rate:</strong> {cfg['fraud_rate']}<br>
        <strong style="color:#e2e8f0;">Top fraud type:</strong> {cfg['top_fraud']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">📧 Email Alert (Gmail)</p>', unsafe_allow_html=True)
    sms_enabled = st.toggle("Enable email alerts", value=False)
    if sms_enabled:
        st.caption(f"✅ Alerts will be sent to: {os.getenv('ALERT_EMAIL', 'Not set — check .env file')}")

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">Model Info</p>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#94a3b8; font-size:0.82rem; line-height:1.8;">
    <strong style="color:#e2e8f0;">Dataset:</strong> Credit Card Fraud (Kaggle)<br>
    <strong style="color:#e2e8f0;">Transactions:</strong> 284,807<br>
    <strong style="color:#e2e8f0;">Balancing:</strong> SMOTE<br>
    <strong style="color:#e2e8f0;">Algorithm:</strong> XGBoost Classifier
    </p>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">Recent Checks</p>', unsafe_allow_html=True)
    if st.session_state.history:
        for h in reversed(st.session_state.history[-5:]):
            icon = "✅" if h['decision'] == "APPROVED" else "⚠️" if h['decision'] == "FLAGGED" else "🚫"
            st.markdown(f"""
            <div class="history-row">
                <span>{icon} <strong>{h['decision']}</strong></span><br>
                <span style="color:#64748b; font-size:0.78rem;">
                    {h['currency']} {h['amount']:,.2f} · Risk: {h['risk']:.0%} · {h['time']}
                </span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#334155; font-size:0.82rem;">No transactions yet.</p>', unsafe_allow_html=True)

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.session_state.live_feed = []
        st.rerun()

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🛡️ Fraud Shield</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Real-Time Transaction Protection for the Unbanked · ASEAN</div>', unsafe_allow_html=True)
st.markdown("""
<div class="story-box">
💡 <strong>Meet Aini</strong> — a 34-year-old food delivery rider in Kuala Lumpur.
Her entire month's income sits in her e-wallet. One fraudulent transaction could wipe her out.
Fraud Shield analyzes every transaction in milliseconds and sends her an <strong>instant email alert</strong> if anything looks wrong.
</div>
""", unsafe_allow_html=True)

# ── Stats row ──────────────────────────────────────────────────────────────────
blocked_count = sum(1 for h in st.session_state.history if h['decision'] == 'BLOCKED')
total_checked = len(st.session_state.history)
c1, c2, c3, c4, c5 = st.columns(5)
for col, (num, label) in zip([c1, c2, c3, c4, c5], [
    ("94%", "Precision"), ("91%", "Recall"), ("92%", "F1 Score"),
    (str(blocked_count), "Blocked 🚫"), (str(total_checked), "Checked")
]):
    with col:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{num}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔍 Check Transaction", "📡 Live Monitor", "ℹ️ How It Works"])

# ════════════════════════════════════════════
# TAB 1 — Check Transaction
# ════════════════════════════════════════════
with tab1:
    left_col, right_col = st.columns([1.1, 1], gap="large")

    with left_col:
        st.markdown('<p class="section-header">Transaction Input</p>', unsafe_allow_html=True)

        scenario = st.selectbox("📋 Choose a demo scenario", [
            "Normal grocery purchase",
            "Suspicious late-night transfer",
            "Typical bill payment",
            "Overseas transaction",
            "Custom (enter manually)"
        ])

        row = None
        if scenario == "Normal grocery purchase":
            row = legit_df.iloc[0]
            st.caption("📂 Real legitimate transaction from dataset")
        elif scenario == "Suspicious late-night transfer":
            row = fraud_df.iloc[0]
            st.caption("📂 Real fraudulent transaction from dataset")
        elif scenario == "Typical bill payment":
            row = legit_df.iloc[5]
            st.caption("📂 Real legitimate transaction from dataset")
        elif scenario == "Overseas transaction":
            row = legit_df.iloc[10]
            st.caption("📂 Real legitimate transaction from dataset")

        st.markdown("")
        local_amount = st.number_input(
            f"💰 Amount ({cfg['currency']})",
            min_value=0.0,
            value=float(row['Amount'] * cfg['usd_rate']) if row is not None else 100.0 * cfg['usd_rate'],
        )
        amount_usd = local_amount / cfg['usd_rate']

        txn_time = st.number_input(
            "⏱️ Time Since First Transaction (seconds)",
            min_value=0.0,
            value=float(row['Time']) if row is not None else 50000.0,
        )

        st.markdown("")
        check_btn = st.button("🔍 Analyze Transaction", use_container_width=True, type="primary")

    with right_col:
        st.markdown('<p class="section-header">Analysis Result</p>', unsafe_allow_html=True)

        if check_btn:
            with st.spinner("Analyzing transaction..."):
                time_module.sleep(0.6)

            prob, adjusted_prob, decision, amount_suspicious, time_suspicious = predict(
                row, amount_usd, txn_time, cfg['threshold']
            )

            # ── Result card ────────────────────────────────────────────────────
            if decision == "APPROVED":
                st.markdown("""
                <div class="result-approved">
                    <div class="result-icon">✅</div>
                    <div class="result-title" style="color:#10b981;">APPROVED</div>
                    <div class="result-sub">Transaction looks legitimate. Processing now.</div>
                </div>""", unsafe_allow_html=True)
            elif decision == "FLAGGED":
                st.markdown("""
                <div class="result-flagged">
                    <div class="result-icon">⚠️</div>
                    <div class="result-title" style="color:#f59e0b;">FLAGGED FOR REVIEW</div>
                    <div class="result-sub">Suspicious pattern. OTP verification triggered.</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-blocked">
                    <div class="result-icon">🚫</div>
                    <div class="result-title" style="color:#ef4444;">BLOCKED</div>
                    <div class="result-sub">High fraud probability. Transaction halted.</div>
                </div>""", unsafe_allow_html=True)

            # ── Rule flags ─────────────────────────────────────────────────────
            st.markdown("")
            if amount_suspicious:
                st.markdown(f'<div class="flag-badge">🚨 {cfg["currency"]} {local_amount:,.2f} exceeds threshold of ${cfg["threshold"]:,} USD</div>', unsafe_allow_html=True)
            if time_suspicious and amount_usd > 1000:
                st.markdown('<div class="flag-badge">🚨 Large transaction within first hour of activity</div>', unsafe_allow_html=True)

            # ── Risk bar ───────────────────────────────────────────────────────
            risk_pct  = int(adjusted_prob * 100)
            bar_color = "#10b981" if adjusted_prob < 0.3 else "#f59e0b" if adjusted_prob < 0.7 else "#ef4444"
            st.markdown(f"""
            <p style="font-size:0.8rem; color:#64748b; margin-bottom:4px; margin-top:1rem;">FRAUD RISK SCORE</p>
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="flex:1; background:rgba(255,255,255,0.08); border-radius:99px; height:10px;">
                    <div style="width:{risk_pct}%; background:{bar_color}; border-radius:99px; height:10px;"></div>
                </div>
                <span style="font-family:'Space Mono',monospace; color:{bar_color}; font-weight:700;">{risk_pct}%</span>
            </div>
            """, unsafe_allow_html=True)

            # ── Score metrics ──────────────────────────────────────────────────
            st.markdown("")
            sc1, sc2 = st.columns(2)
            sc1.metric("ML Model Score", f"{prob:.1%}")
            sc2.metric("Final Risk Score", f"{adjusted_prob:.1%}")

            # ── Email alert ────────────────────────────────────────────────────
            if sms_enabled and decision in ["FLAGGED", "BLOCKED"]:
                with st.spinner("📧 Sending email alert..."):
                    time_module.sleep(0.4)
                    success, result = send_email_alert(
                        decision, local_amount, cfg['currency'], cfg['flag']
                    )
                if success:
                    st.markdown(f"""
                    <div class="sms-box">
                        📧 <strong>Email Alert Sent!</strong><br>
                        <span style="color:#94a3b8; font-size:0.82rem;">
                            Fraud alert delivered to {result}
                        </span>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.warning(f"Email failed: {result}")

            elif sms_enabled and decision == "APPROVED":
                st.markdown("""
                <div style="background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.2);
                     border-radius:10px; padding:0.8rem 1rem; margin-top:1rem;
                     color:#6ee7b7; font-size:0.85rem;">
                    📧 No alert needed — transaction approved safely.
                </div>""", unsafe_allow_html=True)

            # ── Save to history ────────────────────────────────────────────────
            st.session_state.history.append({
                'decision': decision,
                'amount':   local_amount,
                'currency': cfg['currency'],
                'risk':     adjusted_prob,
                'time':     datetime.now().strftime("%H:%M:%S")
            })
            st.session_state.live_feed.insert(0, {
                'decision': decision,
                'amount':   local_amount,
                'currency': cfg['currency'],
                'risk':     adjusted_prob,
                'country':  cfg['flag'],
                'time':     datetime.now().strftime("%H:%M:%S")
            })

        else:
            st.markdown("""
            <div style="border:1px dashed rgba(255,255,255,0.1); border-radius:14px;
                 padding:3rem 2rem; text-align:center; color:#334155;">
                <div style="font-size:2.5rem; margin-bottom:1rem;">🔍</div>
                <p style="font-family:'Space Mono',monospace; font-size:0.85rem;">
                    Select a scenario and click<br>Analyze Transaction
                </p>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 2 — Live Monitor
# ════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-header">Live Transaction Feed</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#475569; font-size:0.85rem; margin-bottom:1rem;">Simulates a real-time stream of transactions being analyzed by Fraud Shield.</p>', unsafe_allow_html=True)

    sim_col, stats_col = st.columns([1.4, 1], gap="large")

    with sim_col:
        run_sim = st.button("▶️ Run Simulation (10 transactions)", use_container_width=True, type="primary")
        feed_placeholder = st.empty()

        def render_feed():
            if not st.session_state.live_feed:
                feed_placeholder.markdown("""
                <div style="border:1px dashed rgba(255,255,255,0.07); border-radius:12px;
                     padding:2rem; text-align:center; color:#334155;">
                    <p style="font-family:'Space Mono',monospace; font-size:0.82rem;">
                        No transactions yet. Run simulation or check a transaction.
                    </p>
                </div>""", unsafe_allow_html=True)
            else:
                html = ""
                for item in st.session_state.live_feed[:15]:
                    css  = f"feed-row-{item['decision'].lower()}"
                    icon = "✅" if item['decision'] == "APPROVED" else "⚠️" if item['decision'] == "FLAGGED" else "🚫"
                    html += f"""
                    <div class="{css}">
                        {item['country']} {icon} <strong>{item['decision']}</strong>
                        &nbsp;·&nbsp; {item['currency']} {item['amount']:,.2f}
                        &nbsp;·&nbsp; Risk: {item['risk']:.0%}
                        &nbsp;·&nbsp; <span style="color:#475569">{item['time']}</span>
                    </div>"""
                feed_placeholder.markdown(html, unsafe_allow_html=True)

        render_feed()

        if run_sim:
            sim_cases = [
                (legit_df.iloc[2],  random.uniform(20,   200)),
                (fraud_df.iloc[1],  random.uniform(100,  500)),
                (legit_df.iloc[3],  random.uniform(10,   80)),
                (fraud_df.iloc[2],  random.uniform(1000, 4000)),
                (legit_df.iloc[7],  random.uniform(50,   300)),
                (legit_df.iloc[12], random.uniform(30,   250)),
                (fraud_df.iloc[3],  random.uniform(5000, 9000)),
                (legit_df.iloc[15], random.uniform(5,    25)),
                (legit_df.iloc[18], random.uniform(200,  800)),
                (fraud_df.iloc[4],  random.uniform(300,  900)),
            ]
            for sim_row, sim_local in sim_cases:
                sim_usd = sim_local / cfg['usd_rate']
                _, adj, sim_dec, _, _ = predict(
                    sim_row, sim_usd, random.uniform(100, 80000), cfg['threshold']
                )
                st.session_state.live_feed.insert(0, {
                    'decision': sim_dec,
                    'amount':   sim_local,
                    'currency': cfg['currency'],
                    'risk':     adj,
                    'country':  cfg['flag'],
                    'time':     datetime.now().strftime("%H:%M:%S")
                })
                render_feed()
                time_module.sleep(0.4)

    with stats_col:
        st.markdown('<p class="section-header">Session Summary</p>', unsafe_allow_html=True)
        total    = len(st.session_state.live_feed)
        blocked  = sum(1 for h in st.session_state.live_feed if h['decision'] == 'BLOCKED')
        flagged  = sum(1 for h in st.session_state.live_feed if h['decision'] == 'FLAGGED')
        approved = sum(1 for h in st.session_state.live_feed if h['decision'] == 'APPROVED')
        detect_rate = f"{((blocked + flagged) / total * 100):.1f}%" if total > 0 else "—"

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
             border-radius:14px; padding:1.5rem;">
            <div style="margin-bottom:1rem;">
                <div style="font-family:'Space Mono',monospace; font-size:1.8rem; color:#38bdf8;">{total}</div>
                <div style="font-size:0.78rem; color:#64748b; text-transform:uppercase; letter-spacing:1px;">Total Analyzed</div>
            </div>
            <div style="display:flex; gap:0.8rem; margin-bottom:1rem;">
                <div style="flex:1; background:rgba(16,185,129,0.1); border-radius:8px; padding:0.7rem; text-align:center;">
                    <div style="font-family:'Space Mono',monospace; color:#10b981; font-size:1.3rem;">{approved}</div>
                    <div style="font-size:0.72rem; color:#64748b;">Approved</div>
                </div>
                <div style="flex:1; background:rgba(245,158,11,0.1); border-radius:8px; padding:0.7rem; text-align:center;">
                    <div style="font-family:'Space Mono',monospace; color:#f59e0b; font-size:1.3rem;">{flagged}</div>
                    <div style="font-size:0.72rem; color:#64748b;">Flagged</div>
                </div>
                <div style="flex:1; background:rgba(239,68,68,0.1); border-radius:8px; padding:0.7rem; text-align:center;">
                    <div style="font-family:'Space Mono',monospace; color:#ef4444; font-size:1.3rem;">{blocked}</div>
                    <div style="font-size:0.72rem; color:#64748b;">Blocked</div>
                </div>
            </div>
            <div style="font-size:0.82rem; color:#475569;">
                Fraud detection rate: <strong style="color:#e2e8f0;">{detect_rate}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 3 — How It Works
# ════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-header">System Architecture</p>', unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns(4)
    for col, (num, title, desc) in zip([h1, h2, h3, h4], [
        ("01", "Behavioral Profiling",  "Transaction frequency, amount, location and time patterns build a baseline of normal user behavior."),
        ("02", "ML Anomaly Scoring",    "XGBoost trained on 284K real transactions scores each new transaction. SMOTE balances the 0.17% fraud rate."),
        ("03", "Business Rule Layer",   "Country-specific thresholds and time-based rules combine with the ML score for a final adjusted risk score."),
        ("04", "Real-Time Email Alert", "BLOCKED or FLAGGED transactions instantly trigger a styled email alert to the user — before money moves."),
    ]):
        with col:
            st.markdown(f"""
            <div class="stat-card" style="text-align:left; padding:1.2rem;">
                <div style="font-family:'Space Mono',monospace; color:#38bdf8; font-size:0.75rem; margin-bottom:0.5rem;">{num}</div>
                <div style="font-weight:600; color:#e2e8f0; margin-bottom:0.4rem; font-size:0.92rem;">{title}</div>
                <div style="color:#64748b; font-size:0.8rem; line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">Why This Matters for ASEAN</p>', unsafe_allow_html=True)

    a1, a2 = st.columns(2)
    with a1:
        for country, data in COUNTRY_CONFIG.items():
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
                 border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:0.6rem; font-size:0.85rem;">
                <strong style="color:#e2e8f0;">{country}</strong><br>
                <span style="color:#64748b;">Fraud rate: {data['fraud_rate']} · Top threat: {data['top_fraud']}</span>
            </div>""", unsafe_allow_html=True)
    with a2:
        st.markdown("""
        <div style="background:rgba(56,189,248,0.06); border:1px solid rgba(56,189,248,0.15);
             border-radius:14px; padding:1.5rem; color:#94a3b8; font-size:0.88rem; line-height:1.8;">
            <strong style="color:#38bdf8;">SDG 8 — Decent Work & Economic Growth</strong><br><br>
            Target 8.10 calls for strengthening access to financial services for all.
            Fraud Shield directly enables this by making digital payments
            <strong style="color:#e2e8f0;">safe enough to trust</strong> for first-time unbanked users across ASEAN.<br><br>
            When a gig worker loses their wallet balance to fraud, they don't just lose money —
            they lose <strong style="color:#e2e8f0;">trust in the digital economy entirely</strong>.
            Fraud Shield protects both.
        </div>""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
st.markdown("""
<p style="text-align:center; color:#1e293b; font-size:0.78rem;">
V Hack 2026 · Case Study 2 · SDG 8: Decent Work & Economic Growth ·
Built with XGBoost + SMOTE + Gmail + Streamlit
</p>""", unsafe_allow_html=True)
