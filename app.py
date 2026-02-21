import streamlit as st
from utils.nutrition_parser import analyze_food, generate_meal_plan, get_recipe_suggestions
from utils.charts import render_macro_chart, render_progress_chart
from utils.session import init_session

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NutriMind AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root Variables ── */
:root {
    --green-dark:   #1a2e1a;
    --green-mid:    #2d5a27;
    --green-accent: #5cb85c;
    --green-light:  #a8d5a2;
    --cream:        #f5f0e8;
    --warm-white:   #faf8f3;
    --text-dark:    #1a1a1a;
    --text-mid:     #4a4a4a;
    --orange-accent:#e8813a;
    --card-shadow:  0 4px 24px rgba(0,0,0,0.08);
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--warm-white);
    color: var(--text-dark);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, var(--green-dark) 0%, var(--green-mid) 100%);
    border-right: none;
}
[data-testid="stSidebar"] * { color: var(--cream) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stTextInput label { color: var(--green-light) !important; font-size:0.8rem; font-weight:500; letter-spacing:0.05em; text-transform:uppercase; }

/* ── Headings ── */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* ── Cards ── */
.nutri-card {
    background: white;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: var(--card-shadow);
    border: 1px solid rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}
.macro-pill {
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 50px;
    font-weight: 600;
    font-size: 0.85rem;
    margin: 0.25rem;
}
.pill-cal   { background:#fff3e0; color:#e65100; }
.pill-pro   { background:#e8f5e9; color:#2e7d32; }
.pill-carb  { background:#e3f2fd; color:#1565c0; }
.pill-fat   { background:#fce4ec; color:#880e4f; }

/* ── Hero Banner ── */
.hero-banner {
    background: linear-gradient(135deg, var(--green-dark) 0%, var(--green-mid) 60%, #3d7a37 100%);
    border-radius: 24px;
    padding: 2.5rem 2rem;
    color: var(--cream);
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::after {
    content: '🥗';
    position: absolute;
    right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 5rem;
    opacity: 0.3;
}
.hero-banner h1 { color: white !important; font-size: 2.2rem; margin:0; }
.hero-banner p  { color: var(--green-light) !important; margin:0.5rem 0 0; font-size:1rem; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--green-mid), var(--green-accent));
    color: white !important;
    border: none;
    border-radius: 12px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    padding: 0.6rem 1.5rem;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(45,90,39,0.3);
}

/* ── Input fields ── */
.stTextArea textarea, .stTextInput input {
    border-radius: 12px !important;
    border: 2px solid #e8e8e8 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--green-accent) !important;
    box-shadow: 0 0 0 3px rgba(92,184,92,0.15) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f0f0f0;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: white;
    border-radius: 16px;
    padding: 1rem;
    box-shadow: var(--card-shadow);
    border: 1px solid rgba(0,0,0,0.05);
}

/* ── Log entries ── */
.log-entry {
    background: white;
    border-left: 4px solid var(--green-accent);
    border-radius: 0 12px 12px 0;
    padding: 0.8rem 1.2rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.log-time { font-size: 0.75rem; color: var(--text-mid); font-weight:500; }
.log-food { font-weight: 600; font-size: 0.95rem; }
.log-macros { font-size: 0.8rem; color: var(--text-mid); margin-top:0.2rem; }

/* ── Success box ── */
.success-box {
    background: linear-gradient(135deg, #e8f5e9, #f1f8f0);
    border: 1px solid var(--green-accent);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
}

/* ── Warning box ── */
.warn-box {
    background: linear-gradient(135deg, #fff8e1, #fffde7);
    border: 1px solid #ffd54f;
    border-radius: 16px;
    padding: 1rem 1.5rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ── Session Init ─────────────────────────────────────────────────────────────
init_session()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🥗 NutriMind AI")
    st.markdown("---")

    st.markdown("### 👤 Your Profile")
    name   = st.text_input("Name", value=st.session_state.profile["name"])
    age    = st.number_input("Age", 10, 100, value=st.session_state.profile["age"])
    weight = st.number_input("Weight (kg)", 30, 250, value=st.session_state.profile["weight"])
    height = st.number_input("Height (cm)", 100, 250, value=st.session_state.profile["height"])
    goal   = st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "Maintenance", "Keto", "Vegan"],
                          index=["Weight Loss","Muscle Gain","Maintenance","Keto","Vegan"].index(st.session_state.profile["goal"]))
    activity = st.selectbox("Activity Level", ["Sedentary","Lightly Active","Active","Very Active"],
                            index=["Sedentary","Lightly Active","Active","Very Active"].index(st.session_state.profile["activity"]))

    if st.button("💾 Save Profile"):
        st.session_state.profile = {
            "name": name, "age": age, "weight": weight,
            "height": height, "goal": goal, "activity": activity
        }
        st.success("Profile saved!")

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; padding:0.5rem 0;'>
        <div style='font-size:0.7rem; color:#a8d5a2; letter-spacing:0.08em; text-transform:uppercase; font-weight:600;'>Built with ❤️ by</div>
        <div style='font-size:0.95rem; font-family:Syne,sans-serif; font-weight:700; color:white; margin:0.2rem 0;'>DOKA CHARLES DANIEL</div>
        <div style='font-size:0.7rem; color:#a8d5a2;'>NutriMind AI™</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    import streamlit as st

    # Load token from Streamlit secrets only once
    if "hf_token" not in st.session_state:
        st.session_state.hf_token = ""

        if "HF_TOKEN" in st.secrets:
            st.session_state.hf_token = st.secrets["HF_TOKEN"]

    # Input field
    hf_token = st.text_input(
        "🔑 HuggingFace API Token",
        type="password",
        value=st.session_state.hf_token,
    )
    # Keep session state updated if user types manually
    st.session_state.hf_token = hf_token
    st.markdown("---")
    st.markdown("### 📊 Daily Targets")
    p = st.session_state.profile
    bmr = 10*p["weight"] + 6.25*p["height"] - 5*p["age"] + 5
    multipliers = {"Sedentary":1.2,"Lightly Active":1.375,"Active":1.55,"Very Active":1.725}
    tdee = int(bmr * multipliers[p["activity"]])
    goal_cal = tdee - 500 if p["goal"]=="Weight Loss" else tdee + 300 if p["goal"]=="Muscle Gain" else tdee
    st.metric("🔥 Daily Calories", f"{goal_cal} kcal")
    st.metric("💪 Protein Target", f"{int(p['weight']*1.8)}g")
    st.metric("🍞 Carbs Target",   f"{int(goal_cal*0.45/4)}g")
    st.metric("🥑 Fat Target",     f"{int(goal_cal*0.25/9)}g")

# ── Main Content ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
  <h1>👋 Hello, {st.session_state.profile['name']}!</h1>
  <p>Your AI-powered nutrition coach — track, plan, and optimize your diet with ease.</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📝 Food Log", "📅 Meal Planner", "🍳 Recipes", "📈 Progress"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — FOOD LOG
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown("### 🍽️ Log Your Meal")
        st.markdown('<div class="nutri-card">', unsafe_allow_html=True)
        food_input = st.text_area(
            "What did you eat?",
            placeholder="e.g. 2 scrambled eggs with toast and a glass of orange juice...",
            height=100
        )
        meal_type = st.selectbox("Meal Type", ["🌅 Breakfast","☀️ Lunch","🌙 Dinner","🍎 Snack"])

        if st.button("🔍 Analyze with AI", use_container_width=True):
            if not food_input.strip():
                st.warning("Please describe what you ate.")
            elif not st.session_state.get("hf_token"):
                st.error("Please add your HuggingFace API token in the sidebar.")
            else:
                with st.spinner("🤖 Analyzing your meal..."):
                    result = analyze_food(food_input, st.session_state["hf_token"],
                                          st.session_state.profile)
                if result:
                    st.session_state.food_log.append({
                        "meal": meal_type.split()[1],
                        "food": food_input,
                        "calories": result["calories"],
                        "protein":  result["protein"],
                        "carbs":    result["carbs"],
                        "fat":      result["fat"],
                        "advice":   result["advice"]
                    })
                    st.markdown(f"""
                    <div class="success-box">
                        <b>✅ Meal Logged!</b><br>
                        <span class="macro-pill pill-cal">🔥 {result['calories']} kcal</span>
                        <span class="macro-pill pill-pro">💪 {result['protein']}g protein</span>
                        <span class="macro-pill pill-carb">🍞 {result['carbs']}g carbs</span>
                        <span class="macro-pill pill-fat">🥑 {result['fat']}g fat</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="warn-box">
                        💡 <b>AI Advice:</b> {result['advice']}
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Today's log
        st.markdown("### 📋 Today's Food Log")
        if not st.session_state.food_log:
            st.info("No meals logged yet. Start by analyzing your first meal above!")
        else:
            for i, entry in enumerate(reversed(st.session_state.food_log)):
                st.markdown(f"""
                <div class="log-entry">
                    <div class="log-time">{entry['meal']}</div>
                    <div class="log-food">{entry['food'][:80]}{'...' if len(entry['food'])>80 else ''}</div>
                    <div class="log-macros">🔥 {entry['calories']} kcal &nbsp;|&nbsp; 💪 {entry['protein']}g protein &nbsp;|&nbsp; 🍞 {entry['carbs']}g carbs &nbsp;|&nbsp; 🥑 {entry['fat']}g fat</div>
                </div>
                """, unsafe_allow_html=True)
            if st.button("🗑️ Clear Log"):
                st.session_state.food_log = []
                st.rerun()

    with col2:
        st.markdown("### 📊 Today's Macros")
        if st.session_state.food_log:
            total_cal  = sum(e["calories"] for e in st.session_state.food_log)
            total_pro  = sum(e["protein"]  for e in st.session_state.food_log)
            total_carb = sum(e["carbs"]    for e in st.session_state.food_log)
            total_fat  = sum(e["fat"]      for e in st.session_state.food_log)

            col_a, col_b = st.columns(2)
            col_a.metric("🔥 Calories",    f"{total_cal}",   f"/{goal_cal} target")
            col_b.metric("💪 Protein",     f"{total_pro}g",  f"/{int(p['weight']*1.8)}g target")
            col_a.metric("🍞 Carbs",       f"{total_carb}g")
            col_b.metric("🥑 Fat",         f"{total_fat}g")

            fig = render_macro_chart(total_pro, total_carb, total_fat)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div class="nutri-card" style="text-align:center;padding:3rem 1rem;">'
                        '<div style="font-size:3rem">📊</div>'
                        '<p style="color:#888">Log meals to see your macro breakdown</p>'
                        '</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — MEAL PLANNER
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📅 AI Meal Plan Generator")
    st.markdown('<div class="nutri-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    days        = col1.selectbox("Plan Duration", ["1 Day","3 Days","7 Days"])
    dietary     = col2.multiselect("Dietary Restrictions",
                                   ["None","Gluten-Free","Dairy-Free","Nut-Free","Halal","Kosher"],
                                   default=["None"])
    cuisine     = col3.selectbox("Cuisine Preference", ["Any","Mediterranean","Asian","Mexican","American","Indian"])
    extra_notes = st.text_input("Any extra notes?", placeholder="e.g. I hate broccoli, love spicy food...")

    if st.button("🤖 Generate My Meal Plan", use_container_width=True):
        if not st.session_state.get("hf_token"):
            st.error("Please add your HuggingFace API token in the sidebar.")
        else:
            with st.spinner("🧠 Building your personalized meal plan..."):
                plan = generate_meal_plan(
                    days=days, dietary=dietary, cuisine=cuisine,
                    profile=st.session_state.profile,
                    notes=extra_notes,
                    token=st.session_state["hf_token"]
                )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("### 🗓️ Your Personalized Meal Plan")
            st.markdown(f'<div class="nutri-card">{plan}</div>', unsafe_allow_html=True)
    else:
        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — RECIPE SUGGESTIONS
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🍳 Recipe Finder from Ingredients")
    st.markdown('<div class="nutri-card">', unsafe_allow_html=True)
    ingredients = st.text_area(
        "What ingredients do you have?",
        placeholder="e.g. chicken breast, spinach, garlic, olive oil, lemon...",
        height=80
    )
    col1, col2 = st.columns(2)
    recipe_goal = col1.selectbox("Recipe Goal", ["High Protein","Low Calorie","Quick (under 20 min)","Comfort Food","Meal Prep"])
    servings    = col2.number_input("Servings", 1, 10, 2)

    if st.button("🔍 Find Recipes", use_container_width=True):
        if not ingredients.strip():
            st.warning("Please list your ingredients.")
        elif not st.session_state.get("hf_token"):
            st.error("Please add your HuggingFace API token in the sidebar.")
        else:
            with st.spinner("🍳 Finding the perfect recipes..."):
                recipes = get_recipe_suggestions(ingredients, recipe_goal, servings,
                                                  st.session_state.profile,
                                                  st.session_state["hf_token"])
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("### 🍽️ Suggested Recipes")
            st.markdown(f'<div class="nutri-card">{recipes}</div>', unsafe_allow_html=True)
    else:
        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — PROGRESS
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📈 Track Your Progress")
    col1, col2 = st.columns([2,1])

    with col2:
        st.markdown('<div class="nutri-card">', unsafe_allow_html=True)
        st.markdown("**Log Today's Weight**")
        today_weight = st.number_input("Weight (kg)", 30.0, 250.0,
                                        value=float(st.session_state.profile["weight"]), step=0.1)
        if st.button("📌 Log Weight"):
            from datetime import date
            st.session_state.weight_log.append({
                "date": str(date.today()),
                "weight": today_weight
            })
            st.success("Weight logged!")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Summary stats ──
        if st.session_state.food_log:
            st.markdown('<div class="nutri-card">', unsafe_allow_html=True)
            st.markdown("**Today's Summary**")
            total = sum(e["calories"] for e in st.session_state.food_log)
            remaining = goal_cal - total
            st.metric("Calories Remaining", f"{max(0,remaining)} kcal",
                      delta=f"{remaining} from goal", delta_color="normal")
            pct = min(100, int(total/goal_cal*100))
            st.progress(pct/100, text=f"{pct}% of daily goal")
            st.markdown('</div>', unsafe_allow_html=True)

    with col1:
        if st.session_state.weight_log:
            fig = render_progress_chart(st.session_state.weight_log)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div class="nutri-card" style="text-align:center;padding:4rem 1rem;">'
                        '<div style="font-size:3rem">📈</div>'
                        '<p style="color:#888">Log your weight daily to see your progress chart!</p>'
                        '</div>', unsafe_allow_html=True)

        # ── Streaks & badges ──
        st.markdown("### 🏆 Achievements")
        meals_logged = len(st.session_state.food_log)
        weights_logged = len(st.session_state.weight_log)
        cols = st.columns(4)
        badges = [
            ("🍽️", "Meals Logged", meals_logged),
            ("⚖️", "Weigh-ins", weights_logged),
            ("🔥", "Calories Tracked", sum(e["calories"] for e in st.session_state.food_log)),
            ("💪", "Protein (g)", sum(e["protein"] for e in st.session_state.food_log)),
        ]
        for col, (icon, label, val) in zip(cols, badges):
            col.markdown(f'<div class="nutri-card" style="text-align:center;">'
                         f'<div style="font-size:2rem">{icon}</div>'
                         f'<div style="font-size:1.4rem;font-weight:700;font-family:Syne,sans-serif">{val}</div>'
                         f'<div style="font-size:0.75rem;color:#888">{label}</div>'
                         f'</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# FOOTER — DOKA CHARLES DANIEL Branding & Legal
# ════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<style>
.footer-wrapper {
    background: linear-gradient(135deg, #1a2e1a 0%, #2d5a27 100%);
    border-radius: 20px;
    padding: 2rem;
    margin-top: 2rem;
    color: #f5f0e8;
}
.footer-brand {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    color: white;
    letter-spacing: 0.02em;
}
.footer-trademark {
    font-size: 0.75rem;
    color: #a8d5a2;
    margin-top: 0.2rem;
}
.footer-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1.5rem;
    margin-top: 1.5rem;
}
.footer-section h4 {
    font-family: 'Syne', sans-serif;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #a8d5a2;
    margin-bottom: 0.6rem;
    font-weight: 700;
}
.footer-section p, .footer-section a {
    font-size: 0.82rem;
    color: #c8e0c5;
    line-height: 1.7;
    text-decoration: none;
}
.footer-section a:hover { color: white; }
.footer-divider { border-color: rgba(255,255,255,0.1); margin: 1.2rem 0; }
.footer-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.75rem;
    color: #7baa77;
}
@media (max-width: 768px) {
    .footer-grid { grid-template-columns: 1fr; }
    .footer-bottom { flex-direction: column; gap: 0.5rem; text-align: center; }
}
</style>

<div class="footer-wrapper">
    <div class="footer-brand">🥗 NutriMind AI™</div>
    <div class="footer-trademark">
        Powered by Streamlit &amp; Hugging Face Transformers &nbsp;·&nbsp;
        Built with ❤️ by <strong>DOKA CHARLES DANIEL</strong>
    </div>

    <div class="footer-grid">
        <div class="footer-section">
            <h4>⚖️ Legal / Trademark</h4>
            <p>NutriMind AI™ — by DOKA CHARLES DANIEL<br>
            The ™ symbol indicates a trademark claim.<br>
            Use ® only after formal registration.<br>
            Do not upload sensitive personal data you do not need.</p>
        </div>
        <div class="footer-section">
            <h4>📧 Contact &amp; Support</h4>
            <p>
                <a href="mailto:charlesdanieldoka@gmail.com">✉️ charlesdanieldoka@gmail.com</a><br>
                <a href="https://github.com/Charles-12345/nutrimind_ai_powered" target="_blank">🐙 GitHub Profile</a><br>
                <a href="https://github.com/Charles-12345/nutrimind-ai_powered#readme" target="_blank">📖 Documentation</a>
            </p>
        </div>
        <div class="footer-section">
            <h4>🤖 Powered By</h4>
            <p>
                LLM: Mistral-7B-Instruct<br>
                UI:  Streamlit<br>
                Charts: Plotly<br>
                AI API: Hugging Face<br>
                IDE: PyCharm &amp; Python 3.10+
            </p>
        </div>
    </div>

    <hr class="footer-divider">

    <div class="footer-bottom">
        <span>NutriMind AI™ — by <strong>DOKA CHARLES DANIEL</strong> &nbsp;·&nbsp; Support: <a href="mailto:charlesdanieldoka@gmail.com" style="color:#7baa77;">charlesdanieldoka@gmail.com</a></span>
        <span>Powered by AI · Created by DOKA CHARLES DANIEL</span>
    </div>
</div>
""", unsafe_allow_html=True)
