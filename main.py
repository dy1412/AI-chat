import streamlit as st
import anthropic

# 페이지 설정
st.set_page_config(
    page_title="Claude AI 질문 앱",
    page_icon="🤖",
    layout="centered"
)

# ───────────────────────────── CSS ─────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #0f1117;
        color: #e8e8e8;
    }
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 780px;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-bottom: 0.3rem;
    }
    .header-sub {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }

    /* 추천 키워드 패널 */
    .recommend-panel {
        background: linear-gradient(135deg, #1a1d2e 0%, #1e2035 100%);
        border: 1px solid #2d3148;
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.8rem;
    }
    .recommend-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .recommend-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #6366f1;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .recommend-dot {
        width: 6px;
        height: 6px;
        background-color: #6366f1;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 1.8s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* 모델 라디오 */
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] > div {
        display: flex;
        gap: 0.75rem;
        flex-direction: row;
    }
    div[data-testid="stRadio"] > div > label {
        background-color: #1e2130;
        border: 1px solid #2d3148;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        color: #9ca3af;
        font-size: 0.88rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    div[data-testid="stRadio"] > div > label:hover {
        border-color: #6366f1;
        color: #ffffff;
    }

    /* 채팅 메시지 */
    div[data-testid="stChatMessage"] {
        background-color: #1a1d2e;
        border: 1px solid #22263a;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
    }

    /* 입력창 */
    div[data-testid="stChatInput"] textarea {
        background-color: #1e2130 !important;
        border: 1px solid #2d3148 !important;
        border-radius: 14px !important;
        color: #e8e8e8 !important;
        font-size: 0.95rem !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
    }

    /* 토큰 카드 */
    .token-card {
        background-color: #1a1d2e;
        border: 1px solid #22263a;
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        text-align: center;
    }
    .token-label {
        font-size: 0.75rem;
        color: #4b5563;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 0.4rem;
    }
    .token-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
    }
    .token-value-accent {
        font-size: 1.6rem;
        font-weight: 700;
        color: #6366f1;
    }

    hr { border-color: #1e2130 !important; margin: 1.8rem 0 !important; }

    /* 초기화 버튼 */
    button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid #2d3148 !important;
        color: #6b7280 !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        transition: all 0.2s !important;
    }
    button[kind="secondary"]:hover {
        border-color: #ef4444 !important;
        color: #ef4444 !important;
    }

    .section-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #4b5563;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# ───────────────────────────── API 키 ─────────────────────────────
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except KeyError:
    st.error("❌ API 키를 찾을 수 없습니다. Streamlit Secrets에 ANTHROPIC_API_KEY를 설정해주세요.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# ───────────────────────────── 세션 초기화 ─────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_input_tokens" not in st.session_state:
    st.session_state.total_input_tokens = 0
if "total_output_tokens" not in st.session_state:
    st.session_state.total_output_tokens = 0
if "auto_send" not in st.session_state:
    st.session_state.auto_send = None
if "recommended_keywords" not in st.session_state:
    st.session_state.recommended_keywords = []
if "keywords_generated" not in st.session_state:
    st.session_state.keywords_generated = False

# ───────────────────────────── 헤더 ─────────────────────────────
st.markdown('<div class="header-title">✦ Claude AI</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">무엇이든 물어보세요. 바로 답해드릴게요.</div>', unsafe_allow_html=True)

# ───────────────────────────── 모델 선택 ─────────────────────────────
model_option = st.radio(
    "모델 선택",
    options=["claude-sonnet-4-6", "claude-opus-4-6"],
    format_func=lambda x: (
        "⚡ Sonnet 4.6  —  빠르고 효율적"
        if x == "claude-sonnet-4-6"
        else "🏆 Opus 4.6  —  가장 강력함"
    ),
    horizontal=True
)

st.markdown("<hr>", unsafe_allow_html=True)

# ───────────────────────────── AI 추천 키워드 패널 ─────────────────────────────
st.markdown("""
<div class="recommend-panel">
    <div class="recommend-header">
        <span class="recommend-dot"></span>
        <span class="recommend-title">AI 질문 추천</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 추천 키워드 생성 함수
def generate_keywords():
    with st.spinner("✨ AI가 추천 질문을 생성하는 중..."):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": (
                        "사용자가 AI 챗봇에게 질문할 만한 흥미롭고 다양한 주제의 질문 5가지를 추천해줘. "
                        "각 질문은 간결하게 한 문장으로, 번호 없이 줄바꿈으로만 구분해서 출력해줘. "
                        "질문은 매번 다르게, 창의적이고 실용적인 것들로 골고루 섞어서 추천해줘. "
                        "예: 학습, 코딩, 창작, 일상, 과학 등 다양한 분야에서 뽑아줘."
                    )
                }]
            )
            raw = response.content[0].text.strip()
            keywords = [k.strip() for k in raw.split("\n") if k.strip()][:5]
            st.session_state.recommended_keywords = keywords
            st.session_state.keywords_generated = True
        except Exception as e:
            st.error(f"추천 질문 생성 실패: {str(e)}")

# 최초 1회 자동 생성
if not st.session_state.keywords_generated:
    generate_keywords()

# 추천 키워드 버튼 출력
if st.session_state.recommended_keywords:
    for kw in st.session_state.recommended_keywords:
        if st.button(f"▸  {kw}", key=f"rec_{kw}", use_container_width=True):
            st.session_state.auto_send = kw

    # 새로고침 버튼
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if st.button("🔄  다른 질문 추천받기", key="refresh_keywords", use_container_width=False):
        st.session_state.keywords_generated = False
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ───────────────────────────── 대화 영역 ─────────────────────────────
col_title, col_reset = st.columns([5, 1])
with col_title:
    st.markdown("#### 💬 대화")
with col_reset:
    if st.button("초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.session_state.auto_send = None
        st.rerun()

# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message("user" if message["role"] == "user" else "assistant"):
        st.markdown(message["content"])

# ───────────────────────────── 입력 처리 ─────────────────────────────
user_input = st.chat_input("메시지를 입력하세요...")

# 키워드 클릭 or 직접 입력 통합
final_input = None
if st.session_state.auto_send:
    final_input = st.session_state.auto_send
    st.session_state.auto_send = None
elif user_input:
    final_input = user_input

# ───────────────────────────── AI 응답 ─────────────────────────────
if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        with st.spinner("생각하는 중..."):
            try:
                response = client.messages.create(
                    model=model_option,
                    max_tokens=2048,
                    messages=st.session_state.messages
                )
                answer = response.content[0].text
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens

                st.session_state.total_input_tokens += input_tokens
                st.session_state.total_output_tokens += output_tokens

                st.markdown(answer)
                st.caption(f"입력 {input_tokens:,} 토큰  ·  출력 {output_tokens:,} 토큰")

                st.session_state.messages.append({"role": "assistant", "content": answer})

            except anthropic.AuthenticationError:
                st.error("❌ API 키가 유효하지 않습니다.")
            except anthropic.RateLimitError:
                st.error("⚠️ API 사용 한도 초과. 잠시 후 다시 시도해주세요.")
            except anthropic.APIError as e:
                st.error(f"❌ API 오류: {str(e)}")

    st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ───────────────────────────── 토큰 사용량 ─────────────────────────────
st.markdown('<div class="section-label">토큰 사용량</div>', unsafe_allow_html=True)

total = st.session_state.total_input_tokens + st.session_state.total_output_tokens

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="token-card">
        <div class="token-label">📥 입력 토큰</div>
        <div class="token-value">{st.session_state.total_input_tokens:,}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="token-card">
        <div class="token-label">📤 출력 토큰</div>
        <div class="token-value">{st.session_state.total_output_tokens:,}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="token-card">
        <div class="token-label">🔢 총 사용량</div>
        <div class="token-value-accent">{total:,}</div>
    </div>""", unsafe_allow_html=True)

st.markdown(
    f'<p style="text-align:center; color:#2d3148; font-size:0.75rem; margin-top:1.5rem;">현재 모델 · {model_option}</p>',
    unsafe_allow_html=True
)
