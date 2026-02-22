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

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found. Check your .env file.")
else:
    st.success("✅ Gemini API Key Loaded Successfully")
# Both Google SDKs need the API key
os.environ["GEMINI_API_KEY"] = API_KEY 
genai_legacy.configure(api_key=API_KEY)

# Initialize Models
# Legacy SDK used for enforcing strict JSON outputs (MCQ & Quest Generation)
mcq_model = genai_legacy.GenerativeModel('gemini-2.5-flash') 
# Modern SDK used for the AI Judge with Code Execution Tools
judge_client = genai_modern.Client()

st.set_page_config(page_title="The Infinite Dungeon", page_icon="🗡️", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. GAME DATABASES & STATIC CONTENT
# ==========================================
MONSTER_TIERS = {
    1: {"name": "Slime", "img": "assets/monster_1_slime.jpeg"},
    2: {"name": "Goblin", "img": "assets/monster_2_goblin.jpeg"},
    3: {"name": "Warrior", "img": "assets/monster_3.jpeg"},
    4: {"name": "Shadow Mage", "img": "assets/monster_4.jpeg"},
    5: {"name": "Golem", "img": "assets/monster_5.jpeg"},
    6: {"name": "Dragon", "img": "assets/monster_6.jpeg"}
}

SUBJECT_STRUCTURE = {
    "Programming": {
        "DSA": ["Arrays & Strings", "Linked Lists", "Stacks & Queues", "Hash Tables", "Trees", "Graphs", "Heaps & Priority Queues", "Dynamic Programming"],
        "OOPS": ["Classes & Objects", "Inheritance", "Polymorphism", "Abstraction", "Encapsulation", "Design Patterns"],
        "CN": ["OSI Model", "TCP/IP", "Routing Algorithms", "Congestion Control", "DNS & HTTP"],
        "DBMS": ["ER Model", "Normalization", "Transactions", "Indexing", "SQL Joins", "Query Optimization"]
    },
    "Mathematics": ["Algebra", "Calculus", "Probability", "Discrete Math", "Geometry"],
    "Physics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Quantum Mechanics"],
    "Chemistry": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry"],
    "History": ["World War II", "Ancient Rome", "Medieval Europe", "Cold War"],
    "Literature": ["Shakespeare", "Modernism", "Poetry", "Classic Novels"]
}

# Fallback pool if API fails
def two_sum_problem(): return {"title": "Two Sum", "difficulty": "Easy", "function": "two_sum", "description": "Return indices of two numbers such that they add up to target.", "starter": "def two_sum(nums, target):\n    pass", "hints": ["Consider storing values while iterating.", "Which data structure allows fast lookup?"], "theory": "### Hash Tables\nHash tables provide near O(1) lookup operations. Brute force uses O(n²), but hashing can reduce to O(n).", "visible_tests": [{"input": {"nums":[2,7,11,15], "target":9}, "output":[0,1]}, {"input": {"nums":[3,2,4], "target":6}, "output":[1,2]}]}
def rotate_array_problem(): return {"title": "Rotate Array", "difficulty": "Easy", "function": "rotate_array", "description": "Rotate the array to the right by k steps.", "starter": "def rotate_array(nums, k):\n    pass", "hints": ["What happens when k exceeds array length?", "Slicing may help."], "theory": "### Rotation Concept\nUse modulo to normalize steps larger than array size.", "visible_tests": [{"input":{"nums":[1,2,3,4,5], "k":2}, "output":[4,5,1,2,3]}]}
problem_pool = [two_sum_problem, rotate_array_problem]

# ==========================================
# 3. CUSTOM CSS (PREMIUM iOS GLASSMORPHISM)
# ==========================================
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global Typography */
        h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; font-weight: 700 !important; color: #ffffff !important; letter-spacing: -0.5px; }
        .stApp { color: #f5f5f7; font-family: 'Inter', sans-serif; }

        /* Main Glassmorphism Containers - Max Roundness */
        [data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stForm"], [data-testid="stExpander"] {
            background: rgba(20, 25, 35, 0.25) !important;
            backdrop-filter: blur(30px) !important; -webkit-backdrop-filter: blur(30px) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important; border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-radius: 36px !important; 
            box-shadow: 0 16px 40px 0 rgba(0, 0, 0, 0.4) !important;
            transition: all 0.4s ease !important; overflow: hidden;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-8px) scale(1.01) !important;
            box-shadow: 0 20px 50px 0 rgba(0, 122, 255, 0.2) !important; border-color: rgba(0, 122, 255, 0.4) !important;
        }

        /* Sidebar Glassmorphism */
        [data-testid="stSidebar"] {
            background: rgba(10, 12, 18, 0.4) !important;
            backdrop-filter: blur(40px) !important; border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        /* Inner Tabs & General Radios */
        div[role="tablist"], .stAlert {
            background: rgba(255, 255, 255, 0.08) !important; backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 24px !important; 
            color: #ffffff !important; padding: 10px;
        }

        /* Custom Pill-Style Radio Buttons for Hierarchical Bounty Selection */
        div[data-testid="stRadio"] div[role="radiogroup"] {
            flex-wrap: wrap !important; gap: 12px !important; padding: 5px 0 !important; background: transparent !important; border: none !important;
        }
        div[data-testid="stRadio"] label[data-baseweb="radio"] {
            background: rgba(25, 30, 45, 0.4) !important; border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 30px !important; padding: 10px 20px !important; margin-right: 0 !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            backdrop-filter: blur(10px) !important; -webkit-backdrop-filter: blur(10px) !important; color: white !important;
        }
        div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
            background: rgba(0, 122, 255, 0.2) !important; border-color: rgba(0, 212, 255, 0.6) !important;
            transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3) !important;
        }
        div[data-testid="stRadio"] label[data-baseweb="radio"][data-checked="true"] {
            background: linear-gradient(135deg, rgba(0, 122, 255, 0.9), rgba(0, 212, 255, 0.9)) !important;
            border-color: rgba(255, 255, 255, 0.6) !important; box-shadow: 0 6px 20px rgba(0, 122, 255, 0.5) !important;
        }
        div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child {
    display: none !important; /* hides radio circle only */
}

div[data-testid="stRadio"] label[data-baseweb="radio"] div:last-child {
    display: block !important;
    color: white !important;
    font-weight: 600 !important;
}
        div[data-testid="stRadio"] label[data-baseweb="radio"] div { font-weight: 600 !important; letter-spacing: 0.5px !important; color: white !important;}

        /* Premium Breathing Buttons */
        @keyframes pulseGlow {
            0% { box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3); }
            50% { box-shadow: 0 4px 25px rgba(0, 212, 255, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.5); }
            100% { box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3); }
        }
        .stButton button, .stFormSubmitButton button {
            background: linear-gradient(135deg, rgba(0, 122, 255, 0.9), rgba(0, 212, 255, 0.9)) !important;
            backdrop-filter: blur(10px) !important; color: #ffffff !important; border: 1px solid rgba(255, 255, 255, 0.3) !important;
            font-weight: 600 !important; border-radius: 24px !important; 
            padding: 0.6rem 1.2rem !important; width: 100%; animation: pulseGlow 3s infinite alternate;
        }
        .stButton button:hover { transform: translateY(-2px) scale(1.02) !important; animation: none !important; box-shadow: 0 8px 30px rgba(0, 122, 255, 0.8) !important; }

        /* Hacker/Execution Terminal */
        .terminal-box {
            background: rgba(0, 0, 0, 0.65) !important; backdrop-filter: blur(10px); border-radius: 20px; 
            border: 1px solid rgba(0, 255, 136, 0.3); padding: 16px; color: #00FF88; font-family: monospace; min-height: 120px; white-space: pre-wrap; margin-top: 10px;
        }

        /* Images & Inputs */
        [data-testid="stImage"] { display: flex !important; justify-content: center !important; }
        [data-testid="stImage"] img {
            height: 200px !important; width: 100% !important; max-width: 280px !important; object-fit: cover !important; 
            border-radius: 24px !important; box-shadow: 0 8px 24px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.15) !important;
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div { 
            background: rgba(0, 0, 0, 0.2) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; color: white !important; border-radius: 20px !important; 
        }

        /* Advanced RPG Stat Bars (Matches Uploaded Image) */
        .stat-container { margin-bottom: 12px; }
        .stat-label { font-size: 13px; font-weight: 600; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; color: #ccc;}
        .stat-bar-bg { background: rgba(255,255,255,0.05); border-radius: 10px; height: 8px; width: 100%; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);}
        .stat-bar-fill-hp { background: linear-gradient(90deg, #00d2ff, #3a7bd5); height: 100%; border-radius: 10px; transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
        .stat-bar-fill-atk { background: linear-gradient(90deg, #ff416c, #ff4b2b); height: 100%; border-radius: 10px; transition: width 0.5s; }
        .stat-bar-fill-dmg { background: linear-gradient(90deg, #f7b733, #fc4a1a); height: 100%; border-radius: 10px; transition: width 0.5s; }
        .stat-bar-fill-def { background: linear-gradient(90deg, #36D1DC, #5B86E5); height: 100%; border-radius: 10px; transition: width 0.5s; }
        .stat-bar-fill-mag { background: linear-gradient(90deg, #8A2387, #E94057); height: 100%; border-radius: 10px; transition: width 0.5s; }

        /* Hide Streamlit Audio Player Element */
        audio { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. BACKGROUND & AUDIO MANAGERS
# ==========================================
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

# ==========================================
# 5. AI ENGINE WRAPPERS (Dynamic Generation)
# ==========================================
def evaluate_submission(user_code: str, problem_desc: str) -> str:
    """Uses the Modern GenAI SDK + Code Execution to evaluate complexity and hidden tests."""
    execution_prompt = f"""You are a strict, helpful AI judge for a coding platform. 
    PROBLEM: {problem_desc}
    USER CODE: ```python\n{user_code}\n```
    TASKS: 
    1. Generate 3 difficult hidden test cases (edge cases). 
    2. Write an execution block running user's code against tests. 
    3. Run with your Code Execution tool. 
    4. If fail, explain the concept it failed without revealing exact numbers. 
    5. If pass, congratulate them. 
    6. CRITICAL: Analyze Big-O time complexity and append EXACTLY: `TIME_COMPLEXITY: O(X)`"""
    try:
        response = judge_client.models.generate_content(
            model="gemini-2.5-flash", contents=execution_prompt,
            config=types.GenerateContentConfig(tools=[types.Tool(code_execution=types.ToolCodeExecution)])
        )
        return response.text
    except Exception as e: return f"AI Judge Connection Error: {e}"

def generate_coding_problem_json(topic):
    """Generate real-time coding question using Gemini with robust error handling."""
    
    if not API_KEY:
        print("❌ Gemini API key not found.")
        return None

    prompt = f"""
You are a LeetCode-style competitive programming generator.

Generate a brand new coding problem for topic: {topic}.

Return STRICT VALID JSON ONLY.
Do NOT wrap in markdown.
Do NOT explain anything.

Format EXACTLY:

{{
  "title": "Problem Title",
  "difficulty": "Easy/Medium/Hard",
  "function": "function_name",
  "description": "Clear problem explanation.",
  "starter": "def function_name(args):\\n    pass",
  "hints": ["Hint 1", "Hint 2"],
  "theory": "Short markdown explanation of algorithm",
  "visible_tests": [
    {{"input": {{"nums":[1,2]}}, "output": 3}},
    {{"input": {{"nums":[0]}}, "output": 0}}
  ]
}}
"""

    try:
        response = mcq_model.generate_content(prompt)
        raw_text = response.text.strip()

        # Clean markdown if exists
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
        
        data = json.loads(raw_text)

        print("✅ Gemini Problem Generated Successfully")
        return data

    except Exception as e:
        print("❌ Gemini Problem Generation Failed:", e)
        return None

def generate_encounter_json(quest):
    """Generates an MCQ question based on the quest subject."""
    prompt = f"""Topic: {quest['subject']}. Generate a multiple-choice academic question. 
    Return ONLY valid JSON. Do not include markdown blocks.
    Format: {{"monster_name": "str", "story": "str", "question": "str", "options": ["wrong1", "wrong2", "wrong3", "correct"], "answer": "correct"}}"""
    try: 
        res = mcq_model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        clean_text = res.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except: 
        return {"monster_name": quest['monster'], "story": "The magic glitches wildly.", "question": f"What is a core concept of {quest['subject']}?", "options": ["Nothing", "Magic", "Syntax", "Logic"], "answer": "Logic"}

def evaluate_attack_json(question, player_answer, correct_answer):
    """
    Evaluates an MCQ attack using Gemini.
    Returns guaranteed valid dictionary even if Gemini fails.
    """

    is_correct = player_answer == correct_answer

    prompt = f"""
You are an RPG combat narrator.

Question: {question}
Player Answer: {player_answer}
Result: {"SUCCESS" if is_correct else "FAILURE"}

Return STRICT VALID JSON ONLY.
Do NOT use markdown.
Format exactly:
{{
  "damage": integer between 20 and 50,
  "flavor_text": "One short epic combat sentence."
}}
"""

    try:
        response = mcq_model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8
            }
        )

        raw_text = response.text.strip()

        # Remove markdown if Gemini adds it
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw_text)

        # Safety validation
        damage = int(data.get("damage", 30))
        damage = max(20, min(50, damage))

        flavor = str(data.get("flavor_text", "A magical force erupts in the arena!"))

        return {
            "correct": is_correct,
            "damage": damage,
            "flavor_text": flavor
        }

    except Exception as e:
        print("⚠️ Gemini MCQ evaluation error:", e)

        # Controlled fallback (still dynamic feeling)
        fallback_damage = random.randint(20, 50)

        return {
            "correct": is_correct,
            "damage": fallback_damage,
            "flavor_text": "Arcane energy crackles violently through the battlefield!"
        }
# ==========================================
# 6. SESSION STATE INITIALIZATION
# ==========================================
default_states = {
    'current_page': "onboarding", 
    'player_hp': 100, 'player_xp': 0, 'player_level': 1, 
    'player_atk': 75, 'player_dmg': 60, 'player_def': 45, 'player_mag': 80, 
    'monster_hp': 100, 'combat_log': [], 
    'inventory': ["potion_of_debuging", "shield_of_syntax"], 
    'active_quest': None, 'current_encounter': None, 'sound_queue': None, 
    'coding_problem': None, 'user_code': None, 'terminal': "> Awaiting code execution...",
    'bounty_subject': None, 'bounty_domain': None, 'bounty_topic': None
}
for key, val in default_states.items():
    if key not in st.session_state: st.session_state[key] = val

if st.session_state.sound_queue:
    autoplay_audio(st.session_state.sound_queue)
    st.session_state.sound_queue = None 

# ==========================================
# 7. HERO PROFILE SIDEBAR (GAMIFIED UI)
# ==========================================
if st.session_state.current_page != "onboarding":
    with st.sidebar:
        st.markdown(f"<h3 style='text-align: center; margin-bottom: 0px;'>{st.session_state.get('name', 'Hero')}</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888; font-size: 14px; margin-top: 0px;'>Tech Warrior</p>", unsafe_allow_html=True)
        
        try: st.image("assets/hero.jpeg", use_container_width=True)
        except: pass
        
        # Level & XP Bar
        st.markdown(f"<div style='display:flex; justify-content:space-between; font-weight:bold; margin-top:10px;'><span>Level {st.session_state.player_level}</span><span style='color:#00d2ff;'>{st.session_state.player_xp}%</span></div>", unsafe_allow_html=True)
        st.markdown(f"""<div class="stat-bar-bg" style="height:12px; margin-bottom:20px;"><div class="stat-bar-fill-hp" style="width: {st.session_state.player_xp}%;"></div></div>""", unsafe_allow_html=True)
        
        # Advanced Combat Stats
        stats_html = f"""
        <div class="stat-container">
            <div class="stat-label"><span style="color:#00d2ff;">♥</span> Health</div>
            <div class="stat-bar-bg"><div class="stat-bar-fill-hp" style="width: {st.session_state.player_hp}%;"></div></div>
        </div>
        <div class="stat-container">
            <div class="stat-label"><span style="color:#ff416c;">⚔️</span> Attack Power</div>
            <div class="stat-bar-bg"><div class="stat-bar-fill-atk" style="width: {st.session_state.player_atk}%;"></div></div>
        </div>
        <div class="stat-container">
            <div class="stat-label"><span style="color:#f7b733;">💥</span> Burst Damage</div>
            <div class="stat-bar-bg"><div class="stat-bar-fill-dmg" style="width: {st.session_state.player_dmg}%;"></div></div>
        </div>
        <div class="stat-container">
            <div class="stat-label"><span style="color:#36D1DC;">🛡️</span> Base Defense</div>
            <div class="stat-bar-bg"><div class="stat-bar-fill-def" style="width: {st.session_state.player_def}%;"></div></div>
        </div>
        <div class="stat-container">
            <div class="stat-label"><span style="color:#8A2387;">🔮</span> Magic Resistance</div>
            <div class="stat-bar-bg"><div class="stat-bar-fill-mag" style="width: {st.session_state.player_mag}%;"></div></div>
        </div>
        """
        st.markdown(stats_html, unsafe_allow_html=True)

        st.divider()

        # Gamification Placeholders
        with st.expander("🛠️ Skill Tree & Quests"):
            st.button("View Skill Tree", disabled=True, use_container_width=True)
            st.button("Quest Log", disabled=True, use_container_width=True)
            st.button("Achievements", disabled=True, use_container_width=True)
        
        with st.expander("🎁 Reward System"):
            st.button("Claim Daily Reward", disabled=True, use_container_width=True)
            st.button("Leaderboard", disabled=True, use_container_width=True)

        st.divider()

        # Inventory Management
        st.markdown("### 🎒 Inventory")
        if not st.session_state.inventory: st.caption("Bag is empty.")
        for i, item in enumerate(st.session_state.inventory):
            col1, col2 = st.columns([1, 2])
            with col1:
                try: st.image(f"assets/{item}.jpeg")
                except: st.write("🧪")
            with col2:
                if st.button("Use", key=f"use_{i}"):
                    if "potion" in item: 
                        st.session_state.player_hp = min(100, st.session_state.player_hp + 40)
                        st.session_state.combat_log.append("🧪 Recovered 40 HP.")
                    st.session_state.inventory.pop(i)
                    st.rerun()

# ==========================================
# 8. PAGE ROUTING & VIEWS
# ==========================================

# --- VIEW 1: ONBOARDING ---
if st.session_state.current_page == "onboarding":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 3.5rem; text-shadow: 0px 4px 20px rgba(0,255,255,0.4); margin-bottom: 2rem;'>The Infinite Dungeon</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            with st.form("char"):
                st.session_state.name = st.text_input("Adventurer Name", value="Pulkit Goyal")
                if st.form_submit_button("Enter the Dungeon", use_container_width=True):
                    st.session_state.current_page = "board"; st.rerun()

# --- VIEW 2: QUEST BOARD ---
elif st.session_state.current_page == "board":
    st.title("🗺️ The Quest Board")
    
    # Initialize Default Quests Once
    if 'quests' not in st.session_state:
        st.session_state.quests = [
            {"id": 1, "title": "The Slime's Array", "category": "Coding", "subject": "Arrays", "monster": "Slime", "img": MONSTER_TIERS[1]["img"], "desc": "A gelatinous slime absorbs your memory pointers. (Coding Boss)"},
            {"id": 2, "title": "Goblin's Logic Gate", "category": "Math", "subject": "Discrete Math", "monster": "Goblin", "img": MONSTER_TIERS[2]["img"], "desc": "A mischievous goblin guards the AND/OR gates. (MCQ)"},
            {"id": 3, "title": "Golem's Infinite Loop", "category": "Coding", "subject": "Loops", "monster": "Golem", "img": MONSTER_TIERS[5]["img"], "desc": "A stone golem trapped in a while(True) cycle. (Coding Boss)"}
        ]
        
    # --- DYNAMIC AI QUEST GENERATOR ---
    with st.expander("✨ Summon Custom Bounty (Create your own Quest!)"):
        st.markdown("<h4 style='text-align: center; color: #fff; margin-bottom: 1rem;'>Select Your Discipline</h4>", unsafe_allow_html=True)
        
        # Level 1: Subject Selection
        selected_subject = st.radio("Subject", list(SUBJECT_STRUCTURE.keys()), horizontal=True, key="bounty_subject", label_visibility="collapsed")
        
        selected_topic = None

        if selected_subject:
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 1.5rem 0;'>", unsafe_allow_html=True)
            
            # Level 2 & 3: Programming Branch
            if selected_subject == "Programming":
                st.markdown("<h5 style='margin-bottom: 0.5rem; color: #00d2ff;'>Programming Domain</h5>", unsafe_allow_html=True)
                selected_domain = st.radio("Domain", list(SUBJECT_STRUCTURE["Programming"].keys()), horizontal=True, key="bounty_domain", label_visibility="collapsed")
                
                if selected_domain:
                    st.markdown("<br><h5 style='margin-bottom: 0.5rem; color: #00d2ff;'>Specific Topic</h5>", unsafe_allow_html=True)
                    selected_topic = st.radio("Topic", SUBJECT_STRUCTURE["Programming"][selected_domain], horizontal=True, key="bounty_topic", label_visibility="collapsed")
            
            # Level 2: General Branch (Math, History, etc.)
            else:
                st.markdown("<h5 style='margin-bottom: 0.5rem; color: #00d2ff;'>Specific Topic</h5>", unsafe_allow_html=True)
                selected_topic = st.radio("Topic", SUBJECT_STRUCTURE[selected_subject], horizontal=True, key="bounty_topic", label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)

        # Action Execution
        if st.button("Summon Bounty", type="primary", use_container_width=True):
            if not selected_subject or not selected_topic:
                st.warning("⚠️ Please complete your selection hierarchy to summon a bounty.")
            else:
                with st.spinner("The AI is weaving your custom challenge into reality..."):
                    new_cat = "Coding" if selected_subject == "Programming" else selected_subject
                    new_sub = selected_topic

                    # Determine difficulty tier
                    try:
                        res = mcq_model.generate_content(f"Rate complexity of '{new_sub}' from 1-6. Return ONLY JSON: {{\"tier\": <int>}}", generation_config={"response_mime_type": "application/json"})
                        clean_text = res.text.replace("```json", "").replace("```", "").strip()
                        tier = max(1, min(6, int(json.loads(clean_text).get("tier", 3))))
                    except: 
                        tier = random.randint(1, 6)
                    
                    mi = MONSTER_TIERS.get(tier, MONSTER_TIERS[1])
                    
                    new_quest = {
                        "id": len(st.session_state.quests) + 1, 
                        "title": f"The {mi['name']}'s Trial", 
                        "category": new_cat, 
                        "subject": new_sub, 
                        "monster": mi['name'], 
                        "img": mi['img'], 
                        "desc": f"Level {tier} threat focusing on {new_sub}."
                    }
                    
                    # API Call: Pre-generate specific coding problem if applicable
                    if new_cat == "Coding":
                        generated_prob = generate_coding_problem_json(new_sub)
                        if generated_prob: 
                            new_quest['dynamic_problem'] = generated_prob
                    
                    st.session_state.quests.append(new_quest)
                    st.success("Bounty Added! Scroll down to accept the challenge.")

    # Render Active Quests
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
                    # Prepare Arena State
                    st.session_state.active_quest = quest; 
                    st.session_state.monster_hp = 100
                    st.session_state.combat_log = [f"A wild {quest['monster']} appeared from the darkness!"]
                    st.session_state.current_encounter = None; 
                    st.session_state.coding_problem = None 
                    st.session_state.terminal = "> Awaiting code execution..."
                    st.session_state.current_page = "arena"
                    st.rerun()

# --- VIEW 3: THE BATTLE ARENA ---
elif st.session_state.current_page == "arena":
    autoplay_audio("assets/sounds/bgm.mp3", loop=True)
    quest = st.session_state.active_quest

    # ----------------------------------------
    # COMBAT MODE A: THE CODING ARENA
    # ----------------------------------------
    if quest['category'] == "Coding":
        
        # Load logic (Dynamic from AI or Fallback)
        if st.session_state.coding_problem is None:
            if 'dynamic_problem' in quest:
                st.session_state.coding_problem = quest['dynamic_problem']
            else:
                st.session_state.coding_problem = random.choice(problem_pool)()
            st.session_state.user_code = st.session_state.coding_problem.get("starter", "def solve():\n    pass")
            
        prob = st.session_state.coding_problem

        # Boss Header UI
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"<h3 style='text-align: center;'>{quest['monster']}</h3>", unsafe_allow_html=True)
            st.progress(max(0, st.session_state.monster_hp) / 100, text=f"Boss HP: {st.session_state.monster_hp}/100")
            try: st.image(quest['img'], use_container_width=True)
            except: pass
            if st.button("🏃 Flee", use_container_width=True): st.session_state.current_page = "board"; st.rerun()
        with c2:
            with st.container(border=True):
                st.markdown("📜 **Combat Log**")
                for log in reversed(st.session_state.combat_log[-2:]): st.caption(f"> {log}")

        # Coding Environment UI
        left, right = st.columns([1, 1.2], gap="large")
        with left:
            with st.container(border=True):
                st.markdown(f"### {prob.get('title', 'Coding Challenge')}")
                st.info(prob.get('description', 'Solve the problem.'))
                t_cases, t_hints, t_theory = st.tabs(["Test Cases", "Hints", "Theory"])
                with t_cases:
                    for tc in prob.get("visible_tests", []): st.code(f"Input: {tc.get('input', '')}\nOutput: {tc.get('output', '')}", language="python")
                with t_hints:
                    for hint in prob.get("hints", []): st.warning(f"💡 {hint}")
                with t_theory: st.markdown(prob.get("theory", ""))

        with right:
            with st.container(border=True):
                st.markdown("### 💻 Grimoire (Code Editor)")
                user_code = st_ace(value=st.session_state.user_code, language="python", theme="monokai", height=280, auto_update=True)
                st.session_state.user_code = user_code

                if st.button("⚡ CAST SPELL (Execute Code)", type="primary"):
                    try:
                        # 1. Local Pre-check
                        local_env = {}
                        exec(user_code, local_env)
                        func = local_env.get(prob.get("function", "solve"))
                        
                        passed_local = True
                        if func and "visible_tests" in prob:
                            # Safely pass args to function based on generated test cases
                            for tc in prob["visible_tests"]:
                                if isinstance(tc["input"], dict):
                                    if func(**tc["input"]) != tc["output"]: passed_local = False; break
                                else:
                                    if func(tc["input"]) != tc["output"]: passed_local = False; break
                        elif not func:
                            raise ValueError(f"Required function '{prob.get('function')}' not found in your code.")
                        
                        if not passed_local:
                            st.session_state.player_hp -= 20; 
                            st.session_state.combat_log.append("🔴 Spell backfired! Failed basic tests. (-20 HP)")
                            st.session_state.terminal = "Execution failed on visible test cases. Check your logic."
                            st.session_state.sound_queue = "assets/sounds/damage.mp3"
                        else:
                            # 2. Deep AI Check (Code Execution Tools)
                            with st.spinner("The AI Judge is testing hidden edge cases and time complexity..."):
                                ai_feedback = evaluate_submission(user_code, prob.get("description", ""))
                                st.session_state.terminal = ai_feedback
                                
                                if "failed" in ai_feedback.lower() or "error" in ai_feedback.lower():
                                    st.session_state.player_hp -= 15
                                    st.session_state.combat_log.append("⚠️ Failed hidden edge cases! (-15 HP)")
                                    st.session_state.sound_queue = "assets/sounds/damage.mp3"
                                else:
                                    # VICTORY
                                    st.session_state.monster_hp = 0
                                    st.session_state.player_xp += 100
                                    st.session_state.combat_log.append("🟢 MASSIVE HIT! Code is flawless! Boss Defeated! (+100 XP)")
                                    st.session_state.sound_queue = "assets/sounds/win.mp3"

                    except Exception as e:
                        # Fallback for syntax errors
                        st.session_state.player_hp -= 10
                        st.session_state.terminal = f"Runtime/Syntax Error:\n{str(e)}"
                        st.session_state.combat_log.append("💥 SYNTAX ERROR! Your wand exploded. (-10 HP)")
                        st.session_state.sound_queue = "assets/sounds/damage.mp3"

                    # Resolve state after attack
                    if st.session_state.player_hp <= 0: st.session_state.current_page = "game_over"
                    elif st.session_state.monster_hp <= 0:
                        # Level up logic
                        st.session_state.player_level += 1
                        st.session_state.player_xp = 0
                        st.session_state.player_hp = 100
                        st.session_state.player_atk = min(100, st.session_state.player_atk + 5)
                        st.session_state.player_mag = min(100, st.session_state.player_mag + 5)
                        st.session_state.current_page = "board"
                    st.rerun()
            st.markdown(f"<div class='terminal-box'>{st.session_state.terminal}</div>", unsafe_allow_html=True)

    # ----------------------------------------
    # COMBAT MODE B: THE MCQ ARENA (Math/History/Physics etc.)
    # ----------------------------------------
    else:
        if st.session_state.current_encounter is None:
            with st.spinner("Generating spell logic..."): 
                st.session_state.current_encounter = generate_encounter_json(quest)
                st.rerun()

        enc = st.session_state.current_encounter
        arena_col1, arena_col2 = st.columns([1, 1.5], gap="large")

        with arena_col1:
            with st.container(border=True):
                st.markdown(f"<h2 style='text-align: center;'>{enc.get('monster_name', quest['monster'])}</h2>", unsafe_allow_html=True)
                st.progress(max(0, st.session_state.monster_hp) / 100, text=f"Boss HP: {st.session_state.monster_hp}/100")
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
                        res = evaluate_attack_json(enc.get('question'), choice, enc.get('answer'))
                        dmg = res.get("damage", 30)
                        
                        if res.get("correct"):
                            st.session_state.monster_hp -= dmg
                            st.session_state.combat_log.append(f"🟢 HIT! {res.get('flavor_text')} ({dmg} DMG)")
                            st.session_state.sound_queue = "assets/sounds/attack.mp3"
                            if st.session_state.monster_hp > 0: st.session_state.current_encounter = None # Generate next question
                        else:
                            st.session_state.player_hp -= dmg
                            st.session_state.combat_log.append(f"🔴 MISS! {res.get('flavor_text')} ({dmg} DMG)")
                            st.session_state.sound_queue = "assets/sounds/damage.mp3"
                            
                        # Resolve State
                        if st.session_state.player_hp <= 0: st.session_state.current_page = "game_over"
                        elif st.session_state.monster_hp <= 0: 
                            st.session_state.player_xp += 50
                            if st.session_state.player_xp >= 100:
                                st.session_state.player_level += 1
                                st.session_state.player_xp -= 100
                                st.session_state.player_hp = 100
                                st.session_state.player_def = min(100, st.session_state.player_def + 5)
                            st.session_state.current_page = "board"
                    
                    if r1c1.button(options[0], use_container_width=True): attack(options[0]); st.rerun()
                    if r1c2.button(options[1], use_container_width=True): attack(options[1]); st.rerun()
                    if r2c1.button(options[2], use_container_width=True): attack(options[2]); st.rerun()
                    if r2c2.button(options[3], use_container_width=True): attack(options[3]); st.rerun()
                else:
                    if st.button("Magic fizzled. Reroll Question."): st.session_state.current_encounter = None; st.rerun()

# --- VIEW 4: GAME OVER ---
elif st.session_state.current_page == "game_over":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #ff3b30 !important;'>☠️ GAME OVER</h1>", unsafe_allow_html=True)
            st.warning(f"You fell at Level {st.session_state.player_level}. The dungeon claims another soul.")
            if st.button("Resurrect (Restart)", use_container_width=True):
                for key in list(st.session_state.keys()): del st.session_state[key]
                st.rerun()