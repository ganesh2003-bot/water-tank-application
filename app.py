import datetime as dt

import streamlit as st

# ---------- Page setup ----------
st.set_page_config(page_title="My Water Tracker", page_icon="💧", layout="centered")

st.markdown(
    """
    <style>
    .block-container {max-width: 720px; padding-top: 1.5rem;}
    .title {text-align:center; font-size:2.2rem; font-weight:800; color:#0277bd; margin-bottom:0;}
    .subtitle {text-align:center; color:#607d8b; margin-bottom:1.2rem;}
    .bar-wrap {background:#e1f5fe; border-radius:999px; height:34px; overflow:hidden;
               border:2px solid #81d4fa; margin:0.6rem 0 0.3rem 0;}
    .bar-fill {height:100%; border-radius:999px; text-align:center; color:white; font-weight:700;
               line-height:30px; background:linear-gradient(90deg,#29b6f6,#0277bd);
               transition: width .6s ease; min-width:48px;}
    .bar-fill.done {background:linear-gradient(90deg,#26c6da,#00897b);}
    div.stButton > button {width:100%; padding:0.7rem 0; font-size:1.05rem; border-radius:12px;}
    div[data-testid="stMetric"] {background:#f1f8ff; border-radius:12px; padding:10px 14px;}
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMetric"] {background:#12283a;}
        .bar-wrap {background:#12283a; border-color:#0277bd;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- State ----------
today = dt.date.today()

if "goal_ml" not in st.session_state:
    st.session_state.goal_ml = 2000
if "log" not in st.session_state:
    st.session_state.log = []  # list of (time string, ml)
if "day" not in st.session_state:
    st.session_state.day = today
if "celebrated" not in st.session_state:
    st.session_state.celebrated = False

# New day -> fresh start
if st.session_state.day != today:
    st.session_state.day = today
    st.session_state.log = []
    st.session_state.celebrated = False


def add_water(ml: int):
    st.session_state.log.append((dt.datetime.now().strftime("%I:%M %p"), ml))


def undo_last():
    if st.session_state.log:
        st.session_state.log.pop()
        if sum(ml for _, ml in st.session_state.log) < st.session_state.goal_ml:
            st.session_state.celebrated = False


def reset_day():
    st.session_state.log = []
    st.session_state.celebrated = False


# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    goal_l = st.slider(
        "Daily goal (litres)", 1.0, 5.0, st.session_state.goal_ml / 1000, step=0.25
    )
    st.session_state.goal_ml = int(goal_l * 1000)
    st.caption("A common guide is about 2–3 litres a day, but needs vary with weather, activity and health.")
    st.button("🔄 Reset today", on_click=reset_day)

# ---------- Header ----------
st.markdown('<div class="title">💧 My Water Tracker</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">{today.strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True
)

goal = st.session_state.goal_ml
total = sum(ml for _, ml in st.session_state.log)
remaining = max(goal - total, 0)
percent = min(total / goal, 1.0) if goal else 0

# ---------- Add water buttons ----------
st.subheader("Add water")
c1, c2, c3 = st.columns(3)
c1.button("🥛 1 Glass\n(250 ml)", on_click=add_water, args=(250,))
c2.button("🧴 Bottle\n(500 ml)", on_click=add_water, args=(500,))
c3.button("🫗 Large\n(750 ml)", on_click=add_water, args=(750,))

with st.expander("➕ Custom amount"):
    custom = st.number_input("Millilitres", min_value=50, max_value=2000, value=300, step=50)
    st.button("Add custom amount", on_click=add_water, args=(int(custom),))

# Recompute after button callbacks have run
total = sum(ml for _, ml in st.session_state.log)
remaining = max(goal - total, 0)
percent = min(total / goal, 1.0) if goal else 0

# ---------- Stats ----------
m1, m2, m3 = st.columns(3)
m1.metric("Consumed", f"{total / 1000:.2f} L")
m2.metric("Remaining", f"{remaining / 1000:.2f} L")
m3.metric("Goal", f"{goal / 1000:.2f} L")

# ---------- Progress ----------
done_cls = " done" if total >= goal else ""
st.markdown(
    f"""
    <div class="bar-wrap">
        <div class="bar-fill{done_cls}" style="width:{percent * 100:.0f}%">{percent * 100:.0f}%</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"{total} ml of {goal} ml")

# ---------- Messages ----------
if total >= goal:
    st.success("🎉 Congratulations! You reached your daily water goal. Great job staying hydrated! 💙")
    if not st.session_state.celebrated:
        st.balloons()
        st.session_state.celebrated = True
elif percent >= 0.75:
    st.info("🌊 Almost there! Just a little more to go.")
elif percent >= 0.5:
    st.info("💪 Halfway done, keep it up!")
elif percent > 0:
    st.info("🚰 Good start! Keep sipping through the day.")
else:
    st.warning("🥤 You haven't logged any water yet. Have a glass to get started!")

# ---------- Today's log ----------
st.subheader("Today's log")
if st.session_state.log:
    rows = [
        {"#": i + 1, "Time": t, "Amount (ml)": ml}
        for i, (t, ml) in enumerate(st.session_state.log)
    ]
    st.dataframe(rows, hide_index=True, use_container_width=True)
    st.button("↩️ Undo last", on_click=undo_last)
else:
    st.caption("Nothing logged yet.")

st.divider()
st.caption("Tip: Data is kept for your current browser session and resets each new day.")
