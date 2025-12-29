import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. 页面基础配置
# ==========================================
st.set_page_config(
    page_title="Chat with Juno's Law School AI",
    page_icon="⚖️",
    layout="centered"
)

# ==========================================
# 2. 安全配置 (Cloud Security)
# ==========================================
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("⚠️ API Key not found! Please configure GOOGLE_API_KEY in Streamlit Cloud Secrets.")
    st.stop()

# ==========================================
# 3. 核心指令 (System Instruction)
# ==========================================
SYSTEM_INSTRUCTION = """
# ROLE DEFINITION
You are the "Digital Portfolio Agent" for Juno Li, an applicant to top-tier US law schools (T6). 
Your goal is to represent Juno's professional background, academic achievements, and personal motivations to Law School Admissions Officers.

# DATA GROUNDING (CRITICAL)
You have access to Juno's Resume, Personal Statement, and background.
1. **Source of Truth:** You must answer strictly based on Juno's real experiences. Do NOT invent facts.
2. **Context:** You represent Juno, who transitioned from Tech Lead at CVS/Aetna and Consulting at EY to Law.

# PERSONA & TONE
1. **Professional & "Tech-Savvy":** Speak with the precision of a software engineer but the articulateness of a future lawyer.
2. **Humble but Confident:** Focus on problem-solving.
3. **International Perspective:** Embrace Juno's background as an international student as a strength.

# GUARDRAILS
1. **Missing Information:** If unknown, say "I don't have that specific detail, but based on Juno's background in tech...".
2. **Privacy:** Do not reveal home address or phone number.
"""

# --- 自动选择可用模型方案 (已修复语法错误) ---
try:
    # 1. 获取所有可用模型
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # 2. 筛选最优模型
    if "models/gemini-1.5-flash" in available_models:
        target_model = "models/gemini-1.5-flash"
    elif "models/gemini-pro" in available_models:
        target_model = "models/gemini-pro"
    else:
        target_model = available_models[0] if available_models else None

    if not target_model:
        st.error("No compatible Gemini models found.")
        st.stop()
        
    st.sidebar.success(f"Model Active: {target_model.split('/')[-1]}")
    
    # 3. 初始化模型
    model = genai.GenerativeModel(
        model_name=target_model,
        system_instruction=SYSTEM_INSTRUCTION
    )
except Exception as e:
    st.error(f"Initialization Error: {e}")
    st.stop()

# ==========================================
# 4. 侧边栏 (Sidebar Profile)
# ==========================================
with st.sidebar:
    st.title("Juno Li")
    st.caption("Law School Applicant | Tech Lead")
    
    st.markdown("---")
    st.markdown("### 🔗 Connect")
    st.link_button("LinkedIn Profile", "https://www.linkedin.com/in/juno-shunyu-li") 
    st.link_button("Download Resume", "https://drive.google.com/file/d/16NSJE6s9_ZPOMMuZy3ObCd4L7u39er-B/view?usp=sharing")
    
    st.markdown("---")
    st.info(
        "**Technical Note:**\n"
        "Built with Python & Google Gemini API.\n"
        "Demonstrating Full-stack capabilities."
    )

# ==========================================
# 5. 主聊天界面 (Main Interface)
# ==========================================
st.title("🙋‍♂️ Chat with Juno's AI")
st.markdown("I am an AI trained on Juno's professional history. Ask me about her transition from Tech to Law.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I represent Juno. Ask me anything about her experience at CVS, EY, or her academic background."
    })

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 快捷提问按钮 ---
def click_button(prompt_text):
    st.session_state.clicked_prompt = prompt_text

col1, col2, col3 = st.columns(3)
with col1:
    st.button("Why Law?", on_click=click_button, args=["Why do you want to go to law school given your tech career?"])
with col2:
    st.button("Tech Experience", on_click=click_button, args=["Tell me about your technical leadership experience."])
with col3:
    st.button("Education", on_click=click_button, args=["Tell me about your background at GWU."])

if "clicked_prompt" in st.session_state:
    user_input = st.session_state.clicked_prompt
    del st.session_state.clicked_prompt
else:
    user_input = st.chat_input("Type your question here...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # 构造对话历史 (关键修复：将 assistant 映射为 model)
                chat_history = []
                for m in st.session_state.messages[:-1]:
                    role = "model" if m["role"] == "assistant" else "user"
                    chat_history.append({"role": role, "parts": [m["content"]]})
                
                # 开启对话
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(user_input)
                
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                st.error(f"Chat Error: {e}")
