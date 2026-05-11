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
    /* 전체 배경 */
    .stApp {
        background-color: #111318;
        color: #e2e4e9;
    }
    .block-container {
        padding-top: 3rem;
        padding-bottom: 4rem;
        max-width: 800px;
    }

    /* 헤더 */
    .header-wrap {
        margin-bottom: 2rem;
    }
    .header-title {
        font-size: 2rem;
        font-weight: 800;
        color: #f0f1f5;
        letter-spacing: -0.5px;
        margin-bottom: 0.4rem;
        line-height: 1.2;
    }
    .header-sub {
        font-size: 1rem;
        color: #8b90a0;
        margin: 0;
    }

    /* 모델 라디오 */
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] > div {
        display: flex;
        gap: 0.6rem;
        flex-direction: row;
    }
    div[data-testid="stRadio"] > div > label {
        background-color: #1c1f2b;
        border: 1.5px solid #2e3246;
        border-radius: 12px;
        padding: 0.55rem 1.1rem;
        color: #8b90a0;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }
    div[data-testid="stRadio"] > div > label:hover {
        border-color: #7c7ff0;
        color: #d0d1fa;
        background-color: #1e2038;
    }
    div[data-testid="stRadio"] > div > label[data-checked="true"] {
        border-color: #7c7ff0;
        color: #d0d1fa;
        background-color: #1e2038;
    }

    /* 구분선 */
    hr {
        border: none !important;
        border-top: 1px solid #1e2130 !important;
        margin: 1.6rem 0 !important;
    }

    /* ── 추천 키워드 패널 ── */
    .recommend-panel {
        background: #161923;
        border: 1.5px solid #252840;
        border-radius: 18px;
        padding: 1.4rem 1.6rem 1.5rem;
        margin-bottom: 1.8rem;
    }
    .recommend-header {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 1.1rem;
    }
    .recommend-dot {
        width: 7px;
        height: 7px;
        background: #7c7ff0;
        border-radius: 50%;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.4; transform: scale(0.85); }
    }
    .recommend-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #7c7ff0;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* 추천 키워드 버튼 개별 스타일 */
    div[data-testid="stButton"] button[kind="secondary"] {
        background-color: #1c2030 !important;
        border: 1.5px solid #2a2f4a !important;
        border-radius: 11px !important;
        color: #c5c8dc !important;          /* ← 밝은 텍스트 */
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 1rem !important;
        text-align: left !important;
        transition: all 0.18s ease !important;
        width: 100% !important;
        line-height: 1.5 !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        background-color: #1e2240 !important;
        border-color: #7c7ff0 !important;
        color: #e8e9ff !important;          /* ← 호버 시 더 밝게 */
        transform: translateX(3px) !important;
    }

    /* 새로고침 버튼 별도 */
    .refresh-btn button {
        background-color: transparent !important;
        border: 1px solid #2a2f4a !important;
        border-radius: 10px !important;
        color: #6b7080 !important;
        font-size: 0.82rem !important;
        padding: 0.4rem 0.9rem !important;
        transition: all 0.18s !important;
    }
    .refresh-btn button:hover {
        border-color: #7c7ff0 !important;
        color: #a5a8f5 !important;
    }

    /* 채팅 메시지 */
    div[data-testid="stChatMessage"] {
        background-color: #161923;
        border: 1.5px solid #1e2235;
        border-radius: 16px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.8rem;
    }

    /* 채팅 메시지 내 텍스트 */
    div[data-testid="stChatMessage"] p {
        color: #dde0ec !important;
        font-size: 0.97rem !important;
        line-height: 1.75 !important;
    }

    /* 입력창 */
    div[data-testid="stChatInput"] textarea {
        background-color: #1c1f2b !important;
        border: 1.5px solid #2e3246 !important;
        border-radius: 14px !important;
        color: #e2e4e9 !important;
        font-size: 0.96rem !important;
        line-height: 1.6 !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #4b5068 !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border-color: #7c7ff0 !important;
        box-shadow: 0 0 0 3px rgba(124,127,240,0.12) !important;
    }

    /* 캡션 (토큰 정보) */
    div[data-testid="stChatMessage"] .stCaptionContainer p,
    .stCaption p {
        color: #4b5068 !important;
        font-size: 0.76rem !important;
    }

    /* 토큰 카드 */
    .token-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-top: 0.5rem;
    }
    .token-card {
        background: #161923;
        border: 1.5px solid #1e2235;
        border-radius: 14px;
        padding: 1.1rem 0.8rem;
        text-align: center;
    }
    .token-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #5a5f78;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    .token-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #e2e4f0;
        letter-spacing: -0.5px;
    }
    .token-value-accent {
        font-size: 1.65rem;
        font-weight: 800;
        color: #7c7ff0;
        letter-spacing: -0.5px;
    }

    /* 섹션 레이블 */
    .section-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #5a5f78;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    /* 대화 헤더 */
    .chat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .chat-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #c8cbdc;
    }

    /* 초기화 버튼 */
    .reset-btn button {
        background-color: transparent !important;
        border: 1px solid #2e3246 !important;
        color: #5a5f78 !important;
        border-radius: 9px !important;
        font-size: 0.8rem !important;
        padding: 0.3rem 0.75rem !important;
        transition: all 0.18s !important;
    }
    .reset-btn button:hover {
        border-color: #e05c6a !important;
        color: #e05c6a !important;
        background-color: rgba(224,92,106,0.06) !important;
    }

    /* 푸터 */
    .footer-text {
        text-align: center;
        color: #2d3248;
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

# ───────────────────────────── AI 추천 키워드 패널 ─────────────────────────────
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
                        "- 실용적이고 흥미로운 질문으로\n"
                        "예시처럼 질문 형태로만 출력해줘."
                    )
                }]
            )
            raw = response.content[0].text.strip()
            keywords = [k.strip() for k in raw.split("\n") if k.strip()][:5]
            st.session_state.recommended_keywords = keywords
            st.session_state.keywords_generated = True
        except Exception as e:
            st.session_state.recommended_keywords = [
                "파이썬으로 웹 크롤러 만드는 법은?",
                "효율적인 공부 습관을 알려줘",
                "우주의 끝은 어디야?",
                "짧은 단편 소설을 써줘",
                "AI가 바꿀 미래 직업은?"
            ]
            st.session_state.keywords_generated = True

# 최초 1회 자동 생성
if not st.session_state.keywords_generated:
    generate_keywords()

# 패널 출력
st.markdown("""
<div class="recommend-panel">
    <div class="recommend-header">
        <span class="recommend-dot"></span>
        <span class="recommend-title">AI 추천 질문</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 키워드 버튼 5개
if st.session_state.recommended_keywords:
    for kw in st.session_state.recommended_keywords:
        if st.button(f"▸  {kw}", key=f"rec_{kw}", use_container_width=True):
            st.session_state.auto_send = kw

    # 새로고침 버튼
    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    col_refresh, _ = st.columns([1.6, 3])
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
