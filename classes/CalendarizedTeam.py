import classes.Team as CTeam

class CalendarizedTeam:
    def __init__(self, team: CTeam.Team, calendar_index: int, played: int, wins: int, draws: int, losses: int, points: int, gf: int, ga: int):
        self.team = team
        self.calendar_index = calendar_index
        self.played = played
        self.wins = wins
        self.draws = draws
        self.losses = losses
        self.points = points
        self.gf = gf
        self.ga = ga

    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items())
        )
    
    def get_team(self) -> CTeam.Team:
        return self.team
    
    def get_name(self):
        return self.team.name
    
    def get_gd(self):
        return (self.gf - self.ga)
    
    def get_str_goals(self) -> str:
        return str(self.gf) + ":" + str(self.ga)
    
    def get_played(self):
        return self.played
    
    def get_str_matches(self) -> str:
        return str(self.played) + " (" + str(self.wins) + "-" + str(self.draws) + "-" + str(self.losses) + ")"
    
    def get_points(self):
        return self.points
    
    def get_market_val(self):
        return self.team.market_val
    
    def update_post_match(self, gf, ga):
        self.played += 1
        self.gf += gf
        self.ga += ga
        if gf > ga:
            self.wins += 1
            self.points += 3
        elif gf < ga:
            self.losses += 1
        elif ga == gf:
            self.draws += 1
            self.points += 1


    def format_data_for_savefile(self) -> str:
        return (str(self.team.get_id()) + " " + str(self.calendar_index) + " " + str(self.played) + " " + str(self.wins) + " " + str(self.draws) + " " + str(self.losses) + " " + str(self.gf) + " " + str(self.ga))
         