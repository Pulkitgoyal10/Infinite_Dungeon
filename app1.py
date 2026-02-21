import streamlit as st
import google.generativeai as genai_legacy
from google import genai as genai_modern
from google.genai import types
from streamlit_ace import st_ace
import os
import json
import base64
import random
from dotenv import load_dotenv

# --- SETUP & CONFIG ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Both SDKs need the API key
os.environ["GEMINI_API_KEY"] = API_KEY 
genai_legacy.configure(api_key=API_KEY)

# Initialize Models
mcq_model = genai_legacy.GenerativeModel('gemini-2.5-flash') 
judge_client = genai_modern.Client()

st.set_page_config(page_title="The Infinite Dungeon", page_icon="🗡️", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS (PREMIUM iOS GLASSMORPHISM - ROUNDER CORNERS) ---
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; font-weight: 700 !important; color: #ffffff !important; letter-spacing: -0.5px; }
        .stApp { color: #f5f5f7; font-family: 'Inter', sans-serif; }

        /* Glassmorphism Containers - INCREASED ROUNDNESS */
        [data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stForm"], [data-testid="stExpander"] {
            background: rgba(20, 25, 35, 0.25) !important;
            backdrop-filter: blur(30px) !important; -webkit-backdrop-filter: blur(30px) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important; border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-radius: 36px !important; /* Increased from 24px */
            box-shadow: 0 16px 40px 0 rgba(0, 0, 0, 0.4) !important;
            transition: all 0.4s ease !important; overflow: hidden;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-8px) scale(1.01) !important;
            box-shadow: 0 20px 50px 0 rgba(0, 122, 255, 0.2) !important; border-color: rgba(0, 122, 255, 0.4) !important;
        }

        [data-testid="stSidebar"] {
            background: rgba(10, 12, 18, 0.4) !important;
            backdrop-filter: blur(40px) !important; border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        /* Tabs & Radios - ROUNDER */
        div[role="radiogroup"], .stAlert, div[role="tablist"] {
            background: rgba(255, 255, 255, 0.08) !important; backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important; 
            border-radius: 24px !important; /* Increased from 16px */
            color: #ffffff !important; padding: 10px;
        }
        div[role="radiogroup"] label { color: white !important; font-weight: 500 !important; }

        /* Breathing Buttons - ROUNDER */
        @keyframes pulseGlow {
            0% { box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3); }
            50% { box-shadow: 0 4px 25px rgba(0, 212, 255, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.5); }
            100% { box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3); }
        }

        .stButton button, .stFormSubmitButton button {
            background: linear-gradient(135deg, rgba(0, 122, 255, 0.9), rgba(0, 212, 255, 0.9)) !important;
            backdrop-filter: blur(10px) !important; color: #ffffff !important; border: 1px solid rgba(255, 255, 255, 0.3) !important;
            font-weight: 600 !important; 
            border-radius: 24px !important; /* Increased from 16px */
            padding: 0.6rem 1.2rem !important; width: 100%; animation: pulseGlow 3s infinite alternate;
        }
        .stButton button:hover { transform: translateY(-2px) scale(1.02) !important; animation: none !important; box-shadow: 0 8px 30px rgba(0, 122, 255, 0.8) !important; }

        /* Terminal Box - ROUNDER */
        .terminal-box {
            background: rgba(0, 0, 0, 0.65) !important; backdrop-filter: blur(10px); 
            border-radius: 20px; /* Increased from 12px */
            border: 1px solid rgba(0, 255, 136, 0.3); padding: 16px; color: #00FF88; font-family: monospace; min-height: 120px; white-space: pre-wrap; margin-top: 10px;
        }

        /* Images & Inputs - ROUNDER */
        [data-testid="stImage"] { display: flex !important; justify-content: center !important; }
        [data-testid="stImage"] img {
            height: 200px !important; width: 100% !important; max-width: 280px !important; object-fit: cover !important; 
            border-radius: 24px !important; /* Increased from 16px */
            box-shadow: 0 8px 24px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.15) !important;
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div { 
            background: rgba(0, 0, 0, 0.2) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: white !important; 
            border-radius: 20px !important; /* Increased from 12px */
        }
        .stProgress > div > div > div > div { background-image: linear-gradient(to right, #007aff, #00d4ff) !important; border-radius: 20px !important; }
        audio { display: none; }
    </style>
    """, unsafe_allow_html=True)

def set_background(video_file: str, image_file: str):
    b64_image = ""
    try:
        with open(image_file, "rb") as f: b64_image = base64.b64encode(f.read()).decode()
    except: pass
    try:
        with open(video_file, "rb") as f: b64_video = base64.b64encode(f.read()).decode()
        st.markdown(f'<style>#myVideo {{ position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%; z-index: -100; object-fit: cover; filter: brightness(0.4); }} .stApp {{ background: transparent !important; }}</style><video autoplay muted loop id="myVideo" poster="data:image/png;base64,{b64_image}"><source src="data:video/mp4;base64,{b64_video}" type="video/mp4"></video>', unsafe_allow_html=True)
    except:
        if b64_image: st.markdown(f'<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/png;base64,{b64_image}") !important; background-size: cover !important; background-attachment: fixed !important; }}</style>', unsafe_allow_html=True)

def autoplay_audio(file_path: str, loop: bool = False):
    try:
        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio controls autoplay {"loop" if loop else ""}><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass 

local_css()
set_background("assets/bg_loop.mp4", "assets/bg.jpeg")

MONSTER_TIERS = {
    1: {"name": "Slime", "img": "assets/monster_1_slime.jpeg"},
    2: {"name": "Goblin", "img": "assets/monster_2_goblin.jpeg"},
    3: {"name": "Warrior", "img": "assets/monster_3.jpeg"},
    4: {"name": "Shadow Mage", "img": "assets/monster_4.jpeg"},
    5: {"name": "Golem", "img": "assets/monster_5.jpeg"},
    6: {"name": "Dragon", "img": "assets/monster_6.jpeg"}
}

# --- CODING PROBLEM POOL ---
def two_sum_problem(): return {"title": "Two Sum", "difficulty": "Easy", "function": "two_sum", "description": "Return indices of two numbers such that they add up to target.", "starter": "def two_sum(nums, target):\n    pass", "hints": ["Consider storing values while iterating.", "Which data structure allows fast lookup?"], "theory": "### Hash Tables\nHash tables provide near O(1) lookup operations. Brute force uses O(n²), but hashing can reduce to O(n).", "visible_tests": [{"input": {"nums":[2,7,11,15], "target":9}, "output":[0,1]}, {"input": {"nums":[3,2,4], "target":6}, "output":[1,2]}]}
def rotate_array_problem(): return {"title": "Rotate Array", "difficulty": "Easy", "function": "rotate_array", "description": "Rotate the array to the right by k steps.", "starter": "def rotate_array(nums, k):\n    pass", "hints": ["What happens when k exceeds array length?", "Slicing may help."], "theory": "### Rotation Concept\nUse modulo to normalize steps larger than array size.", "visible_tests": [{"input":{"nums":[1,2,3,4,5], "k":2}, "output":[4,5,1,2,3]}]}
def palindrome_problem(): return {"title": "Palindrome Check", "difficulty": "Easy", "function": "is_palindrome", "description": "Return True if the string is a palindrome.", "starter": "def is_palindrome(s):\n    pass", "hints": ["Compare characters from both ends.", "Reversing the string might help."], "theory": "### Two Pointer Technique\nComparing from both ends reduces comparisons.", "visible_tests": [{"input":{"s":"racecar"}, "output":True}, {"input":{"s":"hello"}, "output":False}]}
problem_pool = [two_sum_problem, rotate_array_problem, palindrome_problem]

# --- AI ENGINES ---
def evaluate_submission(user_code: str, problem_desc: str) -> str:
    execution_prompt = f"""You are a strict AI judge. 
    PROBLEM: {problem_desc}
    USER CODE: ```python\n{user_code}\n```
    TASKS: 1. Generate 3 hidden test cases. 2. Write execution block. 3. Run with Code Execution tool. 4. If fail, explain concept failed without revealing numbers. 5. If pass, congratulate. 6. Analyze Big-O time complexity and append EXACTLY: `TIME_COMPLEXITY: O(X)`"""
    try:
        response = judge_client.models.generate_content(
            model="gemini-2.5-flash", contents=execution_prompt,
            config=types.GenerateContentConfig(tools=[types.Tool(code_execution=types.ToolCodeExecution)])
        )
        return response.text
    except Exception as e: return f"AI Judge Error: {e}"

def generate_encounter_json(quest):
    prompt = f"Topic: {quest['subject']}. Generate a multiple-choice academic question. Return ONLY JSON: {{\"monster_name\": \"str\", \"story\": \"str\", \"question\": \"str\", \"options\": [\"wrong1\", \"wrong2\", \"wrong3\", \"correct\"], \"answer\": \"correct\"}}"
    try: return json.loads(mcq_model.generate_content(prompt, generation_config={"response_mime_type": "application/json"}).text)
    except: return {"monster_name": quest['monster'], "story": "Magic glitches.", "question": "What is 2+2?", "options": ["3", "4", "5", "6"], "answer": "4"}

def evaluate_attack_json(question, player_answer, correct_answer):
    is_correct = player_answer == correct_answer
    prompt = f"Question: '{question}', Chose: '{player_answer}' ({'SUCCESS' if is_correct else 'FAILURE'}). Return ONLY JSON: {{\"damage\": <int 20-50>, \"flavor_text\": \"1-sentence log.\"}}"
    try:
        data = json.loads(mcq_model.generate_content(prompt, generation_config={"response_mime_type": "application/json"}).text)
        data["correct"] = is_correct; return data
    except: return {"correct": is_correct, "damage": 30, "flavor_text": "A raw magic blast fires!"}

# --- STATE MANAGEMENT ---
for key, val in {'current_page': "onboarding", 'player_hp': 100, 'player_xp': 0, 'player_level': 1, 'monster_hp': 100, 'combat_log': [], 'inventory': ["potion_of_debuging", "shield_of_syntax"], 'active_quest': None, 'current_encounter': None, 'sound_queue': None, 'coding_problem': None, 'user_code': None, 'terminal': "> Awaiting code execution..."}.items():
    if key not in st.session_state: st.session_state[key] = val

if st.session_state.sound_queue:
    autoplay_audio(st.session_state.sound_queue); st.session_state.sound_queue = None 

# --- HUD SIDEBAR ---
if st.session_state.current_page != "onboarding":
    with st.sidebar:
        st.markdown(f"<h2 style='text-align: center;'>🛡️ {st.session_state.get('name', 'Hero')}</h2>", unsafe_allow_html=True)
        try: st.image("assets/hero.jpeg", use_container_width=True)
        except: pass
        st.markdown(f"**Level {st.session_state.player_level} Hero**")
        st.progress(st.session_state.player_hp / 100, text=f"HP: {st.session_state.player_hp}/100")
        st.progress(st.session_state.player_xp / 100, text=f"XP: {st.session_state.player_xp}/100")
        st.divider()
        st.markdown("### 🎒 Inventory")
        if not st.session_state.inventory: st.caption("Empty.")
        for i, item in enumerate(st.session_state.inventory):
            col1, col2 = st.columns([1, 2])
            with col1:
                try: st.image(f"assets/{item}.jpeg")
                except: st.write("🧪")
            with col2:
                if st.button("Use", key=f"use_{i}"):
                    if "potion" in item: st.session_state.player_hp = min(100, st.session_state.player_hp + 40); st.session_state.combat_log.append("🧪 Recovered 40 HP.")
                    st.session_state.inventory.pop(i); st.rerun()

# --- PAGE ROUTING ---
if st.session_state.current_page == "onboarding":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>The Infinite Dungeon</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            with st.form("char"):
                st.session_state.name = st.text_input("Adventurer Name", value="Pulkit Goyal")
                if st.form_submit_button("Enter the Dungeon", use_container_width=True):
                    st.session_state.current_page = "board"; st.rerun()

elif st.session_state.current_page == "board":
    st.title("🗺️ The Quest Board")
    
    if 'quests' not in st.session_state:
        st.session_state.quests = [
            {"id": 1, "title": "The Slime's Array", "category": "Coding", "subject": "Arrays", "monster": "Slime", "img": MONSTER_TIERS[1]["img"], "desc": "A gelatinous slime absorbs your memory pointers. (Coding Boss)"},
            {"id": 2, "title": "Goblin's Logic Gate", "category": "Math", "subject": "Discrete Math", "monster": "Goblin", "img": MONSTER_TIERS[2]["img"], "desc": "A mischievous goblin guards the AND/OR gates. (MCQ)"},
            {"id": 3, "title": "Golem's Infinite Loop", "category": "Coding", "subject": "Loops", "monster": "Golem", "img": MONSTER_TIERS[5]["img"], "desc": "A stone golem trapped in a while(True) cycle. (Coding Boss)"}
        ]
        
    with st.expander("✨ Summon Custom Bounty (Create your own Quest!)"):
        with st.form("custom_quest_form"):
            new_cat = st.selectbox("Category", ["Coding", "Math", "History", "Science", "Literature"])
            new_sub = st.text_input("Specific Topic (e.g., 'React.js', 'Quantum Physics')")
            if st.form_submit_button("Summon Bounty") and new_sub:
                with st.spinner("Analyzing complexity..."):
                    try:
                        res = mcq_model.generate_content(f"Rate complexity of '{new_sub}' from 1-6. Return ONLY JSON: {{\"tier\": <int>}}", generation_config={"response_mime_type": "application/json"})
                        tier = max(1, min(6, int(json.loads(res.text.replace("```json", "").replace("```", "").strip()).get("tier", 3))))
                    except: tier = random.randint(1, 6)
                    mi = MONSTER_TIERS.get(tier, MONSTER_TIERS[1])
                    st.session_state.quests.append({"id": len(st.session_state.quests)+1, "title": f"The {mi['name']}'s Trial", "category": new_cat, "subject": new_sub, "monster": mi['name'], "img": mi['img'], "desc": f"Level {tier} threat focusing on {new_sub}."})
                    st.success("Bounty Added!")

    cols = st.columns(2)
    for index, quest in enumerate(reversed(st.session_state.quests)): 
        with cols[index % 2].container(border=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                try: st.image(quest['img'])
                except: st.write("👾")
            with c2:
                st.markdown(f"#### {quest['title']}"); st.caption(f"_{quest['desc']}_"); st.markdown(f"🏷️ `{quest['category']}`")
                if st.button(f"Battle {quest['monster']}!", key=f"q_{quest['id']}"):
                    st.session_state.active_quest = quest; st.session_state.monster_hp = 100
                    st.session_state.combat_log = [f"A wild {quest['monster']} appeared!"]
                    st.session_state.current_encounter = None; st.session_state.coding_problem = None 
                    st.session_state.terminal = "> Awaiting code execution..."; st.session_state.current_page = "arena"; st.rerun()

elif st.session_state.current_page == "arena":
    autoplay_audio("assets/sounds/bgm.mp3", loop=True)
    quest = st.session_state.active_quest

    # --- CODING ARENA ---
    if quest['category'] == "Coding":
        if st.session_state.coding_problem is None:
            st.session_state.coding_problem = random.choice(problem_pool)(); st.session_state.user_code = st.session_state.coding_problem["starter"]
        prob = st.session_state.coding_problem

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"<h3 style='text-align: center;'>{quest['monster']}</h3>", unsafe_allow_html=True); st.progress(st.session_state.monster_hp / 100, text=f"Boss HP: {st.session_state.monster_hp}/100")
            # FIX: Added image display here
            try: st.image(quest['img'], use_container_width=True)
            except: pass
            if st.button("🏃 Flee", use_container_width=True): st.session_state.current_page = "board"; st.rerun()
        with c2:
            with st.container(border=True):
                st.markdown("📜 **Combat Log**")
                for log in reversed(st.session_state.combat_log[-2:]): st.caption(f"> {log}")

        left, right = st.columns([1, 1.2], gap="large")
        with left:
            with st.container(border=True):
                st.markdown(f"### {prob['title']}")
                st.info(prob['description'])
                t_cases, t_hints, t_theory = st.tabs(["Test Cases", "Hints", "Theory"])
                with t_cases:
                    for tc in prob["visible_tests"]: st.code(f"Input: {tc['input']}\nOutput: {tc['output']}", language="python")
                with t_hints:
                    for hint in prob["hints"]: st.warning(f"💡 {hint}")
                with t_theory: st.markdown(prob["theory"])

        with right:
            with st.container(border=True):
                st.markdown("### 💻 Grimoire (Code Editor)")
                user_code = st_ace(value=st.session_state.user_code, language="python", theme="monokai", height=250, auto_update=True)
                st.session_state.user_code = user_code

                if st.button("⚡ CAST SPELL (Execute Code)", type="primary"):
                    try:
                        local_env = {}; exec(user_code, local_env)
                        func = local_env.get(prob["function"])
                        passed_local = all(func(**tc["input"]) == tc["output"] for tc in prob["visible_tests"]) if func else False
                        
                        if not passed_local:
                            st.session_state.player_hp -= 20; st.session_state.combat_log.append("🔴 Spell backfired! Failed basic tests. (-20 HP)")
                            st.session_state.terminal = "Execution failed on visible test cases."; st.session_state.sound_queue = "assets/sounds/damage.mp3"
                        else:
                            with st.spinner("AI evaluating complexity..."):
                                ai_feedback = evaluate_submission(user_code, prob["description"])
                                st.session_state.terminal = ai_feedback
                                if "failed" in ai_feedback.lower() or "error" in ai_feedback.lower():
                                    st.session_state.player_hp -= 15; st.session_state.combat_log.append("⚠️ Failed hidden edge cases! (-15 HP)"); st.session_state.sound_queue = "assets/sounds/damage.mp3"
                                else:
                                    st.session_state.monster_hp = 0; st.session_state.player_xp += 100
                                    st.session_state.combat_log.append("🟢 MASSIVE HIT! Code flawless! Boss Defeated! (+100 XP)"); st.session_state.sound_queue = "assets/sounds/win.mp3"

                    except Exception as e:
                        st.session_state.player_hp -= 10; st.session_state.terminal = f"Runtime Error:\n{str(e)}"
                        st.session_state.combat_log.append("💥 SYNTAX ERROR! Your wand exploded. (-10 HP)")

                    if st.session_state.player_hp <= 0: st.session_state.current_page = "game_over"
                    elif st.session_state.monster_hp <= 0:
                        st.session_state.player_level += 1; st.session_state.player_xp = 0; st.session_state.player_hp = 100
                        st.session_state.current_page = "board"
                    st.rerun()
            st.markdown(f"<div class='terminal-box'>{st.session_state.terminal}</div>", unsafe_allow_html=True)

    # --- MCQ ARENA ---
    else:
        if st.session_state.current_encounter is None:
            with st.spinner("Generating spell logic..."): st.session_state.current_encounter = generate_encounter_json(quest); st.rerun()

        enc = st.session_state.current_encounter
        arena_col1, arena_col2 = st.columns([1, 1.5], gap="large")

        with arena_col1:
            with st.container(border=True):
                st.markdown(f"<h2 style='text-align: center;'>{enc.get('monster_name', quest['monster'])}</h2>", unsafe_allow_html=True); st.progress(max(0, st.session_state.monster_hp) / 100, text=f"Boss HP: {st.session_state.monster_hp}/100")
                try: st.image(quest['img'])
                except: pass
                if st.button("🏃 Flee", use_container_width=True): st.session_state.current_page = "board"; st.rerun()

        with arena_col2:
            with st.container(border=True):
                st.markdown("📜 **Combat Log**")
                for log in reversed(st.session_state.combat_log[-3:]): st.caption(f"> {log}")
            
            with st.container(border=True):
                st.info(f"**{enc.get('question')}**")
                options = enc.get('options', [])
                if len(options) == 4:
                    r1c1, r1c2 = st.columns(2); r2c1, r2c2 = st.columns(2)
                    def attack(choice):
                        res = evaluate_attack_json(enc.get('question'), choice, enc.get('answer')); dmg = res.get("damage", 30)
                        if res.get("correct"):
                            st.session_state.monster_hp -= dmg; st.session_state.combat_log.append(f"🟢 HIT! {res.get('flavor_text')} ({dmg} DMG)")
                            st.session_state.sound_queue = "assets/sounds/attack.mp3"
                            if st.session_state.monster_hp > 0: st.session_state.current_encounter = None
                        else:
                            st.session_state.player_hp -= dmg; st.session_state.combat_log.append(f"🔴 MISS! {res.get('flavor_text')} ({dmg} DMG)")
                            st.session_state.sound_queue = "assets/sounds/damage.mp3"
                        if st.session_state.player_hp <= 0: st.session_state.current_page = "game_over"
                        elif st.session_state.monster_hp <= 0: st.session_state.player_xp += 50; st.session_state.current_page = "board"
                    
                    if r1c1.button(options[0], use_container_width=True): attack(options[0]); st.rerun()
                    if r1c2.button(options[1], use_container_width=True): attack(options[1]); st.rerun()
                    if r2c1.button(options[2], use_container_width=True): attack(options[2]); st.rerun()
                    if r2c2.button(options[3], use_container_width=True): attack(options[3]); st.rerun()
                else:
                    if st.button("Magic fizzled. Reroll Question."): st.session_state.current_encounter = None; st.rerun()

elif st.session_state.current_page == "game_over":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #ff3b30 !important;'>☠️ GAME OVER</h1>", unsafe_allow_html=True)
            st.warning(f"You fell at Level {st.session_state.player_level}.")
            if st.button("Resurrect"):
                for key in list(st.session_state.keys()): del st.session_state[key]
                st.rerun()