from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import os
from openpyxl import load_workbook
from openpyxl.chart import LineChart, Reference, Series
from openpyxl.utils.dataframe import dataframe_to_rows

# pcode = "69059459"
pcode = "70531547"

def crawl_and_update_excel():
    # Chrome 드라이버 설정
    driver = webdriver.Chrome()

    # 웹페이지 로드
    url = "https://prod.danawa.com/info/?pcode=" + pcode
    driver.get(url)

    # 결과를 저장할 리스트 초기화
    results = []

    try:
        # 명시적 대기 설정 (최대 10초)
        wait = WebDriverWait(driver, 1)

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
            
            # 현재 날짜와 시간 가져오기
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            # 결과 저장
            results.append([pcode, current_datetime, img_alt, price_text])
            print(f"MALL {i}: {img_alt}")
            print(f"가격 {i}: {price_text}")

    except Exception as e:
        print("에러 발생:", str(e))

    finally:
        # 브라우저 종료
        driver.quit()

        # 결과를 데이터프레임으로 변환
        df = pd.DataFrame(results, columns=['PCode', '날짜 및 시간', 'MALL', '가격'])

        # 날짜 및 시간 열을 'YYYY-MM-DD HH' 형식으로 변환
        df['날짜 및 시간'] = pd.to_datetime(df['날짜 및 시간']).dt.strftime('%Y-%m-%d %H:%M')

        # 엑셀 파일로 저장
        file_path = 'danawa_lowest_prices_' + pcode + '.xlsx'
        if os.path.exists(file_path):
            # 기존 파일이 있으면 데이터를 읽어옴
            existing_df = pd.read_excel(file_path)
            # 기존 데이터와 새로운 데이터를 합침
            df = pd.concat([existing_df, df])
        
        # 피벗 테이블 생성
        pivot_df = df.pivot_table(index='날짜 및 시간', columns='MALL', values='가격', aggfunc='first').reset_index()

        # 피벗 테이블을 엑셀 파일로 저장
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a' if os.path.exists(file_path) else 'w') as writer:
            pivot_df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        print("결과가 'danawa_lowest_prices_" + pcode + ".xlsx' 파일로 저장되었습니다.")

        # 엑셀 파일에 차트 추가
        wb = load_workbook(file_path)
        ws = wb.active

        # 차트 생성
        chart = LineChart()
        chart.title = "Mall별 가격 변화"
        chart.style = 13
        chart.y_axis.title = '가격'
        chart.x_axis.title = '날짜 및 시간'
        chart.width = 30  # 차트 너비 설정
        chart.height = 15  # 차트 높이 설정

        # 데이터 참조
        data = Reference(ws, min_col=2, min_row=1, max_col=ws.max_column, max_row=ws.max_row)
        categories = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)

        # 각 Mall별로 데이터 추가
        for col in range(2, ws.max_column + 1):
            series = Series(Reference(ws, min_col=col, min_row=1, max_row=ws.max_row), title_from_data=True)
            chart.series.append(series)

        # 차트 설정 - 선의 두께 및 마커 추가
        colors = ["FF0000", "00FF00", "0000FF", "FFFF00", "FF00FF", "00FFFF", "000000", "800000", "008000", "000080"]
        for i, series in enumerate(chart.series):
            series.graphicalProperties.line.width = 25000  # 선 두께 설정
            series.graphicalProperties.line.solidFill = colors[i % len(colors)]  # 선 색상 설정
            series.smooth = True  # 선을 부드럽게 설정
            series.marker.symbol = "circle"  # 마커 모양 설정
            series.marker.size = 5  # 마커 크기 설정
            series.marker.graphicalProperties.solidFill = colors[i % len(colors)]  # 마커 색상 설정
            series.marker.graphicalProperties.line.solidFill = colors[i % len(colors)]  # 마커 테두리 색상 설정

        # 차트 추가
        ws.add_chart(chart, "E5")

        # 엑셀 파일 저장
        wb.save(file_path)
        print("차트가 'danawa_lowest_prices_" + pcode + ".xlsx' 파일에 추가되었습니다.")

crawl_and_update_excel()