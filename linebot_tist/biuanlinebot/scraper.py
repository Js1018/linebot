from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import requests
from urllib import parse
import pandas as pd
import datetime
import urllib.request as req
from bs4 import BeautifulSoup as bs
 
# 抽象類別
class BIu(ABC):
 
    def __init__(self,keywords):
        if len(keywords)==3:
            self.keywords = keywords[0]
            self.startdate = keywords[1]
            self.endate = keywords[2]  
        elif len(keywords)==2:
            self.keywords = keywords[0]
            self.startdate = keywords[1]
            self.endate = 0
        elif len(keywords)==1:
            self.keywords = keywords[0]
            self.startdate = 0
            self.endate = 0
 
    @abstractmethod
    def scrape(self):
        pass
 
 
# 爬蟲
class BIuan(BIu):
    def scrape(self):
         
        keywords=self.keywords  
        startdate  = self.startdate
        endate = self.endate
        keywords=parse.quote(keywords.encode('utf-8'))
        try:
            if startdate==0:
                pass 
            elif len(startdate)<8:
                return '請寫入西曆'  
            else:
                if '-' in startdate:
                    startdate = datetime.datetime.strptime(startdate, '%Y-%m-%d')
                elif '/' in startdate:
                    startdate = datetime.datetime.strptime(startdate, '%Y/%m/%d')
                else:
                    startdate = datetime.datetime.strptime(startdate, '%Y%m%d')
        except:
            return '請填入正確的起始日期'

        try:
            if endate==0:
                pass 
            elif len(endate)<8:
                return '請寫入西曆'

            else:
                if '-' in endate:
                    endate = datetime.datetime.strptime(endate, '%Y-%m-%d')
                elif '/' in endate:
                    endate = datetime.datetime.strptime(endate, '%Y/%m/%d')
                else:
                    endate = datetime.datetime.strptime(endate, '%Y%m%d')
        except:
            return '請填入正確的結束日期'
        if (startdate!=0) & (endate!=0) :    
            url='https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic?firstSearch=true&searchType=basic&orgName=&orgId=&tenderName='+keywords+'&tenderId=&tenderType=TENDER_DECLARATION&tenderWay=TENDER_WAY_ALL_DECLARATION&dateType=isDate&tenderStartDate='+str(startdate.year)+'%2F'+str(startdate.month)+'%2F'+str(startdate.day)+'&tenderEndDate='+str(endate.year)+'%2F'+str(endate.month)+'%2F'+str(endate.day)
        elif (endate==0) & (endate==0)  :      
            endate = datetime.date.today()
            startdate = endate+datetime.timedelta(-6)
            url='https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic?firstSearch=true&searchType=basic&orgName=&orgId=&tenderName='+keywords+'&tenderId=&tenderType=TENDER_DECLARATION&tenderWay=TENDER_WAY_ALL_DECLARATION&dateType=isNow&tenderStartDate=+&tenderEndDate='
        elif startdate==0 :
            startdate = endate+datetime.timedelta(-6)
            url='https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic?firstSearch=true&searchType=basic&orgName=&orgId=&tenderName='+keywords+'&tenderId=&tenderType=TENDER_DECLARATION&tenderWay=TENDER_WAY_ALL_DECLARATION&dateType=isDate&tenderStartDate='+str(startdate.year)+'%2F'+str(startdate.month)+'%2F'+str(startdate.day)+'&tenderEndDate='+str(endate.year)+'%2F'+str(endate.month)+'%2F'+str(endate.day)
        else :
            endate = datetime.date.today()
            url='https://web.pcc.gov.tw/prkms/tender/common/basic/readTenderBasic?firstSearch=true&searchType=basic&orgName=&orgId=&tenderName='+keywords+'&tenderId=&tenderType=TENDER_DECLARATION&tenderWay=TENDER_WAY_ALL_DECLARATION&dateType=isDate&tenderStartDate='+str(startdate.year)+'%2F'+str(startdate.month)+'%2F'+str(startdate.day)+'&tenderEndDate='+str(endate.year)+'%2F'+str(endate.month)+'%2F'+str(endate.day)

        request = req.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        })
        with req.urlopen(request) as response:
            data = response.read().decode("utf-8")
        try:
            bsobj_1 = bs(data, "lxml")
            tables = bsobj_1.find_all('tbody')

            trs = tables[1].find_all('tr')

            trNum = 0
            tdNum = 0
            result = []
            for i in range(len(trs)):
                tds = trs[i].find_all('td')
                if len(tds) < 5:  # 跳過沒有內容的 tr
                    continue
                trNum += 1
                tdNum = 0
                tempList = []
                for j in tds:
                    if j.text == '\xa0':
                        continue
                    tempText = "  ".join(j.text.split())  # 去掉文字中的 \xa0 空白字元
                    tempList.append(tempText)
                    tdNum += 1
                result.append(tempList)

            base = pd.DataFrame(result,columns=['項次','機關名稱','標案案號','傳輸次數','招標方式','採購性質','公告日期','截止日期','投標預算金額','功能選項'])
            trNum = 0
            tdNum = 0
            result = []
            for i in range(len(trs)):
                tds = trs[i].find_all('script')
                trNum += 1
                tdNum = 0
                tempList = []
                for j in tds:
                    if j.text == '\xa0':
                        continue
                    tempText = "  ".join(j.text.split())  # 去掉文字中的 \xa0 空白字元
                    tempList.append(tempText)
                    tdNum += 1

                result.append(tempList[0][tempList[0].find('(\"')+2:tempList[0].find('\");')])
            base.insert(3,"標案名稱",result)
            del base['功能選項']
            nam=''
            for i in range(base.shape[0]) :
                for j in base.columns:
                    nam=nam+j+':'+ base[j].loc[i]+'\n'
                nam=nam+'\n\n'
            return nam
        except:
            d=endate-startdate

            if d.days>92:
                return "您所設定之查詢區間較長，基於系統效能考量，請用「全文檢索」功能查詢。"
            else:
                return "搜索日期中沒有標案"+str(d)
