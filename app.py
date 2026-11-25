

        
import streamlit as st
import random

# ==============================
# 기본 설정
# ==============================

st.set_page_config(
    page_title="가위바위보 챌린지",
    page_icon="🔥",
    layout="centered"
)

TARGET = 30
FEVER_INTERVAL = 5
REWARD_INTERVAL = 3

CHOICES = ["가위", "바위", "보"]

EMOJI = {
    "가위": "✌️",
    "바위": "✊",
    "보": "✋"
}

BEATS = {
    "가위": "보",
    "바위": "가위",
    "보": "바위"
}

ITEMS = {
    "투시경": "🔍",
    "방어막": "🛡️",
    "재도전": "🎲",
    "더블 포인트": "⚡",
    "무효화": "🧊"
}

DESCRIPTIONS = {
    "투시경": "CPU가 내지 않을 패 공개",
    "방어막": "패배를 무승부로 전환",
    "재도전": "패배 시 CPU의 패 재추첨",
    "더블 포인트": "승리 점수 2배",
    "무효화": "상대 아이템 효과 차단"
}

CPU_ITEMS = [
    "방어막",
    "재도전",
    "더블 포인트",
    "무효화"
]

# ==============================
# CPU 다음 라운드 준비
# ==============================

def prepare_round(g):

    g["cpu_choice"] = random.choice(CHOICES)
    g["cpu_item"] = None
    g["active_item"] = None
    g["hint"] = None

    available = [
        item for item in CPU_ITEMS
        if g["cpu_inventory"][item] > 0
    ]

    fever = g["round"] % FEVER_INTERVAL == 0

    # FEVER 라운드에서는 아이템 사용 확률 증가
    probability = 0.85 if fever else 0.45

    if available and random.random() < probability:
        g["cpu_item"] = random.choice(available)


# ==============================
# 게임 초기화
# ==============================

def reset_game():

    g = {
        "round": 1,
        "player_score": 0,
        "cpu_score": 0,

        "win": 0,
        "lose": 0,
        "draw": 0,

        "streak": 0,
        "best_streak": 0,

        "inventory": {
            item: 2 for item in ITEMS
        },

        "cpu_inventory": {
            item: 2 for item in CPU_ITEMS
        },

        "active_item": None,
        "cpu_item": None,
        "cpu_choice": None,
        "hint": None,

        "reward_pending": False,
        "cpu_reward": None,

        "last": None,
        "history": [],
        "finished": False
    }

    prepare_round(g)

    st.session_state.game = g


if "game" not in st.session_state:
    reset_game()

g = st.session_state.game


# ==============================
# 승패 판정
# ==============================

def judge(player, cpu):

    if player == cpu:
        return "무승부"

    if BEATS[player] == cpu:
        return "승리"

    return "패배"


# ==============================
# 아이템 장착
# ==============================

def equip(item):

    if g["finished"] or g["reward_pending"]:
        return

    if g["active_item"] is not None:
        return

    if g["inventory"][item] <= 0:
        return

    g["active_item"] = item

    # CPU가 무효화를 장착한 경우 투시경 차단
    if item == "투시경":

        if g["cpu_item"] != "무효화":

            excluded = [
                choice for choice in CHOICES
                if choice != g["cpu_choice"]
            ]

            g["hint"] = random.choice(excluded)


# ==============================
# 아이템 보상
# ==============================

def claim_reward(item):

    if not g["reward_pending"]:
        return

    g["inventory"][item] += 1
    g["reward_pending"] = False


# ==============================
# 게임 진행
# ==============================

def play(player):

    if g["finished"] or g["reward_pending"]:
        return

    round_number = g["round"]
    fever = round_number % FEVER_INTERVAL == 0

    cpu = g["cpu_choice"]

    player_item = g["active_item"]
    cpu_item = g["cpu_item"]

    logs = []

    # 장착 아이템 소모
    if player_item:
        g["inventory"][player_item] -= 1

    if cpu_item:
        g["cpu_inventory"][cpu_item] -= 1

    # 실제 발동 가능한 아이템
    p_effect = player_item
    c_effect = cpu_item

    # --------------------------
    # 1단계: 무효화
    # --------------------------

    if player_item == "무효화" and cpu_item == "무효화":

        p_effect = None
        c_effect = None

        logs.append(
            "🧊 양쪽의 무효화가 충돌했습니다!"
        )

    elif player_item == "무효화":

        c_effect = None

        if cpu_item:
            logs.append(
                f"🧊 PLAYER가 CPU의 {cpu_item}을 차단!"
            )
        else:
            logs.append("🧊 차단할 CPU 아이템이 없습니다.")

    elif cpu_item == "무효화":

        p_effect = None

        if player_item:
            logs.append(
                f"🧊 CPU가 PLAYER의 {player_item}을 차단!"
            )
        else:
            logs.append("🧊 CPU의 무효화가 효과 없이 소모!")


    # 최초 승패 판정
    result = judge(player, cpu)

    if p_effect == "투시경":
        logs.append("🔍 PLAYER 투시경 사용!")


    # --------------------------
    # 2단계: 재도전
    # --------------------------

    if p_effect == "재도전" and result == "패배":

        old_cpu = cpu
        cpu = random.choice(CHOICES)

        logs.append(
            f"🎲 PLAYER 재도전! "
            f"{EMOJI[old_cpu]} → {EMOJI[cpu]}"
        )

        result = judge(player, cpu)

    elif c_effect == "재도전" and result == "승리":

        old_cpu = cpu
        cpu = random.choice(CHOICES)

        logs.append(
            f"🎲 CPU 재도전! "
            f"{EMOJI[old_cpu]} → {EMOJI[cpu]}"
        )

        result = judge(player, cpu)


    # --------------------------
    # 3단계: 방어막
    # --------------------------

    if p_effect == "방어막" and result == "패배":

        result = "무승부"

        logs.append(
            "🛡️ PLAYER 방어막! 패배를 막았습니다."
        )

    elif c_effect == "방어막" and result == "승리":

        result = "무승부"

        logs.append(
            "🛡️ CPU 방어막! CPU가 패배를 막았습니다."
        )


    # --------------------------
    # 4단계: 점수 계산
    # --------------------------

    points = 10 if fever else 1

    player_gain = 0
    cpu_gain = 0

    if result == "승리":

        if p_effect == "더블 포인트":
            points *= 2
            logs.append("⚡ PLAYER 더블 포인트 발동!")

        player_gain = points

        g["player_score"] += player_gain
        g["win"] += 1
        g["streak"] += 1

    elif result == "패배":

        if c_effect == "더블 포인트":
            points *= 2
            logs.append("⚡ CPU 더블 포인트 발동!")

        cpu_gain = points

        g["cpu_score"] += cpu_gain
        g["lose"] += 1
        g["streak"] = 0

    else:

        g["draw"] += 1
        g["streak"] = 0

    g["best_streak"] = max(
        g["best_streak"],
        g["streak"]
    )


    # --------------------------
    # 5단계: 결과 저장
    # --------------------------

    g["last"] = {
        "round": round_number,
        "player": player,
        "cpu": cpu,
        "result": result,
        "player_item": player_item,
        "cpu_item": cpu_item,
        "player_gain": player_gain,
        "cpu_gain": cpu_gain,
        "fever": fever,
        "logs": logs
    }

    g["history"].append({
        "라운드": round_number,
        "FEVER": "🔥" if fever else "-",
        "PLAYER": player,
        "CPU": cpu,
        "결과": result,
        "획득 점수": player_gain,
        "CPU 획득 점수": cpu_gain
    })


    # --------------------------
    # 6단계: 최종 승리 판정
    # --------------------------

    if (
        g["player_score"] >= TARGET
        or g["cpu_score"] >= TARGET
    ):

        g["finished"] = True
        return


    # --------------------------
    # 7단계: 아이템 보급
    # --------------------------

    if round_number % REWARD_INTERVAL == 0:

        g["reward_pending"] = True

        reward = random.choice(CPU_ITEMS)

        g["cpu_inventory"][reward] += 1
        g["cpu_reward"] = reward

    g["round"] += 1

    prepare_round(g)


# ==============================
# 화면 디자인
# ==============================

st.markdown("""
<style>

.stApp {
    background-image: radial-gradient(
        ellipse at top,
        rgba(255, 100, 30, 0.10),
        transparent 65%
    );
}

.stButton > button {
    min-height: 48px;
    border-radius: 12px;
    font-weight: bold;
}

[data-testid="stMetricValue"] {
    font-weight: 800;
}

</style>
""", unsafe_allow_html=True)


# ==============================
# 제목
# ==============================

st.title("✊ 가위바위보 챌린지")
st.markdown("### 🔥 FEVER : ITEM BATTLE")
st.caption("30점 선취제 · 아이템전 · FEVER 시스템")

st.divider()


# ==============================
# 점수판
# ==============================

st.subheader("🏟️ SCORE BOARD")

left, center, right = st.columns([2, 1, 2])

with left:

    st.metric(
        "👤 PLAYER",
        g["player_score"]
    )

    st.progress(
        min(g["player_score"] / TARGET, 1.0)
    )

with center:
    st.markdown("## VS")

with right:

    st.metric(
        "🤖 CPU",
        g["cpu_score"]
    )

    st.progress(
        min(g["cpu_score"] / TARGET, 1.0)
    )

st.caption(f"목표 점수 : {TARGET}점")

st.divider()


# ==============================
# 최종 게임 결과
# ==============================

if g["finished"]:

    if g["player_score"] >= TARGET:

        st.success("🏆 FINAL VICTORY!")
        st.header("🎉 최종 승리!")
        st.balloons()

    else:

        st.error("💥 FINAL DEFEAT")
        st.header("CPU가 최종 승리했습니다.")

    st.write(
        f"최종 스코어 : "
        f"{g['player_score']} : {g['cpu_score']}"
    )

    if st.button(
        "🔄 새로운 경기 시작",
        type="primary",
        use_container_width=True
    ):

        reset_game()
        st.rerun()


# ==============================
# 직전 라운드 결과
# ==============================

if g["last"]:

    last = g["last"]

    st.subheader(
        f"📢 ROUND {last['round']} RESULT"
    )

    if last["fever"]:
        st.warning("🔥 FEVER ROUND")

    a, b, c = st.columns([2, 1, 2])

    with a:

        st.markdown("### PLAYER")
        st.markdown(
            f"# {EMOJI[last['player']]}"
        )

        st.write(last["player"])

        if last["player_item"]:
            st.caption(
                ITEMS[last["player_item"]]
                + " "
                + last["player_item"]
            )

    with b:
        st.markdown("## VS")

    with c:

        st.markdown("### CPU")
        st.markdown(
            f"# {EMOJI[last['cpu']]}"
        )

        st.write(last["cpu"])

        if last["cpu_item"]:
            st.caption(
                ITEMS[last["cpu_item"]]
                + " "
                + last["cpu_item"]
            )

    if last["result"] == "승리":

        st.success(
            f"🏆 VICTORY! "
            f"+{last['player_gain']} POINTS"
        )

    elif last["result"] == "패배":

        st.error(
            f"💥 DEFEAT! "
            f"CPU +{last['cpu_gain']} POINTS"
        )

    else:

        st.warning("🤝 DRAW — 획득 점수 없음")

    for message in last["logs"]:
        st.info(message)

    st.divider()


# ==============================
# 아이템 보상 화면
# ==============================

if g["reward_pending"] and not g["finished"]:

    st.header("🎁 ITEM REWARD")

    st.success(
        "3라운드 완료! 원하는 아이템을 획득하세요."
    )

    cpu_reward = g["cpu_reward"]

    st.caption(
        f"CPU도 {ITEMS[cpu_reward]} "
        f"{cpu_reward} 아이템을 획득했습니다."
    )

    reward_cols = st.columns(3)

    for i, item in enumerate(ITEMS):

        with reward_cols[i % 3]:

            st.markdown(
                f"### {ITEMS[item]}"
            )

            st.write(item)

            if st.button(
                "획득",
                key=f"reward_{item}",
                use_container_width=True
            ):

                claim_reward(item)
                st.rerun()

    st.divider()


# ==============================
# 현재 라운드
# ==============================

if not g["finished"] and not g["reward_pending"]:

    current_round = g["round"]

    fever = current_round % FEVER_INTERVAL == 0

    st.header(f"⚔️ ROUND {current_round}")

    if fever:

        st.error(
            "🔥🔥🔥 FEVER TIME 🔥🔥🔥"
        )

        st.markdown("## 승리 시 +10 POINTS")

        st.caption(
            "더블 포인트 사용 시 최대 20점!"
        )

    else:

        remaining = (
            FEVER_INTERVAL
            - current_round % FEVER_INTERVAL
        )

        st.info(
            f"🔥 FEVER까지 {remaining}라운드"
        )

        st.progress(
            (FEVER_INTERVAL - remaining)
            / FEVER_INTERVAL
        )


    # CPU 아이템 공개
    if g["cpu_item"]:

        cpu_item = g["cpu_item"]

        st.warning(
            f"🤖 CPU 장착 아이템 : "
            f"{ITEMS[cpu_item]} {cpu_item}"
        )

    else:

        st.info("🤖 CPU 장착 아이템 없음")


    # ==========================
    # 플레이어 아이템 보관함
    # ==========================

    st.subheader("🎒 ITEM INVENTORY")

    item_cols = st.columns(3)

    for i, item in enumerate(ITEMS):

        with item_cols[i % 3]:

            st.markdown(
                f"### {ITEMS[item]}"
            )

            st.markdown(f"**{item}**")

            st.caption(DESCRIPTIONS[item])

            st.write(
                f"보유 : {g['inventory'][item]}개"
            )

            if st.button(
                "장착 완료"
                if g["active_item"] == item
                else "장착",

                key=f"equip_{item}",

                disabled=(
                    g["inventory"][item] == 0
                    or g["active_item"] is not None
                ),

                use_container_width=True
            ):

                equip(item)
                st.rerun()

    if g["active_item"]:

        active = g["active_item"]

        st.success(
            f"{ITEMS[active]} {active} 장착 완료!"
        )

    else:

        st.caption(
            "아이템 없이도 대결할 수 있습니다."
        )

    # 투시경 힌트
    if g["hint"]:

        hint = g["hint"]

        st.warning(
            f"🔍 CPU의 최초 선택은 "
            f"{EMOJI[hint]} {hint}가 아닙니다!"
        )

    elif (
        g["active_item"] == "투시경"
        and g["cpu_item"] == "무효화"
    ):

        st.error("🧊 CPU가 투시경을 차단했습니다.")


    # CPU 보유 아이템
    with st.expander("🤖 CPU 아이템 보관함"):

        for item, count in g["cpu_inventory"].items():

            st.write(
                f"{ITEMS[item]} {item} : {count}개"
            )


    # ==========================
    # 공격 버튼
    # ==========================

    st.divider()
    st.subheader("⚔️ SELECT YOUR HAND")

    attack_cols = st.columns(3)

    for col, choice in zip(attack_cols, CHOICES):

        with col:

            if st.button(
                f"{EMOJI[choice]} {choice}",
                key=f"attack_{choice}",
                type="primary",
                use_container_width=True
            ):

                play(choice)
                st.rerun()


# ==============================
# 통계
# ==============================

st.divider()

st.subheader("📊 BATTLE STATISTICS")

a, b, c = st.columns(3)

a.metric("승리", g["win"])
b.metric("패배", g["lose"])
c.metric("무승부", g["draw"])

d, e = st.columns(2)

d.metric("🔥 현재 연승", g["streak"])
e.metric("👑 최고 연승", g["best_streak"])

total = g["win"] + g["lose"] + g["draw"]

win_rate = (
    g["win"] / total * 100
    if total > 0 else 0
)

st.write(f"총 대결 : {total}회")
st.write(f"승률 : {win_rate:.1f}%")

st.progress(win_rate / 100)


# ==============================
# 전투 기록
# ==============================

with st.expander("📜 전체 전투 기록"):

    if g["history"]:

        st.dataframe(
            list(reversed(g["history"])),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.write("아직 전투 기록이 없습니다.")


# ==============================
# 초기화
# ==============================

st.divider()

if st.button(
    "🔄 경기 및 아이템 초기화",
    use_container_width=True
):

    reset_game()
    st.rerun()

st.caption(
    "ROCK PAPER SCISSORS : FEVER ITEM BATTLE"
)
