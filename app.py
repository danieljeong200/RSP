
import streamlit as st
import random

# 페이지 설정
st.set_page_config(
    page_title="가위바위보 챌린지",
    page_icon="✊",
    layout="centered"
)

# 제목
st.title("✊ 가위바위보 챌린지")
st.markdown("### 🎮 컴퓨터를 이겨라!")
st.write("가위, 바위, 보 중 하나를 선택하세요.")

st.divider()

# 게임 데이터
choices = ["가위", "바위", "보"]

emojis = {
    "가위": "✌️",
    "바위": "✊",
    "보": "✋"
}

# 게임 기록 초기 설정
defaults = {
    "win": 0,
    "lose": 0,
    "draw": 0,
    "player": None,
    "computer": None,
    "result": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# 게임 실행 함수
def play(player):
    computer = random.choice(choices)

    st.session_state.player = player
    st.session_state.computer = computer

    if player == computer:
        st.session_state.result = "무승부"
        st.session_state.draw += 1

    elif (
        (player == "가위" and computer == "보")
        or (player == "바위" and computer == "가위")
        or (player == "보" and computer == "바위")
    ):
        st.session_state.result = "승리"
        st.session_state.win += 1

    else:
        st.session_state.result = "패배"
        st.session_state.lose += 1


# 사용자 선택 버튼
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✌️ 가위", use_container_width=True):
        play("가위")

with col2:
    if st.button("✊ 바위", use_container_width=True):
        play("바위")

with col3:
    if st.button("✋ 보", use_container_width=True):
        play("보")

st.divider()

# 게임 결과 출력
if st.session_state.player is not None:

    st.subheader("⚔️ 대결 결과")

    left, center, right = st.columns([2, 1, 2])

    with left:
        st.markdown("### 👤 나")
        st.markdown(
            f"# {emojis[st.session_state.player]}"
        )
        st.write(st.session_state.player)

    with center:
        st.markdown("## VS")

    with right:
        st.markdown("### 🤖 컴퓨터")
        st.markdown(
            f"# {emojis[st.session_state.computer]}"
        )
        st.write(st.session_state.computer)

    # 승패 판정 메시지
    if st.session_state.result == "승리":
        st.success("🎉 승리! 컴퓨터를 이겼습니다!")

    elif st.session_state.result == "패배":
        st.error("😢 패배! 다시 도전해 보세요!")

    else:
        st.warning("🤝 무승부! 다시 승부를 겨뤄 보세요!")

else:
    st.info("👆 위의 버튼을 눌러 게임을 시작하세요!")

st.divider()

# 누적 전적
st.subheader("🏆 나의 전적")

a, b, c = st.columns(3)

a.metric("🎉 승리", st.session_state.win)
b.metric("😢 패배", st.session_state.lose)
c.metric("🤝 무승부", st.session_state.draw)

# 전체 게임 수 및 승률
total = (
    st.session_state.win
    + st.session_state.lose
    + st.session_state.draw
)

win_rate = (
    st.session_state.win / total * 100
    if total > 0 else 0
)

st.write(f"🎮 총 플레이 횟수: {total}회")
st.write(f"📊 승률: {win_rate:.1f}%")

st.progress(win_rate / 100)

# 기록 초기화 버튼
if st.button("🔄 기록 초기화", use_container_width=True):
    for key, value in defaults.items():
        st.session_state[key] = value

    st.rerun()

st.divider()

st.caption("Made with Python & Streamlit")
