import streamlit as st
import pandas as pd
import os

# Streamlit 애플리케이션
st.title("Danawa Lowest Prices")
st.write("This application displays the lowest prices from Danawa.")

# 엑셀 파일 경로
file_path = 'danawa_lowest_prices_70531547.xlsx'

# 엑셀 파일 읽기
if os.path.exists(file_path):
    df = pd.read_excel(file_path)

    # 데이터프레임 표시
    st.write("### Data")
    st.dataframe(df)

    # 데이터 요약 통계
    st.write("### Summary Statistics")
    st.write(df.describe())

    # 데이터 필터링
    st.write("### Filter Data")
    date_filter = st.date_input("Select date range", [])
    if date_filter:
        start_date, end_date = date_filter
        df = df[(df['날짜 및 시간'] >= pd.to_datetime(start_date)) & (df['날짜 및 시간'] <= pd.to_datetime(end_date))]
        st.dataframe(df)

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
    st.write("No data available. Please run the Python script to generate the Excel file.")