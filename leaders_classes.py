import json
import threading
import requests
from bs4 import BeautifulSoup
import re
import json
import functools
import time

start = time.perf_counter()


root_url = "https://country-leaders.herokuapp.com"
status_url = "status"
country_url = "countries"
cookie_url = "cookie"
leaders_url = "leaders"

s = requests.session()

l = {}

class FirstParagraph(threading.Thread):
    def __init__(self, wikipedia_url,leader,country):
        super().__init__()
        
        
        self.wikipedia_url = wikipedia_url
        self.firstparagraph = ""
        self.leader = leader
        self.country = country
        
    def run(self):
        #self.wikipedia_url = "https://en.wikipedia.org/wiki/Barack_Obama"
        html_doc = s.get(self.wikipedia_url)
        soup = BeautifulSoup(html_doc.text,"html.parser")   
        product=soup.find('div',id="mw-content-text")
        product=product.find_all('p')
        for elements in product:
            if elements.find("b"):
                self.firstparagraph = elements.text
                break
        
        self.firstparagraph = re.sub("\/.*?\/ \(listen\).*?\[.*?\]","",self.firstparagraph)
        self.firstparagraph = re.sub("\(\/.*?/.*?\)","",self.firstparagraph)
        self.firstparagraph = re.sub("\( uitspraak \(info / uitleg\)\)","",self.firstparagraph)
        self.firstparagraph = re.sub("uitspraak \(info / uitleg\)","",self.firstparagraph)
        self.firstparagraph = re.sub("\[.*?]","",self.firstparagraph)
        self.firstparagraph = re.sub("\\n","",self.firstparagraph)
        self.firstparagraph = self.firstparagraph
        #print(self.firstparagraph)
        l[self.country][leader]["first_paragpraph"] = self.firstparagraph
        return self.firstparagraph
   
   
class GetCountries(threading.Thread):
    def __init__(self,root_url,country_url,cookie_url):
        super().__init__()
    
        self.countryList = []
        self.rootUrl = root_url
        self.countryUrl = country_url
        self.cookieUrl = cookie_url
    
    def run(self):
        cookie = s.get(f"{self.rootUrl}/{self.cookieUrl}")
        countries = s.get(f"{self.rootUrl}/{self.countryUrl}", cookies=cookie.cookies)
        self.countryList = json.loads(countries.content)
        return self.countryList
    
    
class GetLeaders(threading.Thread):
    def __init__(self, country,root_url,leaders_url,cookie_url):
        super().__init__()
        
        self.country = country
        self.rootUrl = root_url
        self.leadersUrl = leaders_url
        self.cookieUrl = cookie_url
        self.leaders = {}
        
    def run(self):
        cookie = s.get(f"{self.rootUrl}/{self.cookieUrl}")
        leaders = s.get(f"{self.rootUrl}/{self.leadersUrl}",params=f"country={self.country}")
        self.leaders = json.loads(leaders.content)
        print(self.country)
        l[self.country] = self.leaders
        return self.leaders        
        
        
#a=FirstParagraph("https://en.wikipedia.org/wiki/Barack_Obama")
#b = a.run()

c = GetCountries(root_url,country_url,cookie_url)
countries = c.run()
print (countries)

e = GetLeaders("us",root_url,leaders_url,cookie_url)
f = e.run()
threads = []
for country in countries:
    t = GetLeaders(country,root_url,leaders_url,cookie_url)
    t.start()
    threads.append(t)

for t in threads:
    t.join()
    print(t)

print(type(l))

threads = []

for country in countries:
    for leader in range (len(l[country])):
        t = FirstParagraph(l[country][leader]["wikipedia_url"],leader,country)
        t.start()
        print(t)
        threads.append(t)
    
    for t in threads:
       t.join()

print(t)
print(time.perf_counter()-start)