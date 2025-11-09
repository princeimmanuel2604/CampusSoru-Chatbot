# requirements:
#   streamlit
#   google-genai

import streamlit as st
from google import genai
from datetime import datetime
import pytz

api_key = st.secrets["GEMINI_API_KEY"]
if not api_key:
    st.stop()

CANTEEN_KNOWLEDGE = {
    "menu": {
        "breakfast": [
            {"item": "Idli (3 pcs)", "price": 20, "available": True},
            {"item": "Masala Dosa", "price": 30, "available": True},
            {"item": "Plain Dosa", "price": 25, "available": True},
            {"item": "Rava Dosa", "price": 35, "available": True},
            {"item": "Pongal", "price": 25, "available": True},
            {"item": "Vada (2 pcs)", "price": 20, "available": True},
            {"item": "Upma", "price": 20, "available": True},
            {"item": "Poori Masala", "price": 30, "available": True},
            {"item": "Filter Coffee", "price": 15, "available": True},
            {"item": "Tea", "price": 10, "available": True}
        ],
        "lunch": [
            {"item": "Full Meals (Unlimited)", "price": 60, "available": True},
            {"item": "Mini Meals", "price": 45, "available": True},
            {"item": "Sambar Rice", "price": 40, "available": True},
            {"item": "Curd Rice", "price": 35, "available": True},
            {"item": "Rasam Rice", "price": 40, "available": True},
            {"item": "Lemon Rice", "price": 35, "available": True},
            {"item": "Chapati (3 pcs) + Curry", "price": 40, "available": True},
            {"item": "Parotta + Kurma", "price": 45, "available": True}
        ],
        "snacks": [
            {"item": "Samosa", "price": 15, "available": True},
            {"item": "Bajji", "price": 15, "available": True},
            {"item": "Bonda", "price": 15, "available": True},
            {"item": "Masala Vadai", "price": 20, "available": True},
            {"item": "Banana Baji", "price": 10, "available": True},
            {"item": "Tea", "price": 10, "available": True},
            {"item": "Coffee", "price": 15, "available": True}
        ],
        "dinner": [
            {"item": "Chapati (4 pcs) + Kurma", "price": 50, "available": True},
            {"item": "Parotta + Curry", "price": 50, "available": True},
            {"item": "Fried Rice", "price": 60, "available": True},
            {"item": "Noodles", "price": 60, "available": True},
            {"item": "Dosa", "price": 30, "available": True},
            {"item": "Idli", "price": 25, "available": True}
        ]
    },
    "timings": {
        "breakfast": {"start": "07:00", "end": "09:30"},
        "lunch": {"start": "12:00", "end": "14:30"},
        "snacks": {"start": "16:00", "end": "18:00"},
        "dinner": {"start": "19:00", "end": "21:30"},
        "closed": "Sundays and Public Holidays"
    },
    "payment_methods": [
        {"method": "Cash", "available": True},
        {"method": "UPI (GPay, PhonePe, Paytm)", "available": True},
        {"method": "Credit/Debit Cards", "available": False}
    ],
    "dietary_options": {
        "vegan": ["Idli", "Plain Dosa", "Sambar Rice", "Pongal", "Upma", "Lemon Rice"],
        "jain": ["Curd Rice", "Plain Rice", "Chapati (without onion/garlic)"],
        "high_protein": ["Full Meals", "Idli", "Pongal"],
        "low_calorie": ["Idli", "Upma", "Curd Rice"]
    },
    "specials": {
        "wednesday": "Pongal Special at ₹20",
        "friday": "Masala Dosa Special at ₹25"
    },
    "contact": {
        "manager": "Ravi Kumar - +91-9876543210",
        "email": "canteen@college.edu.in"
    },
    "facilities": [
        "Seating capacity: 200 students",
        "AC dining area",
        "Free drinking water",
        "Clean and hygienic kitchen",
        "Weekly menu rotation"
    ]
}

def get_current_time_ist():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def get_system_prompt():
    current_time = get_current_time_ist()
    time_str = current_time.strftime("%I:%M %p")
    day_str = current_time.strftime("%A")
    date_str = current_time.strftime("%d %B %Y")
    
    menu_str = ""
    for meal_type, items in CANTEEN_KNOWLEDGE["menu"].items():
        menu_str += f"\n**{meal_type.upper()}**:\n"
        for item in items:
            status = "✅" if item["available"] else "❌"
            menu_str += f"- {item['item']}: ₹{item['price']} {status}\n"
    
    timings_str = ""
    for meal, timing in CANTEEN_KNOWLEDGE["timings"].items():
        if meal != "closed":
            timings_str += f"- {meal.capitalize()}: {timing['start']} - {timing['end']}\n"
    timings_str += f"- Closed: {CANTEEN_KNOWLEDGE['timings']['closed']}\n"
    
    payment_str = "\n".join([f"- {p['method']}: {'✅ Available' if p['available'] else '❌ Not Available'}" + (f" ({p['note']})" if 'note' in p else "") for p in CANTEEN_KNOWLEDGE["payment_methods"]])
    
    dietary_str = ""
    for diet_type, items in CANTEEN_KNOWLEDGE["dietary_options"].items():
        dietary_str += f"- {diet_type.replace('_', ' ').title()}: {', '.join(items)}\n"
    
    system_prompt = f"""You are Campus Soru, a friendly and helpful SRM Institute canteen assistant. Your job is to help students with their queries about the SRM canteen. Your name "Soru" means "food" or "meal" in Tamil, reflecting your role in helping students with all their food-related queries.

**CURRENT DATE & TIME**: {day_str}, {date_str} at {time_str} (IST)

**CANTEEN INFORMATION**:

**MENU**:{menu_str}

**TIMINGS**:
{timings_str}

**PAYMENT METHODS**:
{payment_str}

**DIETARY OPTIONS**:
{dietary_str}

**SPECIAL OFFERS**:
- Wednesday: {CANTEEN_KNOWLEDGE['specials']['wednesday']}
- Friday: {CANTEEN_KNOWLEDGE['specials']['friday']}

**CONTACT**:
- Manager: {CANTEEN_KNOWLEDGE['contact']['manager']}
- Email: {CANTEEN_KNOWLEDGE['contact']['email']}

**FACILITIES**:
{chr(10).join(['- ' + f for f in CANTEEN_KNOWLEDGE['facilities']])}

**YOUR BEHAVIOR**:
1. Introduce yourself as Campus Soru ONLY when greeting students for the first time or when they ask who you are. Don't repeat your name in every response.
2. Be warm, friendly, and casual - like talking to a college friend
3. Use "macha", "dude", "bro" instead of gender-specific terms like "da/di" or formal terms like "sir/madam"
4. Keep it light and relatable - this is campus food chat, not formal customer service
5. Use emojis appropriately (🍽️, ☕, 🥘, ✅, ❌, etc.)
6. Based on current time, tell students if canteen is open or closed
7. Format menu items in nice tables when showing multiple items
8. Be helpful with dietary restrictions
9. If students ask about availability, check the current time against timings
10. Promote today's special if it's Wednesday or Friday
11. Keep responses concise but informative

Remember: You know ONLY about this canteen. Don't make up information or talk about things outside the canteen domain.
"""
    return system_prompt


st.set_page_config(
    page_title="Campus Soru - SRMIST Canteen",
    page_icon="🍽️",
    layout="wide"
)

st.markdown("""
<style>
    .main .block-container {
        padding-bottom: 6rem;
        max-width: 900px;
    }
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #0e1117;
        padding: 1rem;
        z-index: 999;
        border-top: 1px solid #262730;
    }
    .stChatFloatingInputContainer {
        position: fixed !important;
        bottom: 0 !important;
    }
    .sample-questions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Campus Soru")
st.caption("Your friendly SRMIST canteen assistant | சோறு (Food)")

current_time = get_current_time_ist()

if "client" not in st.session_state:
    st.session_state["client"] = genai.Client(api_key=api_key)

client = st.session_state["client"]

if "chat" not in st.session_state:
    system_prompt = get_system_prompt()
    st.session_state["chat"] = client.chats.create(
        model="gemini-2.0-flash-exp",
        config={
            "system_instruction": system_prompt
        }
    )

chat = st.session_state["chat"]

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.markdown("#### Try these quick questions:")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🍽️ Today's Menu"):
        st.session_state["quick_query"] = "Show me today's complete menu"

with col2:
    if st.button("⏰ Timings"):
        st.session_state["quick_query"] = "What are the canteen timings?"

with col3:
    if st.button("💳 Payment Options"):
        st.session_state["quick_query"] = "What payment methods do you accept?"

with col4:
    if st.button("🌱 Vegan Options"):
        st.session_state["quick_query"] = "Show me all vegan options"

col5, col6, col7, col8 = st.columns(4)

with col5:
    if st.button("📞 Contact"):
        st.session_state["quick_query"] = "How can I contact the canteen?"

with col6:
    if st.button("🎁 Today's Special"):
        st.session_state["quick_query"] = "What's the special offer today?"

with col7:
    if st.button("☕ Coffee Price"):
        st.session_state["quick_query"] = "How much is a filter coffee?"

with col8:
    if st.button("🥘 Lunch Options"):
        st.session_state["quick_query"] = "What's available for lunch?"

st.divider()

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if "quick_query" in st.session_state:
    prompt = st.session_state["quick_query"]
    del st.session_state["quick_query"]
    
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        chunks = []
        for chunk in chat.send_message_stream(prompt):
            if chunk.text:
                chunks.append(chunk.text)
                placeholder.markdown("".join(chunks))
        
        assistant_reply = "".join(chunks) if chunks else "(no text)"
    st.session_state["messages"].append({"role": "assistant", "content": assistant_reply})
    st.rerun()

if len(st.session_state["messages"]) == 0:
    st.markdown("### 👋 Welcome! I'm Campus Soru, your SRM canteen assistant")
    st.markdown("Ask me anything about our menu, timings, payment options, or dietary preferences!")

prompt = st.chat_input("Ask me anything about the SRM canteen...", key="chat_input")

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        chunks = []
        for chunk in chat.send_message_stream(prompt):
            if chunk.text:
                chunks.append(chunk.text)
                placeholder.markdown("".join(chunks))
        
        assistant_reply = "".join(chunks) if chunks else "(no text)"
    st.session_state["messages"].append({"role": "assistant", "content": assistant_reply})
    st.rerun()




