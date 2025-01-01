# import streamlit as st
# import pandas as pd

# # 엑셀 파일 경로
# file_path = 'danawa_lowest_prices_70531547.xlsx'

# # 엑셀 파일 읽기
# df = pd.read_excel(file_path)

# # Streamlit 애플리케이션
# st.title("Danawa Lowest Prices")
# st.write("This application displays the lowest prices from Danawa.")

# # 데이터프레임 표시
# st.dataframe(df)

# # 차트 표시
# st.line_chart(df.set_index('날짜 및 시간'))
import streamlit as st
import pandas as pd
import numpy as np

# Streamlit 애플리케이션
st.title("Simple Chart Example")
st.write("This application displays a simple chart using Streamlit.")

# 예제 데이터 생성
np.random.seed(42)
dates = pd.date_range("20230101", periods=100)
data = pd.DataFrame(np.random.randn(100, 4), index=dates, columns=list("ABCD"))

# 데이터프레임 표시
st.write("### Example Data")
st.dataframe(data)

# 라인 차트 표시
st.write("### Line Chart")
st.line_chart(data)

# 바 차트 표시
st.write("### Bar Chart")
st.bar_chart(data)

# 영역 차트 표시
st.write("### Area Chart")
st.area_chart(data)