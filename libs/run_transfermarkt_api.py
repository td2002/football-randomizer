import classes.Team as Team, classes.CalendarizedTeam as CalendarizedTeam
import requests
import os
import random
import base64
import libs.page_requests as prapi
from matplotlib import colors


DEFAULT_STADIUM_SEATS = 100
DEAFULT_MARKET_VALUE = 10000 # this gives a min ovr for a min team of slightly over 200 (??) (min mrkt val in tm.com is 10k)
DEFAULT_AVG_AGE = 100
DEFAULT_STADIUM_NAME = "Stadium"
#DEFAULT_COUNTRY_NAME = "Ʊnknown"
DEFAULT_COUNTRY_NAME = "World"
DEFAULT_LEAGUE_NAME = "Ʊnknown League"
DEFAULT_YOUTH_TIER_NUM = 18
DEFAULT_REGIONAL_TIER_NUM = 30
DEFAULT_UNKNOWN_LEAGUE_NUM = 50
DEFAULT_TIER_NAME = "Ʊnknown"

# not precise, just a result of a test. it's used for random matches, NOT THE BEST!
#MAX_ID = 113412


def format_name(str):

    if (str.find('\\') >= 0) or (str.find('/') >= 0) or (str.find("'")):
        ret_str = str.replace('\\', '⧵')
        ret_str = ret_str.replace('/', '-')
        # this is similar but not too good in gui: ∕
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
    elif str_val.find("m") >= 0:
        val = str_val.split("m")
        mul = 10**6
    elif str_val.find('k') >= 0:
        val = str_val.split('k')
        mul = 10**3
    val = val[0].split("€")
    val_ret = float(val[1]) * mul

    return round(val_ret)

def num_from_stadium_seats(seats_str):
    str_ret = seats_str.replace('.', '')
    return int(str_ret)


def get_team_data(team_id: int):
    try:
        all_data = prapi.Profile(club_id=f"{team_id}").get_club_profile()
        return all_data
    except:
        print("Error during API request for the team (NEW, local)")
        return None
    
def fix_country_for_nts(name: str, country: str) -> str:
    parts = name.split()
    suffixes = ["U"+str(i) for i in range(15,24)]
    l = len(parts)
    if len(parts) > 2 and parts[-1] in suffixes:
        spaced = []
        for i in parts[0:len(parts)-1]:
            spaced.append(i)
            spaced.append(" ")
        parts[0] = "".join(spaced[0:len(spaced)-1])
        parts[1] = parts[len(parts)-1]
    elif len(parts) > 1 and parts[-1] not in suffixes:
        spaced = []
        for i in parts[0:len(parts)]:
            spaced.append(i)
            spaced.append(" ")
        parts[0] = "".join(spaced[0:len(spaced)-1])
        l = 1
    if parts[0] == country and l == 1:
        return "National Team"
    elif parts[0] == country and parts[1] in suffixes:
        return "National Team"
    return country
    

def get_basics_from_search_name(team_name: str, how_many: int) -> tuple[int, str, str, bytes]:

    dec = how_many
    if dec < 0:
        dec = 1
    elif dec > 10:
        dec = 10

    try:
        all_data = prapi.ClubSearch(query=team_name).search_clubs()["results"]
        
        tmp = []
        for i in range(dec):
            tmp.append([])
        tot = dec
        
        for team in all_data:   
                if dec > 0:
                    tmp[tot-dec].append(int(team["id"]))
                    tmp[tot-dec].append(team["name"])
                    country = fix_country_for_nts(team["name"], team["country"])
                    tmp[tot-dec].append(country)
                    img_url = "https://tmssl.akamaized.net/images/wappen/small/" + str(tmp[tot-dec][0]) + ".png"
                    img = requests.get(img_url).content
                    if img == b'':
                        img_url = "https://tmssl.akamaized.net/images/wappen/small/default.png"
                        img = requests.get(img_url).content
                    tmp[tot-dec].append(img)
                    dec-=1
                else: 
                    break

        return tuple(tmp)

    except:
        print("Error during API request for the basics team search with name... (NEW local)")
        return tuple([])
        
    

def get_ids_from_search_name(team_name: str, how_many: int) -> tuple[int]:

    dec = how_many
    if dec < 0:
        dec = 1
    elif dec > 10:
        dec = 10

    try:
        all_data = prapi.ClubSearch(query=team_name).search_clubs()["results"]
        tmp = []
        for team in all_data:
            if dec > 0:
                tmp.append(int(team["id"]))
                dec-=1
            else: 
                break

        return tuple(tmp)
    
    except:
        print("Error during API request for the team search with name... (NEW, local)")
        return tuple([])



def get_ids_from_competition(comp: str, year: int) -> tuple[int]:
    try:
        all_data = prapi.TransfermarktCompetitionClubs(competition_id=comp, season_id=year).get_competition_clubs()
        ret = []
        for c in all_data['clubs']:
            ret.append(int(c['id']))
        return ret
    except:
        print("Error during API request for the competition (NEW, local)")
        return None
    
    

def get_teams_from_ids(ids: tuple[int], badge: int) -> tuple[Team.Team]:
    tmp = []
    for i in ids:
        tmp.append(get_team_from_id(i, badge))
    return tuple(tmp)

# not useful since sometimes the "normquad" version of images doesnt exist!
def format_img_urls(urls: list) -> list:
    ret_list = []
    for u in urls:
        ret_list.append(str.replace(u, "medium", "normquad"))
    return ret_list


def check_colours(colours: list[str]) -> list[str]:
    ret = []
    for c in colours:
        try:
           int(c[1:], 16)
           ret.append(c)
        except:
           ret.append(colors.to_hex(c[1:]))
    return ret
    

def get_team_from_id(id: int, badge: int, only_club_team=False) -> Team.Team:
    team_data = get_team_data(id)
        
    if team_data:
        
        nat_team = False
        bonus = -3

        try:
            market_val = num_from_market_value(team_data['currentMarketValue'])
        except:
            market_val = DEAFULT_MARKET_VALUE
            bonus += -10
        name = team_data['name']
        name = format_name(name)

        try:
            official_name = team_data['officialName']
        except:
            official_name = name
            bonus += -1
        official_name = format_name(official_name)

        try:
            country = team_data['customCountry']
        except:
            country = DEFAULT_COUNTRY_NAME
            bonus += -1
        
        try: 
            # sometimes the country isn't in a proper var but in the last address line (we try...)
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
            colours = check_colours(team_data['colors'])
        except:
            colours = ['#000000']
            bonus += -3
        colours = format_colours(colours)

        try:
            stadium_name = team_data['stadiumName']
            stadium_name = format_name(stadium_name)
        except:
            stadium_name = DEFAULT_STADIUM_NAME
            bonus += -2
        try:
            stadium_seats = num_from_stadium_seats(team_data['stadiumSeats'])
            if stadium_seats < DEFAULT_STADIUM_SEATS:
                stadium_seats = DEFAULT_STADIUM_SEATS
                bonus += 3
        except:
            stadium_seats = DEFAULT_STADIUM_SEATS
            bonus += -1
        
        try:
            confed = team_data['confederation']
            country = confed
            nat_team = True
            if only_club_team and nat_team: return None
        except:
            pass

        try:
            fifa_rank = team_data['fifaWorldRanking']
            nat_team = True
            if only_club_team and nat_team: return None
        except:
            fifa_rank = None

        try:
            squad = int(team_data['squad']['size'])
        except:
            squad = 0
            bonus += -1

        try:
            avg_age = float(team_data['squad']['averageAge'])
        except:
            avg_age = DEFAULT_AVG_AGE
            bonus += -1

        crests_urls = [team_data['image']]
        try:
            crests_urls += team_data['historicalCrests']
            bonus += round((len(crests_urls)-1)/2)
        except:
            pass

        if badge == 2:
            r = random.randint(0, len(crests_urls)-1)
        else:
            r = badge % len(crests_urls)

        #print(crests_urls, r)
        img_url = crests_urls[r]

        #img_url = team_data['image']
        #img, img_file_name = save_img_from_url_place(img_url, name, country, league, tier, nat_team)
        img = requests.get(img_url).content

        # various boni based on fields in response: if many, more bonus ("more famous club")
        try:
            team_data['league']
            bonus += 7
        except:
            pass
        try:
            bonus += round(len(team_data['otherSports'])/2)
        except:
            pass
        try:
            team_data['website']
            bonus += 2
        except:
            pass
        try:
            bonus += len(team_data['historicalCrests'])
        except:
            pass
        try:
            team_data['addressLine1']
            bonus += 3
        except:
            pass
        try:
            team_data['addressLine2']
            bonus += 2
        except:
            pass
        try:
            team_data['addressLine3']
            bonus += 1
        except:
            pass
        try:
            team_data['tel']
            bonus += 1
        except:
            pass
        try:
            team_data['fax']
            bonus += 1
        except:
            pass
        try:
            team_data['foundedOn']
            bonus += 1
        except:
            pass

        #print(bonus)

        if only_club_team and nat_team:
            return None
        else:
            return Team.Team(id, name, official_name, country, league, tier, market_val, img, colours, stadium_name, stadium_seats, squad, avg_age, fifa_rank, bonus)
    
    else:
        raise Exception(f"No team found with id={id}")

    
def save_img_from_url(image_url, dir_name, file_name):
    img_data = requests.get(image_url).content

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    file_name_tot = dir_name + file_name
    with open(file_name_tot, 'wb') as handler:
        handler.write(img_data)
    return handler, file_name_tot

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

'''def view_image(cursor, id):
    sql1="select img from tm_teams.teams where id = " + str(id)
    cursor.execute(sql1)
    data = cursor.fetchall()
    data1=base64.b64decode(data[0][0])
    file_like=io.BytesIO(data1)
    img=PIL.Image.open(file_like)
    img.show()'''

def format_null(x):
    if x:
        return str(x)
    return "NULL"

def get_random_team(badges: int, pot: int, only_club_team=True) -> Team.Team:
    rand_start, rand_end = 0, -1
    div = 3.6
    tmp = None
    gaussian_rands = [round(random.gauss(0,6)) for i in range(2)]
    print(f"gaussian rands = {gaussian_rands[0]}, {gaussian_rands[1]}")

    match pot:
        case 0:
            rand_start, rand_end = 1, 25
        case 1:
            rand_start, rand_end = 1, 100
        case 2:
            rand_start, rand_end = 1, 1000
        case 3:
            with open("files/metadata.txt") as file_tmp:
                rand_start, rand_end = 1, gaussian_rands[1] + int(file_tmp.readline().split()[1])//(div**3)
        case 4:
            with open("files/metadata.txt") as file_tmp:
                tot_teams = int(file_tmp.readline().split()[1])
                rand_start, rand_end = gaussian_rands[0] + tot_teams//(div**3), gaussian_rands[1] + tot_teams//(div**2)
        case 5:
            with open("files/metadata.txt") as file_tmp:
                tot_teams = int(file_tmp.readline().split()[1])
                rand_start, rand_end = (2*gaussian_rands[0]) + tot_teams//(div**2), (2*gaussian_rands[1]) + tot_teams//(div)
        case 6:
            with open("files/metadata.txt") as file_tmp:
                tot_teams = int(file_tmp.readline().split()[1])
                rand_start, rand_end = round(2.5*gaussian_rands[0]) + tot_teams//(div), tot_teams
        case 7:
            with open("files/metadata.txt") as file_tmp:
                rand_start, rand_end = 0, int(file_tmp.readline().split()[1])
        case 8:
            with open("files/metadata.txt") as file_tmp:
                rand_start, rand_end = int(file_tmp.readline().split()[1]), int(file_tmp.readline().split()[1])
    
    print(f"rand start, end = {rand_start}, {rand_end}")
    with open("files/ids_ordered.txt") as file:
        lines = file.readlines()

    while tmp is None:
        l_rand = random.randint(rand_start, rand_end)
        selected_id = lines[l_rand].split()[0]
        print(f"rand selected row num (id) = {l_rand} ({selected_id})")
        tmp = get_team_from_id(int(selected_id), badges, only_club_team)
    return tmp

def get_random_team_old(badges: int, pots: list) -> Team.Team:

    lines = []
    i=0
    for f in pots:
        if f != 0:
            if i==0:
                with open("files/g_100mio.txt", "r") as file:
                    lines+=file.readlines()
            elif i==1:
                with open("files/le_100mio.txt", "r") as file:
                    lines+=file.readlines()
            elif i==2:
                with open("files/le_10mio.txt", "r") as file:
                    lines+=file.readlines()
            elif i==3:
                with open("files/le_1mio.txt", "r") as file:
                    lines+=file.readlines()
            elif i==4:
                with open("files/le_100k.txt", "r") as file:
                    lines+=file.readlines()
            elif i==5:
                with open("files/le_10k.txt", "r") as file:
                    lines+=file.readlines()
            elif i==6:
                with open("files/no_market_val.txt", "r") as file:
                    lines+=file.readlines()
        i+=1

    l_rand = random.randint(0, len(lines)-1)
    content = str.replace(lines[l_rand], "\n", "")
        
    t = get_team_from_id(int(content), badges)
    return t
