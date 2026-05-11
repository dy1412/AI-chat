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
    /* 전체 배경 & 기본 텍스트 */
    .stApp {
        background-color: #f5f7fa;
        color: #1a1d2e;
    }
    .block-container {
        padding-top: 3rem;
        padding-bottom: 4rem;
        max-width: 800px;
    }

    /* 모든 텍스트 기본 어둡게 */
    html, body, [class*="css"], p, span, div, label,
    li, td, th, h1, h2, h3, h4, h5, h6 {
        color: #1a1d2e;
    }

    /* ── 헤더 ── */
    .header-wrap {
        margin-bottom: 2rem;
    }
    .header-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1a1d2e !important;
        letter-spacing: -0.5px;
        line-height: 1.2;
        margin-bottom: 0.4rem;
    }
    .header-sub {
        font-size: 1rem;
        color: #6b7280 !important;
        margin: 0;
    }

    /* ── 구분선 ── */
    hr {
        border: none !important;
        border-top: 1.5px solid #e5e7ef !important;
        margin: 1.6rem 0 !important;
    }

    /* ── 모델 라디오 ── */
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] > div {
        display: flex;
        gap: 0.6rem;
    }
    div[data-testid="stRadio"] > div > label {
        background-color: #ffffff;
        border: 1.5px solid #d1d5e0;
        border-radius: 12px;
        padding: 0.55rem 1.2rem;
        color: #4b5270 !important;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    div[data-testid="stRadio"] > div > label:hover {
        border-color: #6366f1;
        color: #6366f1 !important;
        background-color: #f0f0fe;
    }
    div[data-testid="stRadio"] > div > label[data-checked="true"] {
        border-color: #6366f1;
        background-color: #eef0fd;
        color: #6366f1 !important;
        font-weight: 600;
    }

    /* ── 추천 질문 패널 ── */
    .recommend-panel {
        background: #ffffff;
        border: 1.5px solid #e2e5f0;
        border-radius: 18px;
        padding: 1.4rem 1.6rem 0.6rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(99,102,241,0.06);
    }
    .recommend-header {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 1rem;
    }
    .recommend-dot {
        width: 7px;
        height: 7px;
        background: #6366f1;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.35; transform: scale(0.8); }
    }
    .recommend-title {
        font-size: 0.78rem;
        font-weight: 700;
        color: #6366f1 !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* ── 추천 키워드 버튼 ── */
    div[data-testid="stButton"] button {
        background-color: #f8f9fc !important;
        border: 1.5px solid #e2e5f0 !important;
        border-radius: 11px !important;
        color: #2d3148 !important;
        font-size: 0.93rem !important;
        font-weight: 500 !important;
        padding: 0.6rem 1rem !important;
        text-align: left !important;
        transition: all 0.18s ease !important;
        width: 100% !important;
        line-height: 1.5 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #eef0fd !important;
        border-color: #6366f1 !important;
        color: #4145c8 !important;
        transform: translateX(4px) !important;
        box-shadow: 0 2px 8px rgba(99,102,241,0.12) !important;
    }

    /* ── 채팅 메시지 ── */
    div[data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1.5px solid #e8eaf2;
        border-radius: 16px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] span,
    div[data-testid="stChatMessage"] div,
    div[data-testid="stChatMessage"] h1,
    div[data-testid="stChatMessage"] h2,
    div[data-testid="stChatMessage"] h3 {
        color: #1a1d2e !important;
        line-height: 1.8 !important;
    }

    /* ── 채팅 입력창 ── */
    div[data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        border: 1.5px solid #d1d5e0 !important;
        border-radius: 14px !important;
        color: #1a1d2e !important;
        font-size: 0.96rem !important;
        line-height: 1.6 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #a0a6bc !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    }

    /* ── 캡션 (토큰 정보) ── */
    .stCaption p,
    div[data-testid="stCaptionContainer"] p {
        color: #9ca3b8 !important;
        font-size: 0.76rem !important;
    }

    /* ── 토큰 카드 ── */
    .token-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-top: 0.5rem;
    }
    .token-card {
        background: #ffffff;
        border: 1.5px solid #e8eaf2;
        border-radius: 14px;
        padding: 1.2rem 0.8rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .token-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #9ca3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    .token-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #1a1d2e !important;
        letter-spacing: -0.5px;
    }
    .token-value-accent {
        font-size: 1.65rem;
        font-weight: 800;
        color: #6366f1 !important;
        letter-spacing: -0.5px;
    }

    /* ── 섹션 레이블 ── */
    .section-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #9ca3b8 !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    /* ── 대화 타이틀 ── */
    .chat-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1a1d2e !important;
        padding-top: 0.2rem;
    }

    /* ── 초기화 버튼 ── */
    .reset-btn button {
        background-color: transparent !important;
        border: 1.5px solid #e2e5f0 !important;
        color: #9ca3b8 !important;
        font-size: 0.82rem !important;
        padding: 0.35rem 0.8rem !important;
        transform: none !important;
        text-align: center !important;
        box-shadow: none !important;
    }
    .reset-btn button:hover {
        border-color: #ef4444 !important;
        color: #ef4444 !important;
        background-color: #fff5f5 !important;
        transform: none !important;
    }

    /* ── 새로고침 버튼 ── */
    .refresh-btn button {
        background-color: transparent !important;
        border: 1.5px solid #e2e5f0 !important;
        color: #6b7280 !important;
        font-size: 0.82rem !important;
        padding: 0.35rem 0.9rem !important;
        transform: none !important;
        text-align: center !important;
        box-shadow: none !important;
    }
    .refresh-btn button:hover {
        border-color: #6366f1 !important;
        color: #6366f1 !important;
        background-color: #eef0fd !important;
        transform: none !important;
    }

    /* ── 에러/경고 ── */
    div[data-testid="stAlert"] p {
        color: #1a1d2e !important;
    }

    /* ── 푸터 ── */
    .footer-text {
        text-align: center;
        color: #c8ccd8 !important;
        font-size: 0.74rem;
        margin-top: 1.8rem;
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
st.markdown("""
<div class="header-wrap">
    <div class="header-title">✦ Claude AI</div>
    <p class="header-sub">무엇이든 물어보세요. 바로 답해드릴게요.</p>
</div>
""", unsafe_allow_html=True)

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

# ───────────────────────────── 추천 키워드 생성 ─────────────────────────────
def generate_keywords():
    with st.spinner("✨ 추천 질문을 생성하는 중..."):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                messages=[{
                    "role": "user",
                    "content": (
                        "사용자가 AI 챗봇에게 질문할 만한 흥미롭고 다양한 질문 5가지를 추천해줘.\n"
                        "조건:\n"
                        "- 각 질문은 한 문장, 20자 이내로 간결하게\n"
                        "- 번호나 기호 없이 줄바꿈으로만 구분\n"
                        "- 매번 다양한 분야(학습, 코딩, 창작, 과학, 일상, 역사, 언어 등)에서 골고루 선택\n"
                        "- 실용적이고 흥미로운 질문 형태로만 출력"
                    )
                }]
            )
            raw = response.content[0].text.strip()
            keywords = [k.strip() for k in raw.split("\n") if k.strip()][:5]
            st.session_state.recommended_keywords = keywords
            st.session_state.keywords_generated = True
        except Exception:
            st.session_state.recommended_keywords = [
                "파이썬으로 웹 크롤러 만드는 법은?",
                "효율적인 공부 습관을 알려줘",
                "우주의 끝은 어디야?",
                "짧은 단편 소설을 써줘",
                "AI가 바꿀 미래 직업은?"
            ]
            st.session_state.keywords_generated = True

if not st.session_state.keywords_generated:
    generate_keywords()

# ───────────────────────────── 추천 질문 패널 ─────────────────────────────
st.markdown("""
<div class="recommend-panel">
    <div class="recommend-header">
        <span class="recommend-dot"></span>
        <span class="recommend-title">AI 추천 질문</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.recommended_keywords:
    for kw in st.session_state.recommended_keywords:
        if st.button(f"▸  {kw}", key=f"rec_{kw}", use_container_width=True):
            st.session_state.auto_send = kw

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    col_refresh, _ = st.columns([1.8, 3])
    with col_refresh:
        st.markdown('<div class="refresh-btn">', unsafe_allow_html=True)
        if st.button("🔄  다른 질문 추천받기", key="refresh_keywords"):
            st.session_state.keywords_generated = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ───────────────────────────── 대화 영역 ─────────────────────────────
col_title, col_reset = st.columns([5, 1])
with col_title:
    st.markdown('<div class="chat-title">💬 대화</div>', unsafe_allow_html=True)
with col_reset:
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.session_state.auto_send = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message("user" if message["role"] == "user" else "assistant"):
        st.markdown(message["content"])

# ───────────────────────────── 입력 처리 ─────────────────────────────
user_input = st.chat_input("메시지를 입력하세요...")

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

st.markdown(f"""
<div class="token-grid">
    <div class="token-card">
        <div class="token-label">📥 입력 토큰</div>
        <div class="token-value">{st.session_state.total_input_tokens:,}</div>
    </div>
    <div class="token-card">
        <div class="token-label">📤 출력 토큰</div>
        <div class="token-value">{st.session_state.total_output_tokens:,}</div>
    </div>
    <div class="token-card">
        <div class="token-label">🔢 총 사용량</div>
        <div class="token-value-accent">{total:,}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    f'<div class="footer-text">현재 모델 · {model_option}</div>',
    unsafe_allow_html=True
)
