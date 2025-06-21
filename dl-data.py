import httpx
from bs4 import BeautifulSoup

def save_html(url: str = "https://www.nysedregents.org/algebratwo/") -> None:
    content = httpx.get(url)
    
    with open("regents_data/src.html", "w") as file:
        file.write(content.text)
        
def process_html():
    with open("regents_data/src.html", "r") as file:
        soup = BeautifulSoup(file)
    
    data = []
    
    for test in soup.select('#content-center > ul > li'):
        test_data = {}
        test_data["date"] = test.text
        test_data["test_url"] = test.select("ul > li:nth-child(1) > ul > li:nth-child(1) > a")[0].get("href")
        test_data["answers_url"] = test.select("ul > li:nth-child(2) > ul > li:nth-child(1) > a")[0].get("href")
        data.append(test_data)
    
    
        
        