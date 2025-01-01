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
pcode = st.text_input("물건의 고유 번호를 입력하세요", "")

# 검색 버튼
if st.button("검색"):
    if pcode:
        # 크롤링 함수 정의
        def crawl_and_update_excel(pcode):
            # Chrome 드라이버 설정
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # headless 모드 활성화
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=chrome_options)

            # 웹페이지 로드
            url = "https://prod.danawa.com/info/?pcode=" + pcode
            driver.get(url)

            # 현재 시간의 가격 데이터를 저장할 딕셔너리
            kst = pytz.timezone('Asia/Seoul')
            current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
            current_prices = {'날짜 및 시간': current_time}

            try:
                # 명시적 대기 설정
                wait = WebDriverWait(driver, 10)

                # lowest list tr개수 가져오기 
                browser = driver
                xpath = "/html/body/div[2]/div[5]/div[2]/div[2]/div[2]/div[1]/div[2]/div[3]/table/tbody[1]/tr"
                tr_elements = browser.find_elements(By.XPATH, xpath)
                rows = len(tr_elements)
                print(f"총 {rows}개의 항목이 있습니다.")
                
                for i in range(1, rows + 1):
                    try:
                        # 이미지 요소 찾기 및 src 속성 가져오기
                        img_xpath = f"/html/body/div[2]/div[5]/div[2]/div[2]/div[2]/div[1]/div[2]/div[3]/table/tbody[1]/tr[{i}]/td[1]/div/a/img"
                        img_element = wait.until(EC.presence_of_element_located((By.XPATH, img_xpath)))
                        img_alt = img_element.get_attribute('alt')
                    except:
                        # 이미지 요소가 없을 경우 텍스트 추출
                        img_xpath = f"/html/body/div[2]/div[5]/div[2]/div[2]/div[2]/div[1]/div[2]/div[3]/table/tbody[1]/tr[{i}]/td[1]/div/a"
                        img_alt = wait.until(EC.presence_of_element_located((By.XPATH, img_xpath))).text
                    
                    # 가격 요소 찾기 및 텍스트 가져오기
                    price_xpath = f"/html/body/div[2]/div[5]/div[2]/div[2]/div[2]/div[1]/div[2]/div[3]/table/tbody[1]/tr[{i}]/td[2]/a/span/em"
                    price_element = wait.until(EC.presence_of_element_located((By.XPATH, price_xpath)))
                    price_text = price_element.text.replace(',', '')  # 쉼표 제거
                    price_text = float(price_text)  # 숫자로 변환
                    
                    # 현재 시간의 가격 데이터에 추가
                    current_prices[img_alt] = price_text
                    print(f"MALL {i}: {img_alt}")
                    print(f"가격 {i}: {price_text}")

            except Exception as e:
                print("에러 발생:", str(e))

            finally:
                # 브라우저 종료
                driver.quit()

                file_path = 'danawa_lowest_prices_' + pcode + '.xlsx'
                
                # 현재 가격 데이터를 DataFrame으로 변환
                new_df = pd.DataFrame([current_prices])
                
                if os.path.exists(file_path):
                    # 기존 파일이 있으면 데이터를 읽어옴
                    try:
                        existing_df = pd.read_excel(file_path)
                        # 기존 데이터와 새로운 데이터를 합침
                        df = pd.concat([existing_df, new_df], ignore_index=True)
                    except Exception as e:
                        print(f"기존 파일 읽기 실패: {e}")
                        df = new_df
                else:
                    df = new_df

                # 날짜로 정렬
                df['날짜 및 시간'] = pd.to_datetime(df['날짜 및 시간'])
                df = df.sort_values('날짜 및 시간')
                df['날짜 및 시간'] = df['날짜 및 시간'].dt.strftime('%Y-%m-%d %H:%M')

                # 데이터 저장
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, index=False, sheet_name=pcode)

                print("결과가 'danawa_lowest_prices_" + pcode + ".xlsx' 파일로 저장되었습니다.")

        # 크롤링 함수 실행
        crawl_and_update_excel(pcode)

        # 엑셀 파일 읽기
        file_path = 'danawa_lowest_prices_' + pcode + '.xlsx'
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
        st.write("Please enter a valid product code.")