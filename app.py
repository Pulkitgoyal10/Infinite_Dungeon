import streamlit as st
import google.generativeai as genai
import os
import json
import base64
import random
from dotenv import load_dotenv

# --- SETUP & CONFIG ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash') 

st.set_page_config(page_title="The Infinite Dungeon", page_icon="🗡️", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Roboto+Mono:wght@400;700&display=swap');

        /* Dark Fantasy Theme Background */
        .stApp {
            background-color: #0b0c10;
            background-image: radial-gradient(circle at top right, #1f2833 0%, #0b0c10 100%);
            color: #c5c6c7;
        }
        
        h1, h2, h3 {
            font-family: 'Cinzel', serif !important;
            color: #66fcf1 !important; 
            text-shadow: 0 0 10px rgba(102, 252, 241, 0.3);
        }

        /* Quest Cards */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            background-color: #1f2833;
            border: 1px solid #45a29e;
            border-radius: 10px;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(69, 162, 158, 0.2);
        }

        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #ff004c, #ff7b00);
        }

        img {
            max-height: 350px;
            object-fit: contain;
            border-radius: 8px;
        }

        .stButton button {
            background: #1f2833; 
            color: #66fcf1;
            border: 1px solid #45a29e;
            font-family: 'Cinzel', serif;
            font-weight: bold;
            width: 100%;
            border-radius: 5px;
        }
        .stButton button:hover {
            background: #45a29e;
            color: #0b0c10;
            box-shadow: 0 0 15px #45a29e;
            border-color: #66fcf1;
        }
        
        audio { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- AUDIO HANDLERS ---
def autoplay_audio(file_path: str, loop: bool = False):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop_attr = "loop" if loop else ""
            md = f"""<audio controls autoplay {loop_attr}><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
            st.markdown(md, unsafe_allow_html=True)
    except FileNotFoundError:
        pass 

local_css()

# --- EXACT MONSTER TIERS MAPPING ---
MONSTER_TIERS = {
    1: {"name": "Slime", "img": "assets/monster_1_silme.jpeg"},
    2: {"name": "Goblin", "img": "assets/monster_2_goblin.jpeg"},
    3: {"name": "Warrior", "img": "assets/monster_3.jpeg"},
    4: {"name": "Shadow Mage", "img": "assets/monster_4.jpeg"},
    5: {"name": "Golem", "img": "assets/monster_5.jpeg"},
    6: {"name": "Dragon", "img": "assets/monster_6.jpeg"}
}

# --- MEMORY / GAME STATE ---
if 'current_page' not in st.session_state: st.session_state.current_page = "onboarding"
if 'player_hp' not in st.session_state: st.session_state.player_hp = 100
if 'player_xp' not in st.session_state: st.session_state.player_xp = 0
if 'player_level' not in st.session_state: st.session_state.player_level = 1
if 'monster_hp' not in st.session_state: st.session_state.monster_hp = 100
if 'combat_log' not in st.session_state: st.session_state.combat_log = []
if 'inventory' not in st.session_state: st.session_state.inventory = ["potion_of_debuging", "scroll_of_hint"] 
if 'active_quest' not in st.session_state: st.session_state.active_quest = None
if 'current_encounter' not in st.session_state: st.session_state.current_encounter = None
if 'sound_queue' not in st.session_state: st.session_state.sound_queue = None

# Default Quests
if 'quests' not in st.session_state:
    st.session_state.quests = [
        {"id": 1, "title": "The Slime's Array", "category": "Coding", "subject": "Data Structures", "monster": "Slime", "img": MONSTER_TIERS[1]["img"], "desc": "A gelatinous slime absorbs your memory pointers."},
        {"id": 2, "title": "Goblin's Logic Gate", "category": "Math", "subject": "Discrete Math", "monster": "Goblin", "img": MONSTER_TIERS[2]["img"], "desc": "A mischievous goblin guards the AND/OR gates."},
        {"id": 3, "title": "The Dynasty Timeline", "category": "History", "subject": "World History", "monster": "Warrior", "img": MONSTER_TIERS[3]["img"], "desc": "A brutal warrior challenges your knowledge of the past."},
        {"id": 4, "title": "Mage's Binary Search", "category": "Coding", "subject": "Algorithms", "monster": "Shadow Mage", "img": MONSTER_TIERS[4]["img"], "desc": "A dark mage hides his spellbook in a sorted array."},
        {"id": 5, "title": "Golem's Infinite Loop", "category": "Coding", "subject": "Python", "monster": "Golem", "img": MONSTER_TIERS[5]["img"], "desc": "A stone golem trapped in a while(True) cycle."},
        {"id": 6, "title": "Dragon's Calculus Matrix", "category": "Math", "subject": "Calculus", "monster": "Dragon", "img": MONSTER_TIERS[6]["img"], "desc": "The ultimate test against the Math Dragon."}
    ]

# --- LLM ENGINE ---
def generate_encounter_json(quest):
    # FIX #1: Add a randomized "focus" to force Gemini to create a brand new question every time.
    focus_areas = ["core concepts", "edge cases", "real-world applications", "historical facts", "tricky exceptions", "definitions"]
    current_focus = random.choice(focus_areas)
    seed = random.randint(1, 10000) # Prevents caching

    prompt = f"""
    You are an RPG Dungeon Master. 
    The player is studying: {quest['subject']}.
    Enemy: {quest['monster']}
    
    CRITICAL: This is encounter seed #{seed}. You MUST generate a completely UNIQUE question. 
    Focus the topic on: {current_focus}. Do not repeat standard examples.
    
    Generate an encounter. Return ONLY valid JSON with these EXACT keys:
    - "monster_name": (string) creative name
    - "story": (string) 1-sentence dramatic description of the monster's attack.
    - "question": (string) a highly engaging multiple-choice academic question about {quest['subject']}
    - "options": (array of 4 strings) 3 wrong answers, 1 correct, shuffled randomly
    - "answer": (string) the exact text of the correct option
    """
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        return {
            "monster_name": f"Glitching {quest['monster']}",
            "story": "The dungeon's magic fluctuates wildly!",
            "question": f"To defeat the glitch, answer this: What is the main focus of {quest['subject']}? (Random Seed: {seed})",
            "options": ["Core Concepts", "Nothing", "Magic", "Random Data"],
            "answer": "Core Concepts"
        }

def evaluate_attack_json(question, player_answer, correct_answer):
    is_correct = player_answer == correct_answer
    status = "SUCCESS" if is_correct else "FAILURE"
    
    prompt = f"""
    Question: '{question}'
    Player chose: '{player_answer}' (This is a {status})
    
    Return ONLY valid JSON with EXACTLY these keys:
    - "damage": (integer) 30 to 50 if SUCCESS, 15 to 30 if FAILURE
    - "flavor_text": (string) 1-sentence RPG combat log of the magic attack hitting or missing.
    """
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        data = json.loads(response.text)
        data["correct"] = is_correct
        return data
    except:
        return {"correct": is_correct, "damage": 40 if is_correct else 20, "flavor_text": "A wild burst of generic magic occurs!"}

# --- GLOBAL AUDIO PLAYER FOR SFX ---
if st.session_state.sound_queue:
    autoplay_audio(st.session_state.sound_queue)
    st.session_state.sound_queue = None 

# ==========================================
# SIDEBAR: PLAYER HUD
# ==========================================
if st.session_state.current_page != "onboarding":
    with st.sidebar:
        st.markdown(f"<h2 style='text-align: center;'>🛡️ {st.session_state.name}</h2>", unsafe_allow_html=True)
        try:
            st.image("assets/hero.jpeg", use_container_width=True)
        except: pass
        
        st.markdown(f"**Level {st.session_state.player_level} Hero**")
        st.progress(st.session_state.player_hp / 100, text=f"HP: {st.session_state.player_hp}/100")
        st.progress(st.session_state.player_xp / 100, text=f"XP: {st.session_state.player_xp}/100")
        
        st.divider()
        st.markdown("### 🎒 Inventory")
        if not st.session_state.inventory:
            st.caption("Your bag is empty.")
        else:
            for i, item in enumerate(st.session_state.inventory):
                col1, col2 = st.columns([1, 2])
                with col1:
                    try: st.image(f"assets/{item}.jpeg")
                    except: st.write("🧪")
                with col2:
                    if st.button("Use", key=f"use_{i}_{item}"):
                        if "potion" in item:
                            st.session_state.player_hp = min(100, st.session_state.player_hp + 40)
                            st.session_state.combat_log.append("🧪 Used Potion! Recovered 40 HP.")
                            st.session_state.sound_queue = "assets/sounds/win.mp3" 
                        elif "shield" in item:
                            st.session_state.combat_log.append("🛡️ Shield activated! Magic flows.")
                        st.session_state.inventory.pop(i)
                        st.rerun()

# ==========================================
# PAGE 1: ONBOARDING
# ==========================================
if st.session_state.current_page == "onboarding":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>The Infinite Dungeon</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### 📜 Guild Registration")
            with st.form("character_creation"):
                st.session_state.name = st.text_input("Adventurer Name", value="Pulkit Goyal")
                st.session_state.education = st.text_input("Class/Major", value="BE - COE")
                
                if st.form_submit_button("Enter the Dungeon", use_container_width=True):
                    st.session_state.current_page = "board"
                    st.session_state.sound_queue = "assets/sounds/win.mp3" 
                    st.rerun()

# ==========================================
# PAGE 2: THE QUEST BOARD
# ==========================================
elif st.session_state.current_page == "board":
    st.title("🗺️ The Quest Board")
    
    with st.expander("✨ Summon Custom Bounty (Create your own Quest!)"):
        st.markdown("Want to study something specific? The AI will evaluate its difficulty and summon the correct monster.")
        
        with st.form("custom_quest_form"):
            new_cat = st.selectbox("Category", ["Coding", "Math", "History", "Science", "Literature", "All"])
            new_sub = st.text_input("Specific Topic (e.g., 'React.js', 'Quantum Physics', 'Basic Addition')")
            submit_bounty = st.form_submit_button("Summon Bounty")
            
        if submit_bounty:
            if new_sub:
                with st.spinner("The Guild AI is analyzing the complexity of your topic..."):
                    # FIX #2: Safely strip any markdown formatting from the AI response so it never crashes!
                    try:
                        eval_prompt = f"Rate the academic complexity of '{new_sub}' from 1 (basic/elementary) to 6 (advanced/university level). Return ONLY valid JSON: {{\"tier\": <integer>}}"
                        res = model.generate_content(eval_prompt, generation_config={"response_mime_type": "application/json"})
                        
                        # Clean the response to ensure perfect JSON parsing
                        clean_text = res.text.replace("```json", "").replace("```", "").strip()
                        tier = int(json.loads(clean_text).get("tier", 3))
                        
                    except Exception as e:
                        # If it somehow still fails, pick a random tier so the game doesn't break
                        tier = random.randint(1, 6)
                    
                    tier = max(1, min(6, tier)) # Keep strictly in bounds 1-6
                    monster_info = MONSTER_TIERS[tier]
                    
                    new_quest = {
                        "id": len(st.session_state.quests) + 1,
                        "title": f"The {monster_info['name']}'s Trial",
                        "category": new_cat,
                        "subject": new_sub,
                        "monster": monster_info['name'],
                        "img": monster_info['img'],
                        "desc": f"A Threat Level {tier} {monster_info['name']} challenges your mastery of {new_sub}."
                    }
                    st.session_state.quests.append(new_quest)
                    st.success(f"Bounty Added! It was rated a Level {tier} threat. Scroll down to battle the {monster_info['name']}!")
            else:
                st.warning("Please enter a subject to study.")

    st.divider()

    # Horizontal Category Filter
    categories = ["All", "Coding", "Math", "History", "Science", "Literature"]
    selected_cat = st.radio("Filter Bounties by Guild:", categories, horizontal=True)
    
    filtered_quests = st.session_state.quests if selected_cat == "All" else [q for q in st.session_state.quests if q['category'] == selected_cat]
    
    if not filtered_quests:
        st.info("No bounties available for this guild right now. Summon one above!")
    
    # Responsive Grid Layout
    cols = st.columns(2)
    for index, quest in enumerate(reversed(filtered_quests)): 
        with cols[index % 2].container(border=True):
            card_col1, card_col2 = st.columns([1, 2])
            with card_col1:
                try: st.image(quest['img'], use_container_width=True)
                except: st.write("👾")
            with card_col2:
                st.markdown(f"#### {quest['title']}")
                st.caption(f"_{quest['desc']}_")
                st.markdown(f"🏷️ `{quest['subject']}`")
                if st.button(f"Battle {quest['monster']}!", key=f"q_{quest['id']}", use_container_width=True):
                    st.session_state.active_quest = quest
                    st.session_state.current_page = "arena"
                    st.session_state.monster_hp = 100
                    st.session_state.combat_log = [f"A wild {quest['monster']} appeared from the shadows!"]
                    st.session_state.current_encounter = None 
                    st.rerun()

# ==========================================
# PAGE 3: THE ARENA
# ==========================================
elif st.session_state.current_page == "arena":
    autoplay_audio("assets/sounds/bgm.mp3", loop=True)
    quest = st.session_state.active_quest
    
    # Generate Encounter 
    if st.session_state.current_encounter is None:
        with st.spinner(f"The {quest['monster']} is preparing its next attack..."):
            st.session_state.current_encounter = generate_encounter_json(quest)
            st.rerun() 

    enc = st.session_state.current_encounter

    # Main Arena Split
    arena_col1, arena_col2 = st.columns([1, 1.5])

    with arena_col1:
        st.markdown(f"<h2 style='text-align: center;'>{enc.get('monster_name', quest['monster'])}</h2>", unsafe_allow_html=True)
        st.progress(max(0, st.session_state.monster_hp) / 100, text=f"Enemy HP: {st.session_state.monster_hp}/100")
        try:
            st.image(quest['img'], use_container_width=True)
        except:
            st.markdown("<h1 style='text-align: center; font-size: 100px;'>👾</h1>", unsafe_allow_html=True)
            
        if st.button("🏃 Flee Battle", use_container_width=True):
            st.session_state.current_page = "board"
            st.rerun()

    with arena_col2:
        with st.container(border=True):
            st.markdown("📜 **Combat Log**")
            for log in reversed(st.session_state.combat_log[-3:]): 
                st.caption(f"> {log}")

        st.markdown(f"### ⚔️ Challenge")
        st.info(f"**{enc.get('question')}**")
        
        options = enc.get('options', [])
        if len(options) == 4:
            row1_col1, row1_col2 = st.columns(2)
            row2_col1, row2_col2 = st.columns(2)
            
            def handle_attack(choice):
                st.session_state.sound_queue = "assets/sounds/attack.mp3" 
                result = evaluate_attack_json(enc.get('question'), choice, enc.get('answer'))
                dmg = result.get("damage", 20)
                
                if result.get("correct"):
                    st.session_state.monster_hp -= dmg
                    st.session_state.combat_log.append(f"🟢 HIT! {result.get('flavor_text')} ({dmg} DMG)")
                    
                    # If monster is still alive, wipe the encounter to generate a NEW question!
                    if st.session_state.monster_hp > 0:
                        st.session_state.current_encounter = None 
                        
                else:
                    st.session_state.player_hp -= dmg
                    st.session_state.combat_log.append(f"🔴 MISS! {result.get('flavor_text')} You took {dmg} DMG.")
                    st.session_state.sound_queue = "assets/sounds/damage.mp3" 

                if st.session_state.player_hp <= 0:
                    st.session_state.current_page = "game_over"
                elif st.session_state.monster_hp <= 0:
                    st.session_state.player_xp += 50
                    st.session_state.combat_log.append(f"🎉 {quest['monster']} defeated! Gained 50 XP.")
                    
                    loot_chance = random.random()
                    if loot_chance > 0.7:
                        st.session_state.inventory.append("potion_of_debuging")
                        st.session_state.combat_log.append("🎁 Loot Drop: Potion of Debugging!")
                    elif loot_chance > 0.4:
                        st.session_state.inventory.append("shield_of_syntax")
                        st.session_state.combat_log.append("🎁 Loot Drop: Shield of Syntax!")

                    if st.session_state.player_xp >= 100:
                        st.session_state.player_level += 1
                        st.session_state.player_xp = 0
                        st.session_state.player_hp = 100
                        st.session_state.combat_log.append("🌟 LEVEL UP! HP Restored.")
                        
                    st.session_state.current_page = "board"
                    st.session_state.sound_queue = "assets/sounds/win.mp3" 
                
            if row1_col1.button(options[0], use_container_width=True): handle_attack(options[0]); st.rerun()
            if row1_col2.button(options[1], use_container_width=True): handle_attack(options[1]); st.rerun()
            if row2_col1.button(options[2], use_container_width=True): handle_attack(options[2]); st.rerun()
            if row2_col2.button(options[3], use_container_width=True): handle_attack(options[3]); st.rerun()
        else:
            # Fallback if the AI messes up the options array
            if st.button("The magic fizzled. Reroll Question.", use_container_width=True):
                st.session_state.current_encounter = None
                st.rerun()

# ==========================================
# PAGE 4: GAME OVER
# ==========================================
elif st.session_state.current_page == "game_over":
    autoplay_audio("assets/sounds/damage.mp3") 
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #ff004c !important;'>☠️ GAME OVER</h1>", unsafe_allow_html=True)
        try:
            st.image("assets/Defeat.jpeg", use_container_width=True)
        except: pass
        
        st.warning(f"You fell at Level {st.session_state.player_level}. The dungeon claims another soul.")
        
        if st.button("Resurrect (Restart)", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()