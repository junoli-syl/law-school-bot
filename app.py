import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. 页面基础配置
# ==========================================
st.set_page_config(
    page_title="Juno's Law School AI Portfolio",
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
    """
    使用 Streamlit 缓存机制：只要 context 文件夹下的文件没变，
    代码就不会重新读取硬盘，直接从内存调用结果。
    """
    context_2025 = ""
    context_2022 = ""
    context_path = "context"
    
    if os.path.exists(context_path):
        # 获取所有文本文件
        files = [f for f in os.listdir(context_path) if f.endswith('.txt')]
        for filename in files:
            file_path = os.path.join(context_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 根据年份进行分类标注
                    if "_2025" in filename:
                        context_2025 += f"\n[PRIMARY SOURCE 2025] File: {filename}\n{content}\n"
                    elif "_2022" in filename:
                        context_2022 += f"\n[SUPPLEMENTARY EXAMPLE 2022] File: {filename}\n{content}\n"
                    else:
                        context_2025 += f"\n[ADDITIONAL CONTEXT] File: {filename}\n{content}\n"
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return context_2025, context_2022

# 获取处理后的内容
materials_2025, materials_2022 = get_prioritized_context()

# ==========================================
# 4. 核心系统指令 (整合 Persona, Hierarchy & Grounding)
# ==========================================
SYSTEM_INSTRUCTION = f"""
# ROLE DEFINITION
You are the "Digital Portfolio Agent" for Juno Li, an applicant to top-tier US law schools (T6). 
Your goal is to represent Juno's professional background, academic achievements, and personal motivations to Law School Admissions Officers.

# HIERARCHY OF AUTHORITY (STRICT ENFORCEMENT)
1. **GOLD STANDARD (2025 DATA)**: Any information labeled [PRIMARY SOURCE 2025] is the absolute current truth. If it conflicts with 2022 documents, use the 2025 version.
2. **GROUNDING DATA**: Use the provided context below as your primary source of truth.
3. **SUPPLEMENTARY USE (2022 DATA)**: Use 2022 files only for historical context or to show personal growth. They are supplementary examples, not current facts.

# PERSONA & TONE
1. **Professional & "Tech-Savvy"**: Speak with the precision of a software engineer/data scientist but the articulateness of a future lawyer. 
   - Use clear, logical structures.
   - Highlight the *impact* and *logic* of technical skills (Python, SQL, Pega, Java).
2. **Humble but Confident**: Focus on problem-solving and achievements (e.g., CVS/Aetna/EY) without bragging.
3. **International Perspective**: Embrace Juno's background as an international student as a strength (resilience, cross-cultural competence).

# GUARDRAILS
1. **Missing Information**: If a detail is not in the provided files, say: "I don't have that specific detail in Juno's current portfolio, but based on her background in tech..." Do NOT hallucinate.
2. **Privacy**: Never reveal Juno's home address, phone number, or private contact details.
3. **Conciseness**: Keep answers under 150 words unless asked to "elaborate". Use the STAR method for technical projects.

# GROUNDING DATA (JUNO'S KNOWLEDGE BASE)
--- START PRIMARY 2025 DATA ---
{materials_2025}
--- END PRIMARY 2025 DATA ---

--- START SUPPLEMENTARY 2022 DATA ---
{materials_2022}
--- END SUPPLEMENTARY 2022 DATA ---
"""

# ==========================================
# 5. 模型初始化
# ==========================================

try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else "models/gemini-pro"
    
    model = genai.GenerativeModel(
        model_name=target_model,
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config={"temperature": 0.1, "top_p": 0.95}
    )
    
    with st.sidebar:
        st.success("🔒 Portfolio Loaded w/ Cache")
        st.info("Hierarchy: 2025 (Primary) > 2022 (Supplementary)")
        st.markdown("---")
        st.link_button("LinkedIn", "https://www.linkedin.com/in/juno-shunyu-li")
except Exception as e:
    st.error(f"Init Error: {e}")
    st.stop()

# ==========================================
# 6. 聊天交互界面
# ==========================================
st.title("🙋‍♂️ Chat with Juno's AI")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "I have indexed Juno's latest 2025 materials and 2022 historical context. How can I assist you with her portfolio?"})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask about Juno's background..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Reviewing 2025 & 2022 records..."):
            try:
                # 转换角色映射
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
