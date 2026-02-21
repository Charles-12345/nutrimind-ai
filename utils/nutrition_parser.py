"""
nutrition_parser.py
Handles all AI calls to Mistral-7B-Instruct via HuggingFace Inference API
"""
import re
import json
import streamlit as st

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None

MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"


def _get_client(token: str):
    if InferenceClient is None:
        st.error("huggingface_hub not installed. Run: pip install huggingface-hub")
        return None
    return InferenceClient(model=MODEL_ID, token=token)


def _call_llm(prompt: str, token: str, max_tokens: int = 512) -> str | None:
    client = _get_client(token)
    if not client:
        return None
    try:
        response = client.text_generation(
            prompt,
            max_new_tokens=max_tokens,
            temperature=0.7,
            repetition_penalty=1.1
        )
        return response.strip()
    except Exception as e:
        st.error(f"AI Error: {str(e)}")
        return None


# ── Helpers to extract numbers ─────────────────────────────────────────────
def _extract_int(text: str, keyword: str, default: int = 0) -> int:
    patterns = [
        rf"{keyword}[:\s]+(\d+)",
        rf"(\d+)\s*(?:g|kcal|cal|grams|calories)?[,\s]+{keyword}",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return default


# ── Food Analysis ──────────────────────────────────────────────────────────
def analyze_food(food_description: str, token: str, profile: dict) -> dict | None:
    """
    Sends food description to Mistral and parses back macros + advice.
    """
    prompt = f"""<s>[INST] You are NutriMind, a professional nutritionist AI.

User Profile:
- Goal: {profile['goal']}
- Weight: {profile['weight']}kg
- Activity: {profile['activity']}

The user just ate: "{food_description}"

Please respond in this EXACT format (fill in real numbers):
CALORIES: [number]
PROTEIN: [number]
CARBS: [number]
FAT: [number]
ADVICE: [1-2 sentences of personalized nutrition advice based on their goal]

Only respond with those 5 lines. No extra text. [/INST]"""

    raw = _call_llm(prompt, token, max_tokens=200)
    if not raw:
        return None

    return {
        "calories": _extract_int(raw, "CALORIES", 300),
        "protein":  _extract_int(raw, "PROTEIN",  20),
        "carbs":    _extract_int(raw, "CARBS",    40),
        "fat":      _extract_int(raw, "FAT",      10),
        "advice":   _extract_advice(raw),
    }


def _extract_advice(text: str) -> str:
    m = re.search(r"ADVICE:\s*(.+?)(?:\n|$)", text, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip()
    return "Great job tracking your meals! Consistency is key to reaching your goals."


# ── Meal Plan Generator ────────────────────────────────────────────────────
def generate_meal_plan(days: str, dietary: list, cuisine: str,
                        profile: dict, notes: str, token: str) -> str:
    """
    Generates a personalized multi-day meal plan.
    """
    dietary_str = ", ".join(d for d in dietary if d != "None") or "No restrictions"
    num_days = int(days.split()[0])

    prompt = f"""<s>[INST] You are NutriMind, an expert nutritionist AI.

Create a {num_days}-day meal plan for this person:
- Name: {profile['name']}
- Goal: {profile['goal']}
- Weight: {profile['weight']}kg | Height: {profile['height']}cm | Age: {profile['age']}
- Activity: {profile['activity']}
- Dietary restrictions: {dietary_str}
- Cuisine preference: {cuisine}
- Extra notes: {notes if notes else 'None'}

Format each day clearly with breakfast, lunch, dinner, and a snack.
For each meal include estimated calories and main macros.
Keep it practical, delicious, and aligned with their {profile['goal']} goal.
Use markdown formatting with **bold** headers. [/INST]"""

    result = _call_llm(prompt, token, max_tokens=800)
    return result or "⚠️ Could not generate meal plan. Please check your API token and try again."


# ── Recipe Suggestions ─────────────────────────────────────────────────────
def get_recipe_suggestions(ingredients: str, goal: str, servings: int,
                            profile: dict, token: str) -> str:
    """
    Suggests recipes based on available ingredients.
    """
    prompt = f"""<s>[INST] You are NutriMind, a creative nutritionist and chef AI.

The user has these ingredients: {ingredients}

They want: {goal} recipes for {servings} servings.
Their dietary goal: {profile['goal']}

Please suggest 2 recipes using mainly those ingredients.

For each recipe include:
- **Recipe Name**
- ⏱️ Prep time
- 🍽️ Serves: {servings}
- 📊 Estimated macros per serving
- 📝 Simple step-by-step instructions (5-7 steps)
- 💡 Pro tip

Use clear markdown formatting. Make the recipes sound delicious! [/INST]"""

    result = _call_llm(prompt, token, max_tokens=900)
    return result or "⚠️ Could not generate recipes. Please check your API token and try again."
