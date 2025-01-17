from flask import Flask, render_template, request, redirect

from crawler import book_list
from algorithm import user_book_category, random_books, category
from DataProcessing import sha512_hash, listTostr, strTolist, now_time
from show_data_test import show_data

import sqlite3
import time
import os

try:
    print("database 폴더 생성")
    os.mkdir("database/")
except:
    print("database 폴더가 이미 존재합니다.")

conn = sqlite3.connect("database/bookmate.db")
cur = conn.cursor()

try:
    print("테이블 생성")
    cur.execute(""" CREATE TABLE StudentsData(
        StudentNumber INT(8) PRIMARY KEY,
        HashPassword TEXT(128),
        BookList TEXT,
        CrawlingDate TEXT
    );
    """)
    cur.execute(""" CREATE TABLE Book(
        BookName TEXT PRIMARY KEY,
        BookCategory TEXT
    );
    """)
except:
    print("테이블이 이미 존재합니다.")

# 페이지 이름 설정
app = Flask("Bookmate")

# 메인 페이지(홈 페이지) 라우팅/ 리퀘스트 방법 GET, POST
@app.route("/", methods=["GET"])
def home():
    # 사용자에게 home.html 파일을 보여줌
    return render_template("Home.html")

# "기본 페이지 URL + /UserData" 라우팅
@app.route("/UserData", methods=["POST"])
def inputData():
    start_time = time.time()
    conn = sqlite3.connect("database/bookmate.db")
    cur = conn.cursor()
    id, pw = "", ""
    if request.method == "POST":
        # 사용자가 입력한 데이터를 받아옴
        id = request.form.get("ID")
        pw = request.form.get("PASSWORD")
        print(f"ID: {id}, sha512_hash: {sha512_hash(pw)}")
    # 사용자가 입력한 데이터를 데이터베이스에 저장하기 위한 형변환
    id, pw = int(id), str(pw)

    # 데이터베이스에 학번에 있는지 확인
    user_db_result = cur.execute("SELECT * FROM StudentsData WHERE StudentNumber = ?", (id,)).fetchone()
    # print(f"user_db_result[-1]: {user_db_result[-1]}, now_time(): {now_time()}")
    if user_db_result == None:
        user_book_info_list = book_list(id=id, pw=pw, ReturnData=2)
        print(user_book_info_list)
        # 크롤링에 실패하면 홈으로 리다이렉트(크롤러는 작동 중 오류가 발생하면 0을 리턴)
        if user_book_info_list == 0:
            print("웹 페이지 로딩 오류")
            # 문제가 발생하면 홈으로 리다이렉트
            return redirect("/")


        elif user_book_info_list == 1:
            print("대출 기록이 없습니다.")
            cur.execute("INSERT INTO StudentsData (StudentNumber, HashPassword, BookList, CrawlingDate) VALUES (?, ?, ?, ?)", (id, sha512_hash(pw), listTostr(user_book_info_list), now_time()))
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/")

        cur.execute("INSERT INTO StudentsData (StudentNumber, HashPassword, BookList, CrawlingDate) VALUES (?, ?, ?, ?)", (id, sha512_hash(pw), listTostr(user_book_info_list), now_time()))

        # 책 이름만 저장
        user_book_list = [item[1] for item in user_book_info_list]


    elif user_db_result[1] != sha512_hash(pw):
        print(f"아이디: {id}에 대한 비밀번호가 틀렸습니다.")
        return redirect("/")

    # 업데이트 날짜가 오늘이 아니면 업데이트
    elif user_db_result[-1] != now_time():
        print("책 대출 기록을 업데이트합니다.")
        user_book_info_list = book_list(id=id, pw=pw, ReturnData=2)
        user_book_list = [item[1] for item in user_book_info_list]
        cur.execute("UPDATE StudentsData SET BookList = ?, CrawlingDate = ? WHERE StudentNumber = ?", (listTostr(user_book_info_list), now_time(), id))
        conn.commit()


    else:
        user_book_info_list = []
        for book_name in strTolist(user_db_result[2]):
            # 0: 책 코드, 1: 책 이름, 2: 지은이
            user_book_info_list.append(book_name[1])
        # 책 이름만 저장
        user_book_list = user_book_info_list

        # 저장 웹 페이지에 출력하기 위함, 데이터를 다시 코드, 이름, 저자의 형태로 변환
        user_book_info_list = strTolist(user_db_result[2])
    book_category = {}
    for user_book_name in user_book_list:
        book_db_result = cur.execute("SELECT * FROM Book WHERE BookName = ?", (user_book_name,)).fetchone()
        if book_db_result == None:
            book_category[user_book_name] = user_book_category(user_book_name)[user_book_name]
            cur.execute("INSERT INTO Book (BookName, BookCategory) VALUES (?, ?)", (user_book_name, book_category[user_book_name]))
        else:
            book_category[user_book_name] = book_db_result[1]

    if user_db_result == None:
        show_data(list(book_category.values()), id=id)

    conn.commit()
    cur.close()
    conn.close()

    end_time = time.time() - start_time
    print("총 걸린 시간: {}초\n".format(end_time))
    # 코드가 정상적으로 작동하면 SearchResult.html 페이지에 책 리스트 출력
    return render_template("SearchResult.html", bookinfos=user_book_info_list, bookcategory=book_category, student_number=str(id), re_books=random_books([item[1] for item in user_book_info_list]), loading_time=end_time)

# 이스터 에그, html 연습용
@app.route("/EarthAndMoon")
def EarthAndMoon():
    return render_template("EarthAndMoon.html")

# debug 모드로 실행
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")