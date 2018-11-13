from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
import time
from tkinter import *
import pandas
import threading

class racingSportsScraper:

    def __init__(self, dayoption = 0):
        self.dayoption = dayoption
        self.cur_day = datetime.datetime.now() + datetime.timedelta(days=dayoption)
        self.statue = False
        
        self.initGUI()

    def initGUI(self):
        RACE_DATES = ['TODAY', 'TOMORROW', 'NEXT DAY']
        self.window = Tk()
        self.window.configure(background='#6DC6D8')
        self.window.title("Racing Sports Scraper")
        self.window.geometry("330x200")

        labelframe = LabelFrame(self.window, text = "SELECT DATE", bg='#6DC6D8', fg="BLUE", font=("Courier", 14))
        labelframe.place(x=20, y=20)

        self.var = IntVar()
        i = 0
        for i in range(0, 3):
            R1 = Radiobutton(labelframe, text = RACE_DATES[i], variable = self.var, bg='#6DC6D8', value = i, justify=CENTER, fg="BLUE", font=("Courier", 12),command=self.selectDay)
            R1.configure(activebackground="#6DC6D8")
            R1.pack(anchor = W)
        self.startButton = Button(self.window, command=self.start)
        self.startButton.configure(height=4, width=10)
        self.startButton.configure(font=("Courier", 16))
        self.startButton.configure(foreground="BLUE")
        self.startButton.configure(background="#6DC6D8")
        self.startButton.configure(activebackground="#6DC600")
        self.startButton.configure(highlightbackground="#ffffff")
        self.startButton.configure(text='''START''')
        self.startButton.place(x=170, y=25)

        self.window.mainloop()

    def selectDay(self):
        if self.statue == False:
            self.dayoption = self.var.get()
        else:
            print("Now going...")

    def printList(self, string, lists):
        print(string)
        for row in lists:
            print(row)
        return

    def go(self):
        self.statue = True
        print(self.statue)
        raceInfo = self.read_excel()
        runnerList = self.extractRunnerList()
        raceDay = self.extractRaceDay()
        print('Composing.....')
        result = []
        for listrow in runnerList:
            item = listrow
            i = 0
            for inforow in raceInfo['Horse']:
                if inforow.upper() == listrow['Horse']:
                    race_time = ''
                    for dayrow in raceDay:
                        if listrow['Race'].upper() == dayrow['Race']:
                            race_time = dayrow['Time']
                            break
                    item['Date of Entry'] = raceInfo['Date of Entry'][i]
                    item['Data Source'] = raceInfo['Data Source'][i]
                    item['Race Time'] = race_time
                    result.append(item)
                    break
                i = i + 1
        self.save_excel(result)
        self.statue = False

    def start(self):
        if (self.statue == False):
            t = threading.Thread(target=self.go)
            t.start()
        else:
            print("Now going...")
        return 1

    def f(self):
        return 1

    def extractRunnerList(self):
        print("extracting RunnerList...")
        # url = "https://www.racingandsports.com.au/en/form-guide/index.asp?mdate=" + str(self.cur_day.day) + "%2F" + str(self.cur_day.month) + "%2F" + str(self.cur_day.year) + "&mdiscipline=T&type=Runner+List"
        url = "https://www.racingandsports.com.au/en/form-guide/index.asp"
        
        try:
            browser = webdriver.Chrome()
            browser.get(url)
            time.sleep(2)
            dayButton = None
            if (self.dayoption == 0):
                dayButton = browser.find_element_by_xpath("//form/input[@value='Today']")
            elif (self.dayoption == 1):
                dayButton = browser.find_element_by_xpath("//form/input[@value='Tomorrow']")
            else:
                dayButton = browser.find_element_by_xpath("//form/input[@value='Next Day']")
            
            dayButton.click()
            time.sleep(2)

            listButton = browser.find_element_by_xpath("//form/input[@value='Runner List']")
            listButton.click()
            time.sleep(3)

            soup = BeautifulSoup(browser.page_source, "html.parser")
            
            rows = soup.find("div", {"id":"div_Discipline_T"}).find("table").findAll("tr")[1:]
            result = []
            for row in rows:
                cols = row.findAll("td")
                item = {}
                item["Horse"]   =   cols[0].getText()
                item["Race"]    =   cols[1].getText()
                item["Tab"]     =   cols[2].getText()
                item["WT"]      =   cols[3].getText()
                item["BP"]      =   cols[4].getText()
                result.append(item)
            browser.quit()
            return result

        except Exception as e:
            if hasattr(e, 'message'):
                print("extractRunnerList: " + e.message)
            else:
                print("extractRunnerList: " + e)

    def extractRaceDay(self):

        print("extracting extractRaceDay...")
        url = "https://www.racingandsports.com/race-day"

        try:
            browser = webdriver.Chrome()
            browser.get(url)
            time.sleep(5)
            soup = BeautifulSoup(browser.page_source, "html.parser")            

            todaytab = soup.find("ul", {"class": "nav nav-tabs tabs-secondary date-parent date-filter"}).find("li", {"class":"today"})
            tomorrowtab = todaytab.find_next_sibling("li")
            nextdaytab = tomorrowtab.find_next_sibling("li") 
            
            daytab = None
            if (self.dayoption == 1):
                daytab = tomorrowtab
            elif (self.dayoption == 2):
                daytab = nextdaytab
            else:
                daytab = todaytab
            
            date_info = daytab.find("a")["data-date"]
            tab_content_classname = "cty_AUS_" + date_info + "_T"

            rows = soup.find("div", {"class": tab_content_classname}).find("table").findAll("tr")
            result = []
            for row in rows:
                cols = row.findAll("td")
                racename = cols[0].getText() + " R"
                i = 1
                for col in cols[2:]:
                    item = {}
                    item["Race"] = racename + str(i)
                    item["Time"] = col.getText()
                    i = i + 1
                    if item["Time"] == '':
                        continue
                    result.append(item)
            browser.quit()
            return result
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)

    def read_excel(self):
        # return array json data
        print("Read Excel file....")
        raceinfo = pandas.read_excel('current.xlsx', dtype={'Horse':str, 'Date of Entry': str, 'Data Source':str})
        return raceinfo
    
    def save_excel(self, data):
        print("save excel")
        horses = []
        tabs = []
        race_times = []
        date_of_entrys = []
        data_source = []
        race = []
        wt = []
        bp = []
        for row in data:
            horses.append(row['Horse'])
            tabs.append(row['Tab'])
            race_times.append(row['Race Time'])
            date_of_entrys.append(row['Date of Entry'])
            data_source.append(row['Data Source'])
            race.append(row['Race'])
            wt.append(row['WT'])
            bp.append(row['BP'])
        df = pandas.DataFrame({'Horse':horses, 'Tab':tabs, 'Race Time': race_times, 'Date of Entry':date_of_entrys, 'Data Source': data_source, 'Race':race, 'WT':wt, 'BP':bp})
        filename = 'result'
        if (self.dayoption == 0):
            filename = filename + '_today.xlsx'
        elif (self.dayoption == 1):
            filename = filename + '_tomorrow.xlsx'
        else:
            filename = filename + '_nextday.xlsx'
        df.to_excel(filename, index=False)
        return 1

def main():
    try:
        s = racingSportsScraper()

    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
    else:
        print("Success!")

if __name__ == "__main__":
    main()
