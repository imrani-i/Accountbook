import pymysql
import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

dateli = []
newDay=""

## UI파일 불러오기
ui_path = os.path.dirname(os.path.abspath((__file__)))
form_class = uic.loadUiType(os.path.join(ui_path, "hkbook.ui"))[0]
form_class_in = uic.loadUiType(os.path.join(ui_path, "hkBook_in.ui"))[0]
form_class_del = uic.loadUiType(os.path.join(ui_path, "hkBook_del.ui"))[0]

## 마리아 DB 정보
conn = pymysql.connect(
    host="15.164.217.10",
    port=3306,
    user="seran",
    password="1213",
    db="Ssr")

## 메인 폼 클래스
class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.calendarWidget.clicked.connect(self.refresh) ## 새로고침 버튼이 눌렸을 때 refresh호출
        self.inputBtn.clicked.connect(self.inHis)
        self.delBtn.clicked.connect(self.delHis)
        self.scrollArea.setWidget(self.hisLabel)



    ## 새로고침 함수
    def refresh(self):
        global conn ## 전역 개체도 쓸것임
        global dateli
        global newDay

        ## 선택된 날짜 저장하기
        date_qdata = self.calendarWidget.selectedDate() ## 현재 선택된 날짜 가져오기
        date = date_qdata.toString() ## 날짜는 Qdate개체형식으로 반환되어서 문자열로 바꾸기
        dateli = date.split() ## 문자열 나눠서 리스트에저장. 요일[0] 월[1] 일[2] 년도[3] 순서
        self.reDateLabel.setText(dateli[3] + "년 " + dateli[1] + "월 " + dateli[2] + "일") # 제목 텍스트 바꾸기

        ## DB 커서 설정 후 내용 불러오기
        curs = conn.cursor()
        sql = "select * from history where year = " + dateli[3] + " and month = " + dateli[1] + " and day = " + dateli[2]
        curs.execute(sql)
        rows = curs.fetchall()

        ## 거래내역 텍스트 출력하기

        reportStr=""
        for row in rows:
            if len(row[3].encode('cp949')) <= 8:
                reportStr += str(row[5]) + "\t" + str(row[3]) + "\t\t" + str(row[4])+'원' + "\n"
            else:
                reportStr += str(row[5]) + "\t" + str(row[3]) + "\t" + str(row[4])+'원' + "\n"
        self.hisLabel.setText(reportStr)

        ## 이번달 총 수입/지출/잔액 표시하기
        curs = conn.cursor()
        sql = "select * from history where year = " + dateli[3] + " and month = " + dateli[1]
        curs.execute(sql)
        rows = curs.fetchall()

        income = 0
        spend = 0
        for row in rows:
            if row[4] >= 0:
                income += row[4]
            elif row[4] < 0:
                spend += row[4]
        balance = income + spend
        self.incomeL.setText(str(income)+'원')
        self.spendL.setText(str(spend)+'원')
        self.balL.setText(str(balance)+'원')


        ## 내역이 있는 날짜 색칠해주기
        curs = conn.cursor()
        sql = "select * from history"
        curs.execute(sql)
        rows = curs.fetchall()

        wk=QTextCharFormat()

        wk.setForeground(Qt.black)
        self.calendarWidget.setWeekdayTextFormat(Qt.Sunday, wk)
        self.calendarWidget.setWeekdayTextFormat(Qt.Saturday, wk)

        fm = QTextCharFormat()

        tempYear=self.calendarWidget.yearShown()
        tempMonth = self.calendarWidget.monthShown()


        day="select distinct day from history where year=%s and month=%s"
        curs.execute(day, (tempYear,tempMonth))
        tempDay=curs.fetchall()
        tempDay=list(tempDay)


        for i in range (len(tempDay)):
            sum = "select sum(Hvalue) from history where year=%s and month=%s and day=%s"
            curs.execute(sum, (tempYear,tempMonth,tempDay[i]))
            rows = curs.fetchone()
            rows = list(rows)

            if(tempMonth<10):
                newMonth='0'+str(tempMonth)
            if(tempDay[i][0]<10):
                newDay='0'+str(tempDay[i][0])
            else:
                newDay=str(tempDay[i][0])

            tempstring=str(tempYear)+newMonth+newDay

            if(rows[0]>=0):

                Qdday = QDate.fromString(tempstring, "yyyyMMdd")
                fm.setForeground(QBrush(QColor("#0100FF"))) #파란색
                fm.setBackground(QBrush(QColor("#E6F59E")))
                self.calendarWidget.setDateTextFormat(Qdday, fm)

            elif(rows[0]<0):

                Qdday = QDate.fromString(tempstring, "yyyyMMdd")
                fm.setForeground(QBrush(QColor("#FF0000"))) #빨간색
                fm.setBackground(QBrush(QColor("#E6F59E")))
                self.calendarWidget.setDateTextFormat(Qdday, fm)
                



    ## 입력 함수, 아래에 구문 설명 있음
    def inHis(self):
        global dateli
        date_qdata = self.calendarWidget.selectedDate()  ## 현재 선택된 날짜 가져오기
        date = date_qdata.toString()  ## 날짜는 Qdate개체형식으로 반환되어서 문자열로 바꾸기
        dateli = date.split()  ## 문자열 나눠서 리스트에저장. 요일[0] 월[1] 일[2] 년도[3] 순서

        Win = MyWindow_in()
        Win.showModal()
        self.refresh()

    ## 지우기 함수
    def delHis(self):
        global dateli
        date_qdata = self.calendarWidget.selectedDate()  ## 현재 선택된 날짜 가져오기
        date = date_qdata.toString()  ## 날짜는 Qdate개체형식으로 반환되어서 문자열로 바꾸기
        dateli = date.split()  ## 문자열 나눠서 리스트에저장. 요일[0] 월[1] 일[2] 년도[3] 순서

        Win = MyWindow_del()
        Win.showModal()
        self.refresh()

    def show(self):
        super().show()

## 입력 폼 클래스
class MyWindow_in(QDialog, form_class_in):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.insert)
        self.Hvalue.setPlaceholderText('금액')
        self.Hvalue_2.setPlaceholderText('금액')
        self.hName.setPlaceholderText('상세내역')
        self.hName_2.setPlaceholderText('상세내역')

    def insert(self):
        global conn  ## 전역 개체도 쓸것임
        global dateli

        cate = self.inCombo.currentText()
        name = self.hName.text()
        value = self.Hvalue.text()


        cate2 = self.outCombo.currentText()
        name2 = self.hName_2.text()
        value2 = self.Hvalue_2.text()


        curs = conn.cursor()
        sql = "INSERT INTO history (year, month, day, Hname, Hvalue, chacategory) values(%s, %s, %s, %s, %s, %s)"

        if dateli[3] != None and dateli[1] != None and dateli[2] != None and name != None and value != None and cate != None and len(name) > 0 and len(value) > 0 and len(cate) > 0:
            curs.execute(sql, (dateli[3], dateli[1], dateli[2], name,value, cate))

        if dateli[3] != None and dateli[1] != None and dateli[2] != None and name2 != None and value2!= None and cate2 != None and len(name2) > 0 and len(value2) > 0 and len(cate2) > 0:
            k = (-1) * int(value2)
            curs.execute(sql, (dateli[3], dateli[1], dateli[2], name2, k, cate2))

        conn.commit()
        self.close()

    def showModal(self):
        return super().exec_()

## 지우기 폼 클래스
class MyWindow_del(QDialog, form_class_del):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.delete)
        self.lineEdit.setPlaceholderText('상세내역')

    def delete(self):
        global conn
        global dateli

        name = self.lineEdit.text()
        curs = conn.cursor()
        sql = "DELETE FROM history where year = %s and month = %s and day = %s and Hname = %s"

        if dateli[3] != None and dateli[1] != None and dateli[2] != None and name != None and len(name) > 0:
            curs.execute(sql, (dateli[3], dateli[1], dateli[2], name))

        conn.commit()
        self.close()

    def showModal(self):
        return super().exec_()

## 메인 함수
if __name__ == "__main__":
    ## 메인 폼 호출
    app = QApplication(sys.argv) ## QApplication클래스 형식의 app인스턴스 선언
    Win = MyWindow() ## MyWindow클래스 형식의 myWindow인스턴스 선언
    Win.show() ## MyWindow클래스의 메서드 show호출. 윈도우 창 생성
    Win.refresh() ## 시작과 동시에 화면에 각종 정보 표시
    app.exec_() ## 이벤트가 발생할때까지 무한루프하며 대기하는 메서드(폼을 화면에 계속 표시해줌)

    ## 마리아 DB 연결종료
    conn.close()