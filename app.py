import streamlit as st
from bazi import get_bazi, interpret_bazi
from datetime import date
from bazi import get_bazi, chat_about_bazi

st.title("八字命盘")
st.caption("仅供娱乐参考")

col1, col2 = st.columns(2)
with col1:
    birth_date = st.date_input(
        "出生日期",
        value=date(1995, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date.today(),
    )
    gender = st.radio("性别", ["男", "女"])
with col2:
    birth_time = st.time_input("出生时间")
    city = st.text_input("出生城市", placeholder="例如：Shenzhen")

if st.button("排盘"):
    if not city:
        st.error("请输入出生城市")
    else:
        try:
            with st.spinner("..."):
                result = get_bazi(
                    birth_date.year, birth_date.month, birth_date.day,
                    birth_time.hour, birth_time.minute,
                    gender,
                    city
                )
            st.session_state["result"] = result
        except ValueError as e:
            st.error(str(e))

if "result" in st.session_state:
    result = st.session_state["result"]

    st.subheader("四柱")
    st.write(" ".join(result["四柱"]))
    st.subheader("五行")
    st.write(result["五行"])
    st.subheader("天干十神")
    st.write(result["天干十神"])
    st.subheader("地支十神")
    st.write(result["地支十神"])
    st.subheader("藏干")
    st.write(result["藏干"])
    st.subheader("大运")
    for item in result["大运"]:
        st.write(item)

    st.divider()
    st.subheader("问答")

    # initialize chat history for this chart
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # replay the conversation so far
    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("有什么想问的?"):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("..."):
                answer = chat_about_bazi(result, st.session_state["messages"])
            st.write(answer)

        st.session_state["messages"].append({"role": "assistant", "content": answer})