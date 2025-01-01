import streamlit as st
import pandas as pd

# 엑셀 파일 경로
file_path = 'danawa_lowest_prices_70531547.xlsx'

# 엑셀 파일 읽기
df = pd.read_excel(file_path)

# Streamlit 애플리케이션
st.title("Danawa Lowest Prices")
st.write("This application displays the lowest prices from Danawa.")

# 데이터프레임 표시
st.dataframe(df)

# 차트 표시
st.line_chart(df.set_index('날짜 및 시간'))