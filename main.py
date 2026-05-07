import streamlit as st
import anthropic

# 페이지 설정
st.set_page_config(
    page_title="Claude AI 질문 앱",
    page_icon="🤖",
    layout="centered"
)

# 제목
st.title("🤖 Claude AI 질문 앱")
st.markdown("Claude AI에게 무엇이든 질문해보세요!")
st.divider()

# API 키 로드 (Streamlit Secrets)
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except KeyError:
    st.error("❌ API 키를 찾을 수 없습니다. Streamlit Secrets에 ANTHROPIC_API_KEY를 설정해주세요.")
    st.stop()

# Anthropic 클라이언트 생성
client = anthropic.Anthropic(api_key=api_key)

# 모델 선택
st.subheader("⚙️ 모델 선택")
model_option = st.radio(
    "사용할 Claude 모델을 선택하세요:",
    options=["claude-sonnet-4-5", "claude-opus-4-5"],
    format_func=lambda x: (
        "✨ Claude Sonnet 4.5 (빠르고 효율적)"
        if x == "claude-sonnet-4-5"
        else "🏆 Claude Opus 4.5 (가장 강력함)"
    ),
    horizontal=True
)

st.divider()

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_input_tokens" not in st.session_state:
    st.session_state.total_input_tokens = 0

if "total_output_tokens" not in st.session_state:
    st.session_state.total_output_tokens = 0

# 대화 기록 초기화 버튼
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("💬 대화")
with col2:
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.rerun()

# 이전 대화 출력
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# 질문 입력
user_input = st.chat_input("질문을 입력하세요...")

if user_input:
    # 사용자 메시지 저장 및 출력
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("Claude가 답변을 생성하고 있습니다..."):
            try:
                response = client.messages.create(
                    model=model_option,
                    max_tokens=2048,
                    messages=st.session_state.messages
                )

                # 응답 텍스트 추출
                answer = response.content[0].text

                # 토큰 사용량 누적
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                st.session_state.total_input_tokens += input_tokens
                st.session_state.total_output_tokens += output_tokens

                # 응답 출력
                st.markdown(answer)

                # 이번 응답 토큰 정보
                st.caption(
                    f"📊 이번 응답 — 입력: {input_tokens:,} 토큰 / 출력: {output_tokens:,} 토큰"
                )

                # 응답 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except anthropic.AuthenticationError:
                st.error("❌ API 키가 유효하지 않습니다. Secrets 설정을 확인해주세요.")
            except anthropic.RateLimitError:
                st.error("⚠️ API 사용 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
            except anthropic.APIError as e:
                st.error(f"❌ API 오류가 발생했습니다: {str(e)}")

st.divider()

# 누적 토큰 사용량 표시
st.subheader("📈 누적 토큰 사용량")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📥 총 입력 토큰",
        value=f"{st.session_state.total_input_tokens:,}"
    )
with col2:
    st.metric(
        label="📤 총 출력 토큰",
        value=f"{st.session_state.total_output_tokens:,}"
    )
with col3:
    st.metric(
        label="🔢 총 사용 토큰",
        value=f"{st.session_state.total_input_tokens + st.session_state.total_output_tokens:,}"
    )

# 사용 중인 모델 표시
st.caption(f"🔧 현재 모델: {model_option}")
