import requests
from bs4 import BeautifulSoup


# possibility with these exist !!!!!!!!!!!!
# https://www.transfermarkt.com/wettbewerbe/national/wettbewerbe/{i}


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
}

file = open("utils/data.txt", "a+")

for i in range(1,19):
    url = f'http://www.transfermarkt.com/wettbewerbe/europa?page={i}'
    html = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(html.content)
    for elem in soup.select_one(".items").select_one("tbody").select("tr"):
        try:
            x = elem.select_one("td").select_one("td").select_one("a")['href']
            cod = str.split(x, "/")
            file.write(f"{cod[-1]}\n")
        except:
            pass
        
for i in range(1,6):
    url = f'http://www.transfermarkt.com/wettbewerbe/asien?page={i}'
    html = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(html.content)
    for elem in soup.select_one(".items").select_one("tbody").select("tr"):
        try:
            x = elem.select_one("td").select_one("td").select_one("a")['href']
            cod = str.split(x, "/")
            file.write(f"{cod[-1]}\n")
        except:
            pass
        
for i in range(1,6):
    url = f'http://www.transfermarkt.com/wettbewerbe/amerika?page={i}'
    html = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(html.content)
    for elem in soup.select_one(".items").select_one("tbody").select("tr"):
        try:
            x = elem.select_one("td").select_one("td").select_one("a")['href']
            cod = str.split(x, "/")
            file.write(f"{cod[-1]}\n")
        except:
            pass
        
url = f'http://www.transfermarkt.com/wettbewerbe/afrika?page={1}'
html = requests.get(url, headers=HEADERS)
soup = BeautifulSoup(html.content)
for elem in soup.select_one(".items").select_one("tbody").select("tr"):
    try:
        x = elem.select_one("td").select_one("td").select_one("a")['href']
        cod = str.split(x, "/")
        file.write(f"{cod[-1]}\n")
    except:
        pass

file.close()




