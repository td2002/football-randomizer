class Team:
    
    ENCODING = 'utf-8'

    def __init__(self, id: int, name: str, official_name: str, country: str, league, tier, market_val: int, img: bytes, colours: str, stadium_name: str, stadium_seats: int, squad: int, avg_age: float, fifa_rank: int, bonus: int):
        self.id = id
        self.name = name
        self.official_name = official_name
        self.country = country
        self.league = league
        self.tier = tier
        self.market_val = market_val
        self.img = img
        self.colours = colours
        self.stadium_name = stadium_name
        self.stadium_seats = stadium_seats
        self.squad = squad
        self.avg_age = avg_age
        self.fifa_rank = fifa_rank
        self.bonus = bonus

    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name
    
    def get_country(self):
        return self.country
    
    def get_img(self) -> bytes:
        return self.img
    
    def get_stadium_name(self):
        return self.stadium_name
    
    def get_market_val(self):
        return self.market_val
    
    # last colour of the returned list is the color the font on this should take (b/w)
    def get_colours(self) -> list[str]:

        def single_op(c: int) -> float:
            c = c / 255.0
            if c <= 0.04045 :
                 c = c/12.92
            else:
                c = ((c+0.055)/1.055) ** 2.4
            return c
        
        c_list = self.colours.split()

        first = c_list[0]
        f = []
        f.append(int(first[0:2], 16))
        f.append(int(first[2:4], 16))
        f.append(int(first[4:6], 16))

        c = []
        for i in range(3):
            c.append(single_op(f[i]))
        L = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
        if L > 0.179:
            c_list.append("000000")
        else:
            c_list.append("FFFFFF")

        '''#if all(x < 160 for x in f):
        if ((f[0]+f[2]-f[1]) >= -150):
            c_list.append("FFFFFF")
        else:
            c_list.append("000000")'''

        c_list = ['#'+c for c in c_list]
        return c_list
    

