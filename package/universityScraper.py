import pycountry
from bs4 import BeautifulSoup
import requests
import re


class UniversityScraper:

    

    def __init__(self , country = "cyprus", study = "E", degree = "B", fees = 999999, city=""):

        self.country = country
        self.study = study
        self.degree = degree
        self.fees = fees
        self.city = city
        

    BASE_URL = "https://www.4icu.org"


    STUDY_AREAS = {
        "A" : 0 ,
        "B" : 1,
        "L" : 2,
        "M" : 3,
        "E" : 4,
        "S" : 5
    }


    DEGRESS_LEVELS = {
        "B" : 2,
        "M" : 3,
        "D" : 4
    }



    def textFilter(self,text):
    
        range_ = re.findall(r'\d+,*\d*',text)
        fst_num = int ( range_[0].replace(",","") )
        amount = fst_num

        suitable = False

        if self.fees >= fst_num:
            suitable = True

        if len(range_) >1 :
            amount = range_[0]+"-"+range_[1]+" $"

        return { "suitable" : suitable , "amount" : amount}


    def getFees(self,body):
    
        tr = body.find("tr")
        tds = tr.find_all("td")

        if self.degree == "B":
            
            strong = tds[1].find("strong")

        else:
            strong = tds[2].find("strong")

        text = strong.get_text()

        if text == "Not reported":

            return { "suitable" : True , "amount" : None}

        else:

            text = self.textFilter(text[0:text.index("$")])

        return text


    def getStudy(self,body):

        trs = body.find_all('tr')
        tr = trs[self.STUDY_AREAS[self.study]]
        tds = tr.find_all('td')
        td = tds[self.DEGRESS_LEVELS[self.degree]]
        
        i = td.find('i')
        exist = False
        if i['class'][1] == 'd1':
            exist = True

        return exist


    def getUniDetail(self,href):

        html_text = requests.get(self.BASE_URL+href).text
        soup = BeautifulSoup(html_text,"lxml")
        body = soup.find_all('tbody' )
        

        body_1 = body[1]
        body_2 = body[2]

        study_ = self.getStudy(body_1)
        fees_ = { "suitable" : False , "amount" :-1}


        if study_:
            fees_ =  self.getFees(body_2)

        #print(study_,fees_)
        return { 
            "study" : study_,
            "fees" : fees_
            }


    def start(self):

        
        abb = pycountry.countries.search_fuzzy(self.country)[0].alpha_2.lower()

        html_text = requests.get(self.BASE_URL+"/"+abb+"/"+self.city+"/").text
        soup = BeautifulSoup(html_text,"lxml")

        print(self.BASE_URL+"/"+abb+"/"+self.city+"/")

        body = soup.find('tbody')
        unis = []

        for tr in body.find_all("tr"):

            tds = tr.find_all("td")

            try:
                
                rank = tds[0].contents[0].get_text()
                name = tds[1].contents[0].get_text()
                city = tds[2].contents[0]

                a = tds[1].find('a')
                detail = self.getUniDetail(a['href'])
            


                if detail['study']  and detail['fees']['suitable']:
                    unis.append({
                        'rank' : rank,
                        'name':name,
                        'city':city,
                        'link':a['href'],
                        'detail':detail
                    })

            except:
                break

            

        return unis