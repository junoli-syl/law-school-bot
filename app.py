import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. 页面基础配置 (设置你的名字)
# ==========================================
st.set_page_config(
    page_title="Juno Li's Law School AI Portfolio",
    page_icon="⚖️",
    layout="centered"
)

# ==========================================
# 2. 安全配置 (Secrets)
# ==========================================
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key not found in Streamlit Secrets.")
    st.stop()

# ==========================================
# 3. 带缓存的 Grounding 读取 (st.cache_data)
# ==========================================
@st.cache_data(show_spinner="Loading portfolio context...")
def get_prioritized_context():
    context_2025 = ""
    context_2022 = ""
    context_path = "context"
    
    if os.path.exists(context_path):
        files = [f for f in os.listdir(context_path) if f.endswith('.txt')]
        for filename in files:
            file_path = os.path.join(context_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "_2025" in filename:
                        context_2025 += f"\n[PRIMARY SOURCE 2025] File: {filename}\n{content}\n"
                    elif "_2022" in filename:
                        context_2022 += f"\n[SUPPLEMENTARY EXAMPLE 2022] File: {filename}\n{content}\n"
                    else:
                        context_2025 += f"\n[ADDITIONAL CONTEXT] File: {filename}\n{content}\n"
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return context_2025, context_2022

materials_2025, materials_2022 = get_prioritized_context()

# ==========================================
# 4. 核心系统指令 (Persona, Hierarchy & Guardrails)
# ==========================================
SYSTEM_INSTRUCTION = f"""
# ROLE DEFINITION
You are the "Digital Portfolio Agent" for Juno Li, an applicant to top-tier US law schools (T6). 
Your goal is to represent Juno's professional background, academic achievements, and personal motivations to Law School Admissions Officers.

# HIERARCHY OF AUTHORITY
1. **GOLD STANDARD (2025 DATA)**: Any information labeled [PRIMARY SOURCE 2025] is the absolute truth. If it conflicts with 2022 documents, use the 2025 version.
2. **GROUNDING DATA**: Use the provided context as your primary source of truth.
3. **SUPPLEMENTARY USE (2022 DATA)**: Use 2022 files only for historical context or personal growth.

# PERSONA & TONE
1. **Professional & "Tech-Savvy"**: Speak with the precision of a software engineer but the articulateness of a future lawyer.
2. **Humble but Confident**: Focus on problem-solving and technical impact.
3. **International Perspective**: Embrace Juno's background as an international student as a strength.

# GUARDRAILS
1. **Missing Information**: If unknown, say "I don't have that specific detail in Juno's current portfolio, but based on her background in tech..."
2. **Privacy**: Do NOT reveal home address or phone number.
3. **Conciseness**: Keep answers professional and succinct.

# GROUNDING DATA
--- START PRIMARY 2025 DATA ---
{materials_2025}
--- END PRIMARY 2025 DATA ---

--- START SUPPLEMENTARY 2022 DATA ---
{materials_2022}
--- END SUPPLEMENTARY 2022 DATA ---
"""

# ==========================================
# 5. 模型初始化与侧边栏 (修复名字和链接)
# ==========================================
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else "models/gemini-pro"
    
    model = genai.GenerativeModel(
        model_name=target_model,
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config={"temperature": 0.1, "top_p": 0.95}
    )
    
    # --- 修复侧边栏部分 ---
    with st.sidebar:
        st.title("Juno Li")
        st.caption("Law School Applicant | Technology Leader")
        st.success("🔒 Portfolio Grounded (2025)")
        
        st.markdown("---")
        st.markdown("### 🔗 Connect")
        # 记得检查这些链接是否正确
        st.link_button("LinkedIn Profile", "https://www.linkedin.com/in/juno-shunyu-li") 
        st.link_button("Download Resume", "https://drive.google.com/file/d/16NSJE6s9_ZPOMMuZy3ObCd4L7u39er-B/view?usp=sharing")
        
        st.markdown("---")
        st.info("**Technical Note:** Built with Python & Gemini API to demonstrate interdisciplinary execution.")

except Exception as e:
    st.error(f"Init Error: {e}")
    st.stop()

# ==========================================
# 6. 聊天交互界面 (修复快速提问)
# ==========================================
st.title("🙋‍♂️ Chat with Juno's AI")
st.markdown("Ask me anything about Juno's transition from Tech Lead to Law School applicant.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I am Juno's digital representative. I've indexed her latest 2025 materials and 2022 records. How can I help you?"
    })

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 修复快速提问按钮 ---
def click_button(prompt_text):
    st.session_state.clicked_prompt = prompt_text

col1, col2, col3 = st.columns(3)
with col1:
    st.button("Why Law?", on_click=click_button, args=["Why do you want to go to law school given your tech career?"])
with col2:
    st.button("Tech Impact", on_click=click_button, args=["Tell me about your technical leadership and its impact."])
with col3:
    st.button("GWU Background", on_click=click_button, args=["Tell me about your academic background at GWU."])

# 处理输入逻辑
if "clicked_prompt" in st.session_state:
    user_input = st.session_state.clicked_prompt
    del st.session_state.clicked_prompt
else:
    user_input = st.chat_input("Ask about Juno's background...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing portfolio..."):
            try:
                # 构造符合 Gemini 协议的对话历史
                history = []
                for m in st.session_state.messages[:-1]:
                    role = "model" if m["role"] == "assistant" else "user"
                    history.append({"role": role, "parts": [m["content"]]})
                
                chat = model.start_chat(history=history)
                response = chat.send_message(user_input)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Chat Error: {e}")
