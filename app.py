import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. 页面基础配置 (必须在最前面)
# ==========================================
st.set_page_config(
    page_title="Juno Li's Law School AI Portfolio",
    page_icon="⚖️",
    layout="centered"
)
st.markdown(
    """
    <style>
    /* 全局字体设置为 Times New Roman */
    html, body, [class*="css"], .stMarkdown, p, div {
        font-family: "Times New Roman", Times, serif !important;
    }
    /* 修改输入框字体 */
    .stChatInput textarea {
        font-family: "Times New Roman", Times, serif !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. 带缓存的 Grounding 读取
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
                st.error(f"Error reading {filename}: {e}")
    
    return context_2025, context_2022

# ==========================================
# 3. 初始化逻辑 (安全加载)
# ==========================================
def initialize_agent():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 获取缓存的资料
        materials_2025, materials_2022 = get_prioritized_context()
        
        # 自动探测模型
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in models else models[0]

        system_instruction = f"""
        # ROLE: Digital Portfolio Agent for Juno Li (Law School Applicant).
        # HIERARCHY: Prioritize [PRIMARY SOURCE 2025] over [SUPPLEMENTARY EXAMPLE 2022].
        # PERSONA: Professional, Tech-Savvy, Humble, International Perspective. You are the "Digital Portfolio Agent" for Juno Li, an applicant to top-tier US law schools (T6). Your goal is to represent Juno's professional background, academic achievements, and personal motivations to Law School Admissions Officers.

        # GUARDRAILS
        1. **Missing Information:** If unknown, say "I don't have that specific detail, but based on Juno's background in tech...".
        2. **Privacy:** Do not reveal home address or phone number.
        
        # RESPONSE RULES:
        1. WORD LIMIT: Keep your responses around 300 words. Be concise but detailed enough for admissions officers.
        2. TONE: Use formal, analytical language (Times New Roman style thinking).
        
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

# ==========================================
# 4. 执行初始化并构建侧边栏
# ==========================================
model, active_model_name = initialize_agent()

with st.sidebar:
    st.title("Juno Li")
    st.caption("Technology Leader | JD Applicant")
    if active_model_name:
        st.success(f"✅ Active: {active_model_name.replace('models/', '')}")
    
    st.markdown("---")
    st.markdown("### 🔗 Connect")
    st.link_button("LinkedIn Profile", "https://www.linkedin.com/in/juno-shunyu-li")
    st.link_button("Download Resume", "https://drive.google.com/file/d/16NSJE6s9_ZPOMMuZy3ObCd4L7u39er-B/view?usp=sharing")

# ==========================================
# 5. 主界面渲染 (确保无论如何都会显示)
# ==========================================
st.title("🙋‍♂️ Chat with Juno's AI")
st.markdown("Ask about Juno's transition from Tech to Law.")

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am Juno's digital representative. How can I help you today?"}]

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 快速提问按钮 ---
def handle_click(prompt):
    st.session_state.clicked_prompt = prompt

col1, col2, col3 = st.columns(3)
with col1:
    st.button("Why Law?", on_click=handle_click, args=["Why do you want to go to law school given your tech career?"])
with col2:
    st.button("Tech Impact", on_click=handle_click, args=["Tell me about your technical leadership and its impact."])
with col3:
    st.button("Academic", on_click=handle_click, args=["Tell me about your academic background at GWU."])

# --- 处理用户输入 ---
user_input = st.chat_input("Ask about Juno's background...")

# 检查是否有按钮被点击
if "clicked_prompt" in st.session_state:
    user_input = st.session_state.clicked_prompt
    del st.session_state.clicked_prompt

if user_input:
    # 立即显示用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 生成回答
    with st.chat_message("assistant"):
        if model is None:
            st.error("AI is not ready. Please check API Key and configuration.")
        else:
            with st.spinner("Analyzing portfolio..."):
                try:
                    # 转换历史
                    history = []
                    for m in st.session_state.messages[:-1]:
                        role = "model" if m["role"] == "assistant" else "user"
                        history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=history)
                    response = chat.send_message(user_input)
                    reply = response.text
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Chat Error: {e}")
