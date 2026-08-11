import streamlit as st
from bazi import get_bazi
from datetime import date

st.title("八字命盘")

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
            with st.spinner("计算中..."):
                result = get_bazi(
                    birth_date.year, birth_date.month, birth_date.day,
                    birth_time.hour, birth_time.minute,
                    gender,
                    city
                )
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
        except ValueError as e:
            st.error(str(e))