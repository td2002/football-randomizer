from bs4 import BeautifulSoup
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
}


file = open("comps_ids.txt", "r")
file_out = open("comps_data.txt", "w+")
file_err = open("comps_err.txt", "w+")

comps = file.readlines()

length = len(comps)
print(f'all={length}')

#print(comps)
for i in range(length):
    curid = comps[i][:-1]
    url = f'http://www.transfermarkt.com/-/startseite/wettbewerb/{curid}'
    html = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(html.content)

    try:
        comp_name = str.strip(soup.select_one("h1").contents[0])
        country = str.strip(soup.select_one("main").select_one("header").select("div")[1].select("a")[1].contents[0])
        tier = str.strip(soup.select_one("main").select_one("header").select("div")[1].select("span")[1].select_one("span").contents[0])
        num_teams = str.split(str.strip(soup.select_one("main").select_one("li").select_one("span").contents[0]))[0]
        
        file_out.write(f'{comp_name}§§§{country}§§§{tier}§§§{num_teams}§§§{curid}\n')
        print(i)
    except:
        file_err.write(f'{curid}\n')
        print(f'{i}: error')
        

file.close()
file_out.close()
file_err.close()