# 크롤링을 위한 모듈
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# 딜레이를 위한 모듈
import time

# csv를 위한 모듈
import csv

import random

# 책 정보를 csv파일로 작성
def category(names): 
    driver = webdriver.Chrome()
    driver.get("https://www.kyobobook.co.kr/")
    driver.implicitly_wait(60)

    with open('book_info.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'author', 'category', 'from'])

        for name in names:
            name_set = set() # 중복 체크를 위한 초기화
            # 책 이름 검색
            driver.find_elements(By.CLASS_NAME, "ip_gnb_search")[0].send_keys(name, Keys.ENTER)
            driver.implicitly_wait(60)
        
            # 검색 목록에서 첫번째 책 클릭
            driver.find_elements(By.CLASS_NAME, "prod_info")[0].click()
            driver.implicitly_wait(60)

            # 책 분야 확인
            element = driver.find_element(By.XPATH, '//*[@id="mainDiv"]/main/section[1]/div/ol/li[last()]')
            category_id = element.get_attribute("data-id") # 책 카테고리 코드 추출

            # 1초 대기
            time.sleep(1)

            country = driver.find_element(By.XPATH, '//*[@id="mainDiv"]/main/section[1]/div/ol/li[2]/a')
            country_url = country.get_attribute("href")
            country_id = country_url.split("/")[-1] # 국가 코드 추출

            book_category = driver.find_elements(By.CLASS_NAME, "btn_sub_depth")[2]
            book_category = book_category.text 
    
            #print(f"{name}의 분야: {book_category}")

            full_url = f"https://product.kyobobook.co.kr/category/{country_id}/{category_id}/#?page=1&type=all&per=20&sort=sel"
            # 베이스 URL을 기반으로 국가코드와 책 카테고리 코드를 합치고 판매량 순으로 정렬된 링크를 만듦

            driver.get(full_url)
            driver.implicitly_wait(60)

            # 1초 대기
            time.sleep(1)

            for i in range(1, 11):
                xpath1 = f'//*[@id="homeTabAll"]/div[3]/ol/li[{i}]/div[2]/div[2]/a/span'
                book_element = driver.find_element(By.XPATH, xpath1)
                book_name = book_element.text # 책 이름 크롤링

                xpath2 = f'//*[@id="homeTabAll"]/div[3]/ol/li[{i}]/div[2]/div[2]/span/a'
                author_element = driver.find_element(By.XPATH, xpath2)
                author_name = author_element.text # 책 저자 크롤링

                if book_name not in name_set: # 겹치는 이름이면 csv파일에 작성하지 않음
                    writer.writerow([book_name, author_name, book_category, name])
                    name_set.add(book_name)
    driver.close()     

# 책 이름으로 추천 책 출력
def random_books(name):
    with open("book_info.csv", 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        header = next(reader)

        books = list(reader)
        random.shuffle(books)

        ran_book_rec=[]
        for book in books:
            if book[3] == name:
                if len(ran_book_rec) < 5:
                    ran_book_rec.append(book[0])
                if len(ran_book_rec) == 5:
                    break

    return ran_book_rec