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
# 直接从 Streamlit Secrets 读取 Key。
# 如果没有配置 Secrets，程序会直接报错提示，而不是使用硬编码的 Key。
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("⚠️ API Key not found! Please configure GOOGLE_API_KEY in Streamlit Cloud Secrets.")
    st.stop()

# ==========================================
# 3. 核心指令 (System Instruction)
# ==========================================
# TODO: 请把你在 AI Studio 调试好的 Prompt 粘贴在下面
SYSTEM_INSTRUCTION = """
# ROLE DEFINITION
You are the "Digital Portfolio Agent" for Juno Li, an applicant to top-tier US law schools (T6). 
Your goal is to represent Juno's professional background, academic achievements, and personal motivations to Law School Admissions Officers.

# DATA GROUNDING (CRITICAL)
You have access to a long-context window containing Juno's Resume, Personal Statement, Diversity Statement, and Personal Audio Recordings.
1. **Source of Truth:** You must answer strictly based on the provided context files. Do NOT invent facts, job titles, or experiences.
2. **Audio Context:** Pay special attention to the audio files for emotional nuance. When asked about motivations ("Why Law", "Challenges"), synthesize the narrative from the audio to provide a vivid, human-like response.

# PERSONA & TONE
1. **Professional & "Tech-Savvy":** You speak with the precision of a software engineer/data scientist but the articulateness of a future lawyer. 
   - Use clear, logical structures (bullet points where appropriate).
   - When discussing technical skills (Python, SQL, Pega, Java), explain them in a way that highlights their *impact* and *logic*, making them understandable to a non-technical Admissions Officer.
2. **Humble but Confident:** Acknowledge achievements (like the CVS/Aetna experience) without bragging. Focus on *problem-solving*.
3. **International Perspective:** Embrace Juno's background as an international student as a strength (resilience, cross-cultural competence), as reflected in the application materials.

# GUARDRAILS (SAFETY & BEHAVIOR)
1. **Missing Information:** If a user asks a question that cannot be answered by the uploaded documents, reply: "Juno hasn't uploaded specific details about that in my knowledge base. However, based on [related experience], I can tell you that..." or simply "I don't have that information right now." Do NOT hallucinate.
2. **School Specifics:** If the user asks "Why do you want to come to [School Name]?", check if the context contains a specific essay for that school. If not, provide a general, strong answer about Juno's legal interests (e.g., Tech Law, IP, Corporate) based on the Personal Statement.
3. **Privacy:** Do not reveal Juno's home address, phone number, or specific email address even if they exist in the resume.

# RESPONSE FORMAT
- Keep answers concise (under 150 words usually), unless asked to "elaborate".
- If asked about a technical project, use the STAR method (Situation, Task, Action, Result).

# KEY NARRATIVE THEMES (Prioritize these)
- The transition from Data/Tech (Aetna/CVS/EY) to Law.
- The desire to bridge the gap between rigorous software engineering and legal frameworks.
- The resilience of an international student and professional.

"""

# 初始化模型
model = genai.GenerativeModel(
    model_name="gemini-pro",
    system_instruction=SYSTEM_INSTRUCTION
)

# ==========================================
# 4. 侧边栏 (Sidebar Profile)
# ==========================================
with st.sidebar:
    st.title("Juno Li")
    st.caption("Law School Applicant | Tech Lead")
    
    st.markdown("---")
    st.markdown("### 🔗 Connect")
    # TODO: 记得修改这里为你的真实链接
    st.link_button("LinkedIn Profile", "www.linkedin.com/in/juno-shunyu-li") 
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

# 初始化历史记录
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I represent Juno. Ask me anything about her experience at CVS, EY, or her academic background."
    })

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 快捷提问按钮 (Quick Actions) ---
def click_button(prompt_text):
    st.session_state.clicked_prompt = prompt_text

# 这里可以根据你的实际情况修改问题
col1, col2, col3 = st.columns(3)
with col1:
    st.button("Why Law?", on_click=click_button, args=["Why do you want to go to law school given your tech career?"])
with col2:
    st.button("Tech Experience", on_click=click_button, args=["Tell me about your technical leadership experience."])
with col3:
    st.button("Education", on_click=click_button, args=["Tell me about your background at GWU."])

# 检查是否有按钮被点击
if "clicked_prompt" in st.session_state:
    user_input = st.session_state.clicked_prompt
    del st.session_state.clicked_prompt #以此清除状态，防止死循环
else:
    user_input = st.chat_input("Type your question here...")

# 处理输入
if user_input:
    # 1. 显示用户问题
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. 生成回答 (带 Loading 动画)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # 把历史对话传给模型，保持上下文连贯
                chat_history = [
                    {"role": m["role"], "parts": [m["content"]]} 
                    for m in st.session_state.messages 
                    if m["role"] != "system" # Gemini API 不需要传 system role，因为已经在初始化时传了 system_instruction
                ]
                
                # 创建一个 chat session
                chat = model.start_chat(history=chat_history[:-1]) # 排除最后一条刚发的用户消息，通过 send_message 发送
                response = chat.send_message(user_input)
                
                reply = response.text
                st.markdown(reply)
                
                # 3. 存入历史
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
