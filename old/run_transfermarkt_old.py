import requests
import os
import random
import io
import base64
import PIL.Image

DEFAULT_STADIUM_SEATS = 100
DEAFULT_MARKET_VALUE = 10000
DEFAULT_STADIUM_NAME = "Generic"
DEFAULT_COUNTRY_NAME = "Ʊnknown"
DEFAULT_LEAGUE_NAME = "Ʊnknown League"
DEFAULT_YOUTH_TIER_NUM = 18
DEFAULT_REGIONAL_TIER_NUM = 30
DEFAULT_UNKNOWN_LEAGUE_NUM = 50
DEFAULT_TIER_NAME = "Ʊnknown"

def format_name(str):

    if (str.find('\\') >= 0) or (str.find('/') >= 0) or (str.find("'")):
        ret_str = str.replace('\\', '⧵')
        ret_str = ret_str.replace('/', '∕')
        ret_str = ret_str.replace("'", '\'\'')
        return ret_str
    return str


def format_colours(colours:list):
    str_ret = ""
    for c in colours:
        str_ret += c
        str_ret += " "
    str_ret = str_ret.replace('#', '').upper()
    return str_ret


def num_from_market_value(str_val):
    #m -> million
    #bn -> billion
    #k -> 1000
    #...
    #val = [1]
    mul = 1

    if str_val.find('bn') >= 0:
        val = str_val.split('bn')
        mul = 10**9
    if str_val.find("m") >= 0:
        val = str_val.split("m")
        mul = 10**6
    if str_val.find('k') >= 0:
        val = str_val.split('k')
        mul = 10**3
    val = val[0].split("€")
    val_ret = float(val[1]) * mul

    return round(val_ret)

def num_from_stadium_seats(seats_str):
    str_ret = seats_str.replace('.', '')
    return int(str_ret)


def get_team_data(team_id):
    url = f"http://localhost:8000/clubs/{team_id}/profile"
    x = random.randint(2, 5)
    headers = {
        "User-Agent": f"Mozilla/{x}.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/5{3+x}.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        all_data = response.json()
       
        return all_data
    else:
        print("Error during API request for the team")
        return None

    
def save_img_from_url(image_url, dir_name, file_name):
    img_data = requests.get(image_url).content

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    file_name_tot = dir_name + file_name
    with open(file_name_tot, 'wb') as handler:
        handler.write(img_data)
    return handler, file_name_tot

def save_img_from_url_place(image_url, name, country, tier_str, tier, nat_team):
    if not nat_team:
        str_ret_dir = IMG_FOLDER + "\\" + country + "\\" + str(tier) + " - " + tier_str
    else:
        str_ret_dir = IMG_FOLDER + "\\National Teams\\" + country
    
    str_ret_file = "\\" + name + ".png"
    return save_img_from_url(image_url, str_ret_dir, str_ret_file)

def extract_tier_from_str(tier_str):
    
    if tier_str.find("Youth") >= 0:
        return DEFAULT_YOUTH_TIER_NUM
    if tier_str.find("Regional") >= 0:
        return DEFAULT_REGIONAL_TIER_NUM
    if tier_str.find(DEFAULT_TIER_NAME) >= 0:
        return DEFAULT_UNKNOWN_LEAGUE_NUM
    
    if tier_str.find("First") >= 0:
        return 1
    if tier_str.find("Second") >= 0:
        return 2
    if tier_str.find("Third") >= 0:
        return 3
    if tier_str.find("Fourth") >= 0:
        return 4
    if tier_str.find("Fifth") >= 0:
        return 5
    if tier_str.find("Sixth") >= 0:
        return 6
    if tier_str.find("Seventh") >= 0:
        return 7
    if tier_str.find("Eighth") >= 0:
        return 8
    if tier_str.find("Ninth") >= 0:
        return 9
    else:
        return 10
    
def convert_to_bin_data(filename):
    with open(filename, 'rb') as f:
        photo = f.read()
    encodestring = base64.b64encode(photo)
    return encodestring

def view_image(cursor, id):
    sql1="select img from tm_teams.teams where id = " + str(id)
    cursor.execute(sql1)
    data = cursor.fetchall()
    data1=base64.b64decode(data[0][0])
    file_like=io.BytesIO(data1)
    img=PIL.Image.open(file_like)
    img.show()

def format_null(x):
    if x:
        return str(x)
    return "NULL"

def main():

    start = 1
    end = 117020
    # empiric limit: 117020 last team on transfermarkt.com !
    #ids = range(start, end)
    
    path_to_files_dir = ""

    with open(f"{path_to_files_dir}/MISSED.txt", "r") as file_in:
        lines = file_in.readlines()
    ids = [int(s) for s in lines[:-1]]

    for id in ids:
        #time.sleep(1)
        print(f"{id} : ", end="")
        team_data = get_team_data(id)
        
        if team_data:
            
            nat_team = False

            try:
                market_val = num_from_market_value(team_data['currentMarketValue'])
            except:
                #market_val = DEAFULT_MARKET_VALUE
                market_val = 1

            name = team_data['name']
            name = format_name(name)
            #print(name)

            try:
                official_name = team_data['officialName']
            except:
                official_name = name

            official_name = format_name(official_name)

            try:
                country = team_data['league']['countryName']
                
            except:
                country = DEFAULT_COUNTRY_NAME
            
            try: 
                # sometimes the country isn't in a proper var but in the last address line
                if country == DEFAULT_COUNTRY_NAME:
                    country = team_data['addressLine3']
            except:
                country = DEFAULT_COUNTRY_NAME
                
            try:
                league = team_data['league']['name']
                tier_str = team_data['league']['tier']
            except:
                league = DEFAULT_LEAGUE_NAME
                tier_str = DEFAULT_TIER_NAME


            tier = extract_tier_from_str(tier_str)

            
            try:
                colours = team_data['colors']
            except:
                colours = ['#000000']
            try:
                stadium_name = team_data['stadiumName']
                stadium_name = format_name(stadium_name)
            except:
                stadium_name = DEFAULT_STADIUM_NAME
            try:
                stadium_seats = num_from_stadium_seats(team_data['stadiumSeats'])
                if stadium_seats < DEFAULT_STADIUM_SEATS:
                    stadium_seats = DEFAULT_STADIUM_SEATS
            except:
                stadium_seats = DEFAULT_STADIUM_SEATS
            
            try:
                confed = team_data['confederation']
                country = confed
                nat_team = True
            except:
                pass

            try:
                fifa_rank = team_data['fifaWorldRanking']
            except:
                fifa_rank = None

            img_url = team_data['image']

            print(id)

            #view_image(cursor, id)

            file = open(f"{path_to_files_dir}/ids_with_market_vals_MISSHIT.txt", "a")
            file.write(f"{str(id)} {market_val}\n")
            file.close
            
        
        else:
            file = open(f"{path_to_files_dir}/MISSED_MISSHIT.txt", "a")
            file.write(str(id)+"\n")
            file.close


if __name__ == "__main__":
    main()
