import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. 页面基础配置
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

# GROUNDING DATA
{materials_2025}
{materials_2022}
"""

# ==========================================
# 5. 模型初始化 (动态探测可用模型)
# ==========================================
try:
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if "models/gemini-1.5-flash" in models:
        target_model = "models/gemini-1.5-flash"
    elif "models/gemini-1.5-pro" in models:
        target_model = "models/gemini-1.5-pro"
    else:
        target_model = models[0]

    model = genai.GenerativeModel(
        model_name=target_model,
        system_instruction=SYSTEM_INSTRUCTION,
        generation_config={"temperature": 0.1, "top_p": 0.95}
    )
    
    with st.sidebar:
        st.title("Juno Li")
        st.caption("Law School Applicant | Technology Leader")
        st.success(f"✅ Active: {target_model.replace('models/', '')}")
        
        st.markdown("---")
        st.markdown("### 🔗 Connect")
        st.link_button("LinkedIn Profile", "https://www.linkedin.com/in/juno-shunyu-li") 
        st.link_button("Download Resume", "https://drive.google.com/file/d/16NSJE6s9_ZPOMMuZy3ObCd4L7u39er-B/view?usp=sharing")
        
        st.markdown("---")
        st.info("Technical Note: Built with Python & Gemini API.")

except Exception as e:
    st.error(f"Model Init Error: {e}")
    st.stop()

# ==========================================
# 6. 聊天交互界面
# ==========================================
st.title("🙋‍♂️ Chat with Juno's AI")

if "messages" not in st.session_state:
    st.session_state.messages = []
