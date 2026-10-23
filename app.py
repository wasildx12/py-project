import streamlit as st
from database import init_db, create_user, authenticate, get_user, submit_waste, get_user_submissions, get_wallet, get_transactions, get_stats, get_pending_submissions, review_submission, get_all_users
from config import APP_NAME, WASTE_RATES, ACCEPTED_TYPES, REJECTED_TYPES

st.set_page_config(page_title=APP_NAME, page_icon="♻️", layout="wide", initial_sidebar_state="collapsed")
init_db()

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--ink:#15352e;--muted:#668078;--green:#087f5b;--mint:#c8f4df;--line:rgba(255,255,255,.78)}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)}
.stApp{background:radial-gradient(ellipse at 12% 8%,rgba(162,245,203,.55),transparent 35%),radial-gradient(ellipse at 88% 20%,rgba(191,225,255,.55),transparent 32%),linear-gradient(135deg,#f5fff9 0%,#edf8f3 48%,#f7fbff 100%);background-attachment:fixed}
.stApp:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;background-image:radial-gradient(circle at 15% 20%,rgba(255,255,255,.95) 0 2px,transparent 3px),radial-gradient(circle at 77% 34%,rgba(255,255,255,.8) 0 3px,transparent 4px),radial-gradient(circle at 42% 76%,rgba(255,255,255,.8) 0 2px,transparent 3px);background-size:220px 220px,310px 310px,270px 270px;animation:particles 22s linear infinite}
@keyframes particles{0%{transform:translateY(0)}50%{transform:translateY(-24px)}100%{transform:translateY(0)}}
.block-container{max-width:1240px;padding-top:1.2rem;padding-bottom:4rem;position:relative;z-index:1}
header[data-testid="stHeader"]{background:transparent}
#MainMenu,footer{visibility:hidden}
.glass-nav{display:flex;align-items:center;justify-content:space-between;padding:15px 22px;border:1px solid rgba(255,255,255,.9);border-radius:22px;background:rgba(255,255,255,.52);backdrop-filter:blur(24px) saturate(160%);-webkit-backdrop-filter:blur(24px) saturate(160%);box-shadow:0 12px 38px rgba(42,104,80,.09),inset 0 1px 0 rgba(255,255,255,.95);margin-bottom:28px;animation:slideDown .7s ease both}
.brand{font:800 1.08rem Manrope,sans-serif;letter-spacing:-.04em;color:#123d30}.brand span{color:#11986c}
.nav-note{font-size:.83rem;color:#55766a}
@keyframes slideDown{from{opacity:0;transform:translateY(-12px)}to{opacity:1;transform:translateY(0)}}
.hero{position:relative;overflow:hidden;padding:clamp(25px,5vw,58px);border-radius:32px;border:1px solid rgba(255,255,255,.92);background:linear-gradient(135deg,rgba(255,255,255,.78),rgba(235,255,245,.45));backdrop-filter:blur(26px);box-shadow:0 24px 65px rgba(38,100,76,.10),inset 0 1px 0 #fff;animation:fadeUp .8s ease both}
.hero:after{content:"";position:absolute;width:290px;height:290px;right:-50px;top:-90px;border-radius:50%;background:radial-gradient(circle at 35% 30%,rgba(255,255,255,.95),rgba(142,237,192,.55) 36%,rgba(45,174,122,.12) 68%,transparent 72%);filter:blur(1px);animation:orb 8s ease-in-out infinite}
.hero-kicker{display:inline-flex;padding:8px 13px;border:1px solid rgba(255,255,255,.95);border-radius:999px;background:rgba(255,255,255,.58);color:#16845e;font-size:.78rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
.hero h1{font:800 clamp(2.1rem,5vw,4.3rem)/1.04 Manrope,sans-serif;letter-spacing:-.065em;color:#143d30;max-width:760px;margin:20px 0 14px}
.hero p{font-size:1.05rem;line-height:1.75;color:#5a786e;max-width:620px}
@keyframes orb{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-20px,22px) scale(1.07)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
.section-head{display:inline-flex;align-items:center;gap:9px;padding:10px 15px;border:1px solid rgba(255,255,255,.9);border-radius:15px;background:rgba(255,255,255,.55);backdrop-filter:blur(18px);box-shadow:0 7px 22px rgba(35,94,70,.06),inset 0 1px 0 #fff;font:700 1.05rem Manrope,sans-serif;margin:24px 0 15px}
.metric{padding:21px 22px;border:1px solid rgba(255,255,255,.9);border-radius:23px;background:rgba(255,255,255,.58);backdrop-filter:blur(20px);box-shadow:0 12px 32px rgba(43,105,81,.07),inset 0 1px 0 #fff;transition:transform .25s ease,box-shadow .25s ease;animation:fadeUp .6s ease both}
.metric:hover{transform:translateY(-5px);box-shadow:0 20px 42px rgba(43,105,81,.12)}
.metric-label{font-size:.82rem;color:#68857a;font-weight:600}.metric-value{font:800 clamp(1.45rem,3vw,2.1rem) Manrope,sans-serif;letter-spacing:-.04em;color:#164936;margin-top:8px}.metric-icon{font-size:1.3rem}
.glass-panel{padding:22px;border:1px solid rgba(255,255,255,.88);border-radius:24px;background:rgba(255,255,255,.53);backdrop-filter:blur(20px);box-shadow:0 12px 34px rgba(43,105,81,.065),inset 0 1px 0 #fff}
.stButton>button{border-radius:14px;border:1px solid rgba(255,255,255,.9);background:linear-gradient(135deg,#14976c,#087b57);color:white;font-weight:700;padding:.68rem 1rem;box-shadow:0 8px 18px rgba(8,127,91,.18);transition:transform .2s ease,box-shadow .2s ease}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 12px 25px rgba(8,127,91,.25);border-color:#b8f0d3;color:white}
.stTextInput input,.stNumberInput input,.stSelectbox>div>div,.stTextArea textarea{border-radius:13px!important;border:1px solid rgba(115,169,145,.25)!important;background:rgba(255,255,255,.7)!important}
[data-testid="stTabs"] button{border-radius:12px!important}
[data-testid="stTabs"] [role="tablist"]{gap:8px;padding:6px;background:rgba(255,255,255,.45);border:1px solid rgba(255,255,255,.8);border-radius:17px;backdrop-filter:blur(14px)}
[data-testid="stDataFrame"],[data-testid="stTable"]{border-radius:16px;overflow:hidden}
.small-muted{color:#6b887d;font-size:.9rem}
.status-pill{display:inline-block;padding:5px 10px;border-radius:999px;background:rgba(202,244,221,.7);color:#087f5b;font-size:.78rem;font-weight:700}
@media(max-width:700px){.block-container{padding:1rem 1rem 3rem}.glass-nav{padding:13px 15px}.hero{border-radius:24px}.hero:after{opacity:.55}.metric{padding:17px;border-radius:19px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def nav(user=None):
    who = f"Welcome, {user['name']}" if user else "A smarter way to recycle"
    st.markdown(f'<div class="glass-nav"><div class="brand">eco<span>coin</span> ◌</div><div class="nav-note">{who} &nbsp; · &nbsp; Waste less. Grow more.</div></div>', unsafe_allow_html=True)

def heading(text, icon="✦"):
    st.markdown(f'<div class="section-head"><span>{icon}</span>{text}</div>', unsafe_allow_html=True)

def metric(label, value, icon):
    st.markdown(f'<div class="metric"><div class="metric-icon">{icon}</div><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

def hero():
    st.markdown('<div class="hero"><span class="hero-kicker">♻ &nbsp; Small actions. Real impact.</span><h1>Make every recycle<br>count.</h1><p>Turn responsible recycling into meaningful rewards. Track your impact, grow your EcoCoin wallet, and help build a cleaner future — one submission at a time.</p></div>', unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    nav()
    hero()
    a,b=st.columns([1,1], gap="large")
    with a:
        heading("Sign in to your wallet","↗")
        with st.form("login_form"):
            username=st.text_input("Username")
            password=st.text_input("Password",type="password")
            submitted=st.form_submit_button("Sign in",use_container_width=True)
            if submitted:
                user=authenticate(username.strip(),password)
                if user:
                    st.session_state.user_id=user["id"]
                    st.rerun()
                else: st.error("Invalid username or password.")
    with b:
        heading("Create your account","✳")
        with st.form("register_form"):
            name=st.text_input("Full name",key="reg_name")
            username=st.text_input("Choose username",key="reg_username")
            password=st.text_input("Create password",type="password",key="reg_password")
            confirm=st.text_input("Confirm password",type="password")
            submitted=st.form_submit_button("Create account",use_container_width=True)
            if submitted:
                if not name.strip() or not username.strip() or not password: st.error("Please complete all fields.")
                elif len(password)<8: st.error("Use a password with at least 8 characters.")
                elif password!=confirm: st.error("Passwords do not match.")
                else:
                    ok,msg=create_user(name.strip(),username.strip(),password)
                    if ok: st.success("Account created. Sign in to continue.")
                    else: st.error(msg)
    st.caption("EcoCoin demo · Each account has its own wallet and private activity.")
    st.stop()

user=get_user(st.session_state.user_id)
if not user:
    st.session_state.user_id=None
    st.rerun()
nav(user)
with st.sidebar:
    st.markdown("### eco coin")
    st.caption(f"Signed in as **{user['username']}**")
    page=st.radio("Navigate",["Overview","Submit waste","My wallet","Activity","Admin"])
    if st.button("Sign out",use_container_width=True):
        st.session_state.user_id=None
        st.rerun()

if page=="Overview":
    hero()
    wallet=get_wallet(user["id"])
    stats=get_stats(user["id"])
    heading("Your impact at a glance","✦")
    c1,c2,c3,c4=st.columns(4)
    with c1: metric("Available EcoCoins",f"{wallet['balance']:.1f}","◈")
    with c2: metric("Waste submissions",str(stats["total"]),"♻")
    with c3: metric("Approved submissions",str(stats["approved"]),"✓")
    with c4: metric("Pending review",str(stats["pending"]),"◷")
    heading("Your latest activity","↗")
    tx=get_transactions(user["id"],limit=5)
    if tx: st.dataframe(tx,use_container_width=True,hide_index=True)
    else:
        st.markdown('<div class="glass-panel"><b>Your story starts here.</b><p class="small-muted">Submit your first eligible recycling item to start earning EcoCoins.</p></div>',unsafe_allow_html=True)
elif page=="Submit waste":
    heading("Submit a recycling request","♻")
    st.markdown('<div class="small-muted">Choose a material and enter the amount. Rewards are estimates until an administrator verifies your submission.</div>',unsafe_allow_html=True)
    with st.form("waste_form"):
        material=st.selectbox("Waste material",list(WASTE_RATES.keys()))
        amount=st.number_input("Weight (kg)",min_value=.1,max_value=1000.0,value=1.0,step=.5)
        notes=st.text_area("Notes (optional)",placeholder="Add any helpful details…")
        estimate=amount*WASTE_RATES[material]
        st.info(f"Estimated reward: {estimate:.1f} EcoCoins per submission. Final reward is subject to review.")
        submit=st.form_submit_button("Send for review",use_container_width=True)
        if submit:
            if material in REJECTED_TYPES: st.error("This material is not accepted by EcoCoin.")
            else:
                submit_waste(user["id"],material,amount,notes.strip(),estimate)
                st.success("Submission sent for administrator review.")
    heading("Accepted materials","✓")
    st.markdown('<div class="glass-panel">Plastic · Polythene · Rubber · Wood<br><br><span class="small-muted">Automobile waste and construction waste are not accepted.</span></div>',unsafe_allow_html=True)
elif page=="My wallet":
    heading("Your personal wallet","◈")
    wallet=get_wallet(user["id"])
    c1,c2,c3=st.columns(3)
    with c1: metric("Available balance",f"{wallet['balance']:.1f}","◈")
    with c2: metric("Total earned",f"{wallet['earned']:.1f}","↗")
    with c3: metric("Pending rewards",f"{wallet['pending']:.1f}","◷")
    heading("Wallet transactions","↔")
    tx=get_transactions(user["id"])
    if tx: st.dataframe(tx,use_container_width=True,hide_index=True)
    else: st.info("Your wallet transactions will appear here after your first approved submission.")
elif page=="Activity":
    heading("Your recycling activity","◷")
    rows=get_user_submissions(user["id"])
    if rows: st.dataframe(rows,use_container_width=True,hide_index=True)
    else: st.info("You have not submitted any waste yet.")
elif page=="Admin":
    if not user["is_admin"]:
        st.warning("This area is for administrators only.")
    else:
        heading("Admin review center","⚙")
        pending=get_pending_submissions()
        if not pending: st.success("No pending submissions.")
        for item in pending:
            with st.container(border=True):
                st.markdown(f"**{item['name']}** · @{item['username']} · {item['material']} · {item['weight_kg']} kg")
                st.caption(f"Estimated: {item['estimated_coins']:.1f} EcoCoins · Submitted: {item['created_at']}")
                x,y=st.columns(2)
                with x:
                    if st.button("Approve & credit wallet",key=f"approve_{item['id']}",use_container_width=True):
                        review_submission(item["id"],user["id"],True)
                        st.rerun()
                with y:
                    if st.button("Reject request",key=f"reject_{item['id']}",use_container_width=True):
                        review_submission(item["id"],user["id"],False)
                        st.rerun()
        heading("Registered users","♙")
        st.dataframe(get_all_users(),use_container_width=True,hide_index=True)
st.markdown('<div style="text-align:center;padding:32px 0 8px;color:#78948a;font-size:.82rem">ECOCOIN · Built for a lighter footprint · <span style="color:#13845f">Sustainability, beautifully designed.</span></div>',unsafe_allow_html=True)
