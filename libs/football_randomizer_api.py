import classes.Team as Team, classes.CalendarizedTeam as CalendarizedTeam
import random
import math
import copy

# fitting function: k logx + q (function for calc ovr from market val)
FUNCT_K = 121
FUNCT_Q = -250
# for the squad size add
FUNCT_A = 100

# max bonuses for ovr calcs
MAX_BONUS_STADIUM = 15
#MAX_BONUS_SQUAD_SIZE = 20
#MIN_BONUS_SQUAD_SIZE = -50

# whole bar to divide in 3: team1, nothing, team2 (for minute events)
RANGE_RAND_EVENT = 120000

# possible substitutions and probability
POSSIBLE_SUBS = [1, 2, 3, 4, 5]
PROB_SUBS = [38, 36, 19, 5, 2]
MAX_SUBS = 5

# coeffs to determine if the whole match is more goal likely or not (randomly selected, higher means less goal-like)
#GOAL_COEFF_MIN = 5*(10**4)
#GOAL_COEFF_MAX = 2*(10**5)+20000   old method (bugged for equal low ovr teams)
GOAL_COEFF_DIV_MIN = 18
GOAL_COEFF_DIV_MAX = 59
GOAL_COEFF_MUL = 11


# strings for occasions, cards, etc
'''ARR_STR_OCCASIONS = ["Shot blocked by defence", "Goalkeeper arrives on a good shot", "Shot wide on the right", "Ball goes flying off the left", 
                     "Ball hit the left post", "Weak shot after speedy buildup", "Powerful shot just out on the left", "Free kick goes just out on the left",
                     "Referee stops nice build-up for offside", "Good play in the box read by goalkeeper"]'''
'''ARR_STR_OCCASIONS = [
    "The striker launches a powerful shot but it's blocked by a brave defender",
    "A teasing cross from the winger forces the goalkeeper to make a diving save",
    "The midfielder whips in a dangerous ball, but it's cleared by the defense",
    "A quick one-two between teammates almost unlocks the defense",
    "The striker's header goes just wide of the post",
    "The midfielder unleashes a fierce shot from distance, narrowly missing the target",
    "The winger's cross is cut out by the goalkeeper before it reaches its target",
    "A clever through ball splits the defense, but the striker can't reach it in time",
    "The goalkeeper rushes off his line to smother the ball before the striker can reach it",
    "A powerful shot from outside the box rattles the crossbar",
    "The midfielder attempts a clever chip over the defense, but it's intercepted",
    "The winger beats his marker with a burst of pace but his cross is too close to the goalkeeper",
    "The striker's shot is deflected wide for a corner kick",
    "The goalkeeper misjudges the flight of the ball, but it sails harmlessly over the bar",
    "A lofted pass into the box almost finds the head of the onrushing striker",
    "The midfielder tries to pick out a teammate with a through ball, but it's intercepted",
    "The winger's low cross fizzes across the face of goal, but nobody can get a touch",
    "The striker attempts an audacious bicycle kick, but it's off target",
    "A whipped free kick into the box is cleared by the defense",
    "The midfielder's shot from distance is comfortably saved by the goalkeeper",
    "The winger cuts inside onto his favored foot but his shot is blocked by a defender",
    "A clever flick almost releases the striker behind the defense",
    "The goalkeeper claims a high ball under pressure from the striker",
    "A long-range effort from the midfielder sails over the bar",
    "The winger attempts a curling shot from the edge of the box, but it's wide",
    "The striker's shot is charged down by a defender and goes out for a throw-in",
    "The midfielder tries to thread a pass through the defense, but it's intercepted",
    "The winger's cross is too high for the striker and goes out for a goal kick",
    "A well-timed tackle from the defender denies the striker a shooting opportunity",
    "The goalkeeper collects a looping cross under pressure from the onrushing striker",
    "A powerful shot from outside the box is blocked by a resilient defender",
    "The midfielder's through ball is cut out by the opposition defense",
    "The striker's shot from a tight angle is saved by the goalkeeper",
    "A curling effort from the midfielder is comfortably saved by the goalkeeper",
    "The winger's cross is too close to the goalkeeper who collects it easily",
    "A low shot from the striker is saved by the goalkeeper's outstretched leg",
    "The midfielder attempts a long-range shot but it's blocked by a sliding defender",
    "The winger tries to beat his marker but loses possession near the touchline",
    "A lofted pass into the box is headed away by the defender",
    "The striker attempts an acrobatic volley but doesn't connect cleanly",
    "The goalkeeper punches away a dangerous cross from the winger",
    "The midfielder's shot from distance is blocked by a well-positioned defender",
    "The striker's flick-on header finds a teammate, but his shot is wide of the mark",
    "A driven cross into the box is intercepted by the goalkeeper",
    "The midfielder's shot takes a deflection and goes out for a corner kick",
    "The winger's cross is headed away by the defender at the near post",
    "A clever dummy from the striker almost releases his teammate into space",
    "The midfielder tries to play a one-two with the striker, but the return pass is intercepted",
    "A long ball over the top almost releases the striker, but the goalkeeper is quick off his line",
    "The winger's cross is overhit and sails out of play for a goal kick",
    "The striker attempts to control a high ball but is dispossessed by the defender",
    "A clever dummy from the midfielder creates space for a shot, but it's blocked by a defender",
    "The goalkeeper punches away a dangerous cross, under pressure from the onrushing striker",
    "The midfielder's shot from distance takes a wicked deflection, but the goalkeeper adjusts well to make the save",
    "The winger cuts inside onto his stronger foot and looks for a shooting opportunity, but the defense closes him down quickly",
    "A low cross from the winger is cut out by the goalkeeper, who smothers the ball at the near post",
    "The striker attempts an audacious chip from outside the box, but it sails harmlessly over the bar",
    "A lofted through ball almost finds the run of the striker, but it's intercepted by the defender",
    "The midfielder tries to find a teammate with a lofted pass, but it's too heavy and goes out for a throw-in",
    "The winger's attempted cross is blocked by the defender and goes out for a corner kick",
    "A clever flick from the striker almost releases the winger down the flank",
    "The goalkeeper makes a diving save to deny the midfielder's powerful shot from distance",
    "The striker tries to turn his marker with a quick change of pace, but the defender stays with him",
    "A driven cross into the box is met by the striker, but his header lacks power and is easily saved by the goalkeeper",
    "The midfielder's shot from outside the box takes a deflection off a defender and loops over the bar",
    "The winger's cross is nodded away by the defender at the near post",
    "A clever give-and-go between teammates almost unlocks the defense, but the final pass is intercepted",
    "The goalkeeper comes off his line to punch away a dangerous cross from the winger",
    "The midfielder tries to slide a pass through to the striker, but it's intercepted by the defender",
    "A low shot from outside the box is saved comfortably by the goalkeeper",
    "The winger tries to beat his marker with a step-over but is dispossessed",
    "A lofted ball over the top almost finds the run of the striker, but the goalkeeper is quick off his line to collect",
    "The midfielder's shot from distance is blocked by a sliding defender",
    "The striker tries to flick the ball on for a teammate, but the pass is intercepted by the defender",
    "A driven shot from the midfielder is blocked by a brave defender throwing his body in the way",
    "The winger tries to beat his marker with a burst of pace down the flank, but is ushered out of play",
    "The striker attempts an overhead kick from a difficult angle, but it flies wide of the target",
    "A floated cross into the box is met by the striker, but his header lacks direction and goes wide",
    "The midfielder tries to thread a pass through to the striker, but it's intercepted by the goalkeeper",
    "The winger's cross is met by the head of the striker, but he can't generate enough power to trouble the goalkeeper",
    "A quick turn from the midfielder creates space for a shot, but it's blocked by a defender",
    "The goalkeeper makes a fantastic save to keep out the striker's close-range effort",
    "The striker tries to hold off his marker and get a shot away, but the defender blocks it with a well-timed tackle",
    "A lofted cross into the box is met by the striker, but his header is straight at the goalkeeper",
    "The midfielder tries to play a quick one-two with the winger, but the return pass is intercepted by the defender",
    "The winger cuts inside onto his weaker foot and tries a shot from distance, but it's comfortably saved by the goalkeeper",
    "A low cross into the box is cleared away by the defender before it can reach the waiting striker",
    "The striker attempts to flick the ball on for a teammate, but it's intercepted by the defender",
    "The midfielder tries to play a through ball into the path of the striker, but it's overhit and goes out for a goal kick",
    "A clever dummy from the striker almost releases his teammate in behind the defense, but the pass is cut out at the last moment",
    "The winger tries to beat his marker but is dispossessed and the attack breaks down"
]'''
# ai generated strings
ARR_STR_OCCASIONS = [
    "Striker's shot blocked by defender",
    "Winger's cross saved by goalkeeper",
    "Midfielder's ball cleared by defense",
    "Quick one-two, almost unlocks defense",
    "Striker's header wide",
    "Midfielder's fierce shot misses target",
    "Winger's cross cut out by goalkeeper",
    "Clever through ball, striker can't reach",
    "Goalkeeper rushes out to smother ball",
    "Powerful shot rattles crossbar",
    "Midfielder's chip intercepted",
    "Winger beats marker, cross too close to goalkeeper",
    "Striker's shot deflected wide, corner kick",
    "Goalkeeper misjudges ball, sails over bar",
    "Lofted pass almost finds onrushing striker",
    "Midfielder's pass intercepted",
    "Winger's low cross, no touch",
    "Striker's audacious bicycle kick off target",
    "Whipped free kick cleared by defense",
    "Midfielder's long-range shot saved",
    "Winger's shot blocked by defender",
    "Clever flick almost releases striker",
    "Goalkeeper claims high ball",
    "Midfielder's long-range effort sails over bar",
    "Winger's curling shot wide",
    "Shot charged down by defender, throw-in",
    "Midfielder's pass intercepted",
    "Winger's cross too high, goal kick",
    "Tackle denies striker, goalkeeper collects",
    "Powerful shot blocked by defender",
    "Midfielder's through ball cut out",
    "Striker's shot saved by goalkeeper",
    "Curling effort saved by goalkeeper",
    "Winger's cross too close, easily collected",
    "Low shot saved by goalkeeper's leg",
    "Midfielder's shot blocked by sliding defender",
    "Winger dispossessed near touchline",
    "Lofted pass headed away by defender",
    "Striker's acrobatic volley off target",
    "Goalkeeper punches away dangerous cross",
    "Midfielder's shot blocked by well-positioned defender",
    "Striker's flick-on header wide",
    "Driven cross intercepted by goalkeeper",
    "Midfielder's shot deflected, corner kick",
    "Winger's cross headed away at near post",
    "Clever dummy almost releases teammate",
    "Midfielder's one-two intercepted",
    "Long ball almost releases striker, goalkeeper quick off line",
    "Winger's cross overhit, out for goal kick",
    "Striker dispossessed, clever dummy creates space",
    "Goalkeeper makes diving save, denies powerful shot",
    "Striker tries quick turn, defender stays",
    "Driven cross met by striker, header lacks power",
    "Shot deflected off defender, loops over bar",
    "Winger's cross nodded away at near post",
    "Give-and-go almost unlocks defense, pass intercepted",
    "Goalkeeper punches away dangerous cross",
    "Midfielder's pass intercepted",
    "Low shot saved comfortably by goalkeeper",
    "Winger dispossessed, attack breaks down"
]

ARR_STR_YCARDS = ["Yellow card for a bad foul", "Yellow card for tactical foul"]
ARR_STR_RCARDS = ["Red card for a really bad foul", "Red card for denying clear opportunity"]
ARR_STR_INJ = ["Injured player, shoulder collision", "Injured player, muscular strain", "Injured player, cramps"]

# --------------------- def functions ------

# calculation of a team ovr based on market val, home stadium/away, squad size and avg age, ...
def calc_team_ovr(team: Team.Team, ishome: bool) -> int:
    luck = random.gauss(0, 3.3)
    #print(f"luck={luck}")
    cur = calc_team_ovr_for_betting(team, ishome)
    return cur + round(luck*cur/105)

def calc_team_ovr_for_betting(team: Team.Team, ishome: bool) -> int:
    x = team.market_val
    ovr = round(float(FUNCT_K * math.log(x, 10)) + FUNCT_Q)

    if ishome:
        min_perc_attendance = ovr / 4000
        #rand_attendance = random.randint(round(0.02*team.stadium_seats), round(full_home_seats*team.stadium_seats))
        #stadium_add = int(rand_attendance - team.stadium_seats/4)
        #stadium_add = round(stadium_add*MAX_BONUS_STADIUM*2*2/team.stadium_seats)
        #stadium_add = 
        rand_attendance = random.randint(round(min_perc_attendance*team.stadium_seats), round(team.stadium_seats*0.75))
        stadium_add = round(rand_attendance*MAX_BONUS_STADIUM/team.stadium_seats)
    else:
        stadium_add = random.randint(-5, 0)

    x_2 = team.squad
    size_add = round( FUNCT_A * math.log(x_2+30, 10) - (FUNCT_A+65))

    x_3 = team.avg_age
    if (x_3 < 30):
        a = 0.0589
        b = -3.918
        c = 65.356
        end = math.floor(a*(x_3**2) + b*x_3 + c)
        age_add = random.randint(-end, end)
    elif (x_3 < 40):
        age_add = 0
    else:
        age_add = -3

    return ovr + stadium_add + size_add + age_add + (team.bonus)

def circle_method(teams_num: int) -> list:

    teams = teams_num
    # If there is an odd amount of teams,
    # there will be 1 more 'non-existent' team, standing for no match-up
    ghost = False
    if(teams%2==1):
        teams+=1
        ghost=True

    tot_rounds = teams - 1
    # Matches per round
    mpr = int(teams / 2)

    # Table of teams [1, 2, ..., n]
    t = []
    for i in range(teams+1):
        t.append(i+1)

    # Stores the rounds with the corresponding matches inside
    # e.g.: [[(1, 4), (2, 3)], [(1, 3), (4, 2)], [(1, 2), (3, 4)]]
    rounds = []
    for round in range(tot_rounds):
        rounds.append([])
        for match in range(mpr):
            rounds[round].append([])
            home = (round + match) % (teams-1)
            away = (teams - 1 - match + round) % (teams - 1)
            if match == 0:
                away = teams - 1
            
            rounds[round][match] = (home, away)

    interleaved = []
    evn = 0
    odd = int(teams/2)
    for i in range(len(rounds)):
        interleaved.append([])
        if (i%2 == 0):
            interleaved[i] = rounds[evn]
            evn+=1
        else:
            interleaved[i] = rounds[odd]
            odd+=1

    n_rounds = interleaved

    for roundi in range(len(n_rounds)):
        if roundi%2 == 1:
            n_rounds[roundi][0] = tuple(reversed(n_rounds[roundi][0]))

    rounds_second_half = copy.deepcopy(n_rounds)
    
    for roundi in range(len(rounds_second_half)):
        for matchi in range(len(rounds_second_half[roundi])):
            rounds_second_half[roundi][matchi] = tuple(reversed(rounds_second_half[roundi][matchi]))

    return_total = n_rounds + (rounds_second_half)

    return return_total


def generate_calendar(teams):
    teams_shuffled = copy.deepcopy(teams)
    random.shuffle(teams_shuffled)
    return teams_shuffled, circle_method(len(teams))

def print_fixtures(teams, calendar):
    ret_str = ""
    r = 1
    for round in calendar:
        ret_str = ret_str + "\t- - ROUND " + str(r) + " - -\n"
        r+=1
        for match in round:
            ret_str = ret_str + str(teams[match[0]].get_name()) + " vs " + str(teams[match[1]].get_name()) + "\n"

    return ret_str



# calculation of subdivisions of a team's own slice of bar (depends on ovr of both teams in match)
def calc_subranges_events(cur_ovr: int, opp_ovr: int, start_range: int):

    ranges = RANGE_RAND_EVENT / 3

    #occ_subrange_perc = ((cur_ovr-opp_ovr)/20) + 50
    x = cur_ovr-opp_ovr
    occ_subrange_perc = ((math.atan(0.005*x))*30)+40
    if occ_subrange_perc >= 80:
        occ_subrange_perc = 80
    if occ_subrange_perc <= 20:
        occ_subrange_perc = 20

    card_subrange_perc = 12 - ((occ_subrange_perc - 50)/2)
    if card_subrange_perc < 6:
        card_subrange_perc = 6
    if card_subrange_perc > 11:
        card_subrange_perc = 11

    injury_subrange_perc = 2

    bench_subrange_perc = 13

    # just for DEBUG purposes to see if everything went correct
    #nothing_subrange_perc = 100 - (occ_subrange_perc + card_subrange_perc + injury_subrange_perc + bench_subrange_perc)

    #print(occ_subrange_perc, card_subrange_perc, injury_subrange_perc, bench_subrange_perc, nothing_subrange_perc)
    
    occ_max_num = start_range + round(occ_subrange_perc * ranges / 100)

    card_max_num = occ_max_num + round(card_subrange_perc * ranges / 100)

    injury_max_num = card_max_num + round(injury_subrange_perc * ranges / 100)

    bench_max_num = injury_max_num + round(bench_subrange_perc * ranges / 100)

    return occ_max_num, card_max_num, injury_max_num, bench_max_num

# calc of random chance to score a goal if occasion occurred, based on both ovrs and a random coeff
def calc_perc_goal(min: int, o1: int, o2: int, rand_coeff: int):
    k = 2 + float(float(min)/360) # exp of the formula
    return ((0.1*(o1**k)) / ((o2**k)+rand_coeff))

def calc_ovr_change_goals(goals_1: int, goals_2: int) -> tuple[int, int]:

    # here when goals_1 increases (called inverted when team2 actually scores)

    if goals_1-goals_2 == 7:
        return random.randint(-9, -2), +1

    if goals_1-goals_2 == 5:
        return +1, -2
    
    if goals_1-goals_2 == 4:
        return +1, -2
    
    if goals_1-goals_2 == 3:
        return +1, -2
    
    if goals_1 == 1 and goals_2 == 0:
        # scored the opener: game changer (?)
        return random.randint(-7, +7), random.randint(-7, +7)
    
    if goals_1 == goals_2:
        # team that scored just equalized!
        return random.randint(-5, +1), random.randint(-6, +3)
    
    if goals_1-goals_2 == -1:
        # reduced disadvantage to 1 goal
        return +2, -1

    return 0, 0

def calc_ovr_change_sub(goals_1: int, goals_2: int, how_many: int) -> int:
    if goals_1-goals_2 < 0:
        return random.randint(-1-2*how_many, 5+2*(how_many))
    
    if goals_1 == goals_2:
        return random.randint(-2*how_many, 2*how_many)
    
    if goals_1-goals_2 == 1:
        return random.randint(-1*how_many, 1*how_many)
    
    if goals_1-goals_2 > 4:
        return random.randint((-8)+(-3*how_many), 1)
    
    if goals_1-goals_2 > 1:
        return random.randint(-2*how_many, 2*how_many)
    
    return 0

def minute_event_aux(minute:int, is_first_time:bool, ovr1:int, ovr2:int, goal_coeff:int, subs_1:int, subs_2:int, slots_1:int, slots_2:int, goals_1:int, goals_2:int, who: int, rand_num: int):

    ranges = int(RANGE_RAND_EVENT / 3)
    goal_1 = 0
    goal_2 = 0

    num_subs_1 = subs_1
    num_subs_2 = subs_2
    num_slots_1 = slots_1
    num_slots_2 = slots_2
    num_less_1 = 0
    num_less_2 = 0

    ovr_change_1 = 0
    ovr_change_2 = 0

    str_event = ""
    
    printable = True

    if who == 2:
        ovr1, ovr2 = ovr2, ovr1

    # left side of the bar, event for team 1 possibly happening
    which_team = who
    
    start = (ranges*((who-1)*2)) + 1
    occ_max_num, card_max_num, injury_max_num, bench_max_num = calc_subranges_events(ovr1, ovr2, start)

    #print(occ_max_num, card_max_num, injury_max_num, bench_max_num)

    if(start <= rand_num <= occ_max_num):
        # occasion

        #range_goal = (9*ovr2)+(1*ovr1)+goal_coeff
        #poss_goal = random.randint(1, range_goal)
        #if (poss_goal <= ovr1):
        perc_goal = calc_perc_goal(minute, ovr1, ovr2, goal_coeff)
        perc_arr = [perc_goal, 1-perc_goal]
        poss_goal = random.choices([True, False], perc_arr)
        if poss_goal[0]:
            #goal
            str_event = str_event + " Goal! " + " [" + str(goals_1+1) + "]" + " - " + str(goals_2)
            goal_1 = 1

            ovr_change_1, ovr_change_2 = calc_ovr_change_goals(goals_1+1, goals_2)

        else:
            #no goal
            str_event = str_event + " " + random.choice(ARR_STR_OCCASIONS)


    elif(occ_max_num < rand_num <= card_max_num):
        # card
        if random.random() < (0.09 + minute/2010):
            # red card
            num_less_1 = 1
            str_event = str_event + " " + random.choice(ARR_STR_RCARDS)
        else:
            str_event = str_event + " " + random.choice(ARR_STR_YCARDS)
            ovr_change_1 += -3

    elif(card_max_num < rand_num <= injury_max_num):
        # injury
        str_event = str_event + " " + random.choice(ARR_STR_INJ)

        if(subs_1 < 5 and slots_1 < 3):
            num_subs_1 = subs_1+1
            num_slots_1 = slots_1+1
            str_event = str_event + ": substit."
            ovr_change_1 = calc_ovr_change_sub(goals_1, goals_2, 1)
        else:
            num_less_1 = 1
            str_event = str_event + ": out!"

    elif(injury_max_num < rand_num <= bench_max_num):
        # substitution

        if(subs_1 >= 5 or slots_1 >= 3 or is_first_time):
            printable = False
        else:
            possible_s = list(range(1, 1 + MAX_SUBS - subs_1))
            num_subs_1 = random.choices(possible_s, PROB_SUBS[0:MAX_SUBS - subs_1])[0]

            num_subs_1 = subs_1+num_subs_1
            if(minute != 46):
                num_slots_1 = slots_1+1

            ovr_change_1 = calc_ovr_change_sub(goals_1, goals_2, (num_subs_1-subs_1))
        
            str_event = str_event + " " + str(num_subs_1-subs_1) + " substitution/s made, " +  str(num_subs_1) + " total"

    else:
        #nothing
        printable = False

    #print(str_minute + "evento1")
    return num_subs_1, num_slots_1, num_less_1, goal_1, ovr_change_1, ovr_change_2, str_event, which_team
        

# calc if something happens on a single min of the game and if so changes data accordingly
def minute_event_(minute:int, is_first_time:bool, ovr1:int, ovr2:int, goal_coeff:int, subs_1:int, subs_2:int, slots_1:int, slots_2:int, goals_1:int, goals_2:int):
    rand_num = random.randint(1, RANGE_RAND_EVENT)

    goal_1 = 0
    goal_2 = 0

    num_subs_1 = subs_1
    num_subs_2 = subs_2
    num_slots_1 = slots_1
    num_slots_2 = slots_2
    num_less_1 = 0
    num_less_2 = 0

    ovr_change_1 = 0
    ovr_change_2 = 0

    str_event = ""
    
    printable = True

    #print(rand_num)

    ranges = int(RANGE_RAND_EVENT / 3)

    # DEBUG
    o1=c1=i1=s1=0
    o2=c2=i2=s2=0
    # END DEBUG

    # needed to determine which team has the event
    which_team = 0

    if (minute <= 45):
        str_min = ("[" + str(minute) + "']")
    elif(is_first_time):
        str_min = ("[45+" + str(minute-45) + "']")
    elif(minute <= 90):
        str_min = ("[" + str(minute) + "']")
    else:
        str_min = ("[90+" + str(minute-90) + "']")

    str_event += (str_min)

    if(rand_num <= ranges):
        num_subs_1, num_slots_1, num_less_1, goal_1, ovr_change_1, ovr_change_2, str_event, which_team = minute_event_aux(minute, is_first_time, ovr1, ovr2, goal_coeff, subs_1, subs_2, slots_1, slots_2, goals_1, goals_2, 1, rand_num)
        
    elif((2*ranges) < rand_num <= RANGE_RAND_EVENT):
        num_subs_2, num_slots_2, num_less_2, goal_2, ovr_change_1, ovr_change_2, str_event, which_team = minute_event_aux(minute, is_first_time, ovr1, ovr2, goal_coeff, subs_1, subs_2, slots_1, slots_2, goals_1, goals_2, 2, rand_num)

    else:
        # center of the bar, nothing happens
        printable = False

    #print(o1,o2,c1,c2,i1,i2,s1,s2)
    if not printable:
        #print(str_event)
        str_event = ""
        which_team = 0

    
    if num_less_1 == 1:
        ovr_change_1 -= 15
    if num_less_2 == 1:
        ovr_change_2 -= 15

    return num_subs_1, num_subs_2, num_slots_1, num_slots_2, num_less_1, num_less_2, goal_1, goal_2, ovr_change_1, ovr_change_2, str_event, which_team


def minute_event(minute:int, is_first_time:bool, ovr1:int, ovr2:int, goal_coeff:int, subs_1:int, subs_2:int, slots_1:int, slots_2:int, goals_1:int, goals_2:int):
    rand_num = random.randint(1, RANGE_RAND_EVENT)

    goal_1 = 0
    goal_2 = 0

    num_subs_1 = subs_1
    num_subs_2 = subs_2
    num_slots_1 = slots_1
    num_slots_2 = slots_2
    num_less_1 = 0
    num_less_2 = 0

    ovr_change_1 = 0
    ovr_change_2 = 0

    str_event = ""
    
    printable = True

    #print(rand_num)

    ranges = int(RANGE_RAND_EVENT / 3)

    # DEBUG
    o1=c1=i1=s1=0
    o2=c2=i2=s2=0
    # END DEBUG

    # needed to determine which team has the event
    which_team = 0

    if (minute <= 45):
        str_min = ("[" + str(minute) + "']")
    elif(is_first_time):
        str_min = ("[45+" + str(minute-45) + "']")
    elif(minute <= 90):
        str_min = ("[" + str(minute) + "']")
    else:
        str_min = ("[90+" + str(minute-90) + "']")

    str_event += (str_min)

    if(rand_num <= ranges):
        # left side of the bar, event for team 1 possibly happening
        which_team = 1
        
        start = 1
        occ_max_num, card_max_num, injury_max_num, bench_max_num = calc_subranges_events(ovr1, ovr2, start)

        #print(occ_max_num, card_max_num, injury_max_num, bench_max_num)

        if(start <= rand_num <= occ_max_num):
            # occasion
            o1+=1

            #range_goal = (9*ovr2)+(1*ovr1)+goal_coeff
            #poss_goal = random.randint(1, range_goal)
            #if (poss_goal <= ovr1):
            perc_goal = calc_perc_goal(minute, ovr1, ovr2, goal_coeff)
            perc_arr = [perc_goal, 1-perc_goal]
            poss_goal = random.choices([True, False], perc_arr)
            if poss_goal[0]:
                #goal
                str_event = str_event + " Goal! " + " [" + str(goals_1+1) + "]" + " - " + str(goals_2)
                goal_1 = 1

                ovr_change_1, ovr_change_2 = calc_ovr_change_goals(goals_1+1, goals_2)

            else:
                #no goal
                str_event = str_event + " " + random.choice(ARR_STR_OCCASIONS)


        elif(occ_max_num < rand_num <= card_max_num):
            # card
            c1+=1
            if random.random() < (0.09 + minute/2010):
                # red card
                num_less_1 = 1
                str_event = str_event + " " + random.choice(ARR_STR_RCARDS)
            else:
                str_event = str_event + " " + random.choice(ARR_STR_YCARDS)
                ovr_change_1 += -3

        elif(card_max_num < rand_num <= injury_max_num):
            # injury
            i1+=1
            str_event = str_event + " " + random.choice(ARR_STR_INJ)

            if(subs_1 < 5 and slots_1 < 3):
                num_subs_1 = subs_1+1
                num_slots_1 = slots_1+1
                str_event = str_event + ": substit."
                ovr_change_1 += calc_ovr_change_sub(goals_1, goals_2, 1)
            else:
                num_less_1 = 1
                str_event = str_event + ": out!"

        elif(injury_max_num < rand_num <= bench_max_num):
            # substitution

            if(subs_1 >= 5 or slots_1 >= 3 or is_first_time):
                printable = False
            else:
                s1+=1
                possible_s = list(range(1, 1 + MAX_SUBS - subs_1))
                num_subs_1 = random.choices(possible_s, PROB_SUBS[0:MAX_SUBS - subs_1])[0]

                num_subs_1 = subs_1+num_subs_1
                if(minute != 46):
                    num_slots_1 = slots_1+1

                ovr_change_1 += calc_ovr_change_sub(goals_1, goals_2, (num_subs_1-subs_1))
            
                str_event = str_event + " " + str(num_subs_1-subs_1) + " substitution/s made, " +  str(num_subs_1) + " total"

        else:
            #nothing
            printable = False

        #print(str_minute + "evento1")
        
    elif((2*ranges) < rand_num <= RANGE_RAND_EVENT):
        # right side of the bar, event for team 2 possibly happening
        which_team = 2

        start = (2*ranges)+1
        occ_max_num, card_max_num, injury_max_num, bench_max_num = calc_subranges_events(ovr2, ovr1, start)

        #print(occ_max_num, card_max_num, injury_max_num, bench_max_num)

        if(start <= rand_num <= occ_max_num):
            # occasion
            o2+=1

            #range_goal = (9*ovr1)+(1*ovr2)+goal_coeff
            #range_goal = calc_range_goal(ovr1, ovr2, goal_coeff)
            #poss_goal = random.randint(1, range_goal)
            #if (poss_goal <= ovr2):
            perc_goal = calc_perc_goal(minute, ovr2, ovr1, goal_coeff)
            perc_arr = [perc_goal, 1-perc_goal]
            poss_goal = random.choices([True, False], perc_arr)
            if poss_goal[0]:
                #goal
                str_event = "Goal! " + " " + str(goals_1) + " - [" + str(goals_2+1) + "] " + str_event
                goal_2 = 1

                ovr_change_2, ovr_change_1 = calc_ovr_change_goals(goals_1=goals_2+1, goals_2=goals_1)

            else:
                #no goal
                str_event = random.choice(ARR_STR_OCCASIONS) + " " + str_event

        elif(occ_max_num < rand_num <= card_max_num):
            # card
            c2+=1
            if random.random() < (0.09 + minute/2010):
                # red card
                num_less_2 = 1
                str_event = random.choice(ARR_STR_RCARDS) + " " + str_event
            else:
                str_event = random.choice(ARR_STR_YCARDS) + " " + str_event
                ovr_change_2 += -3

        elif(card_max_num < rand_num <= injury_max_num):
            # injury
            i2+=1
            tmp = random.choice(ARR_STR_INJ)

            if(subs_2 < 5 and slots_2 < 3):
                num_subs_2 = subs_2+1
                num_slots_2 = slots_2+1
                str_event = tmp + ": substit. " + str_event
                ovr_change_2 += calc_ovr_change_sub(goals_2, goals_1, 1)
            else:
                num_less_2 = 1
                str_event = tmp + ": out! " + str_event

        elif(injury_max_num < rand_num <= bench_max_num):
            # substitution

            if(subs_2 >= 5 or slots_2 >= 3 or is_first_time):
                printable = False
            else:
                s2+=1
                possible_s = list(range(1, 1 + MAX_SUBS - subs_2))
                num_subs_2 = random.choices(possible_s, PROB_SUBS[0:MAX_SUBS - subs_2])[0]

                num_subs_2 = subs_2+num_subs_2
                if(minute != 46):
                    num_slots_2 = slots_2+1

                ovr_change_2 += calc_ovr_change_sub(goals_2, goals_1, (num_subs_2-subs_2))

                str_event = str(num_subs_2-subs_2) + " substitution/s made, " +  str(num_subs_2) + " total " + str_event

        else:
            #nothing
            printable = False

    else:
        # center of the bar, nothing happens
        printable = False

    #print(o1,o2,c1,c2,i1,i2,s1,s2)
    if not printable:
        #print(str_event)
        str_event = ""
        which_team = 0

    
    if num_less_1 == 1:
        ovr_change_1 -= 15
    if num_less_2 == 1:
        ovr_change_2 -= 15

    return num_subs_1, num_subs_2, num_slots_1, num_slots_2, num_less_1, num_less_2, goal_1, goal_2, ovr_change_1, ovr_change_2, str_event, which_team


def get_first_half_mins() -> list:
    extras1_seq = [0,1,2,3,4,5,6,7]
    extras1_probs = [21,26,23,14,8,5,2,1]
    extratime1 = random.choices(extras1_seq, extras1_probs)[0]
    f_time = list(range(1, 45))
    for m in range(0, extratime1+1):
        f_time.append(45+m)
    return f_time

def get_second_half_mins() -> list:
    extras2_seq = [0,1,2,3,4,5,6,7,8,9,10]
    extras2_probs = [6,8,9,15,18,17,10,7,5,3,2]
    extratime2 = random.choices(extras2_seq, extras2_probs)[0]
    s_time = list(range(46, 90))
    for m in range(0, extratime2+1):
        s_time.append(90+m)
    return s_time


def get_goal_coeff(ovr1: int, ovr2: int) -> int:
    #rand_div = random.randint(GOAL_COEFF_DIV_MIN, GOAL_COEFF_DIV_MAX)/10
    #ret_coeff = (ovr1*ovr2/rand_div) + GOAL_COEFF_MUL*ovr1 + GOAL_COEFF_MUL*ovr2
    min_r, max_r = 0.91, 0.97
    rand_exp = (random.random() * (max_r-min_r)) + min_r
    ret_coeff = (ovr1*ovr2)**rand_exp
    return int(ret_coeff)
    #return random.randint(GOAL_COEFF_MIN, GOAL_COEFF_MAX)

def string_ranking_table(cal_teams: list) -> str:
    rank_teams = copy.deepcopy(cal_teams)
    rank_teams.sort(key=lambda x: x.points, reverse=True)
    ret = ""
    for team in rank_teams:
        ret = ret + team.get_name() + "\t" + str(team.points) + "| " + str(team.gf) + "-" + str(team.ga) + "=" + str(team.get_gd()) + "\n"

    return ret