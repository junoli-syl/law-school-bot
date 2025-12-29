import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. 页面基础配置 & 视觉样式 (Times New Roman)
# ==========================================
st.set_page_config(page_title="Juno Li's Law School AI Portfolio", layout="centered")

st.markdown(
    """
    <style>
        /* 1. 全局字体强制执行 */
        * { font-family: "Times New Roman", Times, serif !important; }
        
        /* 2. 彻底抹除左上角干扰文本 */
        /* 隐藏侧边栏控制按钮容器 */
        [data-testid="collapsedControl"], button[kind="header"] {
            display: none !important;
        }
        
        /* 针对可能渲染出的文本节点进行彻底隐藏 */
        header, .st-emotion-cache-6qob1r, .st-emotion-cache-16p0qsc {
            visibility: hidden !important;
            height: 0 !important;
            width: 0 !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* 3. 侧边栏整体优化 */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa; 
        }

        /* 侧边栏字体缩小 */
        [data-testid="stSidebar"] .stMarkdown, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            font-size: 0.85rem !important; 
            line-height: 1.3 !important;
        }

        /* 4. 侧边栏照片优化 */
        [data-testid="stSidebar"] [data-testid="stImage"] img {
            border-radius: 50%;
            border: 2px solid #e0e0e0;
            width: 120px !important; 
            height: 120px !important;
            object-fit: cover;
            margin: 0 auto;
            display: block;
        }
    
        /* 5. 专门优化侧边栏底部 Technical Note */
        [data-testid="stSidebar"] .stInfo {
            font-size: 0.75rem !important;
            padding: 0.5rem !important;
        }
    
        /* 6. 其他 UI 元素圆角优化 */
        [data-testid="stHorizontalBlock"] [data-testid="stImage"] img,
        [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarImage"] img {
            border-radius: 50% !important;
            object-fit: cover;
        }
    </style>
    """, 
    unsafe_allow_html=True
)
# ==========================================
# 2. 文件读取逻辑 (Session State 缓存)
# ==========================================
def load_context():
    c2025, c2022 = "", ""
    if os.path.exists("context"):
        for f_name in os.listdir("context"):
            if f_name.endswith(".txt"):
                with open(os.path.join("context", f_name), "r", encoding="utf-8") as f:
                    content = f.read()
                    if "_2025" in f_name:
                        c2025 += f"\n[PRIMARY 2025] {f_name}:\n{content}\n"
                    else:
                        c2022 += f"\n[SUPPLEMENTARY 2022] {f_name}:\n{content}\n"
    return c2025, c2022

if "grounding" not in st.session_state:
    st.session_state.grounding = load_context()

m2025, m2022 = st.session_state.grounding

# ==========================================
# 3. 初始化逻辑
# ==========================================
def initialize_agent(materials_2025, materials_2022):
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in models else models[0]

        system_instruction = f"""
        # ROLE: Digital Portfolio Agent for Juno Li (Law School Applicant).
        # HIERARCHY: Prioritize [PRIMARY SOURCE 2025] over [SUPPLEMENTARY EXAMPLE 2022].
        # PERSONA: Professional, Tech-Savvy, Humble, International Perspective.
        # GOAL: Represent Juno Li's background to Law School Admissions Officers.

        # GUARDRAILS
        1. **Missing Information:** If unknown, say "I don't have that specific detail, but based on Juno's background in tech...".
        2. **Privacy:** Do not reveal home address or phone number.
        
        # RESPONSE RULES:
        1. WORD LIMIT: Keep your responses less than 200 words.
        2. TONE: Formal, analytical.
        
        # GROUNDING DATA:
        {materials_2025}
        {materials_2022}
        """

        model = genai.GenerativeModel(
            model_name=target_model,
            system_instruction=system_instruction,
            generation_config={"temperature": 0.1, "top_p": 0.95}
        )
        return model, target_model
    except Exception as e:
        st.error(f"Initialization Failed: {e}")
        return None, None

if "ai_model" not in st.session_state:
    st.session_state.ai_model, st.session_state.model_name = initialize_agent(m2025, m2022)

model = st.session_state.ai_model
active_model_name = st.session_state.model_name

# ==========================================
# 4. 侧边栏构建 (锁定 juno_photo.jpg)
# ==========================================
with st.sidebar:
    if os.path.exists("juno_photo.jpg"):
        st.image("juno_photo.jpg", use_container_width=True)
        
    st.title("Juno Li")
    st.caption("Technology Leader | JD Applicant")
    if active_model_name:
        st.success(f"✅ Active: {active_model_name.replace('models/', '')}")
    
    st.markdown("### 🔗 Connect")
    st.link_button("LinkedIn Profile", "https://www.linkedin.com/in/juno-shunyu-li")
    st.link_button("Download Resume", "https://drive.google.com/file/d/16NSJE6s9_ZPOMMuZy3ObCd4L7u39er-B/view?usp=sharing")
    st.info("""
    **Technical Note:** This digital agent is built by Juno using Python, Streamlit, and Google Gemini 2.5 Flash API. 
    It demonstrates her proficiency in full-stack AI implementation and its application in professional storytelling.
    """)

# ==========================================
# 5. 主界面渲染 (Header 使用 juno_headshot.jpeg)
# ==========================================
header_photo = "juno_headshot.jpeg"
header_col1, header_col2 = st.columns([1, 6])
with header_col1:
    if os.path.exists(header_photo):
        st.image(header_photo, width=80)

with header_col2:
    st.title("Chat with Juno's AI")

st.markdown("""
**Dear Admission officers, this is your gateway to Juno’s JD candidacy.** This AI agent provides instant insights into her **career transition**, **technical leadership at CVS/Aetna**, and **specific law school motivations**.
""")

# 对话逻辑
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am Juno's digital law school representative. I'm here to help you navigate her professional journey and motivations. Feel free to ask anything, or use the buttons below."}]

for msg in st.session_state.messages:
    # 按照你的要求：Assistant 使用 👩🏻‍💼, User 使用 ⚖️
    avatar_val = "👩🏻‍💼" if msg["role"] == "assistant" else "⚖️"
    with st.chat_message(msg["role"], avatar=avatar_val):
        st.markdown(msg["content"])

# 快速提问按钮
def handle_click(p): st.session_state.clicked_prompt = p

st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.button("Why Law?", on_click=handle_click, args=["Why does Juno want to go to law school given her tech career?"])
with c2:
    st.button("Tech Impact", on_click=handle_click, args=["Tell me about Juno's technical leadership and its impact."])
with c3:
    st.button("Academic", on_click=handle_click, args=["Tell me about Juno's academic background at GWU."])

# 处理输入
user_input = st.chat_input("Ask about Juno's background...")
if "clicked_prompt" in st.session_state:
    user_input = st.session_state.clicked_prompt
    del st.session_state.clicked_prompt

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="⚖️"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="👩🏻‍💼"):
        if model:
            with st.spinner("Synthesizing portfolio data for JD candidacy..."):
                try:
                    history = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                    chat = model.start_chat(history=history)
                    response = chat.send_message(user_input)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    st.rerun()
                except Exception as e:
                    st.error(f"Chat Error: {e}")
