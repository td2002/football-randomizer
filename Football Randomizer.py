import classes.Team as Team, classes.CalendarizedTeam as CalendarizedTeam
import libs.football_randomizer_api as frapi
import libs.run_transfermarkt_api as rtapi
import random
import tkinter as tk
from tkinter import ttk, filedialog
import io
from PIL import ImageTk as itk, Image

# dims for img canvas
CANVAS_DIMS = 100

# app version
# 0 . (functionalities implemented) . (ovr lvl of polish of code/gui) . (quality of match simulation, randomness, etc)
VER = '0.5d.5a.4b'

#TODO change output when season is starting with odd amount of teams! no real feedback


class RootWindow:
    def set_mouse_y_scrolling(self, canvas):

        ############### Scroll Using Mouse Wheel ###############
        #rkmatches.bind_all('<Configure>', lambda event: rkmatches.itemconfigure('expand', width=event.width))
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

        def scroll(event, widget):
            widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def final_scroll(event, widget, func):
            widget.bind_all("<MouseWheel>", func)

        def stop_scroll(event, widget):
            widget.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", lambda event: final_scroll(event, canvas, lambda event: scroll(event, canvas)))
        canvas.bind("<Leave>", lambda event: stop_scroll(event, canvas))
        ################### code for scrolling bottom right box #####################


        return
    
    def __init__(self, master):

        self.intro_text = "        Start a single match or a full season using the menu above"
        # mode: 0 for init, 1 for single match, 2 for season
        self.mode = 0

        # old badges: 0 for current, 1 for oldest, 2 for random
        self.old_badges = 0

        # "pots" for randomized teams (a list of which files to use), default just the strongest one
        self.selected_pot = 0
        self.select_nat_teams = False

        # small advantage for teams playing home (1) or not (0)
        self.home_adv = 1
        

        self.master = master
        self.frame = tk.Frame(self.master, width=1100, height=700)
        self.frame.pack()
        
        main_menu = tk.Menu(self.master)
        season_menu = tk.Menu(main_menu, tearoff=0)
        options_menu = tk.Menu(main_menu, tearoff=0)
        friendly_menu = tk.Menu(main_menu, tearoff=0)

        friendly_menu.add_command(label = "Select two teams", command=self.search_clubs)
        friendly_menu.add_command(label = "Random Match", command=self.random_friendly)

        season_menu.add_command(label = "Custom Season", command=self.season_handler)
        season_menu.add_separator()
        season_menu.add_command(label = "Real Season", command=self.real_season_handler)
        season_menu.add_separator()
        season_menu.add_command(label = "Random Season", command=self.random_season_handler)
        season_menu.add_separator()
        season_menu.add_command(label = "Save Current Season", command=self.save_current_season)
        season_menu.add_command(label = "Load Season from File", command=self.load_season_file)

        options_menu.add_command(label = "Preferences", command=self.prefs_page)
        options_menu.add_command(label='Clear All', command=self.clear_all_teams)
        options_menu.add_separator()
        options_menu.add_command(label = "About", command=self.about_page)

        main_menu.add_cascade(label = "Friendly Match", menu=friendly_menu)
        main_menu.add_cascade(label = "Season", menu=season_menu)
        main_menu.add_cascade(label = "Options", menu=options_menu)

        self.master.config(menu=main_menu)

        #main_menu.add_command(label = "Season Tournament", command=self.season_handler)
        #main_menu.add_command(label = "Season Tournament", command=self.season_handler)
        #main_menu.add_command(label = "Clear All", command=self.clear_all_teams)
        #main_menu.add_command(label = "About", command=self.about_page)

        # first instantiation of 2 teams min 
        self.teams = [Team]
        self.teams.append(None)
        self.teams.append(None)

        # first instantiation of calendarized teams for rankings
        self.rankteams = [CalendarizedTeam] * 2

        self.calendar = []
        self.cur_day = 0
        self.cur_match = 0
        self.next_match = (0, 1)

        #self.teams.append(dbapi.get_team_by_id(conn.cursor(), 2814))
        #self.teams.append(dbapi.get_team_by_id(conn.cursor(), 16))

        # declaration of 2 lists to contain widgets and their corresp coords & opts in the same order inside both lists
        self.widgets = []
        self.widgets_coords = []

        self.widgets.append( tk.Label(self.frame, anchor=tk.CENTER, width=30, font=('Segoe UI', 10, 'bold')) )
        self.widgets_coords.append((135,20, tk.CENTER, "team1name"))
        self.place_widget(len(self.widgets)-1)
        self.widgets.append( tk.Label(self.frame, anchor=tk.CENTER, width=30, font=('Segoe UI', 10, 'bold')) )
        self.widgets_coords.append((485,20, tk.CENTER, "team2name"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(self.frame, anchor=tk.CENTER, width=40, font=('Segoe UI', 8)) )
        self.widgets_coords.append((310,55, tk.CENTER, "matchstadium"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(self.frame, anchor=tk.CENTER, width=20, font=('Segoe UI', 8)) )
        self.widgets_coords.append((135,38, tk.CENTER, "team1country"))
        self.place_widget(len(self.widgets)-1)
        self.widgets.append( tk.Label(self.frame, anchor=tk.CENTER, width=20, font=('Segoe UI', 8)) )
        self.widgets_coords.append((485,38, tk.CENTER, "team2country"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Canvas(self.frame, width=CANVAS_DIMS, height=CANVAS_DIMS, highlightthickness=0) )
        self.widgets_coords.append((135,55, tk.N,"team1img"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Canvas(self.frame, width=CANVAS_DIMS, height=CANVAS_DIMS, highlightthickness=0) )
        self.widgets_coords.append((485,55, tk.N, "team2img"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(self.frame, anchor=tk.CENTER, width=2, font=('Segoe UI', 25, 'bold')) )
        self.widgets_coords.append((235,70, "team1goals"))
        self.place_widget(len(self.widgets)-1)
        self.widgets.append( tk.Label(self.frame, anchor=tk.CENTER, width=2, font=('Segoe UI', 25, 'bold')) )
        self.widgets_coords.append((310,70,tk.N, "goalseparator"))
        self.place_widget(len(self.widgets)-1)
        self.widgets.append( tk.Label(self.frame, anchor=tk.CENTER, width=2, font=('Segoe UI', 25, 'bold')) )
        self.widgets_coords.append((385,70,tk.NE, "team2goals"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Canvas(self.frame, width=250, height=500, highlightthickness=0) )
        self.widgets_coords.append((10, 170, "team1listcanvas"))
        team1canvas = self.widgets[-1]
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Frame(team1canvas, width=250, height=500) )
        self.widgets_coords.append((0, 0, "team1cframe"))
        team1cframe = self.widgets[-1]
        team1canvas.create_window(0,0, window=team1cframe, anchor=tk.CENTER)

        self.widgets.append( tk.Canvas(self.frame, width=250, height=500, highlightthickness=0) )
        self.widgets_coords.append((360, 170, "team2listcanvas"))
        team2canvas = self.widgets[-1]

        self.widgets.append( tk.Frame(team2canvas, width=250, height=500) )
        self.widgets_coords.append((0, 0, "team2cframe"))
        team2cframe = self.widgets[-1]
        team2canvas.create_window(0,0, window=team2cframe, anchor=tk.CENTER)

        self.widgets.append( tk.Label(self.frame, anchor=tk.CENTER, width=60, font=('Arial', 15), text=self.intro_text) )
        self.widgets_coords.append((310, 150, tk.CENTER, "minute"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(team1cframe, anchor=tk.W, wraplength=250, justify=tk.LEFT, font=('Segoe UI', 8)) )
        self.widgets_coords.append((0,0, "team1text"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(team2cframe, anchor=tk.W, wraplength=250, justify=tk.RIGHT, font=('Segoe UI', 8)) )
        self.widgets_coords.append((250,0,tk.NE, "team2text"))
        self.place_widget(len(self.widgets)-1)

        self.set_mouse_y_scrolling(team1canvas)
        self.set_mouse_y_scrolling(team2canvas)

        self.widgets.append( tk.Button(self.frame, text = "START\nMATCH", width=7, height=3, anchor=tk.CENTER, command=self.start_match, fg='darkgreen', font=('Arial', 13, 'bold'), borderwidth=4) )
        self.widgets_coords.append((310,240, tk.CENTER, "btnstart"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( ttk.Scale(self.frame, from_=10, to=1000, orient='vertical', length=200, value=500) )
        self.widgets_coords.append((310,550, tk.CENTER, "speedslider"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(self.frame, text="FAST", anchor=tk.S, width=5, font=('Arial', 7)) )
        self.widgets_coords.append((310,440, tk.CENTER, "fastlabel"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(self.frame, text="SLOW", anchor=tk.S, width=5, font=('Arial', 7)) )
        self.widgets_coords.append((310,660, tk.CENTER, "slowlabel"))
        self.place_widget(len(self.widgets)-1)

        # below: widgets for rankings / already played matches

        self.widgets.append( tk.Button(self.frame, text = "NEXT\nMATCH", width=7, height=3, anchor=tk.CENTER, command=self.start_next_match, fg='darkgreen', font=('Arial', 13, 'bold'), borderwidth=4, state='disabled') )
        self.widgets_coords.append((310,350,tk.CENTER, "btnnext"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Canvas(self.frame, width=350, height=400, highlightthickness=2, highlightbackground='Black') )
        self.widgets_coords.append((700, 20, "rktable"))
        rktable = self.widgets[len(self.widgets)-1]
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(rktable, text="#", anchor=tk.W, justify=tk.CENTER, wraplength=50, font=('Segoe UI', 8)) )
        self.widgets_coords.append((8,10,tk.NW, "tablerank"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(rktable, text="TEAM", anchor=tk.W, justify=tk.LEFT, width=26, font=('Segoe UI', 8)) )
        self.widgets_coords.append((26,10,tk.NW, "tableteams"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(rktable, text="PLAYED", anchor=tk.CENTER, wraplength=100, font=('Segoe UI', 8)) )
        self.widgets_coords.append((245,10,tk.NE, "tableplayed"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(rktable, text="GOALS", anchor=tk.CENTER, wraplength=100, font=('Segoe UI', 8)) )
        self.widgets_coords.append((300,10,tk.NE, "tablegoals"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Label(rktable, text="PTS", anchor=tk.CENTER, wraplength=100, font=('Segoe UI', 8)) )
        self.widgets_coords.append((340,10,tk.NE, "tablepoints"))
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Canvas(self.frame, width=350, height=220, highlightthickness=2, highlightbackground='Black') )
        self.widgets_coords.append((700, 450, "rkmatches"))
        rkmatches = self.widgets[len(self.widgets)-1]
        self.place_widget(len(self.widgets)-1)

        self.widgets.append( tk.Frame(rkmatches, width=350, height=220) )
        self.widgets_coords.append((0, 0, "matchesframe"))
        matches_win = self.widgets[len(self.widgets)-1]
        rkmatches.create_window(0,0, window=matches_win, anchor=tk.CENTER)

        self.widgets.append( tk.Label(matches_win, anchor=tk.N, justify=tk.CENTER, wraplength=350, font=('Segoe UI', 9)) )
        self.widgets_coords.append((175,0, tk.N, "matchestext"))
        self.place_widget(len(self.widgets)-1)

        self.set_mouse_y_scrolling(rkmatches)

        # disabling button for match start and next
        self.widgets[self.get_widget_index("btnstart")].configure(state="disabled")
        self.widgets[self.get_widget_index("btnnext")].configure(state="disabled")


    def place_widget(self, index: int):
        args = len(self.widgets_coords[index])
        anc = "nw"
        x = self.widgets_coords[index][0]
        y = self.widgets_coords[index][1]
        if args >= 4:
            anc = self.widgets_coords[index][2]
        self.widgets[index].place(x=x, y=y, anchor=anc)

    def get_widget_index(self, name: str) -> int:
        index = 0
        for w in self.widgets_coords:
            if w[len(w)-1] == name:
                break
            index+=1
        return index
    
    def save_current_season(self):
        # format: num teams / actual rankteam data (all rankteams) / current (or next, depends on next match) day / next match to be played
        dir = filedialog.asksaveasfilename()
        with open(dir, 'w') as f:
            f.write(str(len(self.rankteams)) + "\n")
            for t in self.rankteams:
                f.write(t.format_data_for_savefile() + "\n")
            f.write(str(self.cur_day) + "\n")
            f.write(str(self.cur_match))
        return
    
    def load_season_file(self):
        dir = filedialog.askopenfilename()
        self.clear_all_teams()
        self.rankteams.clear()
        self.teams.clear()
        self.widgets[self.get_widget_index("minute")].config(text='Season loading, if not working try again...')
        self.mode = 2
        with open(dir, 'r') as f:
            num_teams = int(f.readline())
            for i in range(num_teams):
                data = f.readline().split()
                p = 3*int(data[3]) + int(data[4])
                self.rankteams.append(CalendarizedTeam.CalendarizedTeam(rtapi.get_team_from_id(int(data[0])), int(data[1]), int(data[2]), int(data[3]), int(data[4]), int(data[5]), p, int(data[6]), int(data[7])))
            self.calendar = frapi.circle_method(num_teams)
            self.cur_day = int(f.readline())
            self.cur_match = int(f.readline())
        
        self.update_ranking()
        self.next_match = self.calendar[self.cur_day][self.cur_match]
        #self.init_teams_for_match(self.next_match[0], self.next_match[1])
        
        self.start_next_match()

        
        self.widgets[self.get_widget_index("minute")].config(text='Season loaded!')

        return
    
    def start_next_match(self):
        if self.mode == 1:
            self.invert_teams()
        elif self.mode == 2:
            ghost = self.init_teams_for_match(self.next_match[0], self.next_match[1])
            if ghost:
                self.widgets[self.get_widget_index("btnnext")].configure(state='normal')
            else:
                self.widgets[self.get_widget_index("btnnext")].configure(state='disabled')
            

    def start_match(self):
        
        self.rankteams.sort(key=lambda x: x.calendar_index)
        team1 = self.rankteams[self.next_match[0]]
        team2 = self.rankteams[self.next_match[1]]
        

        self.init_teams_for_match(self.next_match[0], self.next_match[1])

        # disabling button for match start
        self.widgets[self.get_widget_index("btnstart")].configure(state="disabled")
        self.widgets[self.get_widget_index("btnnext")].configure(state="disabled")

        # match simulation
        self.simulate_match_handler(team1, team2)

    def format_table(self) -> tuple[str, str, str, str]:
        if len(self.rankteams) > 0:
            self.rankteams.sort(key=lambda x: (x.points, x.get_gd(), x.gf), reverse=True)
        
        str_rank = "#\n"
        str_teams = "TEAM\n"
        str_played = "PLAYED\n"
        str_goals = "GOALS\n"
        str_points = "PTS\n"
        pos=1
        for t in self.rankteams:
            str_rank = str_rank + str(pos) + "\n"
            str_teams = str_teams + t.get_name() + "\n"
            str_played = str_played + t.get_str_matches() + "\n"
            str_goals = str_goals + t.get_str_goals() + "\n"
            str_points = str_points + str(t.get_points()) + "\n"
            pos+=1
        return str_rank[:-1], str_teams[:-1], str_played[:-1], str_goals[:-1], str_points[:-1]
    
    def update_ranking(self):
        str_rank, str_teams, str_played, str_goals, str_points = self.format_table()
        self.widgets[self.get_widget_index("tablerank")].configure(text=str_rank)
        self.widgets[self.get_widget_index("tableteams")].configure(text=str_teams)
        self.widgets[self.get_widget_index("tableplayed")].configure(text=str_played)
        self.widgets[self.get_widget_index("tablegoals")].configure(text=str_goals)
        self.widgets[self.get_widget_index("tablepoints")].configure(text=str_points)
        return
    
    def set_next_match(self):

        if self.mode == 2:
            self.cur_match += 1
            if self.cur_match >= len(self.calendar[self.cur_day]):
                self.cur_match = 0
                self.cur_day += 1
            if self.cur_day >= len(self.calendar):
                self.widgets[self.get_widget_index("minute")].configure(text="SEASON OVER")
                self.widgets[self.get_widget_index("btnnext")].configure(state="disabled")
            else:
                self.next_match = self.calendar[self.cur_day][self.cur_match]

    def init_teams_for_match(self, ind_1: int, ind_2: int) -> bool:

        if (self.calendar[self.cur_day][self.cur_match][0] == len(self.rankteams) or self.calendar[self.cur_day][self.cur_match][1] == len(self.rankteams)):
            self.set_next_match()

        try:
            self.rankteams.sort(key=lambda x: x.calendar_index)

            team1 = self.rankteams[ind_1].get_team()
            team2 = self.rankteams[ind_2].get_team()

            self.widgets[self.get_widget_index("team1name")].configure(text=team1.get_name())
            self.widgets[self.get_widget_index("team2name")].configure(text=team2.get_name())
            self.place_widget(self.get_widget_index("team1name"))
            self.place_widget(self.get_widget_index("team2name"))
            self.widgets[self.get_widget_index("team1country")].configure(text=team1.get_country())
            self.widgets[self.get_widget_index("team2country")].configure(text=team2.get_country())
            self.place_widget(self.get_widget_index("team1country"))
            self.place_widget(self.get_widget_index("team2country"))

            self.place_widget(self.get_widget_index("team1listcanvas"))
            self.place_widget(self.get_widget_index("team2listcanvas"))
            self.widgets[self.get_widget_index("team1goals")].configure(text=str(0))
            self.widgets[self.get_widget_index("team2goals")].configure(text=str(0))
            self.widgets[self.get_widget_index("goalseparator")].configure(text="-")
            self.place_widget(self.get_widget_index("team1goals"))
            self.place_widget(self.get_widget_index("team2goals"))
            self.place_widget(self.get_widget_index("goalseparator"))
            self.widgets[self.get_widget_index("team1text")].configure(text="")
            self.widgets[self.get_widget_index("team2text")].configure(text="")

            colours1 = team1.get_colours()
            colours2 = team2.get_colours()
            
            self.widgets[self.get_widget_index("team1cframe")].configure(bg=str(colours1[0]))
            self.widgets[self.get_widget_index("team2cframe")].configure(bg=str(colours2[0]))
            self.widgets[self.get_widget_index("team1text")].configure(bg=str(colours1[0]))
            self.widgets[self.get_widget_index("team2text")].configure(bg=str(colours2[0]))
            self.widgets[self.get_widget_index("team1text")].configure(fg=str(colours1[-1]))
            self.widgets[self.get_widget_index("team2text")].configure(fg=str(colours2[-1]))

            if self.home_adv == 1:
                tmp = team1.get_stadium_name()
                print(tmp, rtapi.DEFAULT_STADIUM_NAME)
                if tmp == rtapi.DEFAULT_STADIUM_NAME:
                    tmp = team1.get_name() + " " + tmp
                self.widgets[self.get_widget_index("matchstadium")].configure(text=tmp)
            else:
                self.widgets[self.get_widget_index("matchstadium")].configure(text="Neutral location")

            self.set_team_img(ind_1, True)
            self.set_team_img(ind_2, False)

            self.widgets[self.get_widget_index("minute")].configure(text="PRE MATCH")
            self.place_widget(self.get_widget_index("minute"))
            self.widgets[self.get_widget_index("minute")].lower()

            str_rank, str_teams, str_played, str_goals, str_points = self.format_table()
            self.widgets[self.get_widget_index("tablerank")].configure(text=str_rank)
            self.widgets[self.get_widget_index("tableteams")].configure(text=str_teams)
            self.widgets[self.get_widget_index("tableplayed")].configure(text=str_played)
            self.widgets[self.get_widget_index("tablegoals")].configure(text=str_goals)
            self.widgets[self.get_widget_index("tablepoints")].configure(text=str_points)

            # enabling the start button for the match to actually be played
            self.widgets[self.get_widget_index("btnstart")].configure(state="normal")

            return False
        except:
            print("Ghost...")
            # adding last result to box
            try:
                name = self.rankteams[ind_1].get_name()
            except:
                name = self.rankteams[ind_2].get_name()
            textbox = self.widgets[self.get_widget_index("matchestext")]
            if textbox.cget("text") == "":
                textbox.configure(text= f'{name} resting for this round')
            else:
                textbox.configure(text= (textbox.cget("text") + "\n" + f'{name} resting for this round'))
            if textbox.cget("text").count('\n') > 14:
                self.widgets[self.get_widget_index("matchesframe")].configure(height = self.widgets[self.get_widget_index("matchesframe")].cget("height")+218)
                #self.widgets[self.get_widget_index("matchesframe")].configure(height = self.widgets[self.get_widget_index("matchesframe")].cget("height")+16)
                self.widgets[self.get_widget_index("rkmatches")].config(scrollregion=self.widgets[self.get_widget_index("rkmatches")].bbox(tk.ALL))
            #self.widgets[self.get_widget_index("btnnext")].config(state='normal')

            return True
                


    def min_event(self, team1: CalendarizedTeam.CalendarizedTeam, team2: CalendarizedTeam.CalendarizedTeam, ovr1: int, ovr2: int, g_coeff: int, subs_alr_1: int, subs_alr_2: int, slots_alr_1: int, slots_alr_2: int, goals_1: int, goals_2: int, f_time: list, s_time: list, widget_minute_index: int, widget_team1_index: int, widget_team2_index: int):

        speed = int(self.widgets[self.get_widget_index("speedslider")].get())
        
        is_first_half = True
        f_time_next = []
        s_time_next = []

        if len(f_time) > 0:
            min = f_time[0]
            f_time_next = f_time[1:]
            s_time_next = s_time
        elif len(s_time) > 0:
            min = s_time[0]
            is_first_half = False
            f_time_next = f_time
            s_time_next = s_time[1:]
        else:
            # means the match ended: NEED TO RE ENABLE AND HANDLE EVERYTHING HERE, AFTER THE AFTER METOD !!!
            self.widgets[widget_minute_index].configure(text="MATCH OVER")

            # re-enabling the start and next match button
            if self.mode != 2:
                self.widgets[self.get_widget_index("btnstart")].configure(state="normal")
            self.widgets[self.get_widget_index("btnnext")].configure(state="normal")

            # adding last result to box
            textbox = self.widgets[self.get_widget_index("matchestext")]
            if textbox.cget("text") == "":
                textbox.configure(text= team1.get_name() + " " + str(goals_1) + " - " + str(goals_2) + " " + team2.get_name())
            else:
                textbox.configure(text= (textbox.cget("text") + "\n" + team1.get_name() + " " + str(goals_1) + " - " + str(goals_2) + " " + team2.get_name()))
            if (textbox.cget("text").count('\n')+1) % 14 == 0:
                self.widgets[self.get_widget_index("matchesframe")].configure(height = self.widgets[self.get_widget_index("matchesframe")].cget("height")+218)
                #self.widgets[self.get_widget_index("matchesframe")].configure(height = self.widgets[self.get_widget_index("matchesframe")].cget("height")+16)
                self.widgets[self.get_widget_index("rkmatches")].config(scrollregion=self.widgets[self.get_widget_index("rkmatches")].bbox(tk.ALL))
            #self.widgets[self.get_widget_index("rkmatches")].config(scrollregion=self.widgets[self.get_widget_index("rkmatches")].bbox(tk.ALL))

            # updating ranking in top right box
            self.rankteams.sort(key=lambda x:x.calendar_index)
            self.rankteams[team1.calendar_index].update_post_match(goals_1, goals_2)
            self.rankteams[team2.calendar_index].update_post_match(goals_2, goals_1)
            self.update_ranking()

            self.set_next_match()
            
            return

        # set current min in minute box in gui
        min_str = str(min) + "'"
        if is_first_half and min > 45:
            min_str = str(45) + "+" + str(min-45) + "'"
        elif not is_first_half and min > 90:
            min_str = str(90) + "+" + str(min-90) + "'"
        self.widgets[widget_minute_index].configure(text=min_str)

        tmp_subs_1, tmp_subs_2, tmp_slots_1, tmp_slots_2, tmp_less_1, tmp_less_2, num_goals_1, num_goals_2, ovr_change_1, ovr_change_2, str_event, which_team = frapi.minute_event(min, is_first_half, ovr1, ovr2, g_coeff, subs_alr_1, subs_alr_2, slots_alr_1, slots_alr_2, goals_1, goals_2)
        
        num_subs_1 = tmp_subs_1
        num_subs_2 = tmp_subs_2
        num_slots_1 = tmp_slots_1
        num_slots_2 = tmp_slots_2
        num_goals_1 += goals_1
        num_goals_2 += goals_2

        cur_ovr_1 = ovr_change_1 + ovr1
        cur_ovr_2 = ovr_change_2 + ovr2

        #print(min, cur_ovr_1, cur_ovr_2, num_subs_1, num_slots_1, num_subs_2, num_slots_2)


        if which_team == 1:
            tmp = self.widgets[widget_team1_index].cget("text")
            if tmp.isspace() or tmp == "":
                self.widgets[widget_team1_index].configure(text=(tmp + str_event))
            else:
                self.widgets[widget_team1_index].configure(text=(tmp + "\n" + str_event))
            self.widgets[widget_team2_index].configure(text=(self.widgets[widget_team2_index].cget("text") + "\n"))
            if num_goals_1 != goals_1:
                #time.sleep(1)
                self.widgets[self.get_widget_index("team1goals")].configure(text=str(num_goals_1))
        elif which_team == 2:
            self.widgets[widget_team1_index].configure(text=(self.widgets[widget_team1_index].cget("text") + "\n"))
            tmp = self.widgets[widget_team2_index].cget("text")
            if tmp.isspace() or tmp == "":
                self.widgets[widget_team2_index].configure(text=(tmp + str_event))
            else:
                self.widgets[widget_team2_index].configure(text=(tmp + "\n" + str_event))
            if num_goals_2 != goals_2:
                #time.sleep(1)
                self.widgets[self.get_widget_index("team2goals")].configure(text=str(num_goals_2))
        if which_team == 1 or which_team == 2:
            if self.widgets[widget_team1_index].cget("text").count('\n') > 35:
                # approx 35 rows of text for each box, at least currently...
                f1 = self.get_widget_index("team1listcanvas")
                f2 = self.get_widget_index("team2listcanvas")
                self.widgets[self.get_widget_index("team1cframe")].config(height=850)
                self.widgets[self.get_widget_index("team2cframe")].config(height=850)
                self.widgets[f1].config(scrollregion=self.widgets[f1].bbox(tk.ALL))
                self.widgets[f2].config(scrollregion=self.widgets[f2].bbox(tk.ALL))

        

        # this line below: recursive call to itself with updated stuff in order to do everything the right moment!
        self.frame.after(speed, (lambda : self.min_event(team1, team2, cur_ovr_1, cur_ovr_2, g_coeff, num_subs_1, num_subs_2, num_slots_1, num_slots_2, num_goals_1, num_goals_2, f_time_next, s_time_next, widget_minute_index, widget_team1_index, widget_team2_index)))



    def simulate_match_handler(self, team1: CalendarizedTeam.CalendarizedTeam, team2: CalendarizedTeam.CalendarizedTeam):

        goals_1 = 0
        goals_1t = 0
        goals_2 = 0
        goals_2t = 0

        subs_alr_1 = 0
        subs_alr_2 = 0
        slots_alr_1 = 0
        slots_alr_2 = 0

        players_t1 = 11
        players_t2 = 11
        less_t1 = 0
        less_t2 = 0


        f_time = frapi.get_first_half_mins()
        s_time = frapi.get_second_half_mins()

        if self.home_adv == 1:
            ovr1 = frapi.calc_team_ovr(team1.get_team(), True)
        else:
            ovr1 = frapi.calc_team_ovr(team1.get_team(), False)
        ovr2 = frapi.calc_team_ovr(team2.get_team(), False)

        # higher the goal coeff, more difficult to score a goal (every match has its own for the whole match)
        goal_coeff = frapi.get_goal_coeff(ovr1, ovr2)
        print(f"goal coeff = {goal_coeff}")

        print(team1.get_name(), ovr1, team1.get_market_val(), team1.calendar_index)
        print(team2.get_name(), ovr2, team2.get_market_val(), team2.calendar_index)

        min_label_index = self.get_widget_index("minute")
        team1_widget_index = self.get_widget_index("team1text")
        team2_widget_index = self.get_widget_index("team2text")
            
        # ------------------------ MATCH SIMULATION HERE -----------------

        self.min_event(team1, team2, ovr1, ovr2, goal_coeff, subs_alr_1, subs_alr_2, slots_alr_1, slots_alr_2, goals_1, goals_2,  f_time, s_time, min_label_index, team1_widget_index, team2_widget_index)
        
        # ------------------------ MATCH SIMULATION ABOVE ----------------
        #print("FULL TIME:", team1.get_name(), goals_1, "-", goals_2, team2.get_name())


    def set_team_img(self, team_index: int, is_left_canvas: bool):

        str_index = 1
        if not is_left_canvas:
            str_index = 2

        str_widget = "team" + str(str_index) + "img"

        #bytes_img = dbapi.get_image_from_name(conn.cursor(), name)
        
        bytes_img = self.rankteams[team_index].get_team().get_img()

        file_like=io.BytesIO(bytes_img)
        img = Image.open(file_like)
        if self.old_badges != 0:
            content = img.getbbox()
            img = img.crop(content)
            x, y = img.size
            if x > y:
                img = img.resize((CANVAS_DIMS,int(CANVAS_DIMS*y/x)))
            else:
                img = img.resize((int(CANVAS_DIMS*x/y),CANVAS_DIMS))
        else:
            img = img.resize((CANVAS_DIMS,CANVAS_DIMS))
        imgtk = itk.PhotoImage(img)
        
        self.widgets[self.get_widget_index(str_widget)].create_image(CANVAS_DIMS/2,CANVAS_DIMS/2,anchor=tk.CENTER,image=imgtk)
        self.widgets[self.get_widget_index(str_widget)].imagelist = []
        self.widgets[self.get_widget_index(str_widget)].imagelist.append(imgtk)
        self.place_widget(self.get_widget_index(str_widget))

    def set_friendly_gui(self, t1: Team.Team, t2: Team.Team):

        self.mode = 1

        self.teams[0] = t1
        self.teams[1] = t2

        self.rankteams.clear()
        self.rankteams.append( CalendarizedTeam.CalendarizedTeam(t1, 0, 0, 0, 0, 0, 0, 0, 0) )
        self.rankteams.append( CalendarizedTeam.CalendarizedTeam(t2, 1, 0, 0, 0, 0, 0, 0, 0) )
        
        self.calendar.clear()
        self.cur_day = 0
        self.cur_match = 0

        match1 = (0,1)
        day1 = [match1]
        self.calendar.append(day1)
        self.next_match = self.calendar[0][0]

        self.init_teams_for_match(self.next_match[0], self.next_match[1])


    def search_clubs(self):
        t1, t2 = SearchClubSelector(self)
        
        # after closing of second window
        #self.mode = 1

        self.set_friendly_gui(t1, t2)

        
    def season_init(self, teams_selected: list):

        self.mode = 2

        self.rankteams.clear()
        self.calendar.clear()
        self.cur_day = 0
        self.cur_match = 0
        random_indexes = list(range(len(teams_selected)))
        random.shuffle(random_indexes)
        for i in range(len(teams_selected)):
            self.rankteams.append( CalendarizedTeam.CalendarizedTeam(teams_selected[i], random_indexes[i], 0,0,0,0,0,0,0))

        self.calendar = frapi.circle_method(len(self.rankteams))
        self.next_match = self.calendar[0][0]

        ghost = self.init_teams_for_match(self.next_match[0], self.next_match[1])

        if ghost:
            self.widgets[self.get_widget_index("btnnext")].configure(state='normal')
        else:
            self.widgets[self.get_widget_index("btnnext")].configure(state='disabled')
        return
    

    def random_season_handler(self):

        num = RandomSeasonSelector(self)

        teams = []
        
        for i in range(num):
            tmp = rtapi.get_random_team(self.old_badges, self.selected_pot, self.select_nat_teams)
            while tmp in teams:
                tmp = rtapi.get_random_team(self.old_badges, self.selected_pot, self.select_nat_teams)
            teams.append(tmp)

        #self.mode = 2
        self.season_init(teams)

        return
    
    def real_season_handler(self):
        try:
            comp_id = RealSeasonSelector(self)
            print(comp_id)
            teams_ids = rtapi.get_ids_from_competition(comp_id, 2023)
            teams_selected = rtapi.get_teams_from_ids(teams_ids, self.old_badges)
            
            self.season_init(teams_selected)
            
        except:
            print("error during real season handler..., gui level")
        
        return

    

    def season_handler(self):
        try:
            teams_selected = SeasonHandlerMain(self)

            self.season_init(teams_selected)
            print(self.calendar)

        except:
            pass

        return

    def about_page(self):
        AboutPage(self)
        return

    def extract_league_num(self, c_str: str) -> int:
        return int(c_str.split()[1])
        

    def clear_all_teams(self):
        self.mode = 0
        '''for w in self.widgets:
            w.place_forget()'''
        self.teams.clear()
        self.teams.append(None)
        self.teams.append(None)
        self.rankteams.clear()
        self.update_ranking()
        self.rankteams.append(None)
        self.rankteams.append(None)
        self.calendar.clear()
        self.cur_day=0
        self.cur_match=0
        self.widgets[self.get_widget_index("minute")].configure(text=self.intro_text)
        self.widgets[self.get_widget_index("minute")].lift()
        widgets_to_forget = []
        widgets_to_forget.append(self.widgets[self.get_widget_index("team1name")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("team2name")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("team1country")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("team2country")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("team1img")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("team2img")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("team1listcanvas")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("team2listcanvas")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("team1goals")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("team2goals")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("goalseparator")])
        widgets_to_forget.append(self.widgets[self.get_widget_index("matchstadium")])

        for w in widgets_to_forget:
            w.place_forget()

        # disabling button for match start and next
        self.widgets[self.get_widget_index("btnstart")].configure(state="disabled")
        self.widgets[self.get_widget_index("btnnext")].configure(state="disabled")

    def invert_teams(self):
        #self.teams[0], self.teams[1] = self.teams[1], self.teams[0]
        #self.rankteams[0], self.rankteams[1] = self.rankteams[1], self.rankteams[0]
        self.next_match = (1-self.next_match[0], 1-self.next_match[1])
        self.init_teams_for_match(self.next_match[0], self.next_match[1])

    def random_friendly(self):
        #self.mode = 1
        t1 = rtapi.get_random_team(self.old_badges, self.selected_pot, self.select_nat_teams)
        t2 = rtapi.get_random_team(self.old_badges, self.selected_pot, self.select_nat_teams)

        self.set_friendly_gui(t1,t2)

        return
    
    def prefs_page(self):

        options = PreferencesPage(self)

        self.old_badges = options[0]
        self.selected_pot = options[1]
        self.home_adv = options[2]
        self.select_nat_teams = options[3]

        print(options)

        return


def PreferencesPage(root):
    win_pref = tk.Toplevel()
    #win_pref.geometry("300x600+250+200")
    win_pref.title("About")
    win_pref.resizable(False, False)
    win_pref.grab_set()

    ret_vals = [root.old_badges, root.selected_pot, root.home_adv, root.select_nat_teams]

    def save_changes(destroyer:bool):
        ret_vals[0] = select_badges.get()
        ret_vals[1] = select_pot.get()
        ret_vals[2] = select_home.get()
        ret_vals[3] = select_nat_teams.get()
        if destroyer:
            win_pref.destroy()

    tk.Label(win_pref, text="PREFERENCES MENU", anchor=tk.NW, justify=tk.LEFT, font=("Segoe UI", 11, 'bold')).pack(padx=10, pady=10)

    tk.Label(win_pref, text="Team badges displayed in match", anchor=tk.NW, justify=tk.LEFT, font=("Segoe UI", 9, 'bold')).pack(anchor=tk.NW, padx=10, pady=10)
    select_badges = tk.IntVar(value=root.old_badges)
    tk.Radiobutton(win_pref, variable=select_badges, anchor=tk.W, height=1, width=35, value=0, font=("Segoe UI", 9), text="Current").pack(anchor=tk.NW, padx=10)
    tk.Radiobutton(win_pref, variable=select_badges, anchor=tk.W, height=1, width=35, value=1, font=("Segoe UI", 9), text="Oldest (not always correct)").pack(anchor=tk.NW, padx=10)
    tk.Radiobutton(win_pref, variable=select_badges, anchor=tk.W, height=1, width=35, value=2, font=("Segoe UI", 9), text="Random").pack(anchor=tk.NW, padx=10)
    tk.Radiobutton(win_pref, variable=select_badges, anchor=tk.W, height=1, width=35, value=-1, font=("Segoe UI", 9), text="Second-last").pack(anchor=tk.NW, padx=10)

    # -----

    tk.Label(win_pref, text="Team Randomizer Pots", anchor=tk.NW, justify=tk.LEFT, font=("Segoe UI", 9, 'bold')).pack(anchor=tk.NW, padx=10, pady=10)
    cb_pots = []
    select_pot = tk.IntVar(value=root.selected_pot)
    labels_pots = ["Top 25", "Top 100", "Top 1000"] + [f"Pot {i}" for i in range(1,5)] + ["All For All Enhanced", "Bottom of the ranking"]
    i=0
    for l in labels_pots:
        cb_pots.append( tk.Radiobutton(win_pref, anchor=tk.W, variable=select_pot, value=i, height=1, width=35, font=("Segoe UI", 9), text=l) )
        cb_pots[-1].pack(anchor=tk.NW, padx=10)
        i+=1

    # -----
        
    tk.Label(win_pref, text="Include National Teams in random selection", anchor=tk.NW, justify=tk.LEFT, font=("Segoe UI", 9, 'bold')).pack(anchor=tk.NW, padx=10, pady=10)
    select_nat_teams = tk.BooleanVar(value=root.select_nat_teams)
    tk.Radiobutton(win_pref, anchor=tk.W, variable=select_nat_teams, value=True, height=1, width=35, font=("Segoe UI", 9), text="No").pack(anchor=tk.NW, padx=10)
    tk.Radiobutton(win_pref, anchor=tk.W, variable=select_nat_teams, value=False, height=1, width=35, font=("Segoe UI", 9), text="Yes").pack(anchor=tk.NW, padx=10)

    # -----

    tk.Label(win_pref, text="Location of matches", anchor=tk.NW, justify=tk.LEFT, font=("Segoe UI", 9, 'bold')).pack(anchor=tk.NW, padx=10, pady=10)
    select_home = tk.IntVar(value=root.home_adv)
    tk.Radiobutton(win_pref, variable=select_home, anchor=tk.W, height=1, width=35, value=1, font=("Segoe UI", 9), text="Matches in home team stadium").pack(anchor=tk.NW, padx=10)
    tk.Radiobutton(win_pref, variable=select_home, anchor=tk.W, height=1, width=35, value=0, font=("Segoe UI", 9), text="Matches in neutral locations").pack(anchor=tk.NW, padx=10)

    # ----- save buttons

    tk.Button(win_pref, text="SAVE", width=10, font=("Segoe UI", 10, 'bold'), command=lambda:save_changes(False)).pack(side=tk.LEFT, padx = 10)
    tk.Button(win_pref, text="SAVE & CLOSE", width=20, fg='Red', font=("Segoe UI", 10, 'bold'), command=lambda:save_changes(True)).pack(side=tk.LEFT, padx = 10)


    win_pref.wait_window()
    return ret_vals



def AboutPage(root):
    window_about = tk.Toplevel()
    window_about.geometry("300x175+250+200")
    window_about.title("About")
    window_about.resizable(False, False)
    window_about.grab_set()

    colors = ['#E50000', '#FF8D00', '#FFEE00', '#028121', '#004CFF', '#770088']
    color_index=0

    canvas = tk.Canvas(window_about, width=100, height=100, highlightthickness=0)
    img = Image.open('img/about_emblem.png')
    img.thumbnail((90,90))
    imgtk = itk.PhotoImage(img)
    canvas.create_image(0,0,anchor=tk.NW,image=imgtk)
    canvas.imagelist = []
    canvas.imagelist.append(imgtk)
    canvas.place(x=150, y=30, anchor=tk.N)

    l_text = f'Football Randomizer v{VER} by Diroto, July 2023\nGitHub: td2002\nDiscord: @diroto'
    label = tk.Label(window_about, text=l_text, anchor=tk.CENTER, fg=colors[color_index], font=('Segoe UI', 8, 'bold'))
    label.place(x=150, y=145, anchor=tk.S)

    def change_color(colors, color_index):
        color_index = (color_index+1) % len(colors)
        label.config(fg = colors[color_index])
        window_about.after(1000, lambda : change_color(colors, color_index))
    
    window_about.after(1000, lambda : change_color(colors, color_index))


def RandomSeasonSelector(root) -> int:

    win_r_season = tk.Toplevel()
    win_r_season.geometry("300x200+250+200")
    win_r_season.title("Season Selector")
    win_r_season.resizable(False, False)
    win_r_season.grab_set()

    global amount
    amount = -1

    def save_amount():
        global amount
        try:
            amount = int(entry.get())
            win_r_season.destroy()
        except:
            label.config(text="Amount not valid! Please insert a valid one")

    label = tk.Label(win_r_season, text="Select the amount of teams in the new season")
    label.pack()

    entry = tk.Entry(win_r_season)
    entry.pack()

    btn = tk.Button(win_r_season, text="SAVE & CLOSE", command=save_amount)
    btn.pack()

    win_r_season.wait_window()
    return amount


def RealSeasonSelector(root):
    win_rss = tk.Toplevel()
    win_rss.geometry("300x300+250+200")
    win_rss.title("Real Season Selector")
    win_rss.resizable(False, False)
    win_rss.grab_set()
    
    country_num = 0
    comp_num = 0
    ret_comp_id:str
    
    file_comps = open("files/comps_final.txt", "r")
    data = file_comps.readlines()
    file_comps.close()
    comps = []
    comps.append([])

    tmp = [str.strip(x) for x in data[0].split("§§§")]
    comps[0].append( tmp )

    for s in data:
        tmp = [str.strip(x) for x in s.split("§§§")]
        if comps[-1][0][0] == tmp[0]:
            comps[-1].append( tmp )
        else:
            comps.append([])
            comps[-1].append(tmp)
            
    #print(comps)
    ret_comp_id = comps[0][0][4]
    
    def change_country_left():
        nonlocal country_num
        nonlocal comp_num
        comp_num = 0
        country_num = (country_num-1) % len(comps)
        l_country.config(text = comps[country_num][0][0])
        l_comp_name.config(text = comps[country_num][comp_num][2])
        l_comp_tier.config(text = comps[country_num][comp_num][1])
        return
    def change_country_right():
        nonlocal country_num
        nonlocal comp_num
        comp_num = 0
        country_num = (country_num+1) % len(comps)
        l_country.config(text = comps[country_num][0][0])
        l_comp_name.config(text = comps[country_num][comp_num][2])
        l_comp_tier.config(text = comps[country_num][comp_num][1])
        return
    def change_comp_left():
        nonlocal comp_num
        nonlocal country_num
        comp_num = (comp_num-1) % len(comps[country_num])
        l_comp_name.config(text = comps[country_num][comp_num][2])
        l_comp_tier.config(text = comps[country_num][comp_num][1])
        return
    def change_comp_right():
        nonlocal comp_num
        nonlocal country_num
        comp_num = (comp_num+1) % len(comps[country_num])
        l_comp_name.config(text = comps[country_num][comp_num][2])
        l_comp_tier.config(text = comps[country_num][comp_num][1])
        return
    
    def select_comp():
        nonlocal ret_comp_id
        nonlocal country_num
        nonlocal comp_num
        ret_comp_id = comps[country_num][comp_num][4]
        
    #print(comps)
    l_intro = tk.Label(win_rss, text="Select a real competition")
    l_intro.place(relx=0.5, rely=0.05, anchor=tk.N)
    
    btn_country_left = tk.Button(win_rss, text="<", command=change_country_left)
    btn_country_left.place(relx=0.1, rely=0.3)
    
    l_country = tk.Label(win_rss, text=comps[country_num][0][0])
    l_country.place(relx=0.5, rely=0.3, anchor=tk.N)
    
    btn_country_right = tk.Button(win_rss, text=">", command=change_country_right)
    btn_country_right.place(relx=0.9, rely=0.3, anchor=tk.NE)
    
    btn_comp_left = tk.Button(win_rss, text="<", command=change_comp_left)
    btn_comp_left.place(relx=0.1, rely=0.5)
    
    l_comp_name = tk.Label(win_rss, text=comps[country_num][comp_num][2])
    l_comp_name.place(relx=0.5, rely=0.5, anchor=tk.N)
    
    btn_comp_right = tk.Button(win_rss, text=">", command=change_comp_right)
    btn_comp_right.place(relx=0.9, rely=0.5, anchor=tk.NE)
    
    l_comp_tier = tk.Label(win_rss, text=comps[country_num][comp_num][1])
    l_comp_tier.place(relx=0.5, rely=0.6, anchor=tk.N)
    
    btn_ok = tk.Button(win_rss, text="LOAD COMPETITION", command=select_comp)
    btn_ok.place(relx=0.5, rely=0.9, anchor=tk.N)
    
    win_rss.wait_window()
    return ret_comp_id


def SeasonHandlerMain(root) -> list[Team.Team]:
    win_season_handler = tk.Toplevel()
    win_season_handler.geometry("700x650+100+100")
    win_season_handler.title("Select the teams in the tournament")
    win_season_handler.resizable(False, False)
    win_season_handler.grab_set()

    teams_current = []
    rb = []
    img_rb = []
    basics_got = []
    img_list = []
    imgs_cur = [None] * 10
    label_list = []

    def search_team_by_name_enter_bind(event):
        search_team_by_name()

    def search_team_by_name():

        name = "not working"
        try:
            name = in_text.get()
        except:
            pass
        
        basics_got.clear()
        for i in range(10):
            rb[i].place_forget()
            img_rb[i].place_forget()
        basics = rtapi.get_basics_from_search_name(name, 10)
        i=0
        for t in basics:
            if len(t) > 1:
                basics_got.append( t[0] )
                name = t[1]
                country = t[2]
                rb[i].configure(value=i)
                tmp = name + "\n(" + country + ")"
                rb[i].configure(text=tmp)
                rb[i].place(x=55, y=130+(45*i), anchor=tk.W)
                file_like=io.BytesIO(t[3])
                img = Image.open(file_like)
                img.thumbnail((30,30))
                imgtk = itk.PhotoImage(img)
                imgs_cur[i] = img
                img_rb[i].create_image(15,15,anchor=tk.CENTER,image=imgtk)
                img_rb[i].image = imgtk
                img_rb[i].place(x=20, y=130+(45*i), anchor=tk.W)
                i+=1
            else:
                break

        btn_add.config(state='normal')

    def add_selected_team():
        ind = select1.get()
        team = rtapi.get_team_from_id(basics_got[ind], root.old_badges)
        if team.get_name() not in [teams_current[i].get_name() for i in range(len(teams_current))]:
            teams_current.append(team)
            frame_list.config(height=10+len(teams_current)*40)
        
            img_list.append( tk.Canvas(frame_list, width=30, height=30, highlightthickness=0) )
            #imgtk = copy.deepcopy(img_rb[ind].imagelist)
            imgtk = itk.PhotoImage(imgs_cur[ind])
            img_list[-1].create_image(15,15,anchor=tk.CENTER, image=imgtk)
            img_list[-1].imagelist = []
            img_list[-1].imagelist.append(imgtk)
            img_list[-1].place(x=10, y=25+(len(teams_current)-1)*40, anchor=tk.W)

            tmp = team.get_name() + "\n(" + team.get_country() + ")"
            label_list.append( tk.Label(frame_list, anchor=tk.W, justify=tk.LEFT, text=tmp) )
            label_list[-1].place(x=50, y=25+(len(teams_current)-1)*40, anchor=tk.W)

            #frame_list.config(height=len(label_list)*40)
            list_teams.config(scrollregion=list_teams.bbox(tk.ALL))

        update_after_num_change()

    def remove_last_team():
        img_list[-1].place_forget()
        label_list[-1].place_forget()
        teams_current.pop()
        update_after_num_change()
        return
    
    def update_after_num_change():
        num = len(teams_current)
        if num < 1:
            btn_undo.config(state='disabled', bg='lightgrey')
        elif num >= 1:
            btn_undo.config(state='normal', bg='red')
        if num >= 2:
            btn_ok.config(state='normal', fg='white', bg='darkgreen')
            intro_label.config(text=f'READY TO START WITH THESE {len(teams_current)} TEAMS!')
        elif num < 2:
            btn_ok.config(state='disabled', fg='lightgrey', bg='grey94')
            intro_label.config(text="NOT ENOUGH TEAMS TO START A SEASON")
        

    in_text = tk.Entry(win_season_handler, width=26, font=("Segoe UI", 11), borderwidth=8)
    in_text.bind('<Return>', search_team_by_name_enter_bind)
    in_text.place(x=20, y=20)
    btn1 = tk.Button(win_season_handler, height=1, width=20, command=search_team_by_name, text="SEARCH TEAMS", borderwidth=6)
    btn1.place(x=20, y=60)


    select1 = tk.IntVar()
    for i in range(10):
        rb.append( tk.Radiobutton(win_season_handler, variable=select1, anchor=tk.W, justify=tk.LEFT, height=2, width=35, font=("Segoe UI", 9)) ) 
        img_rb.append( tk.Canvas(win_season_handler, width=30, height=30, highlightthickness=0) )

    btn_add = tk.Button(win_season_handler, command=add_selected_team, text="ADD SELECTED TEAM", width=20, font=("Segoe UI", 10, 'bold'), state='disabled')
    btn_add.place(x=20, y=630, anchor=tk.SW)

    

    list_teams = tk.Canvas(win_season_handler, width=350, height=500, highlightthickness=2, highlightbackground='Black')
    list_teams.place(x=320, y=320, anchor=tk.W)

    frame_list = tk.Frame(list_teams, width=350, height=10)
    list_teams.create_window(0,0, window=frame_list, anchor=tk.CENTER)

    intro_label = tk.Label(win_season_handler, text="NOT ENOUGH TEAMS TO START A SEASON", font=("Segoe UI", 10, 'bold'))
    intro_label.place(x=495, y=30, anchor=tk.N)

    btn_ok = tk.Button(win_season_handler, command=win_season_handler.destroy, text="START SEASON", width=20, font=("Segoe UI", 11, 'bold'), state='disabled')
    btn_ok.place(x=420, y=630, anchor=tk.SW)

    btn_undo = tk.Button(win_season_handler, command=remove_last_team, text="UNDO", width=6, font=("Segoe UI", 10, 'bold'), bg='lightgrey', state='disabled')
    btn_undo.place(x=240, y=630, anchor=tk.SW)

    list_teams.config(scrollregion=list_teams.bbox(tk.ALL))

    ############### Scroll Using Mouse Wheel ###############
    def scroll(event, widget):
        widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def final_scroll(event, widget, func):
        widget.bind_all("<MouseWheel>", func)

    def stop_scroll(event, widget):
        widget.unbind_all("<MouseWheel>")

    list_teams.bind("<Enter>", lambda event: final_scroll(event, list_teams, lambda event: scroll(event, list_teams)))
    list_teams.bind("<Leave>", lambda event: stop_scroll(event, list_teams))
    ################### code for scrolling bottom right box #####################

    win_season_handler.wait_window()
    return teams_current
    


def SearchClubSelector(root):

    win_searcher = tk.Toplevel()
    win_searcher.geometry("700x570+100+100")
    win_searcher.title("Select two teams for a friendly match")
    win_searcher.resizable(False, False)
    win_searcher.grab_set()

    in_text = []
    rb = []
    img_rb = []
    rb.append([])
    rb.append([])
    img_rb.append([])
    img_rb.append([])
    teams_got = []
    teams_got.append([])
    teams_got.append([])

    flags_start = [False, False]

    def search_team_by_name_enter1(event):
        search_team_by_name(0)
    def search_team_by_name_enter2(event):
        search_team_by_name(1)

    in_text.append( tk.Entry(win_searcher, width=26, font=("Segoe UI", 11), borderwidth=8) )
    in_text[0].bind('<Return>', search_team_by_name_enter1)
    in_text[0].place(x=20, y=20)
    btn1 = tk.Button(win_searcher, height=1, width=20, command=(lambda : search_team_by_name(0)), text="SEARCH TEAM 1", borderwidth=6)
    btn1.place(x=20, y=60)


    select1 = tk.IntVar()
    for i in range(10):
        rb[0].append( tk.Radiobutton(win_searcher, variable=select1, anchor=tk.W, height=2, width=34, font=("Segoe UI", 9), justify=tk.LEFT) ) 
        img_rb[0].append( tk.Canvas(win_searcher, width=30, height=30, highlightthickness=0) )

    select2 = tk.IntVar()
    for i in range(10):
        rb[1].append( tk.Radiobutton(win_searcher, variable=select2, anchor=tk.W, height=2, width=34, font=("Segoe UI", 9), justify=tk.LEFT) ) 
        img_rb[1].append( tk.Canvas(win_searcher, width=30, height=30, highlightthickness=0) )
    
    
    in_text.append( tk.Entry(win_searcher, width=24, font=("Segoe UI", 11), borderwidth=8) )
    in_text[1].bind('<Return>', search_team_by_name_enter2)
    in_text[1].place(x=680, y=20, anchor=tk.NE)
    btn2 = tk.Button(win_searcher, height=1, width=20, command=(lambda : search_team_by_name(1)), text="SEARCH TEAM 2", borderwidth=6)
    btn2.place(x=680, y=60, anchor=tk.NE)

    btn_ok = tk.Button(win_searcher, command=win_searcher.destroy, text="START FRIENDLY", width=14, font=("Segoe UI", 10, 'bold'), state='disabled')
    btn_ok.place(x=350, y=40, anchor=tk.N)

    '''img = Image.open('img/loading.gif')
    img = img.resize((30,30))
    imgtk = itk.PhotoImage(img)
    img_rb[0][0].create_image(0,0,anchor=tk.NW,image=imgtk)
    img_rb[0][0].imagelist = []
    img_rb[0][0].imagelist.append(imgtk)'''

    def search_team_by_name(which: int):

        name = "not working"
        try:
            name = in_text[which].get()
        except:
            pass

        teams_got[which].clear()
        for i in range(10):
            rb[which][i].place_forget()
            img_rb[which][i].place_forget()
        basics = rtapi.get_basics_from_search_name(name, 10)
        i=0
        for t in basics:
            if len(t) > 1:
                teams_got[which].append( t[0] )
                name = t[1]
                country = t[2]
                rb[which][i].configure(value=i)
                '''tmp = name + " (" + country + ")"
                if (len(tmp) > 32):'''
                tmp = name + "\n(" + country + ")"
                rb[which][i].configure(text=tmp)
                rb[which][i].place(x=55+(400*which), y=130+(45*i), anchor=tk.W)
                file_like=io.BytesIO(t[3])
                img = Image.open(file_like)
                img.thumbnail((30,30))
                imgtk = itk.PhotoImage(img)
                img_rb[which][i].create_image(15,15,anchor=tk.CENTER,image=imgtk)
                img_rb[which][i].imagelist = []
                img_rb[which][i].imagelist.append(imgtk)
                img_rb[which][i].place(x=20+(400*which), y=130+(45*i), anchor=tk.W)

                flags_start[which] = True
                if flags_start[0] and flags_start[1]:
                    btn_ok.config(state='normal')

                i+=1
            else:
                break


    win_searcher.wait_window()
    #print(teams_got[0][select1.get()].get_name())

    team1 = rtapi.get_team_from_id(teams_got[0][select1.get()], root.old_badges)
    team2 = rtapi.get_team_from_id(teams_got[1][select2.get()], root.old_badges)

    return team1, team2





def main(): 
        
    root = tk.Tk()
    root.title('Football Randomizer')
    root.resizable(False, False)
    root.geometry("1100x700+50+50")
    #root.iconbitmap(default='img/icon.ico')
    app = RootWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
