import streamlit as st
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pytz

# Streamlit 애플리케이션
st.title("다나와 최저가 크롤러")
st.write("다나와 사이트에서 최저가 정보를 크롤링하고 엑셀 파일에 저장합니다.")
st.write("모니터링 요청했던 물건의 pcode를 입력하세요.")

# 고유 번호 입력
if 'pcode' not in st.session_state:
    st.session_state.pcode = ""

pcode = st.text_input("물건의 고유 번호를 입력하세요", st.session_state.pcode)

# 검색 버튼
if st.button("검색"):
    st.session_state.pcode = pcode

# 엑셀 파일 경로
file_path = f'danawa_lowest_prices_{st.session_state.pcode}.xlsx'

# 엑셀 파일 읽기
if st.session_state.pcode:
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        # 데이터 필터링
        st.write("### Filter Data")
        date_filter = st.date_input("Select date range", [])
        if date_filter:
            start_date, end_date = date_filter
            df = df[(df['날짜 및 시간'] >= pd.to_datetime(start_date)) & (df['날짜 및 시간'] <= pd.to_datetime(end_date))]
            st.dataframe(df)

        # 데이터프레임 표시
        st.write("### Data")
        st.dataframe(df)

        # 데이터 요약 통계
        st.write("### Summary Statistics")
        st.write(df.describe())


        # 차트 표시
        st.write("### Line Chart")
        st.line_chart(df.set_index('날짜 및 시간'))

        st.write("### Bar Chart")
        st.bar_chart(df.set_index('날짜 및 시간'))

        st.write("### Area Chart")
        st.area_chart(df.set_index('날짜 및 시간'))

        # 데이터 다운로드
        st.write("### Download Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='danawa_lowest_prices.csv',
            mime='text/csv',
        )
    else:
        st.write("No data")
else:
    st.write("pcode를 입력해주세요.")